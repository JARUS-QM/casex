import warnings
import numpy as np

import casex

class CAircraftSpecs:
    """ Class to hold parameters on the aircraft used in area computations
    
    This class is designed to hold all the parameters on a specific aircraft for which a critical area is to be computed.
    The following parameters are stored in this class:
        
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | Parameters                | Description                                                                                                                     |
    +===========================+=================================================================================================================================+
    | width                     | The width of the aircraft is the horitonal size of the aircraft orthogonal to the direction of                                  |
    |                           | travel. This value is used to determine the width of the glide and slide areas.                                                 |
    |                           | Therefore, this value is the wingspan for fixed wing aircraft, the rotor diameter for rotorcraft,                               |
    |                           | and the rotortip to rotortip distance for multirotor aircraft.                                                                  |            
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | length                    | Length of the aircraft. The concept is the same as width. The length is only used in the RCC model.                             |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | mass                      | Mass of the aircraft in kg. This is the total mass at the time of crash, including fuel.                                        |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | aircraft_type             | The type of aircraft as given in :class:`EAircraftType`.                                                                        |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | fuel_type                 | Fuel type, such as fossil fuels or batteries. Given in :class:`EFuelType`.                                                      |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | fuel_quantity             | Quantity of fuel in L. For batteries the quantity is also given in L, i.e. the volume of the battery.                           |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | friction_coefficient      | Coefficient of friction between aircraft and ground. Appropriate values can be found using :class:`CFrictionCoefficients`.      |
    |                           | Default value is 0.6.                                                                                                           |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | coefficient_of_restitution| Coefficient of restitution expresses the loss of energy on impact. Default value is 0.7.                                        |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | ballistic_frontal_area    | Frontal area of the aircraft during ballistic descent. This is the area size of the aircraft as projected in the direction of   |
    |                           | descent.                                                                                                                        |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    |balllistic_drag_coefficient| Drag coefficient of the aircraft during ballistic descent. For future use.                                                      |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | glide_drag_coefficient    | Drag coefficient of the aircraft during glide descent.                                                                          |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | wing_area                 | Wing area of a fixed wing aircraft.                                                                                             |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | max_flight_time           | Maximum flight time on the given amount of fuel. For future use.                                                                |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | cruise_speed              | Cruise speed of the aircraft.                                                                                                   |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | glide_speed               | Glide speed of the aircraft when descending in a glide without thrust.                                                          |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | glide_ratio               | Glide ratio of the aircraft when descending in an optimal glide angle without thrust.                                           |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | parachute_deployment_time | Deployment time for the parachute, measured from the time deployment is signalled to full deployment.                           |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | parachute_area            | Area of the parachute generating drag during descent and full deployment.                                                       |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    | parachute_drag_coef       | Drag coefficient.                                                                                                                 |
    +---------------------------+---------------------------------------------------------------------------------------------------------------------------------+
    
    Many of the these parameters are not used in computations of critical area, but are reserved for future use.
    """

    def __init__(self, aircraft_type, width, length, mass, fuel_type = casex.enums.EFuelType.GASOLINE, fuel_quantity = 0):
        """ Constructor
        
        Parameters
        ----------        
        aircraft_type : :class:`ECriticalAreaModel`
            Type of aircraft as given by EAircraftType
        width : float
            [m] Width of aircraft (wingspan, characteristic dimension)
        length : float
            [m] Length of aircraft
        mass : float
            [kg] Mass of the aircraft
        """

        self.reset_values()

        self.width = width
        self.length = length
        self.mass = mass
        
        # Default values
        self.friction_coefficient = 0.6
        self.coefficient_of_restitution = 0.7
        self.fuel_type = fuel_type
        self.fuel_quantity = fuel_quantity
        
        self.width_length_mass_check()
    
        if not isinstance(aircraft_type, casex.enums.EAircraftType):
            warnings.warn("Aircraft type not recognized. Type set to fixed wing.")
            self.aircraft_type = casex.enums.EAircraftType.FIXED_WING
        else:
            self.aircraft_type = aircraft_type                
                
    def set_aircraft_type(self, aircraft_type):
        """Set aircraft type.
        
        This value is currently not used in any computation, and is reserved for future use.
                
        Parameters
        ----------
        aircraft_type : :class:`EAircraftType`
            Type of aircraft
 
        Returns
        -------
        None
        """
        if not isinstance(aircraft_type, casex.enums.EAircraftType):
            warnings.warn("Aircraft type not recognized. Type set to fixed wing.")
            self.aircraft_type = casex.enums.EAircraftType.FIXED_WING
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
        """ Set the aircraft length.
        
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
        """ Set the aircraft mass.
                
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
        None

        Returns
        -------
        None        
        """
        if np.any(self.mass <= 0):
            warnings.warn("Non-positive mass does not make sense. Subsequent results are invalid.")
        elif np.any(self.mass < 1):
            warnings.warn("This toolbox is not designed for a mass below 1 kg. Subsequent results cannot be trusted.")
        if np.any(self.width <= 0):
            warnings.warn("Non-positive width does not make sense. Subsequent results are invalid.")
        elif np.any(self.width < 0.1):
            warnings.warn("This toolbox is not designed for a width below 0.1 m. Subsequent results cannot be trusted.")
        if np.any(self.length <= 0):
            warnings.warn("Non-positive length does not make sense. Subsequent results are invalid.")
        elif np.any(self.length < 0.1):
            warnings.warn("This toolbox is not designed for a length below 0.1 m. Subsequent results cannot be trusted.")            

    def set_wing_area(self, wing_area):
        """Set the aircraft wing area (only relevant for fixed wing aircraft).        
                
        Parameters
        ----------
        wing_area : float
            [m^2] Wing area of the aircraft
            
        Returns
        -------
        None
        """
        self.wing_area = wing_area
            
    def set_fuel_type(self, fuel_type):
        """Set the type of fuel.
        
        Sets the type of fuel onboard the aircraft. For a list of options, see :class:`EFuelType`.
        
        Parameters
        ----------       
        fuel_type : :class:`EFuelType`
            Type of fuel
            
        Returns
        -------
        None
        """
        
        if not isinstance(fuel_type, casex.enums.EFuelType):
            warnings.warn("Fuel type not recognized. Type set to gasoline.")
            self.fuel_type = casex.enums.EFuelType.GASOLINE
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
            [-] Coefficient for the glide resistance. Default value if not set is 0.6.
 
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
            [-] Coefficient of restitution for the ground impact. Default value if not set is 0.7.
 
        Returns
        -------
        None
       """
        
        if np.any(coefficient_of_restitution <= 0):
            warnings.warn("Non-positive coefficient of restitution does not make sense. Subsequent results are invalid.")
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
        """ Set drag coefficient for ballistic descent.
 
        Parameters
        ----------
        ballistic_drag_coefficient : float
            [-] Drag coefficient for ballistic descent

        Returns
        -------
        None
       """
        if np.any(ballistic_drag_coefficient <= 0):
            warnings.warn("Non-positive ballistic drag coefficient does not make sense. Subsequent results are invalid.")
        
        self.ballistic_drag_coefficient = ballistic_drag_coefficient

    def set_glide_drag_coefficient(self, glide_drag_coefficient):
        """ Set drag coefficient for glide.
 
        Parameters
        ----------
        glide_drag_coefficient : float
            [-] Drag coefficient for glide descent

        Returns
        -------
        None
       """
        if np.any(glide_drag_coefficient <= 0):
            warnings.warn("Non-positive glide drag coefficient does not make sense. Subsequent results are invalid.")
        
        self.glide_drag_coefficient = glide_drag_coefficient

    def set_max_flight_time(self, max_flight_time):
        """ Set max flight time.
 
        Parameters
        ----------
        max_flight_time : float
            [s] Maximum flight time

        Returns
        -------
        None
       """
        if np.any(max_flight_time <= 0):
            warnings.warn("Non-positive maximum flight time does not make sense. Subsequent results are invalid.")
            
        self.max_flight_time = max_flight_time
        
    def set_cruise_speed(self, cruise_speed):
        """Set cruise speed.
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
            [-] Draf coefficient for the parachute.

        Returns
        -------
        None
        """
        if np.any(parachute_deployment_time < 0):
            warnings.warn("Negative parachute deployment time does not make sense. Subsequent results are invalid.")
        if np.any(parachute_area <= 0):
            warnings.warn("Non-positive parachute area does not make sense. Subsequent results are invalid.")
        if np.any(parachute_drag_coef <= 0):
            warnings.warn("Non-positive parachute drag coefficient does not make sense. Subsequent results are invalid.")

        self.parachute_deployment_time = parachute_deployment_time
        self.parachute_area = parachute_area
        self.parachute_drag_coef = parachute_drag_coef
        
    def set_Oswald_efficiency_number(self, Oswald_efficiency_number):
        """ Set Oswald efficiency number for glide.
 
        Parameters
        ----------
        Oswald_efficiency_number : float
            [-] Oswald efficiency number.

        Returns
        -------
        None
       """
        if np.any(Oswald_efficiency_number <= 0):
            warnings.warn("Non-positive Oswald efficiency number does not make sense. Subsequent results are invalid.")
        
        self.Oswald_efficiency_number = Oswald_efficiency_number
        
    def set_max_LD_ratio(self, max_LD_ratio):
        """ Set maximum L/D ratio
 
        Parameters
        ----------
        max_LD_ratio : float
            [-] Maximum ratio between lift and drag

        Returns
        -------
        None
        """
        if np.any(max_LD_ratio <= 0):
            warnings.warn("Non-positive lift to drag ratio does not make sense. Subsequent results are invalid.")
        
        self.max_LD_ratio = max_LD_ratio
        
    def compute_best_glide_speed_wing_area(self):
        """ Compute the optimal glide speed based on wing area
        
        NOTE THAT THIS FUNCTION IS UNTESTED!!
 
        Parameters
        ----------
        None

        Returns
        -------
        glide_speed : float
            [m/s] Optimal glide speed.
        """
    
        nom = 4 * np.power(self.mass, 2) * np.power(casex.constants.GRAVITY, 2) * np.power(np.cos(np.atan2(1, self.max_LD_ratio)), 2)
        denom = np.pi * np.power(casex.constants.AIR_DENSITY, 2) * self.glide_drag_coefficient * self.wing_area * np.power(self.width, 2) * self.Oswald_efficiency_number
    
        return np.power(np.divide(nom, denom), 1/4)
 
    def terminal_velocity(self, rho):
        """Compute terminal velocity for free falling aircraft
        """
        return np.sqrt(2 * self.mass * casex.constants.GRAVITY / rho / self.ballistic_frontal_area / self.ballistic_drag_coefficient)
    
       
    def COR_from_impact_angle(self, impact_angle, angles = [9, 90], CoRs = [0.9, 0.6]):
        """
        
        Parameters
        ----------        
        impact_angle : float
            [deg] The impact angle between 0 and 90.

        Returns
        ----------
        coefficient of restitution : float
            The coefficient of restitution for the given impact angle.
        """
    
        if np.any(impact_angle < 0):
            warnings.warn("Impact angle must be positive. Output is not valid.")
        if np.any(impact_angle > 90):
            warnings.warn("Impact angle must be less than 90 degrees. Output is not valid.")
            
        param = np.polyfit(angles, CoRs, 1)
            
        return (param[0]*impact_angle + param[1])        
       
    def reset_values(self):
        """Reset all aircraft parameters.

        Parameters
        ----------
        None
 
        Returns
        -------
        None
        """
        self.aircraft_type = None
        self.width = None
        self.length = None
        self.mass = None
        self.wing_area = None
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
        self.Oswald_efficiency_number = None
        self.max_LD_ratio = None