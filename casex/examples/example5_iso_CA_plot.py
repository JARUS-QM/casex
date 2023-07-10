"""
Example 5
---------
This example makes a colored plot of the lethal area for varying impact angle and impact speed. The size of the aircraft
as well as the other parameters are fixed. The target is the second column in the iGRC table, where the lethal area
is 80 m^2. Therefore, the iso-curve for 80 m^2 is shown (in yellow) along with other iso curves for comparison
(in white).

The JARUS model from Annex F Appendix B :cite:`JARUS_AnnexF` is used throughout this example.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from casex import FrictionCoefficients, CriticalAreaModels, enums, AircraftSpecs, AnnexFParms


# Data on person size.
person_width = 0.3
person_height = 1.8

# Instantiate necessary classes.
CA = CriticalAreaModels(person_width, person_height)

# Get the Annex F parameters class, since we will be using values from it.
AFP = AnnexFParms()

# Set aircraft values.
aircraft_type = enums.AircraftType.FIXED_WING
aircraft = AircraftSpecs(aircraft_type, AFP.CA_parms[1].wingspan, AFP.CA_parms[1].mass)
aircraft.set_fuel_type(enums.FuelType.LION)
aircraft.set_fuel_quantity(0)
aircraft.set_friction_coefficient(AFP.friction_coefficient)

y_speed = np.linspace(0, 50, 100)
x_angle = np.linspace(5, 70, 100)
X_angle, Y_speed = np.meshgrid(x_angle, y_speed)

Z_CA = np.zeros((X_angle.shape[0], Y_speed.shape[0]))
for i, y in enumerate(Y_speed):
    for j, x in enumerate(X_angle):
        Z_CA[i, j] = CA.critical_area(aircraft, y_speed[i],
                                      x_angle[j], use_obstacle_reduction = True)[0]

fig = plt.figure()
ax = plt.axes()
divider = make_axes_locatable(ax)
cax = divider.append_axes('right', size='5%', pad=0.05)

im = ax.imshow(Z_CA, extent=[x_angle[0], x_angle[-1], y_speed[0], y_speed[-1]],
               aspect='auto', origin='lower')

CS = ax.contour(X_angle, Y_speed, Z_CA, [5, 10, 15, 20, 30, 40, 60, 100, 120], colors='white')
ax.clabel(CS, inline=1, fontsize=10, fmt="%u m^2")

CS2 = ax.contour(X_angle, Y_speed, Z_CA, [AFP.CA_parms[1].critical_area_target], colors='yellow')
ax.clabel(CS2, inline=1, fontsize=10, fmt="%1.1f m^2")

fig.colorbar(im, cax=cax, orientation='vertical')
ax.set_xlabel('Angle [deg]')
ax.set_ylabel('Speed  [m/s]')
ax.set_title('Lethal area [m^2] for {:d} m, {:d} kg, {:2.2f} friction'.format(AFP.CA_parms[1].wingspan,
                                                                          AFP.CA_parms[1].mass,
                                                                          AFP.friction_coefficient))
plt.show()
