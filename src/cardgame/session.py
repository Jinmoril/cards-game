from __future__ import annotations

from collections.abc import Mapping

from .bot.agent import Agent
from .engine import (
    PLAYER_IDS,
    IllegalActionError,
    PlayerView,
    SelectCard,
    new_match,
    select_card,
    view_for,
)
from .models.enums import Phase
from .models.game_state import GameState


class GameSession:
    def __init__(
        self,
        seed: int | None = None,
        *,
        state: GameState | None = None,
        agents: Mapping[str, Agent] | None = None,
    ) -> None:
        self.state = state if state is not None else new_match(seed)
        self._agents: dict[str, Agent] = dict(agents) if agents is not None else {}

    def register_agent(self, player_id: str, agent: Agent) -> None:
        if player_id not in PLAYER_IDS:
            raise IllegalActionError(f"unknown player: {player_id!r}")
        self._agents[player_id] = agent

    def view_for(self, player_id: str) -> PlayerView:
        return view_for(self.state, player_id)

    def apply_action(self, action: SelectCard) -> GameState:
        self.state = select_card(self.state, action)
        return self.state

    def step(self) -> GameState:
        if self.state.phase is Phase.MATCH_OVER:
            return self.state
        for player_id in PLAYER_IDS:
            if self.state.players[player_id].committed_pick is None:
                agent = self._agents.get(player_id)
                if agent is None:
                    raise IllegalActionError(f"no agent registered for {player_id!r}")
                self.apply_action(agent.choose_action(self.view_for(player_id)))
                return self.state
        return self.state
