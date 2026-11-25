from __future__ import annotations

from enum import Enum

from .models.card import Card
from .models.enums import CardType

_DEFEATS: dict[CardType, CardType] = {
    CardType.EMPEROR: CardType.CITIZEN,
    CardType.CITIZEN: CardType.SLAVE,
    CardType.SLAVE: CardType.EMPEROR,
}


class RoundOutcome(str, Enum):
    FIRST_WINS = "first_wins"
    SECOND_WINS = "second_wins"
    DRAW = "draw"
    WIN = "first_wins"
    LOSS = "second_wins"


Outcome = RoundOutcome


def _coerce(value: Card | CardType | str) -> CardType:
    if isinstance(value, Card):
        return value.type
    if isinstance(value, str):
        return CardType.from_value(value)
    return CardType.from_value(getattr(value, "card_type", getattr(value, "type", value)))


def beats(first: Card | CardType | str, second: Card | CardType | str) -> bool:
    return _DEFEATS[_coerce(first)] is _coerce(second)


def compare_cards(
    first: Card | CardType | str, second: Card | CardType | str
) -> RoundOutcome:
    first_type = _coerce(first)
    second_type = _coerce(second)
    if first_type is second_type:
        return RoundOutcome.DRAW
    if _DEFEATS[first_type] is second_type:
        return RoundOutcome.FIRST_WINS
    return RoundOutcome.SECOND_WINS


def round_winner(
    first: Card | CardType | str, second: Card | CardType | str
) -> CardType | None:
    outcome = compare_cards(first, second)
    if outcome is RoundOutcome.DRAW:
        return None
    if outcome is RoundOutcome.FIRST_WINS:
        return _coerce(first)
    return _coerce(second)


determine_winner = round_winner
