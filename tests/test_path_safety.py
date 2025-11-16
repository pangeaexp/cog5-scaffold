# tests/test_path_safety.py
import pytest
from src.core import ensure_within_base
import pathlib, os

def test_outside_path_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("COG5_WORKDIR", str(tmp_path / "ws"))
    ws = (tmp_path / "ws"); ws.mkdir()
    outside = str(tmp_path / "outside.txt")
    with pytest.raises(ValueError):
        ensure_within_base(outside)