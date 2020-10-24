import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

# Abbreviate this, as it is used several times
from casex.enums import ECriticalAreaModel as Model

"""
example2_vector_input.py

This example shows how to use the models using vector input to generate a vector output.
Using this feature it is possible to generate graphs for variations on one input parameter.

This example shows this for the following parameters:

    width
    length
    impact angle
    impact speed
    leathall area overlap
    fuel quantity
    friction coefficient
    
Note that not all models include all of the above parameters. If a model does not include a
specific parameters, it does not produce a vector output, even if a vector input is given
for that paramater.

Version history:
V1.0: Original version [Oct 19, 2019]
    
Authors:
* Anders la Cour-Harbo, anders@lacourfamily.dk

"""

def example3_vector_input():
    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.CFrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)

    # Set aircraft values
    aircraft_type = casex.enums.EAircraftType.FIXED_WING
    width = 4
    length = 3.2
    mass = 25
    friction_coefficient = FC.get_coefficient(
        casex.friction_coefficient.EAircraftMaterial.ALUMINUM,
        casex.friction_coefficient.EGroundMaterial.CONCRETE)
    
    # Instantiate and add data to CAircraftSpecs class
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_fuel_type(casex.enums.EFuelType.GASOLINE)
    aircraft.set_fuel_quantity(5)
    aircraft.set_friction_coefficient(friction_coefficient)

    # Use the same impact speed for all models
    # Computed here based on kinetic energy.
    impact_speed = 50
    
    # Impact angle
    impact_angle = 25

    # How large overlap between lethal area from aircraft and from deflagration (explosion)
    critical_areas_overlap = 0.5
    
    # Setup figure to plot compare the model for 4 different scenarios    
    fig, ax = plt.subplots(3, 3, figsize=(12,6))
    plt.style.use('fivethirtyeight')
    
    # Compute the leathal area for the vector input parameters
    p = []

    #Varying width
    v_width = np.linspace(1, 5, 100)
    aircraft.set_width(v_width)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    aircraft.set_width(width)
    
    #Varying length
    v_length = np.linspace(1, 5, 100)
    aircraft.set_length(v_length)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    aircraft.set_width(length)
    
    #Varying impact_angle
    v_impact_angle = np.linspace(10, 80, 100)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))
    impact_angle = 25
    
    #Varying impact_speed
    v_impact_speed = np.linspace(5, 40, 100)
    p.append(CA.critical_area(Model.RCC, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))
    impact_speed = 25

    #Varying critical_area_overlap
    v_critical_areas_overlap = np.linspace(0, 1, 100)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))
    
    #Varying fuel_quantity
    v_fuel_quantity = np.linspace(0, 10, 100)
    aircraft.set_fuel_quantity(v_fuel_quantity)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    aircraft.set_fuel_quantity(5)
    
    #Varying friction coeffient (ground friction during slide)
    v_friction_coefficient = np.linspace(0.2, 0.9, 100)
    aircraft.set_friction_coefficient(v_friction_coefficient)
    p.append(CA.critical_area(Model.RCC, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.RTI, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.FAA, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.NAWCAD, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    p.append(CA.critical_area(Model.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    aircraft.set_friction_coefficient(friction_coefficient)
    
    clr = ['blue', 'orange', 'red', 'green', 'purple']
    
    # Plot this first example to the first of the four subplots
    for k in [0, 1, 2, 3, 4]:
        ax[0, 0].plot(v_width, p[k][0], color = clr[k], linewidth=1)
    ax[0, 0].set_xlabel('Width [m]', fontsize=12)
    ax[0, 0].set_ylabel('Lethal area', fontsize=12)
    ax[0, 0].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)

    for k in [5]:
        ax[0, 1].plot(v_length, p[k][0], color = clr[k-5], linewidth=1)
    ax[0, 1].set_xlabel('Length [m]', fontsize=12)
    ax[0, 1].set_ylabel('Lethal area', fontsize=12)
    ax[0, 1].legend(['RCC'], loc = 0, ncol = 2, fontsize=9)

    for k in [10, 11, 12, 13, 14]:
        ax[0, 2].plot(v_impact_angle, p[k][0], color = clr[k-10], linewidth=1)
    ax[0, 2].set_xlabel('Impact angle [deg]', fontsize=12)
    ax[0, 2].set_ylabel('Lethal area', fontsize=12)
    ax[0, 2].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)

    for k in [15, 16, 18, 19]:
        ax[1, 0].plot(v_impact_speed, p[k][0], color = clr[k-15], linewidth=1)
    ax[1, 0].set_xlabel('Impact speed [m/s]', fontsize=12)
    ax[1, 0].set_ylabel('Lethal area', fontsize=12)
    ax[1, 0].legend(['RCC', 'RTI', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)
   
    for k in [20, 21, 22, 23, 24]:
        ax[1, 1].plot(v_critical_areas_overlap * 100, p[k][0], color = clr[k-20], linewidth=1)
    ax[1, 1].set_xlabel('Lethal area overlap [%]', fontsize=12)
    ax[1, 1].set_ylabel('Lethal area', fontsize=12)
    ax[1, 1].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)
   
    for k in [25, 26, 27, 28, 29]:
        ax[1, 2].plot(v_fuel_quantity, p[k][0], color = clr[k-25], linewidth=1)
    ax[1, 2].set_xlabel('Fuel quantity [L]', fontsize=12)
    ax[1, 2].set_ylabel('Lethal area', fontsize=12)
    ax[1, 2].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)
   
    for k in [30, 31, 33, 34]:
        ax[2, 0].plot(v_friction_coefficient, p[k][0], color = clr[k-30], linewidth=1)
    ax[2, 0].set_xlabel('Friction coefficient [-]', fontsize=12)
    ax[2, 0].set_ylabel('Lethal area', fontsize=12)
    ax[2, 0].legend(['RCC', 'RTI', 'NAWCAD', 'JARUS'], loc = 0, ncol = 2, fontsize=9)
   
    plt.show()
    
    
if __name__ == '__main__':
    example3_vector_input()
