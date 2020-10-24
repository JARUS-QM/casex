import platform
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d

import casex

"""
This example is based on the concept from the previous example (example 4), where an iso-curve for the lethal area was generated.
In that example a yellow curve showed the iso-curve for 10 m^2 lethal area and for fixed aircraft parameters.

In this example that same curve is shown, but for varying wingspan and for two different ground friction coefficients.
Four graphs are generated, for 10, 100, 1.000, and 10.000 m^2 lethal areas.

The purpose is to explore the change in lethal area as a function of wingspan.

The JARUS model is used throughout this example.
"""


def example6_iso_plot2():
     # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.CFrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)
    
    # Set aircraft values
    aircraft_type = casex.enums.AircraftType.FIXED_WING
    
    # Width, length, and mass will be set later, so just use dummy values
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, 1, 1, 1)
    aircraft.set_fuel_type(casex.enums.FuelType.LION)
    aircraft.set_fuel_quantity(0)

    critical_area_target = np.array([1e1, 1e2, 1e3, 1e4])

    fig, ax = plt.subplots(2, 2, figsize=(12,6))

    # Indexing for the four subplots
    idx = [[0, 0, 1, 1], [0, 1, 0, 1]]

    # Loop over size of lethal area
    for la in np.arange(0, critical_area_target.size):

        axi = ax[idx[0][la]][idx[1][la]]

        if la == 0:
            width = np.array([0.5, 1, 1.5, 2])
            x_speed = np.linspace(0, 40, 100)
        elif la == 1:
            width = np.array([1, 2, 3, 4, 5])
            x_speed = np.linspace(0, 75, 100)
        elif la == 2:
            width = np.array([4, 6, 8, 10, 12])
            x_speed = np.linspace(0, 100, 100)
        elif la == 3:
            width = np.array([10, 14, 18, 22])
            x_speed = np.linspace(60, 200, 100)

        y_angle = np.linspace(5, 90, 100)
        X_speed, Y_angle = np.meshgrid(x_speed, y_angle)

        c = 0
        clr = ['blue', 'red', 'green']
        for f in np.array([0.3, 0.7]):

            for k in np.arange(0, width.size):
                
                # Set width, length, mass, and friction coefficient according to loop variables
                aircraft.set_width(width[k])
                aircraft.set_length(0.8*width[k])
                aircraft.set_mass(0.8 * np.exp(0.85*width[k]))
                aircraft.set_friction_coefficient(f)
            
                # Generate matrix of LA values
                Z_CA = np.zeros((x_speed.shape[0], y_angle.shape[0]))
                for i, x in enumerate(x_speed):
                    Z_CA[:, i] = CA.critical_area(casex.enums.CriticalAreaModel.JARUS, aircraft, x_speed[i], y_angle, 0)[0]
#                for i, x in enumerate(X_speed):
#                    for j, y in enumerate(Y_angle):
#                        Z_CA[j, i] = CA.critical_area(casex.enums.ECriticalAreaModel.JARUS, aircraft, x_speed[i], y_angle[j], 0)[0]
            
            
                # Generate a single contour line for the specific LA area
                CS = axi.contour(X_speed, Y_angle, Z_CA, [critical_area_target[la]], colors=clr[c])
                axi.clabel(CS, inline=2, fontsize=10, fmt=(str(width[k]) + ' m'))
                
            c = c + 1
        
        axi.set_xlabel('Speed')
        axi.set_ylabel('Angle')
        axi.set_title(str(critical_area_target[la]) + ' m^2 critical area iso-wingspan')
        
        # Manually add legends to the plot
        blue_line = axi.plot([], [], color='blue', label='Friction 0.3')
        red_line = axi.plot([], [], color='red', label='Friction 0.7')
        axi.legend(handles=[blue_line[0], red_line[0]])

    plt.show()

if __name__ == '__main__':
    example6_iso_plot2()
