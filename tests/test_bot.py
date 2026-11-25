from collections import Counter

import pytest

from cardgame.bot import RandomBot
from cardgame.engine import PLAYER_ONE_ID, PlayerView, new_match


def make_view(cards, committed_pick=None):
    return PlayerView(
        cards=tuple(cards),
        committed_pick=committed_pick,
        stars={"p1": 0, "p2": 0},
    )


@pytest.mark.parametrize("committed", [None, 0, 1, 2])
def test_bot_always_returns_a_legal_position(committed):
    cards = new_match(1).players[PLAYER_ONE_ID].cards
    bot = RandomBot(player_id=PLAYER_ONE_ID, seed=9)

    for _ in range(50):
        action = bot.choose_action(make_view(cards, committed))
        assert action.player_id == PLAYER_ONE_ID
        assert isinstance(action.card_position, int)
        assert 0 <= action.card_position < len(cards)
        assert action.card_position != committed


def test_same_seed_produces_same_sequence():
    cards = new_match(1).players[PLAYER_ONE_ID].cards
    views = [make_view(cards) for _ in range(25)]
    first_bot = RandomBot(player_id=PLAYER_ONE_ID, seed=123)
    second_bot = RandomBot(player_id=PLAYER_ONE_ID, seed=123)

    first = [first_bot.choose_action(view) for view in views]
    second = [second_bot.choose_action(view) for view in views]

    assert first == second
    assert len({action.card_position for action in first}) > 1


def test_1000_picks_are_roughly_uniform():
    cards = new_match(1).players[PLAYER_ONE_ID].cards
    view = make_view(cards)
    bot = RandomBot(player_id=PLAYER_ONE_ID, seed=7)

    counts = Counter(bot.choose_action(view).card_position for _ in range(1000))

    assert set(counts) == {0, 1, 2}
    for position in range(3):
        assert 250 <= counts[position] <= 417, counts
