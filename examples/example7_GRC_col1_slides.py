import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

def example7_GRC_col1_slides():
    """Example 7: Slide distance for column 1 in GRC
   
    """
    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.CFrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)

    # Non-used parameters
    critical_areas_overlap = 0
    length = 1
    
    # Set aircraft values
    aircraft_type = casex.enums.EAircraftType.FIXED_WING
    width = 1
    mass = 3
    friction_coefficient = 0.7#FC.get_coefficient(coefs.EAircraftMaterial.ALUMINUM, coefs.EGroundMaterial.CONCRETE)
    
    # Instantiate and add data to CAircraftSpecs class
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_fuel_type(casex.enums.EFuelType.GASOLINE)
    aircraft.set_fuel_quantity(0)
    aircraft.set_friction_coefficient(friction_coefficient)

    # Use the same impact speed for all models
    # Computed here based on kinetic energy.
    impact_speed = 20
    
    # Impact angle
    impact_angle = np.linspace(10, 90, 100)

    # Setup figure to plot compare the model for 4 different scenarios    
    fig, ax = plt.subplots(1, 2, figsize=(12,6))
    plt.style.use('fivethirtyeight')
    fig.suptitle('JARUS model scenario: 1 m, 3 kg, 0.7 fric, 0.7 COR, 80 J lethal KE, 20 m/s', fontsize=14)
    
    # Compute the lethal area for the vector input parameters
    p = []

    # Now set a very high mass to effectively remove slide distance reduction
    aircraft.set_mass(1e6)
    aircraft.set_coefficient_of_restitution(1)
    # No reduction
    p.append(CA.critical_area(casex.enums.ECriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))

    # Reduction with 80 J
    aircraft.set_mass(3)    
    p.append(CA.critical_area(casex.enums.ECriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    
    # Reduction with COR
    aircraft.set_coefficient_of_restitution(0.7)
    p.append(CA.critical_area(casex.enums.ECriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap))
    
    clr = ['blue', 'orange','red', 'green']
    
    ax[0].plot(impact_angle, p[0][0], color = clr[0], linewidth=2)
    ax[0].plot(impact_angle, p[1][0], color = clr[1], linewidth=2)
    ax[0].plot(impact_angle, p[2][0], color = clr[2], linewidth=2)
    ax[0].plot(impact_angle, p[2][1], color = clr[3], linestyle = (0, (5, 10)), linewidth=2)
    ax[0].set_xlabel('Angle [deg]', fontsize=12)
    ax[0].set_ylabel('Total lethal area', fontsize=12)
    ax[0].legend(['No reduction', 'KE reduction', 'KE+COR reduction', 'Exemption'], loc = 0, ncol = 1, fontsize=9)
    ax[0].grid()
    ax[0].set_title('Total lethal area', fontsize=12)

    ax[1].plot(impact_angle, p[0][2], color = clr[0], linewidth=2)
    ax[1].plot(impact_angle, p[1][2], color = clr[1], linewidth=2)
    ax[1].plot(impact_angle, p[2][2], color = clr[2], linewidth=2)
    ax[1].set_xlabel('Angle [deg]', fontsize=12)
    ax[1].set_ylabel('Lethal area', fontsize=12)
    ax[1].legend(['No reduction', 'KE reduction', 'KE+COR reduction'], loc = 0, ncol = 1, fontsize=9)
    ax[1].grid()
    ax[1].set_title('Slide lethal area', fontsize=12)
   
    plt.show()
    
    
if __name__ == '__main__':
    example7_GRC_col1_slides()
