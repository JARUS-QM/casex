"""
Example 4
---------
This example makes a colored plot of the lethal area for varying impact angle and impact speed. The size of the aircraft
as well as the other parameters are fixed. The target is the first column in the iGRC table, where the lethal area
is 10 m^2. Therefore, the iso-curve for to 10 m^2 is shown (in yellow) along with other iso curves for comparison
(in white).

The purpose is to give a relation between angle and speed for impacts to uncover any potential relation between angle
and speed in terms of fixed lethal area.

The JARUS model is used throughout this example.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from casex import FrictionCoefficients, CriticalAreaModels, enums, AircraftSpecs


def example4_iso_CA_plot():
    # Data on person size.
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes.
    FC = FrictionCoefficients()
    CA = CriticalAreaModels(person_width, person_height)

    # Set aircraft values.
    aircraft_type = enums.AircraftType.FIXED_WING
    mass = 3
    friction_coefficient = 0.4

    aircraft = AircraftSpecs(aircraft_type, 1, 1, mass)
    aircraft.set_fuel_type(enums.FuelType.LION)
    aircraft.set_fuel_quantity(0)
    aircraft.set_friction_coefficient(friction_coefficient)

    aircraft.set_width(1)
    aircraft.set_length(0.8)
    aircraft.set_mass(3)

    x_speed = np.linspace(0, 40, 100)
    y_angle = np.linspace(5, 90, 100)
    X_speed, Y_angle = np.meshgrid(x_speed, y_angle)

    Z_CA = np.zeros((X_speed.shape[0], Y_angle.shape[0]))
    for i, x in enumerate(X_speed):
        for j, y in enumerate(Y_angle):
            Z_CA[j, i] = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, x_speed[i], y_angle[j], 0)[0]

    fig = plt.figure()
    ax = plt.axes()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)

    im = ax.imshow(Z_CA, extent=[x_speed[0], x_speed[-1], y_angle[0], y_angle[-1]], aspect='auto', origin='lower')

    CS = ax.contour(X_speed, Y_angle, Z_CA, [2, 5, 20, 30, 40, 60, 80, 100], colors='white')
    ax.clabel(CS, inline=1, fontsize=10, fmt="%u m^2")

    CS2 = ax.contour(X_speed, Y_angle, Z_CA, [10], colors='yellow')
    ax.clabel(CS2, inline=1, fontsize=10, fmt="%u m^2")

    fig.colorbar(im, cax=cax, orientation='vertical')

    ax.set_xlabel('Speed  [m/s]')
    ax.set_ylabel('Angle [deg]')
    ax.set_title('Lethal area [m^2] for 1 m, 3 kg, 0.4 fric')
    plt.show()


if __name__ == '__main__':
    example4_iso_CA_plot()
