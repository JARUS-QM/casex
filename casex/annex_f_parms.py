"""
This class provides support for redoing some of the computations found in Annex F :cite:`a-JARUS_AnnexF`.
"""
import math
import warnings
from dataclasses import dataclass

import numpy as np

from casex import AircraftSpecs, enums, BallisticDescent2ndOrderDragApproximation, constants


class AnnexFParms:
    """This class contains the following parameters for the 5 size classes in the iGRC table:

    Parameters
    ----------
    impact_angle : float
        [deg] The impact angle of the descending aircraft, measured relative to the ground.

    Attributes
    ----------
    aircraft : :class:`AircraftSpecs`
        The class containing information about the aircraft.
    aircraft_type : :class:`enums.AircraftType`
        The type of aircraft. This parameters is not currently used.
    critical_area_target : float
        [m^2] Size of the largest critical area for each size class.
    ballistic_descent_altitude : float
        [m] Assumed altitude for beginning of ballistic descent.
    ballistic_descent_time : float
        [s] Computed descent time for ballistic descent.
    ballistic_distance : float
        [m] Computed horizontal distance traveled during ballistic descent.
    ballistic_drag_coefficient = 0.8 : float
        [-] Drag coefficient used for ballistic descent.
    ballistic_frontal_area : float
        [m^2] Assumed frontal area used in ballistic computations.
    ballistic_impact_angle : float
        [deg] Computed impact angle with 0 being horizontal.
    ballistic_impact_KE : float
        [J] Computed kinetic energy of aircraft just prior to impact.
    ballistic_impact_velocity : float
        [m/s] Assumed horizontal velocity for beginning of ballistic descent.
    cruise_speed : float
        [m/s]Maximum cruise speed for each size class.
    friction_coefficient = 0.65 : float
        [-] The friction coefficient is assumed constant at 0.65 throughout Annex F :cite:`a-JARUS_AnnexF`.
    glide_reduce = 0.65 : float
        [-] Reduction in glide speed relative to cruise speed.
    glide_speed : float
        [m/s] The glide speed resulting from multiplying the cruise speed by glide_reduce.
    impact_angle : float
        [deg] The impact angle of the aircraft when crashing, measure relative to horizontal.
    KE_critical : float
        [J] Non-lethal energy during slide.
    mass : float
        [kg] Assumed biggest mass for each size class.
    population_bands = [0.25 25 250 2500 25000 250000] : float array
        [ppl/km2] The population density bands used for the iGRC.
    scenario_angles = [10, 35, 62] : float array
        [deg] The three impact angles for the three descent scenarios. The 62 degrees is not actually used but
        recomputed for each ballistic descent.
    terminal_velocity : float
        [m/s] Terminal velocity for aircraft.
    wingspan : float
        Characteristic dimension of the aircraft. See Annex F :cite:`a-JARUS_AnnexF`
        for more detailed explanation on what that is.
    """

    # This dataclass make the programming and plotting more smooth in allowing for looping for virtually all values.
    @dataclass
    class CAParameters:
        wingspan: float
        critical_area_target: float
        cruise_speed: float
        iGRC_impact_angle : float
        ballistic_frontal_area: float
        mass: float
        KE_critical: float
        ballistic_descent_altitude: float
        terminal_velocity: float = 0
        ballistic_impact_velocity: float = 0
        ballistic_impact_angle: float = 0
        ballistic_distance: float = 0
        ballistic_impact_KE: float = 0
        ballistic_descent_time: float = 0
        glide_speed: float = 0
        aircraft: AircraftSpecs = None

    def __init__(self, impact_angle):
        self.person_radius = 0.3
        self.person_height= 1.8
        self.glide_reduce = 0.65
        self.friction_coefficient = 0.65
        self.ballistic_drag_coefficient = 0.8
        self.scenario_angles = np.array([10, 35, 62])
        self.obstacle_reduction = 0.6
        self.population_bands = [0.25, 25, 250, 2500, 25000, 250000]

        self.impact_angle = impact_angle

        # Set aircraft type, the type has no effect in this example, but must be given a value.
        self.aircraft_type = enums.AircraftType.GENERIC

        # Setup the parameters used in the plotting.
        self.CA_parms = []
        #                                      Width   CA       Speed    iGRC angle  Drag area   Mass     lethal KE   Altitude
        self.CA_parms.append(self.CAParameters(1,      8,        25,      35,         0.1,        3,       290/0.5,    75))
        self.CA_parms.append(self.CAParameters(3,      80,       35,      35,         0.5,        50,      290,        100))
        self.CA_parms.append(self.CAParameters(8,      800,      75,      35,         2.0,        400,     290,        200))
        self.CA_parms.append(self.CAParameters(20,     8000,     150,     35,         8.0,        5000,    290,        500))
        self.CA_parms.append(self.CAParameters(40,     43000,    200,     35,         14,         10000,   290,        1000))

        self.recompute_parameters()

    def recompute_parameters(self):
        BDM = BallisticDescent2ndOrderDragApproximation()

        # Compute the parameters for each of the 5 size classes.
        for k in range(5):
            # Compute glide speed based on cruise speed
            self.CA_parms[k].glide_speed = self.glide_reduce * self.CA_parms[k].cruise_speed

            # Define the aircraft.
            self.CA_parms[k].aircraft = AircraftSpecs(self.aircraft_type, self.CA_parms[k].wingspan, 1,
                                                      self.CA_parms[k].mass)

            # Set parameters into aircraft.
            self.CA_parms[k].aircraft.set_ballistic_frontal_area(self.CA_parms[k].ballistic_frontal_area)
            self.CA_parms[k].aircraft.set_ballistic_drag_coefficient(self.ballistic_drag_coefficient)
            self.CA_parms[k].aircraft.set_friction_coefficient(self.friction_coefficient)

            if k == 0:
                # The 1 m column uses 0.8 as CoR in all cases.
                if isinstance(self.impact_angle, np.ndarray):
                    self.CA_parms[k].aircraft.set_coefficient_of_restitution(self.CoR_from_impact_angle(np.full(len(self.impact_angle), 10)))
                else:
                    self.CA_parms[k].aircraft.set_coefficient_of_restitution(self.CoR_from_impact_angle(10))
            else:
                # The other columns uses a CoR depending on angle.
                self.CA_parms[k].aircraft.set_coefficient_of_restitution(self.CoR_from_impact_angle(self.impact_angle))

            # Compute terminal velocity.
            self.CA_parms[k].terminal_velocity = self.CA_parms[k].aircraft.terminal_velocity()

            # Compute ballistic descent values.
            BDM.set_aircraft(self.CA_parms[k].aircraft)
            p = BDM.compute_ballistic_distance(self.CA_parms[k].ballistic_descent_altitude,
                                               self.CA_parms[k].cruise_speed, 0)
            self.CA_parms[k].ballistic_impact_velocity = p[1]
            self.CA_parms[k].ballistic_impact_angle = p[2] * 180 / np.pi
            self.CA_parms[k].ballistic_distance = p[0]
            self.CA_parms[k].ballistic_descent_time = p[3]
            self.CA_parms[k].ballistic_impact_KE = 0.5 * self.CA_parms[k].mass * np.power(p[1], 2)        

    @staticmethod
    def iGRC(pop_dens, CA, TLOS=1E-6, width = 0, use_obstacle_reduction = False, use_integer_reduction = False):
        """Compute the finale integer iGRC as described in Annex F :cite:`a-JARUS_AnnexF`.
        
        This method computes the integer and the raw iGRC values for a given population density and
        size of critical area. The TLOS, target level of safety, can also be set, but the default value
        is :math:`10^{-6}` as described in Annex F :cite:`a-JARUS_AnnexF`.
        
        .. note:: This method converts the population density to ppl/m^2 as needed for the equation.
                    This is because the unit for the input is ppl/km^2, since this is typically
                    how the density is known.
        
        Parameters
        ----------
        pop_dens : float
            [ppl/km^2] Population density
        CA : float
            [m^2] Size of the critical area.
        TLOS : float, optional
            [fatalities per flight hour] Target level of safety (the default is 1e-6).
            This value is described in more detail in Annex F :cite:`a-JARUS_AnnexF`.
        use_obstacle_reduction : bool, optional
            If True, the obstacle reduction (see obstacle_reduction_factor()) is applied to the iGRC value.
            This requires width to be set.
            Default value is False.
        width : float, optional
            Width of the aircraft. This is needed if use_obstacle_reduction is set to True. Otherwise, it is ignored.
            Default value is 0.
        use_integer_reduction: bool, optional
            if True, the 0.3 reduction in iGRC value is applied.
            
        Returns
        -------
        iGRC : integer
            The intrinsic ground risk class (as an integer). This is the raw value rounded up to nearest integer.
        raw iGRC : float
            The raw iGRC before rounding up.
        """
        if use_obstacle_reduction:
            if width == 0:
                warnings.warn("width is not set. Using value of 1 m.")
                width = 1
            pop_dens = pop_dens * AnnexFParms.obstacle_reduction_factor(pop_dens, width)
        
        # Note that the 1E-6 here is the conversion from km^2 to m^2.
        raw_iGRC_value = 1 - math.log10(TLOS / (pop_dens * 1E-6 * CA))
        
        if use_integer_reduction:
            raw_iGRC_value = raw_iGRC_value - 0.3
            
        # The raw iGRC value may be rounded to one decimal.
        raw_iGRC_value = round(raw_iGRC_value * 10) / 10

        return math.ceil(raw_iGRC_value), raw_iGRC_value

    @staticmethod
    def obstacle_reduction_factor(pop_dens, width):
        """Compute the obstacle reduction factor used in the iGRC in Annex F :cite:`a-JARUS_AnnexF`.
        
        The obstacle reduction factor as shown in the table below:

        +---------------------------------+--------------------+---------------------+
        |                                 | 1 m < width <= 3 m | 3 m < width <= 20 m |
        +---------------------------------+--------------------+---------------------+
        | 1,500 <= pop density < 100,000  |    120/200         |     700/2000        |
        +---------------------------------+--------------------+---------------------+

        and 1 if either pop density or width is outside ranges in the table.
        
        Parameters
        ----------
        pop_dens : float
            [ppl/km^2] Population density
        width : float
            [m] Width of aircraft.
            
        Returns
        -------
        obstacle_reduction_factor : float
            The reduction factor for use in iGRC.
        """

        obstacle_reduction_factor = 1

        if 1500 <= pop_dens < 100000:
            if 1 < width <= 3:
                obstacle_reduction_factor = 120 / 200
            elif 3 < width <= 20:
                obstacle_reduction_factor = 700 / 2000
            
        return obstacle_reduction_factor

    @staticmethod
    def CoR_from_impact_angle(impact_angle, angles = None, CoRs = None):
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
