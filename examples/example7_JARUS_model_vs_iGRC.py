"""
Example 7
---------
In this example we compare the iGRC table in Annex F with the actual output of the JARUS model. This is done by plotting
the critical area for a variety of wingspan and population densities. This is similar to the iGRC figures that can be
computed with the :class:`Figures` class, which do the same thing, but for the simplified model.
"""
import numpy as np
import matplotlib.pyplot as plt
from casex import CriticalAreaModels, AnnexFParms, enums


# Data on person size.
person_width = 0.3
person_height = 1.8
impact_angle = 35
speed_reduction_factor = 1

# Instantiate necessary classes.
CA = CriticalAreaModels(person_width, person_height)

# Sampling density.
pop_density_samples = 400
wingspan_samples = 200

# Plotting range for the impact angle and speed.
wingspan = np.linspace(0, 21, wingspan_samples)
pop_density = np.logspace(-3 + np.log10(5), 5 + np.log10(5), pop_density_samples)

# Instantiate the class to access parameters for the five scenarios.
AFP = AnnexFParms(impact_angle)

# Initialize GRC matrix.
GRC_matrix = np.zeros((pop_density_samples, wingspan_samples))

# Compute the GRC matrix.
for j in range(len(wingspan)):

    # Set impact speed in correspondence with wingspan.
    if wingspan[j] <= AFP.CA_parms[0].wingspan:
        column = 0
    elif wingspan[j] <= AFP.CA_parms[1].wingspan:
        column = 1
    elif wingspan[j] <= AFP.CA_parms[2].wingspan:
        column = 2
    elif wingspan[j] <= AFP.CA_parms[3].wingspan:
        column = 3
    else:
        column = 4

    # Compute the impact speed.
    impact_speed = AFP.CA_parms[column].cruise_speed * speed_reduction_factor

    # Set the wingspan into the correct class in AFP.
    AFP.CA_parms[column].aircraft.width = wingspan[j]

    # Compute the critical area value for the given wingspan.
    M = 1e-6 * CA.critical_area(enums.CriticalAreaModel.JARUS, AFP.CA_parms[column].aircraft, impact_speed,
                                impact_angle, 0, -1)[0]

    # Compute the corresponding GRC value for all population densities.
    for i in range(len(pop_density)):
        GRC_matrix[i, j] = 1 - np.log10(1e-6 / (pop_density[i] * M))

# A number of lists used for plotting.
x_ticks = [1, 3, 8, 20]
pop_dens_tick = [0.1, 10, 100, 1500, 15000, 100000, 500000]
y_text_pos = [0.02, 1, 33, 400, 5000, 40000, 220000]
x_text_pos = [0.5, 2, 5.5, 14, 20.5]
pop_dens_percentage = [3.15, 24.6, 52.8, 16.6, 2.84, 0.07, 0.0, 0.0]

# Font size and color for the iGRC values.
GRC_fontsize = 18
GRC_color = 'white'

# Creating the plot.
fig, ax = plt.subplots(1, 1, figsize=(13, 7))
ax2 = ax.twinx()

# Show the background matrix.
im = ax2.imshow(np.ceil(GRC_matrix), extent=[wingspan[0], wingspan[-1], pop_density[0], pop_density[-1]],
                aspect='auto', origin='upper')

ax.set_zorder(ax2.get_zorder() + 1)
ax.patch.set_visible(False)
ax2.yaxis.set_major_locator(plt.NullLocator())
ax.set_yscale('log')

# Set white lines vertically and horizontally.
for k in pop_dens_tick:
    ax.plot([wingspan[0], wingspan[-1]], [k, k], 'w--')
for k in x_ticks:
    ax.plot(np.array([k, k]), np.array([pop_density[0], pop_density[-1]]), 'w--')

# Add iGRC values and DK population densities.
for j in range(7):
    ax.text(x_text_pos[0], y_text_pos[j], str(j+1+int(j > 0) - int(j == 6)), horizontalalignment='center',
            verticalalignment='center', fontsize=GRC_fontsize, color=GRC_color)
    if j < 6:
        for k in range(4):
            ax.text(x_text_pos[k+1], y_text_pos[j], str(j+2+k+int(j > 0)), horizontalalignment='center',
                    verticalalignment='center', fontsize=GRC_fontsize, color=GRC_color)
    ax.text(wingspan[-1]*1.05, y_text_pos[j], str(pop_dens_percentage[j]) + '%', horizontalalignment='center',
            verticalalignment='center', fontsize=GRC_fontsize)
ax.text(wingspan[-1]*1.05, 3.2 * 0.0005, 'DK dens', horizontalalignment='center', verticalalignment='center',
        fontsize=GRC_fontsize)

# Show contours for the GRC matrix.
CS = ax.contour(wingspan, pop_density, GRC_matrix, np.arange(1, 18), colors='black')
ax.clabel(CS, inline=1, fontsize=14, fmt="GRC %u")

# Set axes labels and title.
ax.set_ylabel('Population density [ppl/km$^2$]', fontsize=16)
ax.set_xlabel('Wingspan [m]', fontsize=16)
ax.set_title('GRC comparison (angle = {:d} deg, impact speed = 0.7 x max cruise, 1 m no slide)'.format(
    impact_angle), fontsize=20)

# Set axes tick labels.
ax.yaxis.set_major_locator(plt.FixedLocator(pop_dens_tick))
ax.set_yticklabels(pop_dens_tick, fontsize=14)
ax.yaxis.set_minor_locator(plt.NullLocator())
ax.xaxis.set_major_locator(plt.FixedLocator(x_ticks))
ax.set_xticklabels(x_ticks, fontsize=14)

# Set axes limits.
ax.set_xlim(wingspan[0], wingspan[-1])
ax.set_ylim(pop_density[-1], pop_density[0])

plt.show()
