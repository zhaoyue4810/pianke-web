import os
import types

import app as app_module
import pic_selecter.llm_judge as llm_judge
import pic_selecter.vision as vision


def test_app_main_sets_runtime_env(monkeypatch):
    called = {}

    monkeypatch.setattr(app_module, "setup_logger", lambda folder=None: None)
    monkeypatch.setattr(app_module.threading, "Timer", lambda *args, **kwargs: type("T", (), {"start": lambda self: None})())
    monkeypatch.setattr(app_module.app, "run", lambda **kwargs: called.update(kwargs))
    monkeypatch.setattr(app_module, "SCRIPT_TOKEN", None)
    monkeypatch.setattr(app_module.sys, "argv", ["app.py", "--runtime", "cpu", "--port", "6060", "--no-browser"])

    app_module.main()

    assert os.environ["PIC_SELECTER_RUNTIME"] == "cpu"
    assert called["port"] == 6060


def test_apply_runtime_selection_resets_cached_device(monkeypatch):
    from pic_selecter import vision
    vision._DEVICE = "sentinel"
    monkeypatch.setenv("PIC_SELECTER_RUNTIME", "auto")

    app_module._apply_runtime_selection("cpu")

    assert os.environ["PIC_SELECTER_RUNTIME"] == "cpu"
    assert vision._DEVICE is None


def test_require_engine_local_vlm_defaults_to_expert_vision_stack(monkeypatch):
    calls = {}

    monkeypatch.setattr(app_module, "logger", type("L", (), {"info": lambda self, msg: None})())

    def fake_require_expert_capabilities():
        calls["vision_require"] = True

    def fake_prewarm_all():
        calls["vision_prewarm"] = True

    def fake_require_llm_capabilities(provider="ark", model=None):
        calls["llm_provider"] = provider
        calls["llm_model"] = model

    monkeypatch.setattr(vision, "require_expert_capabilities", fake_require_expert_capabilities)
    monkeypatch.setattr(vision, "prewarm_all", fake_prewarm_all)
    monkeypatch.setattr(llm_judge, "require_llm_capabilities", fake_require_llm_capabilities)

    app_module._require_engine("local_vlm", llm_model="gemma4:12b")

    assert calls == {
        "vision_require": True,
        "vision_prewarm": True,
        "llm_provider": "local_vlm",
        "llm_model": "gemma4:12b",
    }


def test_require_engine_local_vlm_can_disable_aesthetic_stack(monkeypatch):
    calls = {}

    monkeypatch.setattr(app_module, "logger", type("L", (), {"info": lambda self, msg: None})())

    def fake_require_tycoon_capabilities():
        calls["vision_require"] = "tycoon"

    def fake_prewarm_tycoon():
        calls["vision_prewarm"] = "tycoon"

    def fake_require_llm_capabilities(provider="ark", model=None):
        calls["llm_provider"] = provider
        calls["llm_model"] = model

    monkeypatch.setattr(vision, "require_tycoon_capabilities", fake_require_tycoon_capabilities)
    monkeypatch.setattr(vision, "prewarm_tycoon", fake_prewarm_tycoon)
    monkeypatch.setattr(llm_judge, "require_llm_capabilities", fake_require_llm_capabilities)

    app_module._require_engine("local_vlm", llm_model="gemma4:12b", aesthetic_enabled=False)

    assert calls == {
        "vision_require": "tycoon",
        "vision_prewarm": "tycoon",
        "llm_provider": "local_vlm",
        "llm_model": "gemma4:12b",
    }


def test_api_start_forwards_local_vlm_aesthetic_toggle(monkeypatch, tmp_path):
    started = {}

    class FakeThread:
        def __init__(self, target, args, daemon):
            started["target"] = target
            started["args"] = args
            started["daemon"] = daemon

        def start(self):
            started["started"] = True

    monkeypatch.setattr(app_module.threading, "Thread", FakeThread)
    monkeypatch.setattr(app_module, "_apply_runtime_selection", lambda runtime: None)
    app_module.JOB = None
    app_module.SESSION = None

    client = app_module.app.test_client()
    response = client.post(
        "/api/start",
        json={
            "folder": str(tmp_path),
            "engine": "local_vlm",
            "llm_model": "gemma4:12b",
            "aesthetic_enabled": False,
        },
        headers={"Origin": "http://localhost"},
    )

    assert response.status_code == 200
    assert response.get_json()["ok"] is True
    assert app_module.JOB.aesthetic_enabled is False
    assert started["started"] is True
    assert started["args"][-1] is False
    app_module.JOB = None


