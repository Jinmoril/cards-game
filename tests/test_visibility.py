from dataclasses import replace

from cardgame.engine import (
    PLAYER_ONE_ID,
    PLAYER_TWO_ID,
    new_match,
    reveal_cards,
    select_card,
    view_for,
)
from cardgame.engine.actions import SelectCard
from cardgame.models.enums import Phase


def test_view_shows_only_own_commit_and_both_star_counts():
    state = select_card(new_match(3), SelectCard(PLAYER_ONE_ID, 0))

    first_view = view_for(state, PLAYER_ONE_ID)
    second_view = view_for(state, PLAYER_TWO_ID)

    assert set(first_view) == {"cards", "committed_pick", "stars"}
    assert first_view["cards"] == state.players[PLAYER_ONE_ID].cards
    assert first_view["committed_pick"] == 0
    assert first_view["stars"] == {PLAYER_ONE_ID: 0, PLAYER_TWO_ID: 0}
    assert second_view["committed_pick"] is None
    assert second_view["cards"] == state.players[PLAYER_TWO_ID].cards
    assert second_view["stars"] == first_view["stars"]


def test_view_never_exposes_opponent_pick_even_after_reveal():
    state = new_match(7)
    players = dict(state.players)
    players[PLAYER_ONE_ID] = replace(players[PLAYER_ONE_ID], committed_pick=0)
    players[PLAYER_TWO_ID] = replace(players[PLAYER_TWO_ID], committed_pick=2)
    revealed = reveal_cards(replace(state, players=players))
    assert revealed.phase is Phase.REVEALED

    first_view = view_for(revealed, PLAYER_ONE_ID)
    second_view = view_for(revealed, PLAYER_TWO_ID)

    assert first_view["committed_pick"] == 0
    assert second_view["committed_pick"] == 2
    assert "opponent_committed_pick" not in first_view
    assert "picks" not in first_view
    assert "log" not in first_view
    assert set(first_view["stars"]) == {PLAYER_ONE_ID, PLAYER_TWO_ID}
    assert first_view["cards"] == revealed.players[PLAYER_ONE_ID].cards
    assert second_view["cards"] == revealed.players[PLAYER_TWO_ID].cards


def test_view_does_not_mutate_state():
    state = select_card(new_match(1), SelectCard(PLAYER_ONE_ID, 1))
    before = state.players[PLAYER_TWO_ID]

    view_for(state, PLAYER_ONE_ID)

    assert state.players[PLAYER_TWO_ID] is before
    assert state.players[PLAYER_TWO_ID].committed_pick is None
