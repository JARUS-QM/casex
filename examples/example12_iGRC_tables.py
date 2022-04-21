"""
Example 12
---------
This example provides the code for producing some of the iGRC tables in Annex F.
"""
import numpy as np
from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms

show_with_obstacles = True

# Data on person size.
person_width = 0.3
person_height = 1.8

impact_angle = 35

# Instantiate necessary classes.
FC = FrictionCoefficients()
CA = CriticalAreaModels(person_width, person_height)
AFP = AnnexFParms(impact_angle)

# Set aircraft values.
aircraft_type = enums.AircraftType.GENERIC
width = 1.5 # This will be changed later for each column.
length = 1  # This is not used in JARUS model.
mass = 5    # This will be changed later for each column.

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, length, mass)
aircraft.set_friction_coefficient(0.5)

# Set parameters for fuel
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(0)

pop_density = np.array([0.1, 10, 100, 1500, 15000, 100000])

iGRC_table = np.zeros((len(pop_density), 5))
critical_area = np.zeros((5))
slide_distance = np.zeros((5))

# Loop over columns in the iGRC table.
for j in range(0, 5):
    
    # Set mass according to Annex F.
    aircraft.set_mass(AFP.CA_parms[j].mass)

    # First, set width and speed to nominal values.
    aircraft.set_width(AFP.CA_parms[j].wingspan)
    impact_speed = AFP.CA_parms[j].cruise_speed

    # Get CoR using the aircraft class.
    if j > 1:
        aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))
    else:
        aircraft.set_coefficient_of_restitution(0.9)

    # Compute the AC.
    p = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, 0, -1)
    critical_area[j] = p[0]
    slide_distance[j] = p[2] / AFP.CA_parms[j].wingspan

for i in range(len(pop_density)):

    for j in range(0, 5):

        ObstacleReduction = 1
        if 1499 < pop_density[i] < 100000 and 6.5 < critical_area[j] < 20000 and show_with_obstacles:
            ObstacleReduction = 120 / 200

        iGRC_table[i][j] = AFP.iGRC(pop_density[i], critical_area[j] * ObstacleReduction)[1] - 0.3


print("Final iGRC")
print("            1 m    3 m    8 m    20 m   40 m")
for i in range(len(pop_density)):
    if (pop_density[i] > 1):
        print("{:7.0f} |  ".format(pop_density[i]), end = "")
    else:
        print("Control |  ", end = "")
 
    for j in range(0, 5):
        print("{:4.1f}   ".format(iGRC_table[i][j]), end = "")
    
    print("")
print("CA [m^2]| ", end = "")
for j in range(0, 5):
    print("{:5.0f}  ".format(critical_area[j]), end = "")
print("")
print("Distance| ", end = "")
for j in range(0, 5):
    print("{:5.0f}  ".format(slide_distance[j]), end = "")
print("")
