from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..models.card import Card, validate_color
from ..models.enums import CardType

DEFAULT_CARDS_PATH = Path(__file__).with_name("cards.json")


@dataclass(frozen=True, slots=True)
class CardCollection:
    cards: dict[CardType, Card]
    card_back: str

    def get(self, card_type: CardType | str) -> Card:
        return self.cards[CardType.from_value(card_type)]

    def __iter__(self):
        return iter(self.cards.values())

    def __len__(self) -> int:
        return len(self.cards)


def _read_payload(path: str | Path | None) -> object:
    target = Path(path) if path is not None else DEFAULT_CARDS_PATH
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {target}: {exc}") from exc


def load_card_collection(path: str | Path | None = None) -> CardCollection:
    payload = _read_payload(path)
    if not isinstance(payload, dict):
        raise ValueError("Card data must be a JSON object")

    raw_cards = payload.get("cards")
    if not isinstance(raw_cards, list) or not raw_cards:
        raise ValueError("Card data must contain a non-empty 'cards' list")
    if "card_back" not in payload:
        raise ValueError("Card data is missing required field 'card_back'")

    card_back = validate_color(payload["card_back"], "card_back")
    cards: dict[CardType, Card] = {}
    names: set[str] = set()

    for index, raw_card in enumerate(raw_cards):
        field = f"cards[{index}]"
        if not isinstance(raw_card, dict):
            raise ValueError(f"{field} must be an object")

        name = raw_card.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{field}.name must be a non-empty string")
        normalized_name = name.strip()
        if normalized_name.casefold() in names:
            raise ValueError(f"Duplicate card name: {normalized_name!r}")
        names.add(normalized_name.casefold())

        raw_type = raw_card.get("type")
        if raw_type is None and "card_type" in raw_card:
            raw_type = raw_card["card_type"]
        try:
            card_type = CardType.from_value(raw_type)
        except ValueError as exc:
            raise ValueError(f"{field}.type: {exc}") from exc
        if card_type in cards:
            raise ValueError(f"Duplicate card type: {card_type.value!r}")

        color = validate_color(raw_card.get("color"), f"{field}.color")
        cards[card_type] = Card(name=normalized_name, type=card_type, color=color)

    return CardCollection(cards=cards, card_back=card_back)


def load_cards(path: str | Path | None = None) -> dict[CardType, Card]:
    return load_card_collection(path).cards


def load_cards_list(path: str | Path | None = None) -> list[Card]:
    return list(load_card_collection(path).cards.values())


def load_card_back(path: str | Path | None = None) -> str:
    return load_card_collection(path).card_back
