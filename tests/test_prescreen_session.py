import importlib
import sys
import types
from pathlib import Path


def import_app_module():
    sys.modules.setdefault("imagehash", types.SimpleNamespace(phash=lambda *args, **kwargs: "0" * 16))
    try:
        importlib.import_module("flask")
    except ImportError:
        class FakeFlask:
            def __init__(self, *args, **kwargs):
                self.static_folder = kwargs.get("static_folder", "static")

            def route(self, *args, **kwargs):
                return lambda fn: fn

            def after_request(self, fn):
                return fn

            def before_request(self, fn):
                return fn

            def run(self, *args, **kwargs):
                return None

        sys.modules["flask"] = types.SimpleNamespace(
            Flask=FakeFlask,
            Response=lambda *args, **kwargs: types.SimpleNamespace(headers={}, *args, **kwargs),
            abort=lambda *args, **kwargs: None,
            jsonify=lambda *args, **kwargs: args[0] if args else kwargs,
            request=types.SimpleNamespace(path="/", host="localhost:5057", headers={}, method="GET", args={}),
            send_file=lambda *args, **kwargs: None,
            send_from_directory=lambda *args, **kwargs: None,
        )
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def response_json(result):
    return result.get_json() if hasattr(result, "get_json") else result


def make_info(path: Path, score=80.0, auto_reject=False, reason=None):
    app = import_app_module()
    path.write_bytes(b"fake")
    return app.ImageInfo(
        path=str(path),
        phash="0" * 16,
        size=path.stat().st_size,
        mtime=path.stat().st_mtime,
        exif_summary={"width": 1000, "height": 800, "file_size": path.stat().st_size},
        quality={
            "quality_score": score,
            "flags": ["very_blurry"] if auto_reject else [],
            "auto_reject": auto_reject,
            "reject_reason": reason,
        },
    )


def build_session(tmp_path, raw_groups, enabled=True, strength="standard"):
    app = import_app_module()
    return app.build_session_from_groups(
        str(tmp_path),
        dry_run=True,
        mode="copy",
        raw_groups=raw_groups,
        infos=[info for group in raw_groups for info in group],
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
        prescreen_enabled=enabled,
        prescreen_strength=strength,
    )


def build_prescreen_session(tmp_path, infos, enabled=True, strength="standard"):
    app = import_app_module()
    app.LAST_INFOS = infos
    return app.build_prescreen_session_from_infos(
        str(tmp_path),
        dry_run=True,
        mode="copy",
        infos=infos,
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
        prescreen_enabled=enabled,
        prescreen_strength=strength,
    )


