from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from ..models import AdapterResult


class HostAdapter(ABC):
    host: str

    @abstractmethod
    def capability_profile(self) -> Dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def activate(self, project_id: str, skill_ids: List[str]) -> AdapterResult:
        raise NotImplementedError

    @abstractmethod
    def deactivate(self, project_id: str, skill_ids: List[str]) -> AdapterResult:
        raise NotImplementedError
