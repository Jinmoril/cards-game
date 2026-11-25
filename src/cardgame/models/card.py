from __future__ import annotations

import re
from dataclasses import dataclass

from .enums import CardType

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def validate_color(value: object, field_name: str = "color") -> str:
    if not isinstance(value, str) or HEX_COLOR_PATTERN.fullmatch(value) is None:
        raise ValueError(
            f"{field_name} must be a 6-digit hex color such as '#FFFFFF', got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True, init=False)
class Card:
    name: str
    type: CardType
    color: str

    def __init__(
        self,
        name: str,
        type: CardType | str | None = None,
        color: str | None = None,
        *,
        card_type: CardType | str | None = None,
    ) -> None:
        if type is not None and card_type is not None and type != card_type:
            raise ValueError("Conflicting card type values provided")
        resolved_type = type if type is not None else card_type
        if resolved_type is None:
            raise TypeError("Card requires a type")
        if color is None:
            raise TypeError("Card requires a color")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"name must be a non-empty string, got {name!r}")

        object.__setattr__(self, "name", name.strip())
        object.__setattr__(self, "type", CardType.from_value(resolved_type))
        object.__setattr__(self, "color", validate_color(color))

    @property
    def card_type(self) -> CardType:
        return self.type

    @property
    def kind(self) -> CardType:
        return self.type

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Card":
        data = dict(payload)
        if "type" not in data and "card_type" in data:
            data["type"] = data.pop("card_type")
        try:
            return cls(
                name=data["name"],
                type=data["type"],
                color=data["color"],
            )
        except KeyError as exc:
            raise ValueError(f"Card is missing required field: {exc.args[0]!r}") from exc
        except TypeError as exc:
            raise ValueError(str(exc)) from exc

    def __str__(self) -> str:
        return self.name
