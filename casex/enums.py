from enum import Enum

class EFuelType(Enum):
    """Enum for fuel type
    
    
    """
    GASOLINE = 1
    PETROL = 1          # Same fuel as gasoline
    DIESEL = 2
    JETA1 = 3
    AVGAS = 5
    METHANOL = 6
    LIFE = 7            # LiFe (Lithium-iron) battery
    LION = 8            # Lithium-ion battery
    LIQUID_HYDROGEN = 9
    LIQUID_BUTANE = 10
    
class EWrapping(Enum):
    """Enum for wrapping type for aircraft heading.
    """
    PI2PI = 1
    NONE = 2
    
class EAircraftType(Enum):
    """Enum for aircraft type.
    """
    GENERIC = 1
    FIXED_WING = 2
    ROTORY_WING = 3
    MULTI_ROTOR = 4
    LIGHTER_THAN_AIR = 5
    
    
class ECriticalAreaModel(Enum):
    """Enum for critical area models.
    """
    RCC= 1
    RTI = 2
    FAA = 3
    NAWCAD = 4
    JARUS = 5