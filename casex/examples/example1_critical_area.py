"""
Example 1
---------
This examples provide the basic functionality for computing a critical area.
"""
from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms

# Data on person size.
person_radius = 0.3
person_height = 1.8

# Instantiate necessary classes.
FC = FrictionCoefficients()
CA = CriticalAreaModels(person_radius, person_height)

# Choose impact speed and impact angle.
impact_speed = 45
impact_angle = 35

# Set aircraft values.
aircraft_type = enums.AircraftType.GENERIC
width = 1.5
mass = 5
friction_coefficient = FC.get_coefficient(enums.AircraftMaterial.RUBBER,
                                          enums.GroundMaterial.CONCRETE)

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, mass)
aircraft.set_friction_coefficient(friction_coefficient)

# Set parameters for fuel
aircraft.set_fuel_type(enums.FuelType.GASOLINE)
aircraft.set_fuel_quantity(0)

# Get CoR using the aircraft class.
aircraft.set_coefficient_of_restitution(AnnexFParms.CoR_from_impact_angle(impact_angle))

# Fraction of overlap between lethal area from aircraft and from deflagration.
# Note that this value is not relevant when there is not fuel onboard, and therefore no deflagration.
critical_areas_overlap = 0.5

# A limit for the non-lethal kinetic energy during slide.
# Set this value to -1 to use the default value from Annex F Appendix A.
# See the documentation for the critical_area function for details.
lethal_kinetic_energy = -1

# The output from lethal_area is:
p = CA.critical_area(aircraft, impact_speed, impact_angle,
                     critical_areas_overlap, lethal_kinetic_energy)

# Compute the raw iGRC according to Annex F.
raw_iGRC = AnnexFParms.iGRC(800, p[0])

print("Wingspan:                   {:1.1f} m".format(aircraft.width))
print("Mass:                       {:1.0f} kg".format(aircraft.mass))
print("Horizontal impact speed:    {:1.1f} m/s".format(CA.horizontal_speed_from_angle(impact_angle, impact_speed)))
print("Glide area:                 {:1.1f} m^2".format(p[1]))
print("Slide area:                 {:1.1f} m^2".format(p[2]))
print("Critical area inert:        {:1.1f} m^2".format(p[3]))
print("Critical area deflagration: {:1.1f} m^2".format(p[4]))
print("Total critical area:        {:1.0f} m^2".format(p[0]))
print("Raw iGRC:                   {:1.1f}".format(raw_iGRC[1]))
