"""
Example 11
---------
This example provides the code for producing a large variety of iGRC tables, including the tables found in Annex F and the SORA.

It can show iGRC for varying popuplation densities, for a specific impact angle or for a ballistic descent, and with and without obstacles.
"""
import numpy as np
from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms

show_with_obstacles = False
show_ballistic = False
show_convervative_reduction = True
show_CFIT_angle = True

# Data on person size.
person_width = 0.3
person_height = 1.8

# Set impact angle.
impact_angle = 9 if show_CFIT_angle else 35

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
# Values are not relevant here, since they will be changed below.
aircraft = AircraftSpecs(enums.AircraftType.GENERIC, 1, 1, 1)

# Friction coefficient from Annex F.
aircraft.set_friction_coefficient(AFP.friction_coefficient)

# Set parameters for fuel
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(0)

# Set list of population density bands in the table.
pop_density = np.sort(np.array([0.1, 10, 100, 1500, 15000, 100000, 30, 300, 2000, 2500, 3000, 10000, 20000, 50000]))

# Initialize variables.,
iGRC_table = np.zeros((len(pop_density), 5))
impact_angles = np.zeros((5))
p = np.zeros((5, 5))

# Loop over columns in the iGRC table.
for j in range(0, 5):
    
    # Set mass according to Annex F.
    aircraft.set_mass(AFP.CA_parms[j].mass)

    # First, set width and speed to nominal values.
    aircraft.set_width(AFP.CA_parms[j].wingspan)
    
    if show_ballistic:
        impact_speed = AFP.CA_parms[j].ballistic_impact_velocity
        impact_angle = AFP.CA_parms[j].ballistic_impact_angle
    else:
        impact_speed = AFP.CA_parms[j].glide_speed if show_CFIT_angle else AFP.CA_parms[j].cruise_speed

    # Get CoR using the aircraft class.
    if j > 1:
        aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))
    else:
        aircraft.set_coefficient_of_restitution(0.9)

    # Compute the CA.
    p[j] = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, 0, -1)
    
    # Store the impact angle (only relevant for ballistic).
    impact_angles[j] = impact_angle

# Compute the iGRC values.
for i in range(len(pop_density)):
    for j in range(0, 5):
        iGRC_table[i][j] = AFP.iGRC(pop_density[i],
                                    p[j][0],
                                    use_obstacle_reduction = show_with_obstacles,
                                    use_convervative_reduction = show_convervative_reduction)[1]

print("Final iGRC", end = "")

if show_ballistic:
    print(" (ballistic)")
else:
    print(" ({:d} deg)".format(impact_angle))
    
print("                          1 m       3 m       8 m      20 m      40 m")
print("--------------------+-------------------------------------------------")

for i in range(len(pop_density)):
    
    if (pop_density[i] > 1):
        print("{:7.0f} [ppl/km^2]  | ".format(pop_density[i]), end = "")
    else:
        print("Controlled (< 0.1)  | ", end = "")
 
    for j in range(0, 5):
        print("{:7.1f}   ".format(iGRC_table[i][j]), end = "")
    
    print("")
    
print("--------------------+-------------------------------------------------")
print("     CA size [m^2]  |", end = "")

for j in range(0, 5):
    print("{:8.0f}  ".format(p[j][0]), end = "")
    
print("")
print("Slide distance [m]  |", end = "")

for j in range(0, 5):
    print("{:8.0f}  ".format(p[j][2] / AFP.CA_parms[j].wingspan), end = "")
    
if show_ballistic:
    print("")
    print("Impact angle [deg]  |", end = "")
    
    for j in range(0, 5):
        print("{:8.0f}  ".format(impact_angles[j]), end = "")
        
    print("")
    print("Altitude [m]        |    ", end = "")
    
    for k in range(5):
        print("{:4.0f}      ".format(AFP.CA_parms[k].ballistic_descent_altitude), end = "")
        
    print("")
    print("Impact angle [deg]  |    ", end = "")
    
    for k in range(5):
        print("{:4.1f}      ".format(AFP.CA_parms[k].ballistic_impact_angle), end = "")
        
    print("")
    print("Impact vel [m/s]    |   ", end = "")
    
    for k in range(5):
        print("{:5.1f}     ".format(AFP.CA_parms[k].ballistic_impact_velocity), end = "")
        
    print("")
    print("Drag area [m^2]     |    ", end = "")
    
    for k in range(5):
        print("{:4.1f}      ".format(AFP.CA_parms[k].ballistic_frontal_area), end = "")
        
        
print("")
print("--------------------+-------------------------------------------------")

