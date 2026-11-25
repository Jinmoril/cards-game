from cardgame.bot import RandomBot
from cardgame.engine import (
    PLAYER_IDS,
    STARS_TO_WIN,
    SelectCard,
)
from cardgame.models.enums import Phase
from cardgame.session import GameSession


class RecordingAgent:
    def __init__(self, delegate):
        self.delegate = delegate
        self.actions = []

    def choose_action(self, view):
        action = self.delegate.choose_action(view)
        assert 0 <= action.card_position < len(view["cards"])
        assert action.card_position != view["committed_pick"]
        self.actions.append(action)
        return action


def make_session(seed=11):
    agents = {
        player_id: RecordingAgent(
            RandomBot(player_id=player_id, seed=seed + offset)
        )
        for offset, player_id in enumerate(PLAYER_IDS, start=1)
    }
    return GameSession(seed=seed, agents=agents), agents


def test_session_view_hides_opponent_pick():
    session = GameSession(seed=5)
    session.apply_action(SelectCard("p1", 0))

    first_view = session.view_for("p1")
    second_view = session.view_for("p2")

    assert first_view["committed_pick"] == 0
    assert second_view["committed_pick"] is None
    assert set(second_view) == {"cards", "committed_pick", "stars"}
    assert "opponent_committed_pick" not in second_view
    assert second_view["cards"] == session.state.players["p2"].cards
    assert second_view["stars"] == {"p1": 0, "p2": 0}


def test_full_match_between_random_bots_terminates():
    session, agents = make_session()

    for _ in range(200):
        if session.state.phase is Phase.MATCH_OVER:
            break
        session.step()

    assert session.state.phase is Phase.MATCH_OVER
    assert session.state.winner in PLAYER_IDS
    assert session.state.players[session.state.winner].stars == STARS_TO_WIN
    assert all(action.card_position in (0, 1, 2) for action in agents["p1"].actions)
    assert all(action.card_position in (0, 1, 2) for action in agents["p2"].actions)
    assert agents["p1"].actions and agents["p2"].actions
