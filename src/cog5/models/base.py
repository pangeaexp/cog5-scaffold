# src/cog5/models/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class IModel(ABC):
    @abstractmethod
    def load(self, source: str, **kwargs) -> None:
        """Load model from source (path/uri)."""

    @abstractmethod
    def predict(self, inputs: Any) -> Any:
        """Run inference and return result."""

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return model metadata."""