"""
MISSING DOC
"""
import warnings

from casex.enums import AircraftMaterial, GroundMaterial


class FrictionCoefficients:
    """Friction coefficients between a variety of aircraft materials and ground types.
    
    This class provides some help to determine an appropriate friction coefficient for a sliding aircraft.
    The values provided here are guidance only, and not all combinations of aircraft material and ground type is
    known in this class.
    
    The coefficient takes the following values.
    +-------------------------+------------------------------------------------------+
    |                         | Ground type                                          |
    +-------------------------+----------+----------+----------+----------+----------+
    |                         | Concrete | Asphalt  | Grass    | Sand     | Soil     | 
    +                         +----------+----------+----------+----------+----------+
    | Aircraft material       |                                                      |
    +=========================+==========+==========+==========+==========+==========+
    | Glass fiber             | 0.2      | n/a      | 0.15     | n/a      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Carbon fiber            | n/a      | n/a      | n/a      | n/a      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Aluminum                | 0.4      | n/a      | n/a      | n/a      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Steel                   | 0.45     | n/a      | n/a      | 0.2      | 0.4      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Wood                    | 0.6      | n/a      | n/a      | n/a      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Styrofoam               | n/a      | n/a      | n/a      | n/a      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    | Rubber                  | 0.7      | 0.9      | 0.35     | 0.5      | n/a      |
    +-------------------------+----------+----------+----------+----------+----------+
    
    .. note:: The above coefficients are drawn from a variety of sources of unconfirmed reliability.
              As such, these are the authors' best guesses at appropriate coefficients.
              The true coefficient depends on the state of the materials (wet, dry, greased, etc.) and the actual
              material (e.g. there are numerous types of concrete, soil, etc.).
    
    .. warning:: The friction coefficients provided are guidance only!
                 Ultimate responsibility for correct choice and use of friction coefficient rests with the user!
    """

    def get_coefficient(self, aircraft_material, ground_material):
        """Provide friction coefficient for aircraft sliding over ground.
        
        Parameters
        ----------
        aircraft_material : :class:`enums.AircraftMaterial`
            Type of the aircraft material.
        ground_material : :class:`enums.GroundMaterial`
            Type of the ground material.
            
        Returns
        -------
        friction_coefficient : float
            The friction coefficient between the aircraft and ground material.
            Returns -1 if the coefficient is not available (see table above).
            Returns -2 if either material is not recognized.
        """
        if not isinstance(aircraft_material, AircraftMaterial):
            warnings.warn("aircraft_material is not recognized. Use a material from enums.AircraftMaterial.")
            return -2
        if not isinstance(ground_material, GroundMaterial):
            warnings.warn("ground_material is not recognized. Use a material from enums.GroundMaterial.")
            return -2

        # This returns the appropriate coefficient. It returns -1 if there is no appropriate coefficient.
        return {
            GroundMaterial.CONCRETE: self.__on_concrete(aircraft_material),
            GroundMaterial.ASPHALT: self.__on_asphalt(aircraft_material),
            GroundMaterial.GRASS: self.__on_grass(aircraft_material),
            GroundMaterial.SAND: self.__on_sand(aircraft_material),
            GroundMaterial.SOIL: self.__on_soil(aircraft_material)
        }.get(ground_material, -2)

    @staticmethod
    def __on_concrete(aircraft_material):
        # MISSING DOC
        return {
            AircraftMaterial.GLASSFIBER: 0.2,
            AircraftMaterial.CARBONFIBER: -1,        # TODO: To be updated
            AircraftMaterial.ALUMINUM: 0.4,
            AircraftMaterial.STEEL: 0.45,
            AircraftMaterial.WOOD: 0.6,
            AircraftMaterial.STYROFOAM: -1,          # TODO: To be updated
            AircraftMaterial.RUBBER: 0.7
        }.get(aircraft_material, -2)

    @staticmethod
    def __on_asphalt(aircraft_material):
        # MISSING DOC
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: -1,             # TODO: To be updated
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.9
        }.get(aircraft_material, -2)

    @staticmethod
    def __on_grass(aircraft_material):
        # MISSING DOC
        return {
            AircraftMaterial.GLASSFIBER: 0.15,
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: -1,             # TODO: To be updated
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.35
        }.get(aircraft_material, -2)

    @staticmethod
    def __on_sand(aircraft_material):
        # MISSING DOC
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: 0.2,
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.5
        }.get(aircraft_material, -2)

    @staticmethod
    def __on_soil(aircraft_material):
        # MISSING DOC
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: 0.4,
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: -1             # TODO: To be updated
        }.get(aircraft_material, -2)
