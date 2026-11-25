import json

import pytest

from cardgame.data.loader import load_card_collection, load_cards, load_cards_list
from cardgame.models.enums import CardType


def test_load_bundled_cards():
    collection = load_card_collection()

    assert len(collection) == 3
    assert [card.name for card in collection] == ["Emperor", "Citizen", "Slave"]
    assert set(collection.cards) == set(CardType)
    assert collection.get("emperor").name == "Emperor"
    assert collection.card_back == "#1E1E24"


def test_loaded_cards_keep_expected_colors():
    cards = load_cards()

    assert cards[CardType.EMPEROR].color == "#C9A227"
    assert cards[CardType.CITIZEN].color == "#2F6FB3"
    assert cards[CardType.SLAVE].color == "#8B5A2B"
    assert [card.name for card in load_cards_list()] == [
        "Emperor",
        "Citizen",
        "Slave",
    ]


@pytest.mark.parametrize(
    "bad_color",
    ["C9A227", "#C9A22", "#GGGGGG", "#C9A2277", 123456, None],
)
def test_loader_rejects_invalid_card_colors(tmp_path, bad_color):
    payload = {
        "cards": [{"name": "Emperor", "type": "emperor", "color": bad_color}],
        "card_back": "#1E1E24",
    }
    path = tmp_path / "cards.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=r"cards\[0\]\.color"):
        load_card_collection(path)


@pytest.mark.parametrize("bad_color", ["1E1E24", "#12345", "#ZZZZZZ", 42, None])
def test_loader_rejects_invalid_card_back(tmp_path, bad_color):
    payload = {
        "cards": [{"name": "Citizen", "type": "citizen", "color": "#2F6FB3"}],
        "card_back": bad_color,
    }
    path = tmp_path / "cards.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="card_back"):
        load_card_collection(path)


def test_loader_rejects_unknown_card_type(tmp_path):
    payload = {
        "cards": [{"name": "Joker", "type": "joker", "color": "#FFFFFF"}],
        "card_back": "#1E1E24",
    }
    path = tmp_path / "cards.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid card type"):
        load_card_collection(path)


def test_loader_rejects_duplicate_card_types(tmp_path):
    payload = {
        "cards": [
            {"name": "Emperor", "type": "emperor", "color": "#C9A227"},
            {"name": "Ruler", "type": "emperor", "color": "#C9A227"},
        ],
        "card_back": "#1E1E24",
    }
    path = tmp_path / "cards.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate card type"):
        load_card_collection(path)
