import json
import sys
import types
import urllib.request
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from pic_selecter import llm_judge


class _FakeModel:
    def __init__(self, model_id):
        self.id = model_id


class _FakeModels:
    def __init__(self, ids):
        self._ids = ids

    def list(self):
        return types.SimpleNamespace(data=[_FakeModel(model_id) for model_id in self._ids])


class _FakeCompletions:
    def __init__(self, capture):
        self._capture = capture

    def create(self, **kwargs):
        self._capture["chat_kwargs"] = kwargs
        message = types.SimpleNamespace(
            content='{"flaws":"subject clear", "verdict":"reject", "reason":"subject clear", "fixable":"no"}'
        )
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)])


class _FakeOpenAI:
    capture = {}
    model_ids = ["gemma4:12b"]

    def __init__(self, api_key, base_url, timeout):
        self.capture["api_key"] = api_key
        self.capture["base_url"] = base_url
        self.capture["timeout"] = timeout
        self.models = _FakeModels(self.model_ids)
        self.chat = types.SimpleNamespace(completions=_FakeCompletions(self.capture))


def _install_fake_openai(monkeypatch):
    _FakeOpenAI.capture = {}
    _FakeOpenAI.model_ids = ["gemma4:12b"]
    fake_module = types.SimpleNamespace(OpenAI=_FakeOpenAI)
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    llm_judge._CLIENT = None
    llm_judge._MODELS_CACHE = {"at": 0.0, "data": None}


class _FakeUrlResponse:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _install_fake_ollama_tags(monkeypatch, models):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append({
            "url": req.full_url,
            "timeout": timeout,
            "body": getattr(req, "data", None),
        })
        return _FakeUrlResponse({"models": models})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return calls


def test_local_vlm_models_default_to_gemma_without_ark_key(monkeypatch):
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_VLM_MODEL", raising=False)
    monkeypatch.delenv("LOCAL_VLM_BASE_URL", raising=False)
    _install_fake_openai(monkeypatch)
    _FakeOpenAI.model_ids = ["gemma4:12b", "text-only:latest"]
    calls = _install_fake_ollama_tags(monkeypatch, [
        {
            "name": "text-only:latest",
            "model": "text-only:latest",
            "capabilities": ["completion"],
        },
        {
            "name": "gemma4:12b",
            "model": "gemma4:12b",
            "capabilities": ["vision", "completion", "thinking"],
        },
    ])

    models = llm_judge.list_models(provider="local_vlm")

    assert models == [{
        "id": "gemma4:12b",
        "tier": "local",
        "label": "gemma4:12b（本地）",
    }]
    assert calls[0]["url"] == "http://127.0.0.1:11434/api/tags"


def test_local_vlm_require_rejects_non_vision_ollama_model(monkeypatch):
    monkeypatch.delenv("LOCAL_VLM_BASE_URL", raising=False)
    _install_fake_openai(monkeypatch)
    _FakeOpenAI.model_ids = ["gemma4:12b", "text-only:latest"]
    _install_fake_ollama_tags(monkeypatch, [
        {
            "name": "text-only:latest",
            "model": "text-only:latest",
            "capabilities": ["completion"],
        },
        {
            "name": "gemma4:12b",
            "model": "gemma4:12b",
            "capabilities": ["vision", "completion"],
        },
    ])

    with pytest.raises(llm_judge.LLMJudgeError, match="text-only:latest"):
        llm_judge.require_llm_capabilities(
            provider="local_vlm",
            model="text-only:latest",
        )


def test_local_vlm_judge_disables_ollama_thinking_with_native_api(monkeypatch):
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_VLM_MODEL", raising=False)
    monkeypatch.delenv("LOCAL_VLM_BASE_URL", raising=False)
    monkeypatch.setattr(llm_judge.time, "sleep", lambda *_args, **_kwargs: None)
    _install_fake_openai(monkeypatch)
    calls = []

    class FakeUrlResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({
                "message": {
                    "role": "assistant",
                    "content": '{"verdict":"pass","reason":"subject clear"}',
                },
                "done_reason": "stop",
            }).encode("utf-8")

    def fake_urlopen(req, timeout):
        calls.append({
            "url": req.full_url,
            "timeout": timeout,
            "body": json.loads(req.data.decode("utf-8")),
        })
        return FakeUrlResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = llm_judge.judge_image(
        Image.new("RGB", (16, 16), "white"),
        model="gemma4:12b",
        strength="standard",
        provider="local_vlm",
    )

    assert calls, "local_vlm should call Ollama native /api/chat so thinking can be disabled"
    assert result == {"verdict": "pass", "reason": "subject clear"}
    assert calls[0]["url"] == "http://127.0.0.1:11434/api/chat"
    body = calls[0]["body"]
    assert body["model"] == "gemma4:12b"
    assert body["stream"] is False
    assert body["think"] is False
    assert body["format"] == "json"
    assert body["options"]["temperature"] == 0.0
    assert body["options"]["num_predict"] == 128
    assert body["options"]["num_ctx"] == 8192
    assert body["messages"][0]["images"][0]
    assert _FakeOpenAI.capture.get("chat_kwargs") is None


