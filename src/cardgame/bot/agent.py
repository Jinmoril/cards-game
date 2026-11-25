from __future__ import annotations

from typing import Protocol

from ..engine import PlayerView, SelectCard


class Agent(Protocol):
    def choose_action(self, view: PlayerView) -> SelectCard:
        ...
