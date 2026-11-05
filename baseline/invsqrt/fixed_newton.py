
import math

from config import InverseSqrtConfig
from fixed_point import (
    to_fixed,
    from_fixed,
    fixed_multiply,
    fixed_square,
)

MAX_INPUT = 3_133_452




def inverse_sqrt_fixed_integer(
    x,
    fractional_bits=40,
    iterations=6,
):
    """Return floor(approximation * 2**fractional_bits).

    This is a classical fixed-point model, not a quantum circuit.
    All arithmetic in the refinement uses integers.
    """
    if isinstance(x, bool) or not isinstance(x, int):
        raise TypeError("x must be an integer")

    if not 1 <= x <= MAX_INPUT:
        raise ValueError(f"x must be between 1 and {MAX_INPUT}")

    if (
        isinstance(fractional_bits, bool)
        or not isinstance(fractional_bits, int)
        or fractional_bits < 32
    ):
        raise ValueError("fractional_bits must be an integer >= 32")

    if (
        isinstance(iterations, bool)
        or not isinstance(iterations, int)
        or iterations < 0
    ):
        raise ValueError("iterations must be a nonnegative integer")

    F = fractional_bits
    scale = 1 << F

    # x = m * 4**k, where 1 <= m < 4.
    k = (x.bit_length() - 1) // 2

    # Exact normalized input for the supported input range.
    # m_fixed represents m * 2**F.
    m_fixed = x << (F - 2 * k)

    # For every normalized input, 0.5 is a safe starting guess:
    # 0.5 <= sqrt(m) * y < 1.
    y = scale // 2

    for _ in range(iterations):
        # y_next = y * (3 - m*y*y) / 2
        #
        # Keep the square and products at full precision.
        # Truncate only at the end of the Newton step.
        numerator = y * (
            3 * scale**3 - m_fixed * y * y
        )
        y = numerator >> (3 * F + 1)

    # 1/sqrt(x) = (1/sqrt(m)) / 2**k.
    # The returned integer still has F fractional bits.
    return y >> k


def inverse_sqrt_fixed(x, fractional_bits=40, iterations=6):
    """Convenient floating-point view of the fixed-point result."""
    result = inverse_sqrt_fixed_integer(
        x,
        fractional_bits=fractional_bits,
        iterations=iterations,
    )
    return result / (1 << fractional_bits)







def main():
    tolerance = 2**-24

    for x in (1, 4, 16, 256, 10_000, 1_000_000, MAX_INPUT):
        approximation = inverse_sqrt_fixed(x)

        # Floating point is used only to evaluate the model's error.
        actual = 1 / math.sqrt(x)
        relative_error = abs(approximation - actual) / actual

        print(
            f"x={x:>9}  "
            f"result={approximation:.12f}  "
            f"relative_error={relative_error:.3e}  "
            f"within_target={relative_error <= tolerance}"
        )


if __name__ == "__main__":
    main()