def test_local_vlm_ollama_options_can_be_overridden(monkeypatch):
    monkeypatch.setenv("LOCAL_VLM_NUM_PREDICT", "96")
    monkeypatch.setenv("LOCAL_VLM_NUM_CTX", "4096")
    monkeypatch.setattr(llm_judge.time, "sleep", lambda *_args, **_kwargs: None)
    _install_fake_openai(monkeypatch)
    calls = []

    class FakeUrlResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({
                "message": {"content": '{"verdict":"pass","reason":"ok"}'},
                "done_reason": "stop",
            }).encode("utf-8")

    def fake_urlopen(req, timeout):
        calls.append(json.loads(req.data.decode("utf-8")))
        return FakeUrlResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    result = llm_judge.judge_image(
        Image.new("RGB", (16, 16), "white"),
        model="gemma4:12b",
        strength="standard",
        provider="local_vlm",
    )

    assert result == {"verdict": "pass", "reason": "ok"}
    assert calls[0]["options"]["num_predict"] == 96
    assert calls[0]["options"]["num_ctx"] == 4096


def test_local_vlm_errors_are_not_reported_as_decode_failures():
    from pic_selecter import grouper

    reason = grouper._format_process_error(
        llm_judge.LLMJudgeError("本地 VLM 返回空 content")
    )

    assert reason == "VLM 判定失败: 本地 VLM 返回空 content"
    assert "解码失败" not in reason


def test_local_vlm_process_one_propagates_judge_failures(monkeypatch, tmp_path):
    from pic_selecter import grouper
    from pic_selecter.quality import QualityInfo

    photo = tmp_path / "frame.jpg"
    Image.new("RGB", (32, 24), "white").save(photo)

    monkeypatch.setattr(grouper, "_load_image_for_analysis", lambda *_args: Image.new("RGB", (32, 24), "white"))

    import pic_selecter.vision as vision
    import pic_selecter.llm_judge as lj
    import pic_selecter.fast_quality as fast_quality

    monkeypatch.setattr(vision, "extract_dinov2", lambda _img: np.ones(3, dtype=np.float32))
    monkeypatch.setattr(vision, "extract_faces", lambda _img: [])
    monkeypatch.setattr(vision, "extract_aesthetic_score", lambda _img: 6.7)
    monkeypatch.setattr(vision, "extract_musiq_score", lambda _img: 72.0)
    monkeypatch.setattr(vision, "extract_clipiqa_score", lambda _img: 0.71)
    monkeypatch.setattr(lj, "default_model", lambda provider="ark": "gemma4:12b")

    def qinfo(**overrides):
        data = dict(
            blur_score=100.0,
            brightness_mean=128.0,
            brightness_std=20.0,
            contrast_score=20.0,
            overexposed_ratio=0.0,
            underexposed_ratio=0.0,
            entropy=4.0,
            width=32,
            height=24,
            file_size=1000,
            quality_score=80.0,
            flags=[],
            auto_reject=False,
        )
        data.update(overrides)
        return QualityInfo(**data)

    monkeypatch.setattr(fast_quality, "analyze_image_fast", lambda *_args, **_kwargs: qinfo())
    monkeypatch.setattr(
        lj,
        "judge_image",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(lj.LLMJudgeError("ollama down")),
    )

    with pytest.raises(lj.LLMJudgeError, match="ollama down"):
        grouper._process_one(str(photo), engine="local_vlm", llm_model="gemma4:12b")


