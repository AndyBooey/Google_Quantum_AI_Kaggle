# at a high level, this file is used to run the inverse square root but 
# outputs a quantum circuit instead of outputting the result of the inverse squareroot



# inputs: A positive integer (x), represented by 22 qubits
# Input range	1 to 3,133,452
# Mathematical function	(1\sqrt{x})
# Required output	Apply the corresponding quantum phase
# Input afterward	Must remain unchanged
# Temporary qubits	Must return to 0
# Accuracy	Relative phase tolerance of \(2^{-24}\)
# Submission	invsqrt.kmb or invsqrt.kmx




import math


def inverse_sqrt(x, initial_guess, iterations=3):
    """
    Approximate 1/sqrt(x) using Newton's method.
    """
    if x <= 0:
        raise ValueError("x must be positive")

    if initial_guess <= 0:
        raise ValueError("Initial guess must be positive")

    y = initial_guess

    for i in range(iterations):
        y = y * (3 - x * y**2) / 2      # Newton's method update for 1/sqrt(x)    

        print(f"Iteration {i + 1}: {y:.10f}")

    return y


def main():
    x = 4
    initial_guess = 0.4

    approximation = inverse_sqrt(
        x,
        initial_guess,
        iterations=5
    )

    actual = 1 / math.sqrt(x)

    absolute_error = abs(actual - approximation)
    relative_error = absolute_error / abs(actual)

    print("\nResults:")
    print(f"Input: {x}")
    print(f"Approximation: {approximation:.10f}")
    print(f"Actual: {actual:.10f}")
    print(f"Absolute error: {absolute_error:.10f}")
    print(f"Relative error: {relative_error:.10f}")


if __name__ == "__main__":
    main()
