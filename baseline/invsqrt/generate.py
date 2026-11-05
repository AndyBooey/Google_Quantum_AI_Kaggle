"""Six-step inverse-square-root phase circuit.

Matches fixed_newton.py with 40 fractional bits and six iterations.
Prioritizes correctness over circuit size.
"""

from fractions import Fraction

import kickmix as km

try:
    from .arithmetic import reversible_multiply, reversible_square
except ImportError:
    from arithmetic import reversible_multiply, reversible_square


def allocate_clean(builder, width):
    register = builder.alloc_qubits(width)
    builder.reset(register)
    return register


def normalize(builder, x, flags, *, inverse=False):
    """Shift x left by two bits per leading zero pair.

    flags stores the number of shifts in unary.
    """
    indices = (
        reversed(range(len(flags)))
        if inverse
        else range(len(flags))
    )

    for i in indices:
        lanes = (x[2*i::2], x[2*i+1::2])

        if inverse:
            for lane in lanes:
                builder.right_rotate(lane, 1, control=flags[i])

        # Compute or erase the flag for a top pair of 00.
        builder.x(x[-2:])
        builder.ccx(x[-2], x[-1], flags[i])
        builder.x(x[-2:])

        if not inverse:
            for lane in lanes:
                builder.left_rotate(lane, 1, control=flags[i])


def shift_result(builder, result, flags, F, *, inverse=False):
    """Shift left once per set flag, or undo those shifts."""
    indices = (
        reversed(range(len(flags)))
        if inverse
        else range(len(flags))
    )

    for i in indices:
        # The extra high bit is zero, so rotation acts as a shift.
        lane = result[i:i+F+2]

        if inverse:
            builder.right_rotate(lane, 1, control=flags[i])
        else:
            builder.left_rotate(lane, 1, control=flags[i])


def build_newton_step(
    builder,
    m,
    y,
    new_y,
    workspace,
    *,
    fractional_bits=40,
):
    """XOR one refined estimate into new_y.

    m represents the normalized input, with F fractional bits.
    y and new_y also have F fractional bits.

    Preserve m and y, and restore workspace to zero.
    Calling this function twice restores new_y.
    """
    F = fractional_bits
    square, correction, numerator = workspace

    expected = (
        F + 2,       # m
        F + 1,       # y
        F + 1,       # new_y
        2*F + 2,     # square
        3*F + 4,     # correction
        4*F + 5,     # numerator
    )
    actual = tuple(
        map(len, (m, y, new_y, square, correction, numerator))
    )

    if actual != expected:
        raise ValueError(
            f"Expected register widths {expected}, got {actual}"
        )

    # Full integer square: scale 2**(2F).
    reversible_square(builder, y, square)

    # Full integer m*y*y: scale 2**(3F).
    reversible_multiply(builder, m, square, correction)

    # correction = 3*2**(3F) - m_integer*y_integer**2.
    # Complement plus C+1 implements C - correction.
    constant = (3 << (3*F)) + 1
    builder.x(correction)
    builder.iadd(constant, target=correction)

    # Full numerator: scale 2**(4F).
    reversible_multiply(builder, y, correction, numerator)

    # Divide by 2 and rescale to F fractional bits.
    # Copy selected bits; retain discarded bits for cleanup.
    start = 3*F + 1
    builder.cx(numerator[start:start+F+1], new_y)

    # Uncompute all intermediate values.
    reversible_multiply(
        builder, y, correction, numerator, inverse=True
    )

    builder.isub(constant, target=correction)
    builder.x(correction)

    reversible_multiply(
        builder, m, square, correction, inverse=True
    )
    reversible_square(builder, y, square, inverse=True)


def generate_inverse_sqrt():
    F = 40
    iterations = 6
    n_p = 10

    builder = km.CircuitBuilder()

    # The official verifier permits only this named register.
    x = builder.create_quantum_register(22, name="x")

    flags = allocate_clean(builder, n_p)
    m = allocate_clean(builder, F + 2)

    # Preserve previous estimates so every step can be undone.
    estimates = [
        allocate_clean(builder, F + 1)
        for _ in range(iterations + 1)
    ]

    square = allocate_clean(builder, 2*F + 2)
    correction = allocate_clean(builder, 3*F + 4)
    numerator = allocate_clean(builder, 4*F + 5)
    workspace = (square, correction, numerator)

    result = allocate_clean(builder, F + n_p + 1)

    # Normalize: m = x_normalized / 2**20 lies in [1, 4).
    normalize(builder, x, flags)

    # Encode m using F fractional bits.
    m_offset = F - 2*n_p
    builder.cx(x, m[m_offset:m_offset+len(x)])

    # Starting estimate: 0.5 * 2**F.
    builder.x(estimates[0][F-1])

    for i in range(iterations):
        build_newton_step(
            builder,
            m,
            estimates[i],
            estimates[i+1],
            workspace,
            fractional_bits=F,
        )

    # If s shifts normalized x:
    # 1/sqrt(original_x) = normalized_estimate * 2**(s-10).
    builder.cx(estimates[-1], result[:F+1])
    shift_result(builder, result, flags, F)

    # result now has F+10 fractional bits.
    # Skip its lowest 10 bits to match the classical model's
    # final truncation to F fractional bits.
    phase_bits = F + n_p

    for j in range(n_p, phase_bits):
        # Z**exponent contributes exponent/2 turns.
        exponent = Fraction(2) ** (j - phase_bits + 1)
        builder.z_pow(result[j], exponent)

    # Undo scaling and erase the result register.
    shift_result(builder, result, flags, F, inverse=True)
    builder.cx(estimates[-1], result[:F+1])

    # Recompute each step to XOR its stored estimate back to zero.
    for i in reversed(range(iterations)):
        build_newton_step(
            builder,
            m,
            estimates[i],
            estimates[i+1],
            workspace,
            fractional_bits=F,
        )

    builder.x(estimates[0][F-1])

    # Erase m and restore the original input.
    builder.cx(x, m[m_offset:m_offset+len(x)])
    normalize(builder, x, flags, inverse=True)

    for register in (
        flags,
        m,
        *estimates,
        *workspace,
        result,
    ):
        builder.free(register)

    return builder.finish_circuit()


def main():
    circuit = generate_inverse_sqrt()
    circuit.to_file("invsqrt.kmb", format="kmb")

    stats = circuit.operation_statistics()

    print("Generated invsqrt.kmb")
    print(f"Qubits: {circuit.num_qubits:,}")
    print(f"Instructions: {len(circuit):,}")
    print(f"Toffoli-like gates: {stats.num_toffoli_like:,}")


if __name__ == "__main__":
    main()