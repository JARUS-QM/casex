"""
Example 3
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
friction_coefficient = FC.get_coefficient(enums.AircraftMaterial.ALUMINUM, enums.GroundMaterial.CONCRETE)

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
fig, ax = plt.subplots(3, 3, figsize=(12, 6))
plt.style.use('fivethirtyeight')

# Compute the lethal area for the vector input parameters.
p = []

# This is how to very the width.
v_width = np.linspace(1, 5, 100)
aircraft.set_width(v_width)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the length.
aircraft.set_width(width)
v_length = np.linspace(1, 5, 100)
aircraft.set_length(v_length)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the impact_angle.
aircraft.set_width(width)
v_impact_angle = np.linspace(10, 80, 100)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, v_impact_angle, critical_areas_overlap))

# Varying impact_speed.
v_impact_speed = np.linspace(5, 40, 100)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, v_impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the critical_area_overlap.
impact_speed = 25
v_critical_areas_overlap = np.linspace(0, 1, 100)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, v_critical_areas_overlap))

# This is how to vary the fuel_quantity.
v_fuel_quantity = np.linspace(0, 10, 100)
aircraft.set_fuel_quantity(v_fuel_quantity)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# This is how to vary the friction coefficient (ground friction during slide).
aircraft.set_fuel_quantity(5)
v_friction_coefficient = np.linspace(0.2, 0.9, 100)
aircraft.set_friction_coefficient(v_friction_coefficient)
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

clr = ['blue', 'orange', 'red', 'green', 'purple']

# Now plotting all the results for all the models.
# Note that not all models support all types of variations, and therefore bellow
# some plots do not have all the models.
for k in [0, 1, 2, 3, 4]:
    ax[0, 0].plot(v_width, p[k][0], color=clr[k], linewidth=1)
ax[0, 0].set_xlabel('Width [m]', fontsize=12)
ax[0, 0].set_ylabel('Lethal area', fontsize=12)
ax[0, 0].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

for k in [5]:
    ax[0, 1].plot(v_length, p[k][0], color=clr[k - 5], linewidth=1)
ax[0, 1].set_xlabel('Length [m]', fontsize=12)
ax[0, 1].set_ylabel('Lethal area', fontsize=12)
ax[0, 1].legend(['RCC'], loc=0, ncol=2, fontsize=9)

for k in [10, 11, 12, 13, 14]:
    ax[0, 2].plot(v_impact_angle, p[k][0], color=clr[k - 10], linewidth=1)
ax[0, 2].set_xlabel('Impact angle [deg]', fontsize=12)
ax[0, 2].set_ylabel('Lethal area', fontsize=12)
ax[0, 2].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

for k in [15, 16, 18, 19]:
    ax[1, 0].plot(v_impact_speed, p[k][0], color=clr[k - 15], linewidth=1)
ax[1, 0].set_xlabel('Impact speed [m/s]', fontsize=12)
ax[1, 0].set_ylabel('Lethal area', fontsize=12)
ax[1, 0].legend(['RCC', 'RTI', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

for k in [20, 21, 22, 23, 24]:
    ax[1, 1].plot(v_critical_areas_overlap * 100, p[k][0], color=clr[k - 20], linewidth=1)
ax[1, 1].set_xlabel('Lethal area overlap [%]', fontsize=12)
ax[1, 1].set_ylabel('Lethal area', fontsize=12)
ax[1, 1].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

for k in [25, 26, 27, 28, 29]:
    ax[1, 2].plot(v_fuel_quantity, p[k][0], color=clr[k - 25], linewidth=1)
ax[1, 2].set_xlabel('Fuel quantity [L]', fontsize=12)
ax[1, 2].set_ylabel('Lethal area', fontsize=12)
ax[1, 2].legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

for k in [30, 31, 33, 34]:
    ax[2, 0].plot(v_friction_coefficient, p[k][0], color=clr[k - 30], linewidth=1)
ax[2, 0].set_xlabel('Friction coefficient [-]', fontsize=12)
ax[2, 0].set_ylabel('Lethal area', fontsize=12)
ax[2, 0].legend(['RCC', 'RTI', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

plt.show()
