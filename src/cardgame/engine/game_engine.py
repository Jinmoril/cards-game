from __future__ import annotations

import secrets
from dataclasses import replace
from typing import TypedDict

from ..data.loader import load_cards
from ..models.card import Card
from ..models.enums import Phase
from ..models.game_state import GameState
from ..models.player import PlayerState
from ..rules import RoundOutcome, compare_cards
from .actions import IllegalActionError, SelectCard
from .events import CardsRevealed, Event, MatchWon, RoundWon, TieReshuffle
from .rng import SeededRng

PLAYER_ONE_ID = "p1"
PLAYER_TWO_ID = "p2"
PLAYER_IDS = (PLAYER_ONE_ID, PLAYER_TWO_ID)
STARS_TO_WIN = 3

_SELECTABLE_PHASES = (Phase.SELECTING, Phase.RESOLVED)


class PlayerView(TypedDict):
    cards: tuple[Card, ...]
    committed_pick: int | None
    stars: dict[str, int]


def new_match(seed: int | None = None) -> GameState:
    resolved_seed = secrets.randbits(64) if seed is None else seed
    if isinstance(resolved_seed, bool) or not isinstance(resolved_seed, int):
        raise ValueError(f"seed must be an integer, got {resolved_seed!r}")
    cards = tuple(load_cards().values())
    players = {player_id: PlayerState(stars=0, cards=cards) for player_id in PLAYER_IDS}
    return GameState(players=players, rng_seed=resolved_seed)


def select_card(state: GameState, action: SelectCard) -> GameState:
    if state.phase not in _SELECTABLE_PHASES:
        raise IllegalActionError(f"cannot select a card in phase {state.phase.value}")
    if action.player_id not in state.players:
        raise IllegalActionError(f"unknown player: {action.player_id!r}")
    player = state.players[action.player_id]
    position = action.card_position
    if (
        isinstance(position, bool)
        or not isinstance(position, int)
        or not 0 <= position < len(player.cards)
    ):
        raise IllegalActionError(
            f"card position out of hand: {position!r} for player {action.player_id!r}"
        )
    if player.committed_pick is not None:
        raise IllegalActionError(
            f"player {action.player_id!r} has already committed this round"
        )

    players = dict(state.players)
    players[action.player_id] = replace(player, committed_pick=position)
    advanced = replace(state, players=players)
    if all(p.committed_pick is not None for p in players.values()):
        advanced = resolve_round(reveal_cards(advanced))
    return advanced


def reveal_cards(state: GameState) -> GameState:
    if state.phase not in _SELECTABLE_PHASES or any(
        p.committed_pick is None for p in state.players.values()
    ):
        raise IllegalActionError("both players must commit before cards can be revealed")
    picks = {
        player_id: player.committed_pick for player_id, player in state.players.items()
    }
    cards = {
        player_id: player.cards[player.committed_pick]
        for player_id, player in state.players.items()
    }
    event = CardsRevealed(
        round_number=state.round_number, picks=picks, cards=cards
    )
    return replace(state, phase=Phase.REVEALED, log=state.log + (event,))


def resolve_round(state: GameState) -> GameState:
    if state.phase is not Phase.REVEALED:
        raise IllegalActionError(f"cannot resolve phase {state.phase.value}")
    player_ids = list(state.players)
    first = state.players[player_ids[0]]
    second = state.players[player_ids[1]]
    if first.committed_pick is None or second.committed_pick is None:
        raise IllegalActionError("both players must commit before resolving")

    outcome = compare_cards(
        first.cards[first.committed_pick], second.cards[second.committed_pick]
    )
    if outcome is RoundOutcome.DRAW:
        rng = SeededRng(state.rng_seed)
        players = {
            player_id: replace(
                player,
                cards=rng.shuffle(player.cards, salt=state.round_number),
                committed_pick=None,
            )
            for player_id, player in state.players.items()
        }
        event = TieReshuffle(
            round_number=state.round_number,
            cards={player_id: player.cards for player_id, player in players.items()},
        )
        return replace(
            state,
            players=players,
            phase=Phase.SELECTING,
            log=state.log + (event,),
        )

    winner_id = player_ids[0] if outcome is RoundOutcome.FIRST_WINS else player_ids[1]
    players = {}
    for player_id, player in state.players.items():
        stars = player.stars + 1 if player_id == winner_id else player.stars
        players[player_id] = replace(player, stars=stars, committed_pick=None)
    winner_stars = players[winner_id].stars
    event = RoundWon(
        round_number=state.round_number, winner_id=winner_id, stars=winner_stars
    )
    resolved = replace(
        state,
        players=players,
        round_number=state.round_number + 1,
        phase=Phase.RESOLVED,
        log=state.log + (event,),
    )
    if winner_stars >= STARS_TO_WIN:
        match_event = MatchWon(
            round_number=state.round_number,
            winner_id=winner_id,
            stars=winner_stars,
        )
        return replace(
            resolved,
            winner=winner_id,
            phase=Phase.MATCH_OVER,
            log=resolved.log + (match_event,),
        )
    return resolved


def view_for(state: GameState, player_id: str) -> PlayerView:
    if player_id not in state.players:
        raise IllegalActionError(f"unknown player: {player_id!r}")
    player = state.players[player_id]
    return PlayerView(
        cards=tuple(player.cards),
        committed_pick=player.committed_pick,
        stars={other_id: other.stars for other_id, other in state.players.items()},
    )