def test_global_prescreen_lists_single_auto_rejected_image_for_review(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")

    sess = build_prescreen_session(tmp_path, [bad])

    assert sess.groups == []
    assert sess.prescreen_rejected == [bad.path]
    assert sess.prescreen_reject_reasons[bad.path] == "严重模糊"
    assert sess.prescreen_reviewed is False


def test_global_prescreen_removes_bad_photos_before_tournament(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=5, auto_reject=True, reason="曝光过低")
    good1 = make_info(tmp_path / "good1.jpg", score=72)
    good2 = make_info(tmp_path / "good2.jpg", score=74)

    sess = build_prescreen_session(tmp_path, [bad, good1, good2])

    assert sess.groups == []
    assert sess.prescreen_rejected == [bad.path]
    assert sess.prescreen_reject_reasons[bad.path] == "曝光过低"


def test_global_prescreen_defers_clean_photos_until_review_confirm(tmp_path):
    best = make_info(tmp_path / "best.jpg", score=94)
    ok = make_info(tmp_path / "ok.jpg", score=62)
    weak = make_info(tmp_path / "weak.jpg", score=55)

    sess = build_prescreen_session(tmp_path, [best, ok, weak], enabled=True, strength="standard")

    assert sess.groups == []
    assert sess.prescreen_rejected == []
    assert sess.prescreen_reviewed is False


def test_disabled_prescreen_keeps_original_multi_group_flow(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=5, auto_reject=True, reason="严重模糊")
    good = make_info(tmp_path / "good.jpg", score=90)

    sess = build_session(tmp_path, [[bad, good]], enabled=False)

    group = sess.groups[0]
    assert group.finished is False
    assert group.left == bad.path
    assert group.right == good.path
    assert group.losers == []
    assert group.auto_rejected == []


def test_auto_rejected_api_lists_rejected_items(tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.SESSION = build_prescreen_session(tmp_path, [bad])

    with app.app.app_context():
        payload = response_json(app.api_auto_rejected())

    assert payload["items"][0]["path"] == bad.path
    assert payload["items"][0]["reason"] == "严重模糊"
    assert payload["items"][0]["restored"] is False


def test_restore_rejected_adds_photo_to_winners_once(tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.SESSION = build_prescreen_session(tmp_path, [bad])

    with app.app.test_request_context(
        "/api/restore_rejected",
        method="POST",
        json={"group_id": "__prescreen__", "path": bad.path},
    ):
        first = response_json(app.api_restore_rejected())
    with app.app.test_request_context(
        "/api/restore_rejected",
        method="POST",
        json={"group_id": "__prescreen__", "path": bad.path},
    ):
        second = response_json(app.api_restore_rejected())

    assert first["ok"] is True
    assert second["ok"] is True
    assert app.SESSION.prescreen_restored == [bad.path]


def test_confirm_prescreen_marks_session_reviewed(monkeypatch, tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.LAST_INFOS = [bad]
    app.SESSION = build_prescreen_session(tmp_path, [bad])

    class InlineThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

    monkeypatch.setattr(app.threading, "Thread", InlineThread)

    with app.app.test_request_context("/api/confirm_prescreen", method="POST"):
        payload = response_json(app.api_confirm_prescreen())

    assert payload["ok"] is True
    assert payload["async"] is True
    assert app.SESSION.prescreen_reviewed is True


def test_confirm_prescreen_groups_only_passed_and_restored_photos(monkeypatch, tmp_path):
    app = import_app_module()
    bad_drop = make_info(tmp_path / "drop.jpg", score=8, auto_reject=True, reason="严重模糊")
    bad_restore = make_info(tmp_path / "restore.jpg", score=9, auto_reject=True, reason="曝光过低")
    good = make_info(tmp_path / "good.jpg", score=88)
    infos = [bad_drop, bad_restore, good]
    app.LAST_INFOS = infos
    app.SESSION = app.build_prescreen_session_from_infos(
        str(tmp_path),
        dry_run=True,
        mode="copy",
        infos=infos,
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
            prescreen_enabled=True,
            prescreen_strength="standard",
        )

    class InlineThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args

        def start(self):
            self.target(*self.args)

    monkeypatch.setattr(app.threading, "Thread", InlineThread)
    monkeypatch.setattr(app, "group_infos", lambda accepted_infos, **_kwargs: [accepted_infos])

    with app.app.test_request_context(
        "/api/restore_rejected",
        method="POST",
        json={"group_id": "__prescreen__", "path": bad_restore.path},
    ):
        restored = response_json(app.api_restore_rejected())
    with app.app.test_request_context("/api/confirm_prescreen", method="POST"):
        confirmed = response_json(app.api_confirm_prescreen())

    assert restored["ok"] is True
    assert confirmed["ok"] is True
    all_group_images = [p for group in app.SESSION.groups for p in group.images]
    assert good.path in all_group_images
    assert bad_restore.path in all_group_images
    assert bad_drop.path in all_group_images  # kept only as an auto-rejected loser record
    tournament_images = [
        p
        for group in app.SESSION.groups
        if not group.auto_rejected
        for p in group.images
    ]
    assert good.path in tournament_images
    assert bad_restore.path in tournament_images
    assert bad_drop.path not in tournament_images
    assert app.SESSION.prescreen_reviewed is True