def test_local_vlm_process_one_defaults_to_aesthetic_metrics(monkeypatch, tmp_path):
    from pic_selecter import grouper
    from pic_selecter.quality import QualityInfo

    photo = tmp_path / "frame.jpg"
    Image.new("RGB", (32, 24), "white").save(photo)

    monkeypatch.setattr(grouper, "_load_image_for_analysis", lambda *_args: Image.new("RGB", (32, 24), "white"))

    import pic_selecter.vision as vision
    import pic_selecter.llm_judge as lj
    import pic_selecter.fast_quality as fast_quality
    import pic_selecter.quality as quality

    monkeypatch.setattr(vision, "extract_dinov2", lambda _img: np.ones(3, dtype=np.float32))
    monkeypatch.setattr(vision, "extract_faces", lambda _img: [{"embedding": np.ones(2, dtype=np.float32)}])
    monkeypatch.setattr(vision, "extract_aesthetic_score", lambda _img: 6.7)
    monkeypatch.setattr(vision, "extract_musiq_score", lambda _img: 72.0)
    monkeypatch.setattr(vision, "extract_clipiqa_score", lambda _img: 0.71)
    monkeypatch.setattr(lj, "default_model", lambda provider="ark": "gemma4:12b")
    monkeypatch.setattr(lj, "judge_image", lambda *_args, **_kwargs: {"verdict": "pass", "reason": "ok"})

    def qinfo(**overrides):
        data = dict(
            blur_score=100.0,
            brightness_mean=128.0,
            brightness_std=20.0,
            contrast_score=20.0,
            overexposed_ratio=0.0,
            underexposed_ratio=0.0,
            entropy=4.0,
            width=32,
            height=24,
            file_size=1000,
            quality_score=80.0,
            flags=[],
            auto_reject=False,
        )
        data.update(overrides)
        return QualityInfo(**data)

    monkeypatch.setattr(fast_quality, "analyze_image_fast", lambda *_args, **_kwargs: qinfo())
    monkeypatch.setattr(quality, "analyze_basic", lambda *_args, **_kwargs: qinfo())

    info, reason = grouper._process_one(str(photo), engine="local_vlm", llm_model="gemma4:12b")

    assert reason is None
    assert info is not None
    assert info.aesthetic_score == 6.7
    assert info.musiq_score == 72.0
    assert info.clipiqa_score == 0.71
    assert info.quality["aesthetic_score"] == 6.7
    assert info.quality["musiq_score"] == 72.0
    assert info.quality["clipiqa_score"] == 0.71


def test_local_vlm_soft_fast_reject_still_uses_vlm_judgement(monkeypatch, tmp_path):
    from pic_selecter import grouper
    from pic_selecter.quality import QualityInfo

    photo = tmp_path / "frame.jpg"
    Image.new("RGB", (32, 24), "white").save(photo)

    monkeypatch.setattr(grouper, "_load_image_for_analysis", lambda *_args: Image.new("RGB", (32, 24), "white"))

    import pic_selecter.fast_quality as fast_quality
    import pic_selecter.llm_judge as lj
    import pic_selecter.quality as quality
    import pic_selecter.vision as vision

    monkeypatch.setattr(vision, "extract_dinov2", lambda _img: np.ones(3, dtype=np.float32))
    monkeypatch.setattr(vision, "extract_faces", lambda _img: [])
    monkeypatch.setattr(vision, "extract_aesthetic_score", lambda _img: 6.7)
    monkeypatch.setattr(vision, "extract_musiq_score", lambda _img: 72.0)
    monkeypatch.setattr(vision, "extract_clipiqa_score", lambda _img: 0.71)
    monkeypatch.setattr(lj, "default_model", lambda provider="ark": "gemma4:12b")
    calls = {"judge": 0}

    def fake_judge(*_args, **_kwargs):
        calls["judge"] += 1
        return {"verdict": "pass", "reason": "vlm accepts"}

    monkeypatch.setattr(lj, "judge_image", fake_judge)

    def qinfo(**overrides):
        data = dict(
            blur_score=100.0,
            brightness_mean=128.0,
            brightness_std=20.0,
            contrast_score=20.0,
            overexposed_ratio=0.0,
            underexposed_ratio=0.0,
            entropy=4.0,
            width=32,
            height=24,
            file_size=1000,
            quality_score=80.0,
            flags=[],
            auto_reject=False,
        )
        data.update(overrides)
        return QualityInfo(**data)

    monkeypatch.setattr(
        fast_quality,
        "analyze_image_fast",
        lambda *_args, **_kwargs: qinfo(
            auto_reject=True,
            flags=["subject_blurry"],
            reject_reason="subject blurry",
        ),
    )
    monkeypatch.setattr(quality, "analyze_basic", lambda *_args, **_kwargs: qinfo())

    info, reason = grouper._process_one(str(photo), engine="local_vlm", llm_model="gemma4:12b")

    assert reason is None
    assert info is not None
    assert calls["judge"] == 1
    assert info.llm_verdict == "pass"
    assert info.llm_reason == "vlm accepts"
    assert info.quality["auto_reject"] is False


