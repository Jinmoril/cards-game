from __future__ import annotations

import os
import threading
from dataclasses import asdict, is_dataclass
from typing import Any, Optional
from uuid import uuid4

from flask import Flask, jsonify, request

from .engine import IllegalActionError, SelectCard
from .session import GameSession

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

_matches: dict[str, GameSession] = {}
_matches_lock = threading.Lock()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _get_match(match_id: str) -> Optional[GameSession]:
    with _matches_lock:
        return _matches.get(match_id)


def _json_body() -> Optional[dict[str, Any]]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None
    return payload


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/play")
def play_page():
    return app.send_static_file("index.html")


@app.post("/api/matches")
def create_match():
    payload = _json_body()
    if payload is None:
        return jsonify(error="Malformed JSON body"), 400

    required = ("player_a", "player_b", "seed")
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    player_a = payload["player_a"]
    player_b = payload["player_b"]
    seed = payload["seed"]
    if not isinstance(player_a, str) or not isinstance(player_b, str):
        return jsonify(error="player_a and player_b must be strings"), 400
    if isinstance(seed, bool) or not isinstance(seed, int):
        return jsonify(error="seed must be an integer"), 400

    match_id = uuid4().hex
    session = GameSession(seed=seed)
    with _matches_lock:
        _matches[match_id] = session
    return jsonify(match_id=match_id), 201


@app.get("/api/matches/<match_id>")
def get_match_view(match_id: str):
    session = _get_match(match_id)
    if session is None:
        return jsonify(error="Unknown match"), 404

    player_id = request.args.get("player")
    if not isinstance(player_id, str) or not player_id:
        return jsonify(error="Missing player query parameter"), 400

    with _matches_lock:
        try:
            view = session.view_for(player_id)
        except IllegalActionError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(_jsonable(view))


@app.post("/api/matches/<match_id>/select")
def select_match_card(match_id: str):
    session = _get_match(match_id)
    if session is None:
        return jsonify(error="Unknown match"), 404

    payload = _json_body()
    if payload is None:
        return jsonify(error="Malformed JSON body"), 400

    required = ("player", "position")
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    player_id = payload["player"]
    position = payload["position"]
    if not isinstance(player_id, str):
        return jsonify(error="player must be a string"), 400
    if isinstance(position, bool) or not isinstance(position, int):
        return jsonify(error="position must be an integer"), 400

    with _matches_lock:
        try:
            session.apply_action(SelectCard(player_id, position))
            view = session.view_for(player_id)
        except IllegalActionError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(_jsonable(view))


def main():
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
