import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

def example8_ballistic_descent():
    """
    example8_ballistic_descent.py
    

    """
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
    aircraft.set_ballistic_frontal_area(0.6*0.6)
    BDM.set_aircraft(aircraft)
    
    altitude = 100
    initial_velocity_x = 28
    initial_velocity_y = 0
       
    p = BDM.compute_ballistic_distance(altitude, initial_velocity_x, initial_velocity_y)

    print("Distance: {:1.1f} m    Impact speed: {:1.1f} m/s   Angle: {:1.1f} deg   Time : {:1.2f} s".format(p[0], p[1], p[2] * 180 / np.pi, p[3]))
    print("Distances: {:1.3f}  {:1.3f}  {:1.3f}".format(BDM.distance1, BDM.distance2, BDM.distance3))
    print("Times: {:1.3f}   {:1.3f}   {:1.3f}".format(BDM.time_top, BDM.time_cross, BDM.time_impact))
    print("Speeds: {:1.3f}   {:1.3f}".format(BDM.velocity_x, BDM.velocity_y))

if __name__ == '__main__':
    example8_ballistic_descent()