def test_local_vlm_process_one_can_disable_aesthetic_metrics(monkeypatch, tmp_path):
    from pic_selecter import grouper
    from pic_selecter.quality import QualityInfo

    photo = tmp_path / "frame.jpg"
    Image.new("RGB", (32, 24), "white").save(photo)

    monkeypatch.setattr(grouper, "_load_image_for_analysis", lambda *_args: Image.new("RGB", (32, 24), "white"))

    import pic_selecter.vision as vision
    import pic_selecter.llm_judge as lj
    import pic_selecter.fast_quality as fast_quality
    import pic_selecter.quality as quality

    calls = {"aesthetic": 0}
    monkeypatch.setattr(vision, "extract_dinov2", lambda _img: np.ones(3, dtype=np.float32))
    monkeypatch.setattr(vision, "extract_faces", lambda _img: [{"embedding": np.ones(2, dtype=np.float32)}])
    monkeypatch.setattr(vision, "extract_aesthetic_score", lambda _img: calls.__setitem__("aesthetic", calls["aesthetic"] + 1))
    monkeypatch.setattr(vision, "extract_musiq_score", lambda _img: 72.0)
    monkeypatch.setattr(vision, "extract_clipiqa_score", lambda _img: 0.71)
    monkeypatch.setattr(lj, "default_model", lambda provider="ark": "gemma4:12b")
    monkeypatch.setattr(lj, "judge_image", lambda *_args, **_kwargs: {"verdict": "pass", "reason": "ok"})

    def qinfo(**overrides):
        data = dict(
            blur_score=100.0,
            brightness_mean=128.0,
            brightness_std=20.0,
            contrast_score=20.0,
            overexposed_ratio=0.0,
            underexposed_ratio=0.0,
            entropy=4.0,
            width=32,
            height=24,
            file_size=1000,
            quality_score=80.0,
            flags=[],
            auto_reject=False,
        )
        data.update(overrides)
        return QualityInfo(**data)

    monkeypatch.setattr(fast_quality, "analyze_image_fast", lambda *_args, **_kwargs: qinfo())
    monkeypatch.setattr(quality, "analyze_basic", lambda *_args, **_kwargs: qinfo())

    info, reason = grouper._process_one(
        str(photo),
        engine="local_vlm",
        llm_model="gemma4:12b",
        aesthetic_enabled=False,
    )

    assert reason is None
    assert info is not None
    assert calls["aesthetic"] == 0
    assert info.aesthetic_score is None
    assert info.musiq_score is None
    assert info.clipiqa_score is None


def test_compute_infos_local_vlm_releases_vision_before_ollama(monkeypatch, tmp_path):
    from pic_selecter import grouper

    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    first.write_bytes(b"fake-a")
    second.write_bytes(b"fake-b")

    order = []

    def fake_scan(_folder):
        return [(str(first), []), (str(second), [])]

    def fake_features(path, *args, **kwargs):
        order.append(("features", Path(path).name))
        rejected = path == str(first)
        return grouper.ImageInfo(
            path=path,
            phash="0" * 16,
            quality={
                "quality_score": 40.0 if rejected else 80.0,
                "auto_reject": rejected,
                "flags": ["very_blurry"] if rejected else [],
                "reject_reason": "主体失焦" if rejected else None,
            },
            aesthetic_score=5.5,
            musiq_score=70.0,
            clipiqa_score=0.55,
        ), None

    def fake_write_cache(folder, infos):
        order.append(("cache", len(infos)))

    def fake_release():
        order.append(("release", None))

    def fake_finalize(info, *args, **kwargs):
        order.append(("ollama", Path(info.path).name))
        assert ("release", None) in order
        return info, None

    monkeypatch.setattr(grouper, "scan_folder", fake_scan)
    monkeypatch.setattr(grouper, "_process_local_vlm_features", fake_features)
    monkeypatch.setattr(grouper, "_write_local_vlm_stage1_cache", fake_write_cache)
    monkeypatch.setattr(grouper, "_release_vision_models_for_local_vlm", fake_release)
    monkeypatch.setattr(grouper, "_finalize_local_vlm_judgement", fake_finalize)
    monkeypatch.setenv("LOCAL_VLM_TWO_STAGE", "1")

    infos, skipped = grouper.compute_infos(
        str(tmp_path),
        engine="local_vlm",
        llm_model="gemma4:12b",
        aesthetic_enabled=True,
    )

    assert skipped == []
    assert [Path(info.path).name for info in infos] == ["a.jpg", "b.jpg"]
    assert order == [
        ("features", "a.jpg"),
        ("features", "b.jpg"),
        ("cache", 2),
        ("release", None),
        ("ollama", "b.jpg"),
    ]


