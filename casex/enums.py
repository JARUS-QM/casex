from enum import Enum


class FuelType(Enum):
    """Enum for fuel type."""
    GASOLINE = 1
    PETROL = 1  # Same fuel as gasoline.
    DIESEL = 2
    JETA1 = 3
    AVGAS = 5
    METHANOL = 6
    LIFE = 7  # LiFe (Lithium-iron) battery.
    LION = 8  # Lithium-ion battery.
    LIQUID_HYDROGEN = 9
    LIQUID_BUTANE = 10


class Wrapping(Enum):
    """Enum for wrapping type for aircraft heading."""
    PI2PI = 1
    NONE = 2


class AircraftType(Enum):
    """Enum for aircraft type."""
    GENERIC = 1
    FIXED_WING = 2
    ROTORY_WING = 3
    MULTI_ROTOR = 4
    LIGHTER_THAN_AIR = 5


class AircraftMaterial(Enum):
    """Enum of the aircraft materials."""
    GLASSFIBER = 1
    CARBONFIBER = 2
    ALUMINUM = 3
    STEEL = 4
    WOOD = 5
    STYROFOAM = 6
    RUBBER = 7


class GroundMaterial(Enum):
    """Enum of the ground materials."""
    CONCRETE = 1
    ASPHALT = 2
    GRASS = 3
    SAND = 4
    SOIL = 5
