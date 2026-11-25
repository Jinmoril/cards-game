from dataclasses import replace

from cardgame.engine import (
    PLAYER_ONE_ID,
    PLAYER_TWO_ID,
    CardsRevealed,
    RoundWon,
    new_match,
    reveal_cards,
    resolve_round,
    select_card,
)
from cardgame.engine.actions import SelectCard
from cardgame.models.enums import CardType, Phase


def commit(state, first_position, second_position):
    return select_card(
        select_card(state, SelectCard(PLAYER_ONE_ID, first_position)),
        SelectCard(PLAYER_TWO_ID, second_position),
    )


def test_first_commit_is_hidden_and_does_not_resolve():
    state = new_match(5)
    after_one = select_card(state, SelectCard(PLAYER_ONE_ID, 0))

    assert after_one.phase is Phase.SELECTING
    assert after_one.log == ()
    assert after_one.round_number == 1
    assert after_one.players[PLAYER_ONE_ID].stars == 0
    assert after_one.players[PLAYER_ONE_ID].committed_pick == 0
    assert after_one.players[PLAYER_TWO_ID].committed_pick is None
    assert state.players[PLAYER_ONE_ID].committed_pick is None


def test_second_commit_reveals_then_awards_star():
    state = commit(new_match(5), 0, 1)

    assert len(state.log) == 2
    revealed, won = state.log
    assert isinstance(revealed, CardsRevealed)
    assert isinstance(won, RoundWon)
    assert revealed.round_number == 1
    assert revealed.picks == {PLAYER_ONE_ID: 0, PLAYER_TWO_ID: 1}
    assert revealed.cards[PLAYER_ONE_ID].type is CardType.EMPEROR
    assert revealed.cards[PLAYER_TWO_ID].type is CardType.CITIZEN
    assert won.winner_id == PLAYER_ONE_ID
    assert won.stars == 1
    assert state.players[PLAYER_ONE_ID].stars == 1
    assert state.players[PLAYER_TWO_ID].stars == 0
    assert state.round_number == 2
    assert state.phase is Phase.RESOLVED
    assert all(player.committed_pick is None for player in state.players.values())


def test_second_player_wins_when_beats_map_favours_them():
    state = commit(new_match(9), 1, 0)

    assert state.log[-1].winner_id == PLAYER_TWO_ID
    assert state.players[PLAYER_TWO_ID].stars == 1
    assert state.players[PLAYER_ONE_ID].stars == 0
    assert state.round_number == 2


def test_reveal_and_resolve_phases_are_explicit():
    state = new_match(11)
    players = dict(state.players)
    players[PLAYER_ONE_ID] = replace(players[PLAYER_ONE_ID], committed_pick=2)
    players[PLAYER_TWO_ID] = replace(players[PLAYER_TWO_ID], committed_pick=0)
    staged = replace(state, players=players)

    revealed = reveal_cards(staged)
    assert revealed.phase is Phase.REVEALED
    assert isinstance(revealed.log[-1], CardsRevealed)

    resolved = resolve_round(revealed)
    assert resolved.phase is Phase.RESOLVED
    assert resolved.players[PLAYER_ONE_ID].stars == 1
    assert isinstance(resolved.log[-1], RoundWon)