def test_finalize_local_vlm_judgement_propagates_judge_failures(monkeypatch, tmp_path):
    from pic_selecter import grouper

    photo = tmp_path / "frame.jpg"
    Image.new("RGB", (32, 24), "white").save(photo)

    monkeypatch.setattr(grouper, "_load_image_for_analysis", lambda *_args: Image.new("RGB", (32, 24), "white"))

    import pic_selecter.llm_judge as lj
    monkeypatch.setattr(lj, "default_model", lambda provider="local_vlm": "gemma4:12b")
    monkeypatch.setattr(
        lj,
        "judge_image",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(lj.LLMJudgeError("empty content")),
    )

    info = grouper.ImageInfo(path=str(photo), phash="0" * 16, quality={"auto_reject": False})

    with pytest.raises(lj.LLMJudgeError, match="empty content"):
        grouper._finalize_local_vlm_judgement(info, llm_model="gemma4:12b")


def test_compute_infos_local_vlm_defaults_to_inline_judgement(monkeypatch, tmp_path):
    from pic_selecter import grouper

    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    first.write_bytes(b"fake-a")
    second.write_bytes(b"fake-b")
    calls = []

    monkeypatch.delenv("LOCAL_VLM_TWO_STAGE", raising=False)
    monkeypatch.setattr(grouper, "scan_folder", lambda _folder: [(str(first), []), (str(second), [])])

    def fake_two_stage(*_args, **_kwargs):
        pytest.fail("local_vlm should not use two-stage processing unless LOCAL_VLM_TWO_STAGE is enabled")

    def fake_process(path, *_args, **_kwargs):
        calls.append(Path(path).name)
        return grouper.ImageInfo(path=path, phash="0" * 16), None

    monkeypatch.setattr(grouper, "_compute_infos_local_vlm_two_stage", fake_two_stage)
    monkeypatch.setattr(grouper, "_process_one", fake_process)

    infos, skipped = grouper.compute_infos(
        str(tmp_path),
        engine="local_vlm",
        llm_model="gemma4:12b",
        aesthetic_enabled=True,
    )

    assert skipped == []
    assert calls == ["a.jpg", "b.jpg"]
    assert [Path(info.path).name for info in infos] == ["a.jpg", "b.jpg"]


def test_local_vlm_prefilter_only_hard_failures_skip_vlm():
    from pic_selecter import grouper
    from pic_selecter.quality import QualityInfo

    def qinfo(**overrides):
        data = dict(
            blur_score=100.0,
            brightness_mean=128.0,
            brightness_std=20.0,
            contrast_score=20.0,
            overexposed_ratio=0.0,
            underexposed_ratio=0.0,
            entropy=4.0,
            width=32,
            height=24,
            file_size=1000,
            quality_score=20.0,
            flags=[],
            auto_reject=True,
        )
        data.update(overrides)
        return QualityInfo(**data)

    assert grouper._local_vlm_should_skip_llm(qinfo(flags=["very_blurry"])) is True
    assert grouper._local_vlm_should_skip_llm(qinfo(flags=["too_small"])) is True
    assert grouper._local_vlm_should_skip_llm(qinfo(flags=["subject_blurry"])) is False
    assert grouper._local_vlm_should_skip_llm(qinfo(flags=["horizon_severe"])) is False
    assert grouper._local_vlm_should_skip_llm(qinfo(flags=["bad_composition"])) is False
    assert grouper._local_vlm_should_skip_llm(qinfo(reject_reason="score_too_low")) is False
