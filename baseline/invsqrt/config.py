
from dataclasses import dataclass


@dataclass(frozen=True)
class InverseSqrtConfig:
    fractional_bits: int = 32
    newton_iterations: int = 4

    def __post_init__(self):
        if self.fractional_bits < 0:
            raise ValueError("fractional_bits must be nonnegative")

        if self.newton_iterations < 0:
            raise ValueError("newton_iterations must be nonnegative")
