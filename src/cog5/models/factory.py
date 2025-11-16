# src/cog5/models/factory.py
from typing import Dict
from .fake import FakeModel

_MODEL_REGISTRY = {
    "fake": FakeModel,
}

def create_model(kind: str = "fake", **kwargs):
    cls = _MODEL_REGISTRY.get(kind)
    if cls is None:
        raise ValueError(f"unknown model kind: {kind}")
    return cls(**kwargs)