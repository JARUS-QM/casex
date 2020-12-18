"""
Example 6
---------
The use of obstacles for reducing the critical area is demonstrated in this example.
This is similar to the figure that can be created wiht the :class:`Figures` class.
"""
import numpy as np
import matplotlib.pyplot as plt

from casex import Obstacles


# Wingspan or characteristic dimension of aircraft.
CA_width = 3

# Nominal length (length of CA without obstacles).
CA_length = 200/CA_width

# Obstacle density in obstacles per square meter.
houses_per_square_km = 850
obstacle_density = houses_per_square_km / 1e6

# Average width of house and variation in house width.
obstacle_width_mu = 23
obstacle_width_sigma = 6

# Average house length and variation in house length.
obstacle_length_mu = 9
obstacle_length_sigma = 2

# Instantiate Obstacles class.
OS = Obstacles(CA_width, CA_length, 0)

# Set resolution along first axis.
# This does not need to be terribly high for plotting, since the resulting curve is always smooth.
# But it should not be too low if you plan to use the expected value (average length), which is
# also returned by the `cdf` method.
x_resolution = 30
x = np.linspace(0, CA_length, x_resolution)

# Resolution of PDFs in computations. Higher res gives better accuracy, but also longer computation time.
# Value of 25 is usually good.
pdf_resolution = 25

# Compute the probability curve.
p_x, EX, beta_analytical, sanity_check = OS.cdf(x, obstacle_density, obstacle_width_mu, obstacle_width_sigma,
                                            obstacle_length_mu, obstacle_length_sigma, pdf_resolution)

# Plot the curve and the target CA.
fig = plt.figure(1, figsize=(12, 8), dpi=90)
ax = fig.add_subplot(111)
ax.plot(x * CA_width, p_x, linewidth=1.5, label='CDF')

ax.plot([EX * CA_width, EX * CA_width], [p_x[0], 1], '--', linewidth=1.5, label='Average CA size')

ax.set_xlabel('Critical area [m$^2$]', fontsize=12)
ax.set_xlim([0, x[-1] * CA_width])

ax.set_ylim([p_x[0], 1])
ax.set_ylabel('Probability', fontsize=12)

ax.legend()

plt.grid()
plt.show()
