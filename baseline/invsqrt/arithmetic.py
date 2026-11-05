# Reversible arithmetic operations
# defines how mathematical operations are performed using reversible quantum gates.Function	Responsibility

import kickmix as km



"""
Reusable reversible arithmetic operations.

These functions add quantum operations to a kickmix
circuit builder. They do not calculate ordinary Python
integer results directly.
"""


def reversible_add(builder, target, offset):
    """
    Add offset into target reversibly.

    target = (target + offset) mod 2^n
    offset remains unchanged.
    """
    builder.iadd(target=target, offset=offset)


def reversible_and(builder, a, b, target):
    """
    Apply a Toffoli gate.

    target = target XOR (a AND b)
    """
    builder.ccx(a, b, target)


def _check_disjoint(*registers):
    """Require nonempty registers with no shared qubits."""
    seen = set()

    for register in registers:
        if not len(register):
            raise ValueError("Registers must not be empty")

        for qubit in register:
            if qubit in seen:
                raise ValueError("Registers must use distinct qubits")
            seen.add(qubit)



def reversible_multiply(builder, a, b, output, *, inverse=False):
    """
    Unsigned multiplication:
        output += a * b

    With inverse=True:
        output -= a * b

    Arithmetic is modulo 2**len(output).
    Inputs a and b are preserved.
    """
    _check_disjoint(a, b, output)

    operation = builder.isub if inverse else builder.iadd

    # Clean zero qubits extend a to the required unsigned width.
    padding = builder.alloc_qubits(
        max(0, len(output) - len(a))
    )
    if len(padding):
        builder.reset(padding)

    count = min(len(b), len(output))
    indices = reversed(range(count)) if inverse else range(count)

    for i in indices:
        # Adding into output[i:] implements multiplication by 2**i.
        width = len(output) - i

        bits = list(a[:width])
        bits += list(padding[:width - len(bits)])
        offset = km.array(bits)

        builder_operation_target = output[i:]

        operation(
            offset=offset,
            target=builder_operation_target,
            control=b[i],
        )

    # Padding has been restored to zero by the add/subtract operations.
    builder.free(padding)


def reversible_square(builder, a, output, *, inverse=False):
    """
    output += a*a, or output -= a*a with inverse=True.
    Input a is preserved.
    """
    _check_disjoint(a, output)

    # Separate controls and offsets are needed by the multiplier.
    workspace = builder.alloc_qubits(len(a))
    builder.reset(workspace)

    # Encode a's computational-basis bits into clean workspace.
    builder.cx(a, workspace)

    reversible_multiply(
        builder,
        a,
        workspace,
        output,
        inverse=inverse,
    )

    # Restore workspace to zero before releasing it.
    builder.cx(a, workspace)
    builder.free(workspace)





def uncompute_multiply(builder, a, b, output):
    """Undo multiplication using the unchanged original inputs."""
    reversible_multiply(builder, a, b, output, inverse=True)


def uncompute_square(builder, a, output):
    """Undo squaring using the unchanged original input."""
    reversible_square(builder, a, output, inverse=True)