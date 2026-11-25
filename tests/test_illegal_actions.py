from dataclasses import replace

import pytest

from cardgame.engine import (
    PLAYER_ONE_ID,
    new_match,
    select_card,
    view_for,
)
from cardgame.engine.actions import IllegalActionError, SelectCard
from cardgame.models.enums import Phase


@pytest.mark.parametrize("phase", [Phase.REVEALED, Phase.MATCH_OVER])
def test_wrong_phase_is_rejected(phase):
    state = replace(new_match(1), phase=phase)
    with pytest.raises(IllegalActionError, match="phase"):
        select_card(state, SelectCard(PLAYER_ONE_ID, 0))


def test_unknown_player_is_rejected():
    state = new_match(1)
    with pytest.raises(IllegalActionError, match="unknown player"):
        select_card(state, SelectCard("nobody", 0))


@pytest.mark.parametrize("position", [-1, 3, 99])
def test_out_of_hand_position_is_rejected(position):
    state = new_match(1)
    with pytest.raises(IllegalActionError, match="card position"):
        select_card(state, SelectCard(PLAYER_ONE_ID, position))


def test_non_integer_position_is_rejected():
    state = new_match(1)
    with pytest.raises(IllegalActionError, match="card position"):
        select_card(state, SelectCard(PLAYER_ONE_ID, "0"))


def test_committing_twice_in_one_round_is_rejected():
    state = select_card(new_match(1), SelectCard(PLAYER_ONE_ID, 0))
    with pytest.raises(IllegalActionError, match="already committed"):
        select_card(state, SelectCard(PLAYER_ONE_ID, 1))


def test_unknown_player_in_view_is_rejected():
    state = new_match(1)

    with pytest.raises(IllegalActionError, match="unknown player"):
        view_for(state, "nobody")