def test_api_start_rejects_duplicate_job_while_checking(monkeypatch, tmp_path):
    started = {}

    class FakeThread:
        def __init__(self, target, args, daemon):
            started["created"] = True

        def start(self):
            started["started"] = True

    monkeypatch.setattr(app_module.threading, "Thread", FakeThread)
    app_module.JOB = app_module.JobState(
        folder=str(tmp_path),
        dry_run=False,
        mode="copy",
        engine="local_vlm",
        status="checking",
    )
    app_module.SESSION = None

    client = app_module.app.test_client()
    response = client.post(
        "/api/start",
        json={"folder": str(tmp_path), "engine": "fast"},
        headers={"Origin": "http://localhost"},
    )

    assert response.status_code == 409
    assert "已有任务" in response.get_json()["error"]
    assert started == {}
    app_module.JOB = None


def test_api_job_rejected_running_is_cumulative_after_event_window_truncates(tmp_path):
    app_module.JOB = app_module.JobState(
        folder=str(tmp_path),
        dry_run=False,
        mode="move",
        engine="local_vlm",
        status="hashing",
    )
    info_pass = types.SimpleNamespace(
        quality={"auto_reject": False},
        exif_summary={},
        dinov2=None,
        aesthetic_score=None,
        musiq_score=None,
        clipiqa_score=None,
        face_embeddings=[],
    )
    info_reject = types.SimpleNamespace(
        quality={"auto_reject": True, "reject_reason": "bad"},
        exif_summary={},
        dinov2=None,
        aesthetic_score=None,
        musiq_score=None,
        clipiqa_score=None,
        face_embeddings=[],
    )

    for i in range(45):
        app_module._job_event(f"reject-{i}.jpg", str(tmp_path / f"reject-{i}.jpg"), info_reject, None)
    for i in range(25):
        app_module._job_event(f"pass-{i}.jpg", str(tmp_path / f"pass-{i}.jpg"), info_pass, None)

    assert len(app_module.JOB.recent_events) == 60
    assert sum(1 for e in app_module.JOB.recent_events if e.get("reject")) == 35

    client = app_module.app.test_client()
    response = client.get("/api/job")

    assert response.status_code == 200
    assert response.get_json()["rejected_running"] == 45
    app_module.JOB = None


def test_api_job_rejected_running_keeps_rolling_window_outside_local_vlm(tmp_path):
    app_module.JOB = app_module.JobState(
        folder=str(tmp_path),
        dry_run=False,
        mode="move",
        engine="expert",
        status="hashing",
    )
    info_pass = types.SimpleNamespace(
        quality={"auto_reject": False},
        exif_summary={},
        dinov2=None,
        aesthetic_score=None,
        musiq_score=None,
        clipiqa_score=None,
        face_embeddings=[],
    )
    info_reject = types.SimpleNamespace(
        quality={"auto_reject": True, "reject_reason": "bad"},
        exif_summary={},
        dinov2=None,
        aesthetic_score=None,
        musiq_score=None,
        clipiqa_score=None,
        face_embeddings=[],
    )

    for i in range(45):
        app_module._job_event(f"reject-{i}.jpg", str(tmp_path / f"reject-{i}.jpg"), info_reject, None)
    for i in range(25):
        app_module._job_event(f"pass-{i}.jpg", str(tmp_path / f"pass-{i}.jpg"), info_pass, None)

    client = app_module.app.test_client()
    response = client.get("/api/job")

    assert response.status_code == 200
    assert response.get_json()["rejected_running"] == 35
    app_module.JOB = None
