"""
Class to hold parameters on the aircraft used in area computations.
"""
import warnings
import numpy as np

from casex import enums, constants

class AircraftSpecs:
    """    
    This class is designed to hold all the parameters on a specific aircraft for which a critical area is to be
    computed. Many of the these parameters are not used in computations of critical area, but are reserved for
    future use.

    Parameters
    ----------
    aircraft_type : :class:`enums.AircraftType`
        Type of aircraft.
    width : float
        [m] Width of aircraft (wingspan, characteristic dimension).
    length : float
        [m] Length of aircraft.
    mass : float
        [kg] Mass of the aircraft.
    fuel_type : :class:'enums.FuelType, optional
        Fuel type, such as fossil fuels or batteries (the default is `FuelType.GASOLINE`).
    fuel_quantity : float, optional
        [L] The quantity of fuel in liters. For batteries the quantity is also given in L,
        i.e. the volume of the battery (the default is 0, which means that no deflagration is assumed upon crash).

    Attributes
    ----------
    width : float
        [m] The width of the aircraft is the horizontal size of the aircraft orthogonal to the direction of travel.
        This value is used to determine the width of the glide and slide areas. Therefore, this value is the wingspan
        for fixed wing aircraft, the rotor diameter for rotorcraft, and the rotortip to rotortip distance for
        multirotor aircraft.
    length : float
        [m] Length of the aircraft. The concept is the same as width. The length is only used in the RCC model.
    mass : float
        [kg] Mass of the aircraft in kg. This is the total mass at the time of crash, including fuel.
    aircraft_type : :class:`enums.AircraftType`
        The type of aircraft.
    fuel_type : :class:`enums.FuelType`
        Fuel type, such as fossil fuels or batteries (the default is `FuelType.GASOLINE`).
    fuel_quantity : float
        [L] The quantity of fuel in liters. For batteries the quantity is also given in L,
        i.e. the volume of the battery (the default is 0, which means that no deflagration is assumed upon crash).
    friction_coefficient : float
        [-] Coefficient of friction between aircraft and ground. Appropriate values can be found using
        :class:`FrictionCoefficients` (the default is 0.6).
    coefficient_of_restitution : float
        [-] Coefficient of restitution expresses the loss of energy on impact (the default is 0.7).
    ballistic_frontal_area : float
        [m^2] Frontal area of the aircraft during ballistic descent. This is the area size of the aircraft as projected
        in the direction of descent.
    ballistic_drag_coefficient : float
        [-] Drag coefficient of the aircraft during ballistic descent. For future use.
    glide_drag_coefficient : float
        [-] Drag coefficient of the aircraft during glide descent.
    max_flight_time : float
        [s] Maximum flight time on the given amount of fuel. For future use.
    cruise_speed : float
        [m/s] Cruise speed of the aircraft.
    glide_speed : float
        [m/s] Glide speed of the aircraft when descending in a glide without thrust.
    glide_ratio : float
        [-] Glide ratio of the aircraft when descending in an optimal glide angle without thrust.
    parachute_deployment_time : float
        [s] Deployment time for the parachute, measured from the time deployment is signalled to full deployment.
    parachute_area : float
        [m^2] Area of the parachute generating drag during descent and full deployment.
    parachute_drag_coef : float
        [-] Drag coefficient.
    """

    def __init__(self, aircraft_type, width, length, mass, fuel_type=enums.FuelType.GASOLINE, fuel_quantity=0):
        self.ballistic_frontal_area = None
        self.ballistic_drag_coefficient = None
        self.glide_drag_coefficient = None
        self.max_flight_time = None
        self.cruise_speed = None
        self.glide_speed = None
        self.glide_ratio = None
        self.parachute_deployment_time = None
        self.parachute_area = None
        self.parachute_drag_coef = None

        self.reset_values()

        self.width = width
        self.length = length
        self.mass = mass

        # Default values.
        self.friction_coefficient = 0.6
        self.coefficient_of_restitution = 0.7
        self.fuel_type = fuel_type
        self.fuel_quantity = fuel_quantity

        self.width_length_mass_check()

        if not isinstance(aircraft_type, enums.AircraftType):
            warnings.warn("Aircraft type not recognized. Type set to fixed wing.")
            self.aircraft_type = enums.AircraftType.FIXED_WING
        else:
            self.aircraft_type = aircraft_type

    def set_aircraft_type(self, aircraft_type):
        """Set aircraft type.
        
        The type of aircraft such as fixed wing or rotorcraft.
        
        .. note: This value is currently not used in any computation, and is reserved for future use.
                
        Parameters
        ----------
        aircraft_type : :class:`enums.AircraftType`
            Type of aircraft.
 
        Returns
        -------
        None
        """
        if not isinstance(aircraft_type, enums.AircraftType):
            warnings.warn("Aircraft type not recognized. Type set to FIXED_WING.")
            self.aircraft_type = enums.AircraftType.FIXED_WING
        else:
            self.aircraft_type = aircraft_type

    def set_width(self, width):
        """Set the aircraft width.        
                
        Parameters
        ----------
        width : float
            [m] Width of the aircraft
            
        Returns
        -------
        None
        """
        self.width = width
        self.width_length_mass_check()

    def set_length(self, length):
        """Set the aircraft length.
        
        Parameters
        ----------
        length : float
            [m] Length of the aircraft.

        Returns
        -------
        None
        """
        self.length = length
        self.width_length_mass_check()

    def set_mass(self, mass):
        """Set the aircraft mass.
                
        Parameters
        ----------
        mass : float
            [kg] Mass of aircraft.

        Returns
        -------
        None
        """
        self.mass = mass
        self.width_length_mass_check()

    def width_length_mass_check(self):
        """Out of range check on width, length, and mass.
        
        Performs an out of range check of width, length, and mass. Warnings are issued for parameters out of range.
        
        Parameters
        ----------

        Returns
        -------
        None
        """
        if np.any(self.mass <= 0):
            warnings.warn("Non-positive mass does not make sense. Subsequent results are invalid.")
        elif np.any(self.mass < 1):
            warnings.warn("This package is not designed for a mass below 1 kg. Subsequent results cannot be trusted.")
        if np.any(self.width <= 0):
            warnings.warn("Non-positive width does not make sense. Subsequent results are invalid.")
        elif np.any(self.width < 0.1):
            warnings.warn("This package is not designed for a width below 0.1 m. Subsequent results cannot be trusted.")
        if np.any(self.length <= 0):
            warnings.warn("Non-positive length does not make sense. Subsequent results are invalid.")
        elif np.any(self.length < 0.1):
            warnings.warn(
                "This package is not designed for a length below 0.1 m. Subsequent results cannot be trusted.")

    def set_fuel_type(self, fuel_type):
        """Set the type of fuel.
        
        Sets the type of fuel onboard the aircraft. For a list of options, see :class:`enums.FuelType`.
        
        Parameters
        ----------       
        fuel_type : :class:`enums.FuelType`
            Type of fuel.
            
        Returns
        -------
        None
        """
        if not isinstance(fuel_type, enums.FuelType):
            warnings.warn("Fuel type not recognized. Type set to gasoline.")
            self.fuel_type = enums.FuelType.GASOLINE
        else:
            self.fuel_type = fuel_type

    def set_fuel_quantity(self, fuel_quantity):
        """Set the fuel quantity.
        
        Parameters
        ----------
        fuel_quantity : float
            [L] Quantify of fuel. Set to 0 for no fuel in case no deflagration is desired in the computations.

        Returns
        -------
        None
        """
        if np.any(fuel_quantity < 0):
            warnings.warn("Negative fuel quantity does not make sense. Subsequent results are invalid.")

        self.fuel_quantity = fuel_quantity

    def set_friction_coefficient(self, friction_coefficient):
        """Set coefficient of friction between aircraft and ground.
        
        Parameters
        ----------
        friction_coefficient : float
            [-] Coefficient for the glide resistance (the default is 0.6).

        Returns
        -------
        None
        """
        if np.any(friction_coefficient <= 0):
            warnings.warn("Non-positive friction coefficient does not make sense. Subsequent results are invalid.")
        if np.any(friction_coefficient > 1.5):
            warnings.warn("Friction coefficient seems very large. Subsequent results may be invalid.")

        self.friction_coefficient = friction_coefficient

    def set_coefficient_of_restitution(self, coefficient_of_restitution):
        """Set coefficient of restitution.
        
        Parameters
        ----------
        coefficient_of_restitution : float
            [-] Coefficient of restitution for the ground impact (the default is 0.7).
 
        Returns
        -------
        None
        """
        if np.any(coefficient_of_restitution <= 0):
            warnings.warn(
                "Non-positive coefficient of restitution does not make sense. Subsequent results are invalid.")
        if np.any(coefficient_of_restitution > 1.5):
            warnings.warn("Coefficient of restitution seems very large. Subsequent results may be invalid.")

        self.coefficient_of_restitution = coefficient_of_restitution

    def set_ballistic_frontal_area(self, ballistic_frontal_area):
        """Set frontal area for computation of terminal velocity in ballistic descent.
        
        Parameters
        ----------
        ballistic_frontal_area : float
            [m^2] Frontal area of the aircraft during ballistic descent.
 
        Returns
        -------
        None
        """
        if np.any(ballistic_frontal_area <= 0):
            warnings.warn("Non-positive ballistic frontal area does not make sense. Subsequent results are invalid.")

        self.ballistic_frontal_area = ballistic_frontal_area

    def set_ballistic_drag_coefficient(self, ballistic_drag_coefficient):
        """Set drag coefficient for ballistic descent.
 
        Parameters
        ----------
        ballistic_drag_coefficient : float
            [-] Drag coefficient for ballistic descent.

        Returns
        -------
        None
        """
        if np.any(ballistic_drag_coefficient <= 0):
            warnings.warn(
                "Non-positive ballistic drag coefficient does not make sense. Subsequent results are invalid.")

        self.ballistic_drag_coefficient = ballistic_drag_coefficient

    def set_glide_drag_coefficient(self, glide_drag_coefficient):
        """Set drag coefficient for glide.
 
        Parameters
        ----------
        glide_drag_coefficient : float
            [-] Drag coefficient for glide descent.

        Returns
        -------
        None
        """
        if np.any(glide_drag_coefficient <= 0):
            warnings.warn("Non-positive glide drag coefficient does not make sense. Subsequent results are invalid.")

        self.glide_drag_coefficient = glide_drag_coefficient

    def set_max_flight_time(self, max_flight_time):
        """Set max flight time.
 
        Parameters
        ----------
        max_flight_time : float
            [s] Maximum flight time.

        Returns
        -------
        None
        """
        if np.any(max_flight_time <= 0):
            warnings.warn("Non-positive maximum flight time does not make sense. Subsequent results are invalid.")

        self.max_flight_time = max_flight_time

    def set_cruise_speed(self, cruise_speed):
        """Set cruise speed.

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        None
        """
        if np.any(cruise_speed <= 0):
            warnings.warn("Non-positive cruise speed does not make sense. Subsequent results are invalid.")

        self.cruise_speed = cruise_speed

    def set_glide_speed_ratio(self, glide_speed, glide_ratio):
        """Set glide ratio.
 
        Parameters
        ----------
        glide_speed : float
            [m/s] Glide speed in the direction of travel.
        glide_ratio : float
            [-] The horizontal distance per vertical distance for the aircraft at glide speed.

        Returns
        -------
        None
        """
        if np.any(glide_speed <= 0):
            warnings.warn("Non-positive glide speed does not make sense. Subsequent results are invalid.")
        if np.any(glide_ratio < 0):
            warnings.warn("Negative glide ratio does not make sense. Subsequent results are invalid.")

        self.glide_speed = glide_speed
        self.glide_ratio = glide_ratio

    def set_parachute(self, parachute_deployment_time, parachute_area, parachute_drag_coef):
        """Set parachute parameters.
        
        Parameters
        ----------
        parachute_deployment_time : float
            [s] Time from initiation of parachute deployment to a fully deployed parachute.
        parachute_area : float
            [m^2] Size of the parachute.
        parachute_drag_coef : float
            [-] Drag coefficient for the parachute.

        Returns
        -------
        None
        """
        if np.any(parachute_deployment_time < 0):
            warnings.warn("Negative parachute deployment time does not make sense. Subsequent results are invalid.")
        if np.any(parachute_area <= 0):
            warnings.warn("Non-positive parachute area does not make sense. Subsequent results are invalid.")
        if np.any(parachute_drag_coef <= 0):
            warnings.warn(
                "Non-positive parachute drag coefficient does not make sense. Subsequent results are invalid.")

        self.parachute_deployment_time = parachute_deployment_time
        self.parachute_area = parachute_area
        self.parachute_drag_coef = parachute_drag_coef

    def terminal_velocity(self):
        """Compute terminal velocity for free falling aircraft.

        Parameters
        ----------

        Returns
        -------
        terminal_velocity : float
            [m/s] The terminal velocity for the aircraft.
        """
        return np.sqrt(2 * self.mass * constants.GRAVITY / constants.AIR_DENSITY / self.ballistic_frontal_area /
                       self.ballistic_drag_coefficient)

    def COR_from_impact_angle(self, impact_angle, angles=None, CoRs=None):
        """Compute a coefficient of restitution for a given impact angle.
        
        This method assumes an affine relation between impact angle and CoR. Therefore, two angles and two CoR values
        are used to determine this relation. The default is as described in Annex F that the CoR is 0.8 at a 10 degree
        impact and 0.6 at a 90 degree (vertical) impact. This values are used as defaults, but others can be specified.
        
        Parameters
        ----------        
        impact_angle : float
            [deg] The impact angle between 0 and 90.
        angles : float array, optional
            [deg] Array with two different angle of impact values (the default is [10, 90]).
        CoRs : float array, optional
            [-] Array with two COR values corresponding to the two angles (the default is [0.8, 0.6]).

        Returns
        -------
        coefficient of restitution : float
            [-] The coefficient of restitution for the given impact angle.
        """
        if angles is None:
            angles = [10, 90]
        if CoRs is None:
            CoRs = [0.8, 0.6]

        if np.any(impact_angle < 0):
            warnings.warn("Impact angle must be positive. Output is not valid.")
        if np.any(impact_angle > 90):
            warnings.warn("Impact angle must be less than 90 degrees. Output is not valid.")

        param = np.polyfit(angles, CoRs, 1)

        return param[0] * impact_angle + param[1]

    def reset_values(self):
        """Reset all aircraft parameters.

        Parameters
        ----------
 
        Returns
        -------
        None
        """
        self.aircraft_type = None
        self.width = None
        self.length = None
        self.mass = None
        self.cruise_speed = None
        self.max_flight_time = None
        self.fuel_type = None
        self.fuel_quantity = None
        self.glide_speed = None
        self.glide_ratio = None
        self.glide_drag_coefficient = None
        self.ballistic_frontal_area = None
        self.ballistic_drag_coefficient = None
        self.parachute_deployment_time = None
        self.parachute_area = None
        self.parachute_drag_coef = None
