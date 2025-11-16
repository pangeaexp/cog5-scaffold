# src/cog5/models/fake.py
from .base import IModel
from typing import Any, Dict

class FakeModel(IModel):
    def __init__(self, name: str = "fake"):
        self._name = name
        self._loaded = False

    def load(self, source: str, **kwargs) -> None:
        self._source = source
        self._loaded = True

    def predict(self, inputs: Any) -> Any:
        if not self._loaded:
            raise RuntimeError("model not loaded")
        return {"result": str(inputs), "model": self._name}

    def metadata(self) -> Dict[str, Any]:
        return {"name": self._name, "type": "fake", "source": getattr(self, "_source", None)}