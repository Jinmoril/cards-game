import pytest

from cardgame.data.loader import load_cards
from cardgame.models.enums import CardType
from cardgame.rules import RoundOutcome, beats, compare_cards, round_winner


@pytest.mark.parametrize(
    ("winner", "loser"),
    [
        (CardType.EMPEROR, CardType.CITIZEN),
        (CardType.CITIZEN, CardType.SLAVE),
        (CardType.SLAVE, CardType.EMPEROR),
    ],
)
def test_beats_follows_ecard_cycle(winner, loser):
    assert beats(winner, loser)
    assert not beats(loser, winner)


@pytest.mark.parametrize("card_type", list(CardType))
def test_same_cards_draw(card_type):
    assert compare_cards(card_type, card_type) is RoundOutcome.DRAW
    assert round_winner(card_type, card_type) is None


def test_compare_cards_returns_directional_outcomes():
    assert compare_cards("emperor", "citizen") is RoundOutcome.FIRST_WINS
    assert compare_cards("citizen", "emperor") is RoundOutcome.SECOND_WINS
    assert RoundOutcome.WIN is RoundOutcome.FIRST_WINS
    assert RoundOutcome.LOSS is RoundOutcome.SECOND_WINS


def test_rules_accept_card_objects():
    cards = load_cards()

    assert beats(cards[CardType.SLAVE], cards[CardType.EMPEROR])
    assert round_winner(cards[CardType.CITIZEN], cards[CardType.SLAVE]) is (
        CardType.CITIZEN
    )


@pytest.mark.parametrize("function", [beats, compare_cards, round_winner])
def test_rules_reject_unknown_types(function):
    with pytest.raises(ValueError, match="Invalid card type"):
        function("emperor", "joker")
