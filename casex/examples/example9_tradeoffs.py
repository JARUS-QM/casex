"""
Example 9
---------
This example demonstrates the validity of the trade offs between population density, speed and max dimensions.

The example prints one of the 6 different trade-offs described in Annex F for alternative iGRC tables.
It is also possible to print the difference between the original iGRC and any of the 6 alternatives.

Note that this example accounts for both the 0.3 reduction in iGRC and reduction due to obstacles, as described in the Annex.
"""
from casex import enums, CriticalAreaModels, AircraftSpecs, AnnexFParms

# Data on person size.
person_width = 0.3
person_height = 1.8

# Instantiate necessary classes.
CA = CriticalAreaModels(person_width, person_height)

# The trade-off tables are only valid for impact angle 35 degrees.
impact_angle = 35

# Instantiate the Annex F parameter class.
AFP = AnnexFParms(impact_angle)

# Instantiate and add data to AircraftSpecs class.
# Note that the values here are not important, since they will be changed below.
aircraft = AircraftSpecs(enums.AircraftType.GENERIC, 1, 1, 1)

# Friction coefficient from Annex F
aircraft.set_friction_coefficient(AFP.friction_coefficient)

# Set parameters for fuel.
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(0)

# Get CoR using the aircraft class.
aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))

# Set to the number of the trade-off according to the trade-off table in Annex F.
# 0 means no trade off (original iGRC table), while 1 through 6 are the 6 different trade-offs.
trade_off = 0

# Set to true to see difference between trade-off iGRC and original iGRC.
relative = False    

# Set the appropriate changes for each type of trade-off.
if trade_off == 0:
    width_factor        = 1
    impact_speed_factor = 1
    Dpop_factor         = 1
elif trade_off == 1:
    width_factor        = 1     
    impact_speed_factor = 1.4  
    Dpop_factor         = 0.5                             
elif trade_off == 2:
    width_factor        = 2   
    impact_speed_factor = 1        
    Dpop_factor         = 0.5                             
elif trade_off == 3:
    width_factor        = 0.5 
    impact_speed_factor = 1      
    Dpop_factor         = 2                            
elif trade_off == 4:
    width_factor        = 0.5
    impact_speed_factor = 1.4
    Dpop_factor         = 1                               
elif trade_off == 5:
    width_factor        = 1      
    impact_speed_factor = 0.75 
    Dpop_factor         = 1.7                       
elif trade_off == 6:
    width_factor        = 1.7
    impact_speed_factor = 0.75   
    Dpop_factor         = 1                            
else:
    print("trade_off value not legal.")
    exit()

if trade_off > 0:
    print("Modified raw iGRC table for trade-off scenario T{:1}".format(trade_off))
else:
    print("Original raw iGRC table")
    
if relative:
    print("Table show difference to the original raw iGRC table.")
print("")

print("             Max dim   |  ", end = "")
for j in range(0, 5):
    print("{:4.1f} m    ".format(AFP.CA_parms[j].wingspan * width_factor), end = "")
print("")                                                                    

print("Dpop         Max speed |", end = " ")

for j in range(0, 5):
    print("{:4} m/s  ".format(int(AFP.CA_parms[j].cruise_speed * impact_speed_factor)), end = "")
    
print("")                                                                    
print("-----------------------+--------------------------------------------------")

for Dpop in [0.1, 10, 100, 1500, 15000, 100000, 1000000]:
    
    if (Dpop > 1):
        print ("{:7} ppl/km^2       |   ".format(int(Dpop * Dpop_factor)), end = "")
    else:
        print ("      Controlled       |   ", end = "")

    # Loop over columns in the iGRC table.
    for j in range(0, 5):
        
        # Set mass according to Annex F.
        aircraft.set_mass(AFP.CA_parms[j].mass)

        # First, set width and speed to nominal values.
        aircraft.set_width(AFP.CA_parms[j].wingspan)
        impact_speed = AFP.CA_parms[j].cruise_speed

        # Compute the AC.
        p_original = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, 0, -1)
        
        # Then set to modified values.
        aircraft.set_width(AFP.CA_parms[j].wingspan * width_factor)
        impact_speed = AFP.CA_parms[j].cruise_speed * impact_speed_factor
    
        # And again, compute AC.
        p_trade_off = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, 0, -1)

        # Compute the raw iGRC according to Annex F.
        raw_iGRC_original = AnnexFParms.iGRC(Dpop,
                                             p_original[0],
                                             use_convervative_reduction=True,
                                             use_obstacle_reduction=True) 
        raw_iGRC_trade_off = AnnexFParms.iGRC(Dpop * Dpop_factor,
                                              p_trade_off[0],
                                              use_convervative_reduction=True,
                                              use_obstacle_reduction=True) 

        if relative:
            print("{:4.1f}      ".format(raw_iGRC_trade_off[1] - raw_iGRC_original[1]), end = "")
        else:
            print("{:4.1f}      ".format(raw_iGRC_trade_off[1]), end = "")
        
    print ("")
    
if relative:
    print("")
    print("Negative number means lower iGRC relative to no trade-off, and positive means higher iGRC.")