from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .enums import Phase
from .player import PlayerState

if TYPE_CHECKING:
    from ..engine.events import Event


@dataclass(frozen=True, slots=True)
class GameState:
    players: dict[str, PlayerState]
    round_number: int = 1
    phase: Phase = Phase.SELECTING
    winner: str | None = None
    rng_seed: int = 0
    log: tuple[Event, ...] = ()
