from enum import Enum


class CardType(str, Enum):
    EMPEROR = "emperor"
    CITIZEN = "citizen"
    SLAVE = "slave"

    @classmethod
    def from_value(cls, value: str | "CardType") -> "CardType":
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValueError(f"Invalid card type: {value!r}")
        try:
            return cls(value.strip().lower())
        except ValueError as exc:
            raise ValueError(f"Invalid card type: {value!r}") from exc


CardKind = CardType


class Phase(str, Enum):
    SELECTING = "selecting"
    REVEALED = "revealed"
    RESOLVED = "resolved"
    MATCH_OVER = "match_over"
