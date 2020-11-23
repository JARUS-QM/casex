"""
Example 2
--------
This example shows the basics of using the different models in casex.
It shows how to set up the necessary parameters and variables, and how
to call the critical area method to calculate critical areas for the
models.

It also shows how to modify an existing setup to change from one aircraft
to another.
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

# Set aircraft values
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
aircraft.set_coefficient_of_restitution(0.7)  # default value, so in fact no need to set.

# Use the same impact speed for all models.
# Computed here based on kinetic energy.
impact_speed = CA.speed_from_kinetic_energy(34000, aircraft.mass)

# Impact angle.
impact_angle = 25

# Fraction of overlap between lethal area from aircraft and from deflagration (explosion).
critical_areas_overlap = 0.5

# Compute the lethal area for the four different models.
p = []

# One set of parameters.
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# Same setup, but different impact angle.
impact_angle = 65
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# Let's try another aircraft size.
aircraft.set_width(1.8)
aircraft.set_length(1)
aircraft.set_mass(1.1)
aircraft.set_fuel_quantity(1)
impact_speed = CA.speed_from_kinetic_energy(700, aircraft.mass)

impact_angle = 25
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# And now with the steeper impact angle.
impact_angle = 65
for model in enums.CriticalAreaModel:
    p.append(CA.critical_area(model, aircraft, impact_speed, impact_angle, critical_areas_overlap))

# The CA.critical_area returns four outputs. The first is the lethal area.
# The lethal area for the first model is thus obtained by p[0][0], and for the second by p[1][0], etc.

# Setup figure to plot compare the model for 4 different scenarios.
fig, ax = plt.subplots(1, 1, figsize=(12, 6))
plt.style.use('fivethirtyeight')

bar_width = 0.15
index = np.arange(4)

for k in np.arange(0, 5):
    plt.bar(index + k * bar_width, [p[k][0], p[k + 5][0], p[k + 10][0], p[k + 15][0]], bar_width)

ax.set_xlabel('Scenario', fontsize=12)
ax.set_ylabel('Lethal area', fontsize=12)
ax.xaxis.set_ticks(index + 2 * bar_width)
ax.set_xticklabels(['4 m span, 25 deg', '4 m span, 65 deg', '1.8 m span, 25 deg', '1.8 m span, 65 deg'])

ax.legend(['RCC', 'RTI', 'FAA', 'NAWCAD', 'JARUS'], loc=0, ncol=2, fontsize=9)

plt.show()
