from __future__ import annotations

from dataclasses import dataclass


class IllegalActionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SelectCard:
    player_id: str
    card_position: int
