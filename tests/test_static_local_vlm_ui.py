from pathlib import Path


def test_llm_picker_static_label_is_provider_neutral():
    html = Path("static/index.html").read_text(encoding="utf-8")

    assert 'id="llm-model-label">选择模型</label>' in html
    assert 'id="llm-model-label">选择视觉能力</label>' not in html


def test_processing_rejected_counter_keeps_default_copy_but_local_vlm_overrides():
    html = Path("static/index.html").read_text(encoding="utf-8")
    js = Path("static/app.js").read_text(encoding="utf-8")

    assert '<div class="proc-stat-cap" id="proc-counter-rejected-cap">检出失败</div>' in html
    assert 'currentEngine() === "local_vlm" ? "已淘汰" : "检出失败"' in js


def test_local_vlm_aesthetic_toggle_defaults_on():
    html = Path("static/index.html").read_text(encoding="utf-8")
    js = Path("static/app.js").read_text(encoding="utf-8")

    assert 'id="opt-local-vlm-aesthetic"' in html
    assert '<input type="checkbox" id="opt-local-vlm-aesthetic" checked>' in html
    assert 'aesthetic_enabled,' in js
