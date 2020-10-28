"""
Example 1
---------
MISSING DOC
"""
import casex


def example1_critical_area():
    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.FrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)

    # Choose impact speed
    impact_speed = 35

    # Choose impact angle
    impact_angle = 35

    # Set aircraft values
    aircraft_type = casex.enums.AircraftType.GENERIC
    width = 1.2
    length = 1
    mass = 25
    friction_coefficient = FC.get_coefficient(casex.enums.AircraftMaterial.ALUMINUM, casex.enums.GroundMaterial.CONCRETE)

    # Instantiate and add data to CAircraftSpecs class
    aircraft = casex.aircraft_specs.AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_fuel_type(casex.enums.FuelType.GASOLINE)
    aircraft.set_fuel_quantity(0)
    aircraft.set_friction_coefficient(friction_coefficient)

    # Get CoR using the Aircraft class
    aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))

    # How large overlap between lethal area from aircraft and from deflagration (explosion)
    # Note that this value is not relevant when there is not fuel onboard, and therefore no explosion
    critical_areas_overlap = 0.5

    # A limit for the non-lethal kinetic energy during slide
    # Set this value to -1 to use the default value from Annex F Appendix A.
    # See the documentation for the critical_area function for details
    KE_lethal = -1

    # The output from lethal_area is: 
    p = CA.critical_area(casex.enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle,
                         critical_areas_overlap, KE_lethal)

    print("Wingspan: {:1.0f}    Mass: {:1.0f}".format(aircraft.width, aircraft.mass))
    print("Horizontal impact speed: {:1.1f} m/s".format(CA.horizontal_speed_from_angle(impact_angle, impact_speed)))
    print("Glide area: {:1.2f} m^2".format(p[1]))
    print("Slide area: {:1.2f} m^2".format(p[2]))
    print("Critical area inert: {:1.1f} m^2".format(p[3]))
    print("Critical area explosion: {:1.1f} m^2".format(p[4]))
    print("Total critical area: {:1.2f} m^2".format(p[0]))


if __name__ == '__main__':
    example1_critical_area()
