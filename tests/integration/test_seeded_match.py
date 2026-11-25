from cardgame.bot import RandomBot
from cardgame.models.enums import Phase
from cardgame.session import GameSession

MAX_STEPS = 200


def run_match(seed):
    session = GameSession(
        seed=seed,
        agents={
            "p1": RandomBot(player_id="p1", seed=seed * 2 + 1),
            "p2": RandomBot(player_id="p2", seed=seed * 2 + 2),
        },
    )
    steps = 0
    while session.state.phase is not Phase.MATCH_OVER and steps < MAX_STEPS:
        session.step()
        steps += 1
    return session, steps


def test_seeded_match_reaches_match_over_within_bounded_rounds():
    session, steps = run_match(42)

    assert steps < MAX_STEPS
    assert session.state.round_number <= MAX_STEPS
    assert session.state.phase is Phase.MATCH_OVER
    assert session.state.winner in ("p1", "p2")


def test_replaying_same_seed_yields_identical_final_state():
    first, _ = run_match(77)
    second, _ = run_match(77)

    assert first.state == second.state
