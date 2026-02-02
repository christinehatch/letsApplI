# src/discovery/signals/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from discovery.models import Signal, DiscoveredJob


class SignalAdapter(ABC):
    @abstractmethod
    def poll(self, signal: Signal) -> List[DiscoveredJob]:
        """Return metadata-only discovered jobs for this signal."""
        raise NotImplementedError

