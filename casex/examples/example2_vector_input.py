"""
Example 2
---------
This example shows how to use the models using vector input to generate a vector output.
Using this feature it is possible to generate graphs for variations on one input parameter.

This example shows this for the following parameters:
    width
    length
    impact angle
    impact speed
    lethal area overlap
    fuel quantity
    friction coefficient

Note that not all models include all of the above parameters. If a model does not include a
specific parameters, it does not produce a vector output, even if a vector input is given
for that parameter.
"""
import matplotlib.pyplot as plt
import numpy as np

from casex import FrictionCoefficients, CriticalAreaModels, enums, AircraftSpecs


# Data on person size.
person_width = 0.3
person_height = 1.8

# Instantiate necessary classes.
FC = FrictionCoefficients()
CA = CriticalAreaModels(person_width, person_height)

# Set aircraft values.
aircraft_type = enums.AircraftType.FIXED_WING
width = 4
length = 3.2
mass = 25
friction_coefficient = FC.get_coefficient(enums.AircraftMaterial.ALUMINUM,
                                          enums.GroundMaterial.CONCRETE)

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, length, mass)
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(5)
aircraft.set_friction_coefficient(friction_coefficient)

# Set impact speed and angle.
impact_speed = 50
impact_angle = 25

# Fraction of overlap between lethal area from aircraft and from deflagration (explosion).
critical_areas_overlap = 0.5

# Setup figure to plot a comparison of the model for 4 different scenarios.
fig, ax = plt.subplots(3, 2, figsize=(12, 6))
plt.style.use('fivethirtyeight')

# Compute the lethal area for the vector input parameters.
p = []

# This is how to vary the width.
v_width = np.linspace(1, 5, 100)
aircraft.set_width(v_width)
p.append(CA.critical_area(aircraft, impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the impact_angle.
v_impact_angle = np.linspace(10, 80, 100)
aircraft.set_width(width)
p.append(CA.critical_area(aircraft, impact_speed, v_impact_angle, critical_areas_overlap))

# Varying impact_speed.
v_impact_speed = np.linspace(5, 40, 100)
p.append(CA.critical_area(aircraft, v_impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the critical_area_overlap.
v_critical_areas_overlap = np.linspace(0, 1, 100)
p.append(CA.critical_area(aircraft, impact_speed, impact_angle, v_critical_areas_overlap))

# This is how to vary the fuel_quantity.
v_fuel_quantity = np.linspace(0, 10, 100)
aircraft.set_fuel_quantity(v_fuel_quantity)
p.append(CA.critical_area(aircraft, impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the friction coefficient (ground friction during slide).
aircraft.set_fuel_quantity(5)
v_friction_coefficient = np.linspace(0.2, 0.9, 100)
aircraft.set_friction_coefficient(v_friction_coefficient)
p.append(CA.critical_area(aircraft, impact_speed, impact_angle, critical_areas_overlap))

# Now plotting all the results for all the models.
ax[0, 0].plot(v_width, p[0][0], linewidth=1)
ax[0, 0].set_xlabel('Width [m]', fontsize=12)
ax[0, 0].set_ylabel('Lethal area [m$^2$]', fontsize=12)

ax[0, 1].plot(v_impact_angle, p[1][0], linewidth=1)
ax[0, 1].set_xlabel('Impact angle [deg]', fontsize=12)
ax[0, 1].set_ylabel('Lethal area [m$^2$]', fontsize=12)

ax[1, 0].plot(v_impact_speed, p[2][0], linewidth=1)
ax[1, 0].set_xlabel('Impact speed [m/s]', fontsize=12)
ax[1, 0].set_ylabel('Lethal area [m$^2$]', fontsize=12)

ax[1, 1].plot(v_critical_areas_overlap * 100, p[3][0], linewidth=1)
ax[1, 1].set_xlabel('Lethal area overlap [%]', fontsize=12)
ax[1, 1].set_ylabel('Lethal area [m$^2$]', fontsize=12)

ax[2, 0].plot(v_fuel_quantity, p[4][0], linewidth=1)
ax[2, 0].set_xlabel('Fuel quantity [L]', fontsize=12)
ax[2, 0].set_ylabel('Lethal area [m$^2$]', fontsize=12)

ax[2, 1].plot(v_friction_coefficient, p[5][0], linewidth=1)
ax[2, 1].set_xlabel('Friction coefficient [-]', fontsize=12)
ax[2, 1].set_ylabel('Lethal area [m$^2$]', fontsize=12)

plt.show()
