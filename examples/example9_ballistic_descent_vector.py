import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

def example9_ballistic_descent_vector():
    """
    example9_ballistic_descent_vector.py
    

    """
    # Instantiate necessary classes
    rho = 1.3
    BDM = casex.ballistic_descent_models.BallisticDescent2ndOrderDragApproximation(rho)

    # Set aircraft values
    aircraft_type = casex.enums.EAircraftType.FIXED_WING
    width = 4
    length = 3.2
    mass = 25
    
    # Instantiate and add data to CAircraftSpecs class
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_ballistic_drag_coefficient(0.9)
    aircraft.set_ballistic_frontal_area(0.25)
    BDM.set_aircraft(aircraft)
    
    altitude = 150
    initial_velocity_x = []
    initial_velocity_y = []
    initial_velocity_x.append(np.linspace(0, 60, 100))
    initial_velocity_y.append(-2)
    initial_velocity_x.append(30)
    initial_velocity_y.append(np.linspace(-5, 5, 100))
    initial_velocity_x.append(30)
    initial_velocity_y.append(-2)
       
    p = []
    p.append(BDM.compute_ballistic_distance(altitude, initial_velocity_x[0], initial_velocity_y[0]))
    p.append(BDM.compute_ballistic_distance(altitude, initial_velocity_x[1], initial_velocity_y[1]))

    drag_coef = np.linspace(0.7, 1, 100)
    aircraft.set_ballistic_drag_coefficient(drag_coef)
    BDM.set_aircraft(aircraft)
    
    p.append(BDM.compute_ballistic_distance(altitude, initial_velocity_x[2], initial_velocity_y[2]))
    
    # Setup figure    
    fig, ax = plt.subplots(3, 4, figsize=(12,6))
    plt.style.use('fivethirtyeight')
    
    ax[0,0].plot(initial_velocity_x[0], p[0][0], linewidth=2)
    ax[0,0].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[0,0].set_ylabel('Impact distance [m]', fontsize=12)
    ax[0,1].plot(initial_velocity_x[0], p[0][1], linewidth=2)
    ax[0,1].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[0,1].set_ylabel('Impact velocity [m/s]', fontsize=12)
    ax[0,2].plot(initial_velocity_x[0], p[0][2] * 180 / np.pi, linewidth=2)
    ax[0,2].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[0,2].set_ylabel('Angle [deg]', fontsize=12)
    ax[0,3].plot(initial_velocity_x[0], np.linspace(p[0][3], p[0][3], 100), linewidth=2)
    ax[0,3].set_xlabel('Initial velocity X [m/s]', fontsize=12)
    ax[0,3].set_ylabel('Descent time [s]', fontsize=12)

    ax[1,0].plot(initial_velocity_y[1], p[1][0], linewidth=2)
    ax[1,0].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
    ax[1,0].set_ylabel('Impact distance [m]', fontsize=12)
    ax[1,1].plot(initial_velocity_y[1], p[1][1], linewidth=2)
    ax[1,1].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
    ax[1,1].set_ylabel('Impact velocity [m/s]', fontsize=12)
    ax[1,2].plot(initial_velocity_y[1], p[1][2] * 180 / np.pi, linewidth=2)
    ax[1,2].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
    ax[1,2].set_ylabel('Angle [deg]', fontsize=12)
    ax[1,3].plot(initial_velocity_y[1], p[1][3], linewidth=2)
    ax[1,3].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
    ax[1,3].set_ylabel('Descent time [s]', fontsize=12)

    ax[2,0].plot(drag_coef, p[2][0], linewidth=2)
    ax[2,0].set_xlabel('Drag coefficient [-]', fontsize=12)
    ax[2,0].set_ylabel('Impact distance [m]', fontsize=12)
    ax[2,1].plot(drag_coef, p[2][1], linewidth=2)
    ax[2,1].set_xlabel('Drag coefficient [-]', fontsize=12)
    ax[2,1].set_ylabel('Impact velocity [m/s]', fontsize=12)
    ax[2,2].plot(drag_coef, p[2][2] * 180 / np.pi, linewidth=2)
    ax[2,2].set_xlabel('Drag coefficient [-]', fontsize=12)
    ax[2,2].set_ylabel('Angle [deg]', fontsize=12)
    ax[2,3].plot(drag_coef, p[2][3], linewidth=2)
    ax[2,3].set_xlabel('Drag coefficient [-]', fontsize=12)
    ax[2,3].set_ylabel('Descent time [s]', fontsize=12)
    plt.show()

if __name__ == '__main__':
    example9_ballistic_descent_vector()

