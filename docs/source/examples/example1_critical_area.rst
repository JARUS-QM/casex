========================
Example 1: Critical area
========================

*General text explaining what the example shows*

*Text explaining the first part of the code*

.. code-block:: python

    from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs

    # Data on person size.
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes.
    FC = FrictionCoefficients()
    CA = CriticalAreaModels(person_width, person_height)

    # Choose impact speed.
    impact_speed = 35

    # Choose impact angle.
    impact_angle = 35

    # Set aircraft values.
    aircraft_type = enums.AircraftType.GENERIC
    width = 1.2
    length = 1
    mass = 25
    friction_coefficient = FC.get_coefficient(enums.AircraftMaterial.ALUMINUM, enums.GroundMaterial.CONCRETE)

*Text explaining the second part of the code*

.. code-block:: python

    # Instantiate and add data to AircraftSpecs class.
    aircraft = AircraftSpecs(aircraft_type, width, length, mass)
    aircraft.set_fuel_type(enums.FuelType.GASOLINE)
    aircraft.set_fuel_quantity(0)
    aircraft.set_friction_coefficient(friction_coefficient)

    # Get CoR using the aircraft class.
    aircraft.set_coefficient_of_restitution(aircraft.COR_from_impact_angle(impact_angle))

    # Fraction of overlap between lethal area from aircraft and from deflagration (explosion).
    # Note that this value is not relevant when there is not fuel onboard, and therefore no explosion.
    critical_areas_overlap = 0.5

    # A limit for the non-lethal kinetic energy during slide.
    # Set this value to -1 to use the default value from Annex F Appendix A.
    # See the documentation for the critical_area function for details.
    KE_lethal = -1

    # The output from lethal_area is:
    p = CA.critical_area(enums.CriticalAreaModel.JARUS, aircraft, impact_speed, impact_angle, critical_areas_overlap, KE_lethal)

*Text explaining the output of the code*

.. code-block:: console

    Wingspan: 1    Mass: 25
    Horizontal impact speed: 28.7 m/s
    Glide area: 7.17 m^2
    Slide area: 111.02 m^2
    Critical area inert: 118.2 m^2
    Critical area explosion: 0.0 m^2
    Total critical area: 118.20 m^2
