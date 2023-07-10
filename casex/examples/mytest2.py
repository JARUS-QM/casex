import numpy as np
from scipy.optimize import curve_fit

# Define the multivariate polynomial function
def multivariate_polynomial(x, *coeffs):
    num_terms = len(coeffs)
    num_variables = len(x)
    if num_terms != num_variables + 1:
        raise ValueError("Number of coefficients should be one more than number of variables.")
    result = 0.0
    for i in range(num_terms):
        indices = np.unravel_index(i, (num_variables,) * num_variables)
        term = coeffs[i]
        for j in range(num_variables):
            term *= x[j] ** indices[j]
        result += term
    return result

def evaluate_polynomial_2nd_order(x, *coeffs):
    """
    Evaluate a 2nd order polynomial in two variables.

    Args:
        x (float): The value of the first variable.
        y (float): The value of the second variable.
        coeffs (list): The coefficients of the polynomial in the form [c00, c10, c01, c20, c11, c02, c21, c12, c22],
                       where cij represents the coefficient of x^i * y^j.

    Returns:
        float: The value of the polynomial at the given (x, y) coordinates.
    """
    c00, c10, c01, c20, c11, c02, c21, c12, c22 = coeffs
    return c00 + c10 * x[0] + c01 * x[1] + c20 * x[0]**2 + c11 * x[0] * x[1] + c02 * x[1]**2 + c21 * x[0]**2 * x[1] + c12 * x[0] * x[1]**2 + c22 * x[0]**2 * x[1]**2


# Generate some sample data
x1 = np.linspace(-5, 5, 50)
x2 = np.linspace(-5, 5, 50)
X1, X2 = np.meshgrid(x1, x2)
Y = 3.0 * X1 + 2.0 * X2 + 1.0 * X1 ** 2 + 0.5 * X2 ** 2 + 0.1 * X1 * X2 + 5.0

# Flatten the input variables
x1_flat = X1.flatten()
x2_flat = X2.flatten()
y_flat = Y.flatten()

# Fit the multivariate polynomial to the data
initial_guess = [1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1]  # Initial guess for the coefficients
popt, pcov = curve_fit(evaluate_polynomial_2nd_order, (x1_flat, x2_flat), y_flat, p0=initial_guess)

# Print the fitted coefficients
print("Fitted coefficients:")
for i, coeff in enumerate(popt):
    indices = np.unravel_index(i, (3, 3))
    print(f"Coefficient for x1^{indices[0]} * x2^{indices[1]}: {coeff}")

# Evaluate the fitted polynomial on a grid of points
X1_eval, X2_eval = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))
y_eval = evaluate_polynomial_2nd_order((X1_eval.flatten(), X2_eval.flatten()), *popt)
Y_eval = y_eval.reshape(X1_eval.shape)

# Plot the original data and the fitted polynomial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.scatter(X1, X2, Y, c="b", label="Original data")
ax.plot_surface(X1_eval, X2_eval, Y_eval, color="r", alpha=0.5, label="Fitted polynomial")
ax.set_xlabel("X1")
ax.set_ylabel("X2")
ax.set_zlabel("Y")
plt.show()
