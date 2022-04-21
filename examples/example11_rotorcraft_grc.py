"""
Example 11
---------

"""
from casex import enums, CriticalAreaModels, AircraftSpecs, AnnexFParms

# Data on person size.
person_width = 0.3
person_height = 1.8

# Instantiate necessary classes.
CA = CriticalAreaModels(person_width, person_height)

# Set to the number of the trade-off according to the trade-off table in Annex F.
# 0 means no trade off (original iGRC table), while 1 through 6 are the 6 different trade-offs.
trade_off = 1

# Set to true to see difference between trade-off iGRC and original iGRC.
relative = True    

# Set the appropriate changes for each type of trade-off.
if trade_off == 0:
    impact_angle = 35
    width_factor = 1
    impact_speed_factor = 1
    Dpop_factor = 1
elif trade_off == 1:
    impact_angle = 70
    width_factor = 1
    impact_speed_factor = 1
    Dpop_factor = 1
elif trade_off == 2:
    impact_angle = 80
    width_factor = 1
    impact_speed_factor = 1
    Dpop_factor = 1
else:
    print("trade_off value not legal.")
    exit()

# Instantiate the Annex F parameter class.
AFP_35 = AnnexFParms(35)
AFP_bal = AnnexFParms(impact_angle)

# Change parameters in AFP and recompute ballistic values
for k in range(5):
    AFP_bal.CA_parms[k].cruise_speed = AFP_bal.CA_parms[k].cruise_speed * impact_speed_factor
    AFP_bal.CA_parms[k].wingspan = AFP_bal.CA_parms[k].wingspan * width_factor
    
AFP_bal.recompute_parameters()

# Set aircraft values.
aircraft_type = enums.AircraftType.GENERIC
width = 1
length = 1
mass = 2
friction_coefficient = 0.5

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, length, mass)
aircraft.set_friction_coefficient(friction_coefficient)

# Set parameters for fuel.
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(0)

# Get CoR using the aircraft class.
aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))

if trade_off > 0:
    print("Modified raw iGRC table for trade-off scenario T{:1}".format(trade_off))
else:
    print("Original raw iGRC table")
if relative:
    print("Table show difference to the original raw iGRC table.")
print("")

print("          Max dim   |  ", end = "")
for j in range(0, 5):
    print("{:4.1f} m    ".format(AFP_bal.CA_parms[j].wingspan), end = "")
print("")                                                                    

print("Dpop      Max speed |", end = " ")
for j in range(0, 5):
    print("{:4} m/s  ".format(int(AFP_bal.CA_parms[j].cruise_speed)), end = "")
print("")                                                                    
print("--------------------+------------------------------------------------")

for Dpop in [0.1, 10, 100, 1500, 15000, 100000, 1000000]:
    if (Dpop > 1):
        print ("{:7}             |   ".format(int(Dpop * Dpop_factor)), end = "")
    else:
        print ("Control             |   ", end = "")

    # Loop over columns in the iGRC table.
    for j in range(0, 5):
        
        # Set mass according to Annex F.
        aircraft.set_mass(AFP_35.CA_parms[j].mass)

        # First, set width to nominal values.
        aircraft.set_width(AFP_35.CA_parms[j].wingspan)

        # Compute the AC.
        aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(35))
        p_original = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, AFP_35.CA_parms[j].cruise_speed, 35, 0, -1)
        
        # Then set to modified values.
        aircraft.set_width(AFP_bal.CA_parms[j].wingspan)
    
        # And again, compute AC.
        aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))
        p_trade_off = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, AFP_bal.CA_parms[j].ballistic_impact_velocity, impact_angle, 0, -1)
        # Use this line to use the actual impact angles from AFP.
        #p_trade_off = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, AFP_bal.CA_parms[j].ballistic_impact_velocity, AFP_bal.CA_parms[j].ballistic_impact_angle, 0, -1)
        
        # Compute the raw iGRC according to Annex F.
        raw_iGRC_original = AnnexFParms.iGRC(Dpop, p_original[0]) 
        raw_iGRC_trade_off = AnnexFParms.iGRC(Dpop * Dpop_factor, p_trade_off[0]) 

        if relative:
            print("{:4.1f}      ".format(raw_iGRC_trade_off[1] - raw_iGRC_original[1]), end = "")
        else:
            print("{:4.1f}      ".format(raw_iGRC_trade_off[1] - 0.3), end = "")
        
    print ("")

print("--------------------------------------------------------------------")    
print("Altitude (m)        |   ", end = "")
for k in range(5):
    print("{:4.0f}      ".format(AFP_bal.CA_parms[k].ballistic_descent_altitude), end = "")
print("")
print("Impact angle (deg)  |   ", end = "")
for k in range(5):
    print("{:4.1f}      ".format(AFP_bal.CA_parms[k].ballistic_impact_angle), end = "")
print("")
print("Impact vel (m/s)    |  ", end = "")
for k in range(5):
    print("{:5.1f}     ".format(AFP_bal.CA_parms[k].ballistic_impact_velocity), end = "")
print("")
print("Drag area (m^2)     |   ", end = "")
for k in range(5):
    print("{:4.1f}      ".format(AFP_bal.CA_parms[k].ballistic_frontal_area), end = "")
    
if relative:
    print("")
    print("")
    print("Negative number means lower iGRC relative to no trade-off, and positive means higher iGRC.")