from __future__ import annotations

from dataclasses import dataclass

from ..models.card import Card


@dataclass(frozen=True, slots=True)
class Event:
    pass


@dataclass(frozen=True, slots=True)
class CardsRevealed(Event):
    round_number: int
    picks: dict[str, int]
    cards: dict[str, Card]


@dataclass(frozen=True, slots=True)
class RoundWon(Event):
    round_number: int
    winner_id: str
    stars: int


@dataclass(frozen=True, slots=True)
class TieReshuffle(Event):
    round_number: int
    cards: dict[str, tuple[Card, ...]]


@dataclass(frozen=True, slots=True)
class MatchWon(Event):
    round_number: int
    winner_id: str
    stars: int
