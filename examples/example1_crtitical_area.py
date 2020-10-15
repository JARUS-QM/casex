import casex

"""
Example 1
---------
    

"""
def example1_critical_area():
    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.CFrictionCoefficients()
    CA = casex.critical_area_models.CCriticalAreaModels(person_width, person_height)
    
    # Choose impact speed
    impact_speed = 35
    
    # Choose impact angle
    impact_angle = 35

    # Set aircraft values
    aircraft_type = casex.enums.EAircraftType.GENERIC
    width = 0.001
    length = 1
    mass = 25
    friction_coefficient = 0.5 #FC.get_coefficient(casex.friction_coefficient.EAircraftMaterial.ALUMINUM, casex.friction_coefficient.EGroundMaterial.CONCRETE)
    
    # Instantiate and add data to CAircraftSpecs class
    Aircraft = casex.aircraft_specs.CAircraftSpecs(aircraft_type, width, length, mass)
    Aircraft.set_fuel_type(casex.enums.EFuelType.GASOLINE)
    Aircraft.set_fuel_quantity(0)
    Aircraft.set_friction_coefficient(friction_coefficient)

    # Get CoR using the Aircraft class
    Aircraft.set_coefficient_of_restitution(Aircraft.COR_from_impact_angle(impact_angle))
    
    # How large overlap between lethal area from aircraft and from deflagration (explosion)
    # Note that this value is not relevant when there is not fuel onboard, and therefore no explosion
    critical_areas_overlap = 0.5
    
    # A limit for the non-lethal kinetic energy during slide
    # Set this value to -1 to use the default value from Annex F Appendix A. See the documentation for the critical_area function for details
    KE_lethal = -1
    
    # The output from lethal_area is: 
    p = CA.critical_area(casex.enums.ECriticalAreaModel.JARUS, Aircraft, impact_speed, impact_angle, critical_areas_overlap, KE_lethal)

    print("Wingspan: {:1.0f}    Mass: {:1.0f}".format(Aircraft.width, Aircraft.mass))
    print("Horizontal impact speed: {:1.1f} m/s".format(CA.horizontal_speed_from_angle(impact_angle, impact_speed)))
    print("Glide area: {:1.2f} m^2".format(p[1]))
    print("Slide area: {:1.2f} m^2".format(p[2]))
    print("Critical area inert: {:1.1f} m^2".format(p[3]))
    print("Critical area explosion: {:1.1f} m^2".format(p[4]))
    print("Total critical area: {:1.2f} m^2".format(p[0]))
    
if __name__ == '__main__':
    example1_critical_area()

