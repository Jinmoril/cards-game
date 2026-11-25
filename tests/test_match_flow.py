import pytest

from cardgame.engine import (
    STARS_TO_WIN,
    MatchWon,
    RoundWon,
    new_match,
    select_card,
    view_for,
)
from cardgame.engine.actions import IllegalActionError, SelectCard
from cardgame.models.enums import Phase


def play_winning_round(state, winner="p1"):
    wanted = ("emperor", "citizen") if winner == "p1" else ("citizen", "emperor")
    positions = []
    for player_id, card_type in zip(("p1", "p2"), wanted):
        position = next(
            index
            for index, card in enumerate(state.players[player_id].cards)
            if card.type.value == card_type
        )
        positions.append(position)
    state = select_card(state, SelectCard("p1", positions[0]))
    return select_card(state, SelectCard("p2", positions[1]))


def test_scripted_sequence_reaches_three_stars_and_match_over():
    state = new_match(21)

    for round_number in range(1, STARS_TO_WIN):
        state = play_winning_round(state)
        assert state.players["p1"].stars == round_number
        assert state.players["p2"].stars == 0
        assert state.round_number == round_number + 1
        assert state.winner is None
        assert state.phase is Phase.RESOLVED

    state = play_winning_round(state)

    assert state.players["p1"].stars == STARS_TO_WIN
    assert state.round_number == STARS_TO_WIN + 1
    assert state.phase is Phase.MATCH_OVER
    assert state.winner == "p1"
    assert isinstance(state.log[-2], RoundWon)
    assert isinstance(state.log[-1], MatchWon)
    assert state.log[-1].winner_id == "p1"
    assert view_for(state, "p1")["stars"] == {"p1": 3, "p2": 0}

    with pytest.raises(IllegalActionError):
        select_card(state, SelectCard("p2", 0))


def test_tie_does_not_count_as_a_round_toward_the_match():
    state = select_card(new_match(13), SelectCard("p1", 0))
    state = select_card(state, SelectCard("p2", 0))
    assert state.round_number == 1

    for _ in range(STARS_TO_WIN):
        state = play_winning_round(state)

    assert state.winner == "p1"
    assert state.phase is Phase.MATCH_OVER
    assert state.round_number == STARS_TO_WIN + 1
