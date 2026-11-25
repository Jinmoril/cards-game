from cardgame.engine import (
    PLAYER_ONE_ID,
    PLAYER_TWO_ID,
    CardsRevealed,
    SeededRng,
    TieReshuffle,
    new_match,
    select_card,
)
from cardgame.engine.actions import SelectCard
from cardgame.models.enums import Phase

SEED = 7


def play_tie(seed):
    state = new_match(seed)
    original = tuple(state.players[PLAYER_ONE_ID].cards)
    state = select_card(state, SelectCard(PLAYER_ONE_ID, 0))
    return state, original, select_card(state, SelectCard(PLAYER_TWO_ID, 0))


def test_tie_keeps_round_and_stars_and_reshuffles_hands():
    first_state, original, state = play_tie(SEED)

    assert state.phase is Phase.SELECTING
    assert state.round_number == 1
    assert all(player.stars == 0 for player in state.players.values())
    assert all(player.committed_pick is None for player in state.players.values())
    assert isinstance(state.log[0], CardsRevealed)
    assert isinstance(state.log[1], TieReshuffle)
    assert state.log[1].cards == {
        player_id: player.cards for player_id, player in state.players.items()
    }

    expected = SeededRng(SEED).shuffle(original, salt=1)
    assert tuple(state.players[PLAYER_ONE_ID].cards) == tuple(expected)
    assert tuple(state.players[PLAYER_TWO_ID].cards) == tuple(expected)
    assert tuple(expected) != original
    assert first_state.players[PLAYER_ONE_ID].cards == original


def test_same_seed_reproduces_the_same_reshuffle():
    _, _, first = play_tie(SEED)
    _, _, second = play_tie(SEED)

    assert first.players == second.players
    assert first.log == second.log
    assert first.round_number == second.round_number


def test_different_seeds_can_produce_different_reshuffles():
    _, original, first = play_tie(SEED)
    _, _, other = play_tie(99)

    assert tuple(first.players[PLAYER_ONE_ID].cards) != tuple(
        other.players[PLAYER_ONE_ID].cards
    )
    assert tuple(other.players[PLAYER_ONE_ID].cards) != original
