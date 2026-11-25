from cardgame import server
from cardgame.models.enums import Phase


def client():
    server._matches.clear()
    return server.app.test_client()


def create_match(c, seed=7):
    response = c.post(
        "/api/matches",
        json={"player_a": "p1", "player_b": "p2", "seed": seed},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert "match_id" in body
    return body["match_id"]


def test_create_match_returns_201_and_match_id():
    c = client()
    response = c.post(
        "/api/matches",
        json={"player_a": "p1", "player_b": "p2", "seed": 1},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert isinstance(body["match_id"], str)
    assert body["match_id"]


def test_get_view_hides_opponent_pick_before_reveal():
    c = client()
    match_id = create_match(c, seed=5)

    select_response = c.post(
        f"/api/matches/{match_id}/select",
        json={"player": "p1", "position": 0},
    )
    assert select_response.status_code == 200

    p1_view = c.get(f"/api/matches/{match_id}?player=p1").get_json()
    p2_view = c.get(f"/api/matches/{match_id}?player=p2").get_json()

    assert p1_view["committed_pick"] == 0
    assert p2_view["committed_pick"] is None
    assert "opponent_committed_pick" not in p2_view
    assert "picks" not in p2_view
    assert "log" not in p2_view


def test_select_with_valid_card_returns_200():
    c = client()
    match_id = create_match(c)

    response = c.post(
        f"/api/matches/{match_id}/select",
        json={"player": "p1", "position": 0},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["committed_pick"] == 0
    assert len(body["cards"]) == 3


def test_select_with_illegal_card_returns_400():
    c = client()
    match_id = create_match(c)

    response = c.post(
        f"/api/matches/{match_id}/select",
        json={"player": "p1", "position": 99},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_unknown_match_returns_404():
    c = client()

    response = c.get("/api/matches/unknown?player=p1")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_missing_json_fields_return_400():
    c = client()

    response = c.post("/api/matches", json={"player_a": "p1"})

    assert response.status_code == 400
    assert "error" in response.get_json()


def _pick_for_type(cards, wanted_type):
    for index, card in enumerate(cards):
        if card["type"] == wanted_type:
            return index
    raise AssertionError(f"missing card type {wanted_type}")


def _play_winning_round(c, match_id, winner="p1"):
    p1_view = c.get(f"/api/matches/{match_id}?player=p1").get_json()
    p2_view = c.get(f"/api/matches/{match_id}?player=p2").get_json()
    p1_type, p2_type = ("emperor", "citizen") if winner == "p1" else ("citizen", "emperor")

    r1 = c.post(
        f"/api/matches/{match_id}/select",
        json={"player": "p1", "position": _pick_for_type(p1_view["cards"], p1_type)},
    )
    assert r1.status_code == 200
    r2 = c.post(
        f"/api/matches/{match_id}/select",
        json={"player": "p2", "position": _pick_for_type(p2_view["cards"], p2_type)},
    )
    assert r2.status_code == 200
    return r2.get_json()


def test_full_match_via_api_reaches_match_over_with_winner():
    c = client()
    match_id = create_match(c, seed=21)

    last_view = None
    for _ in range(3):
        last_view = _play_winning_round(c, match_id, winner="p1")

    assert last_view is not None
    assert last_view["stars"]["p1"] == 3
    assert last_view["stars"]["p2"] == 0

    with server._matches_lock:
        state = server._matches[match_id].state
    assert state.phase is Phase.MATCH_OVER
    assert state.winner == "p1"
