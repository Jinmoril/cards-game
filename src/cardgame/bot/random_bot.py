from __future__ import annotations

from ..engine import IllegalActionError, PlayerView, SeededRng, SelectCard


class RandomBot:
    def __init__(self, player_id: str, seed: int) -> None:
        self.player_id = player_id
        self.seed = seed
        self._rng = SeededRng(seed)
        self._draws = 0

    def choose_action(self, view: PlayerView) -> SelectCard:
        committed = view["committed_pick"]
        legal_positions = [
            position
            for position in range(len(view["cards"]))
            if position != committed
        ]
        if not legal_positions:
            raise IllegalActionError("no legal card positions remain in hand")
        chosen = self._rng.shuffle(legal_positions, salt=self._draws)[0]
        self._draws += 1
        return SelectCard(player_id=self.player_id, card_position=chosen)
