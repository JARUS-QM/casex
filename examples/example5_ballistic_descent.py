"""
Example 8
---------
MISSING DOC
"""
import numpy as np
import matplotlib.pyplot as plt

import casex

def example5_ballistic_descent():
    # Instantiate necessary classes
    rho = 1.225
    BDM = casex.ballistic_descent_models.BallisticDescent2ndOrderDragApproximation(rho)

    # Set aircraft values
    aircraft_type = casex.enums.AircraftType.FIXED_WING
    width = 2.8
    length = 3.2
    mass = 90

    # Instantiate and add data to CAircraftSpecs class
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_ballistic_drag_coefficient(0.8)
    aircraft.set_ballistic_frontal_area(0.6 * 0.6)
    BDM.set_aircraft(aircraft)

    # Set initial values for the descent
    altitude = 100
    initial_velocity_x = 28
    initial_velocity_y = 0

    # Compute ballistic descent values.
    # Note that the return in p contains numerous different values.
    p = BDM.compute_ballistic_distance(altitude, initial_velocity_x, initial_velocity_y)

    print("Distance: {:1.1f} m    Impact speed: {:1.1f} m/s   Angle: {:1.1f} deg   Time : {:1.2f} s".format(
        p[0], p[1], p[2] * 180 / np.pi, p[3]))
    print("Distances: {:1.3f}  {:1.3f}  {:1.3f}".format(BDM.distance1, BDM.distance2, BDM.distance3))
    print("Times: {:1.3f}   {:1.3f}   {:1.3f}".format(BDM.time_top, BDM.time_cross, BDM.time_impact))
    print("Speeds: {:1.3f}   {:1.3f}".format(BDM.velocity_x, BDM.velocity_y))

    # In the following, there are three examples, where horizontal velocity (first example), vertical velocity (second example),
    # and drag coefficient (third example) are arrays rather than scalar.
    altitude = 150
    initial_velocity_x = np.linspace(0, 60, 100)
    initial_velocity_y = np.linspace(-5, 5, 100)

    p = []
    # Array for horizontal velocity
    p.append(BDM.compute_ballistic_distance(altitude, initial_velocity_x, -2))
    # Array for vertical velocity
    p.append(BDM.compute_ballistic_distance(altitude, 30, initial_velocity_y))

    # Array for drag coefficient
    drag_coef = np.linspace(0.7, 1, 100)
    aircraft.set_ballistic_drag_coefficient(drag_coef)
    BDM.set_aircraft(aircraft)
    p.append(BDM.compute_ballistic_distance(altitude, 30, -2))

    # Set up figure    
    fig, ax = plt.subplots(2, 2, figsize=(12, 6))
    plt.style.use('fivethirtyeight')

    ax[0,0].plot(initial_velocity_x, p[0][0], linewidth=2)
    ax[0,0].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[0,0].set_ylabel('Impact distance [m]', fontsize=12)
    ax[0,0].set_title('Impact distance for vayring initial horizontal velocity')

    ax[0,1].plot(initial_velocity_y, p[1][1], linewidth=2)
    ax[0,1].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
    ax[0,1].set_ylabel('Impact velocity [m/s]', fontsize=12)
    ax[0,1].set_title('Impact distance for vayring initial vertical velocity')

    ax[1,0].plot(drag_coef, p[2][2] * 180 / np.pi, linewidth=2)
    ax[1,0].set_xlabel('Drag coefficient [-]', fontsize=12)
    ax[1,0].set_ylabel('Angle [deg]', fontsize=12)
    ax[1,0].set_title('Impact angle for vayring drag coefficient')
    
    ax[1,1].plot(initial_velocity_y, p[1][3], linewidth=2)
    ax[1,1].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[1,1].set_ylabel('Descent time [s]', fontsize=12)
    ax[1,1].set_title('Descent time for vayring initial vertical velocity')

    plt.show()

if __name__ == '__main__':
    example5_ballistic_descent()
