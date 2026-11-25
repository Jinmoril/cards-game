from __future__ import annotations

from dataclasses import dataclass

from .card import Card


@dataclass(frozen=True, slots=True)
class PlayerState:
    stars: int
    cards: tuple[Card, ...]
    committed_pick: int | None = None
