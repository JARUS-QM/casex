import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

# Abbreviate this, as it is used several times
import casex.enums
from casex.enums import CriticalAreaModel as Model

"""
Example2
--------

This example shows the basics of using the different models in casex.
It shows how to set up the necessary parameters and variables, and how
to call the lethal_model function to calculate lethal areas for the
models.

It also shows how to modify an existing setup to change from one aircraft
to another.
"""

def example2_model_comparison():
    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.FrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)

    # Set aircraft values
    aircraft_type = casex.enums.AircraftType.FIXED_WING
    width = 4
    length = 3.2
    mass = 25
    friction_coefficient = FC.get_coefficient(
        casex.enums.AircraftMaterial.ALUMINUM,
        casex.enums.GroundMaterial.CONCRETE)
    
    # Instantiate and add data to CAircraftSpecs class
    Aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    Aircraft.set_fuel_type(casex.enums.FuelType.GASOLINE)
    Aircraft.set_fuel_quantity(5)
    Aircraft.set_friction_coefficient(friction_coefficient)
    Aircraft.set_coefficient_of_restitution(0.7) # default value, so in fact no need to set

    # Use the same impact speed for all models
    # Computed here based on kinetic energy.
    impact_speed = CA.speed_from_kinetic_energy(34000, Aircraft.mass)
    
    # Impact angle
    impact_angle = 25

    # How large overlap between lethal area from aircraft and from deflagration (explosion)
    critical_areas_overlap = 0.5
    
    # Compute the leathal area for the four different models
    p = []

    # One set of parameters
    p.append(CA.critical_area(Model.RCC, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    
    # Same setup, but different impact angle
    impact_angle = 65
    p.append(CA.critical_area(Model.RCC, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, Aircraft, impact_speed, impact_angle, critical_areas_overlap))

    # Let's try another aircraft size
    Aircraft.set_width(1.8)
    Aircraft.set_length(1)
    Aircraft.set_mass(1.1)
    Aircraft.set_fuel_quantity(1)
    impact_speed = CA.speed_from_kinetic_energy(700, Aircraft.mass)
    impact_angle = 25
    p.append(CA.critical_area(Model.RCC, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, Aircraft, impact_speed, impact_angle, critical_areas_overlap))

    # and now with the steeper impact angle
    impact_angle = 65
    p.append(CA.critical_area(Model.RCC, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, Aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, Aircraft, impact_speed, impact_angle, critical_areas_overlap))

    # The CA.critical_area returns four outputs. The first is the lethal area.
    # The lethal area for the first model is thus obtained by p[0][0], and for the second by p[1][0], etc
    
    # Setup figure to plot compare the model for 4 different scenarios    
    fig, ax = plt.subplots(1, 1, figsize=(12,6))
    plt.style.use('fivethirtyeight')
    
    bar_width = 0.15
    index = np.arange(4)
    
    for k in np.arange(0, 5):
        plt.bar(index + k * bar_width, [p[k][0], p[k+5][0], p[k+10][0], p[k+15][0]], bar_width)
        
    ax.set_xlabel('Scenario', fontsize=12)
    ax.set_ylabel('Lethal area', fontsize=12)
    ax.xaxis.set_ticks(index + 2*bar_width)
    ax.set_xticklabels(['4 m span, 25 deg', '4 m span, 65 deg', '1.8 m span, 25 deg', '1.8 m span, 65 deg'])

    ax.legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)
    
    plt.show()
    
    
if __name__ == '__main__':
    example2_model_comparison()
