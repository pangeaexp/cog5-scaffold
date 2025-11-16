# tests/test_models.py
from src.cog5.models.factory import create_model

def test_fake_model_predict():
    m = create_model("fake", name="tst")
    m.load("dummy")
    out = m.predict({"x": 1})
    assert out["model"] == "tst"
    assert "result" in out