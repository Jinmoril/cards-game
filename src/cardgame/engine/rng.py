from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class SeededRng:
    seed: int

    def shuffle(self, items: Sequence[T], *, salt: int = 0) -> list[T]:
        shuffled = list(items)
        random.Random(f"cardgame:{self.seed}:{salt}").shuffle(shuffled)
        return shuffled
