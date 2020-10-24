import warnings

import casex
import casex.enums
from casex.enums import AircraftMaterial, GroundMaterial


class CFrictionCoefficients:
    """Friction coefficients between a variety of aircraft materials and ground types
    
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
       The true coefficient depends on the state of the materials (wet, dry, greased, etc.) and the actual material (e.g. there are numerous types of concrete, soil, etc.).
    
    .. warning:: The friction coefficients provided are guidance only!
       Ultimate responsibility for correct choice and use of friction coefficient rests with the user!
    
    
    """
    def __init__(self):
        self._self_test()
    
    def get_coefficient(self, aircraft_material, ground_material):
        """Provide friction coefficient for aircraft sliding over ground
        
        Parameters
        ----------
        aircraft_material : :class:`casex.enums.AircraftMaterial`
            Type of the aircraft material.
        ground_material : :class:`casex.enums.GroundMaterial`
            Type of the ground material.
            
        Returns
        -------
        friction_coeficient : float
            The friction coefficient between the aircraft and ground material.
            Returns -1 if the coefficient is not available (see table above).
            Returns -2 if either material is not recognized.
        """
        if not isinstance(aircraft_material, AircraftMaterial):
            warnings.warn("aircraft_material is not recognized. Use a material from EAircraftMaterial.")
            return -2
        if not isinstance(ground_material, GroundMaterial):
            warnings.warn("ground_material is not recognized. Use a material from EGroundMaterial.")
            return -2
            
        # This returns the appropriate coefficient.
        # It returns -1 if there is no appropriate coefficient.
        return {
            GroundMaterial.CONCRETE: self._on_concrete(aircraft_material),
            GroundMaterial.ASPHALT: self._on_asphalt(aircraft_material),
            GroundMaterial.GRASS: self._on_grass(aircraft_material),
            GroundMaterial.SAND: self._on_sand(aircraft_material),
            GroundMaterial.SOIL: self._on_soil(aircraft_material)
        }.get(ground_material, -2)
    
    def _on_concrete(self, aircraft_material):
        return {
            AircraftMaterial.GLASSFIBER: 0.2,
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: 0.4,
            AircraftMaterial.STEEL: 0.45,
            AircraftMaterial.WOOD: 0.6,
            AircraftMaterial.STYROFOAM: -1,          # TODO: To be updated
            AircraftMaterial.RUBBER: 0.7
        }.get(aircraft_material, -2)
    
    def _on_asphalt(self, aircraft_material):
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: -1,             # TODO: To be updated
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.9
        }.get(aircraft_material, -2)
    
    def _on_grass(self, aircraft_material):
        return {
            AircraftMaterial.GLASSFIBER: 0.15,
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: -1,             # TODO: To be updated
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.35
        }.get(aircraft_material, -2)

    def _on_sand(self, aircraft_material):
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: 0.2,
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: 0.5
        }.get(aircraft_material, -2)

    def _on_soil(self, aircraft_material):
        return {
            AircraftMaterial.GLASSFIBER: -1,        # TODO: To be updated
            AircraftMaterial.CARBONFIBER: -1,       # TODO: To be updated
            AircraftMaterial.ALUMINUM: -1,          # TODO: To be updated
            AircraftMaterial.STEEL: 0.4,
            AircraftMaterial.WOOD: -1,              # TODO: To be updated
            AircraftMaterial.STYROFOAM: -1,         # TODO: To be updated
            AircraftMaterial.RUBBER: -1             # TODO: To be updated
        }.get(aircraft_material, -2)


    def _self_test(self):
        """Self test of member functions.
        
        This function can be use to perform a self test of all functions.
        The purpose it make sure that there are not code errors.
        It does not check for equation errors.
        It is not exhaustive, but gives a good indication.
        """
        
        #get_coefficient(self, aircraft_material, ground_material):
        self.get_coefficient(casex.enums.AircraftMaterial.GLASSFIBER, casex.enums.GroundMaterial.CONCRETE)
