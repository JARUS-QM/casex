"""
This class provides support for redoing some of the computations found in Annex F :cite:`a-JARUS_AnnexF`.
"""
import math
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
    wingspan : float
        Characteristic dimension of the aircraft. See Annex F :cite:`a-JARUS_AnnexF`
        for more detailed explanation on what that is.
    critical_area_target : float
        [m^2] Size of the largest critical area for each size class.
    cruise_speed : float
        [m/s]Maximum cruise speed for each size class.
    mass : float
        [kg] Assumed biggest mass for each size class.
    KE_critical : float
        [J] Non-lethal energy during slide.
    friction_coefficient = 0.5 : float
        [-] The friction coefficient is assumed constant at 0.5 throughout Annex F :cite:`a-JARUS_AnnexF`.
    glide_reduce = 0.7 : float
        [-] Reduction in glide speed relative to cruise speed.
    glide_speed : float
        [m/s] The glide speed resulting from multiplying the cruise speed by glide_reduce.
    aircraft : :class:`AircraftSpecs`
        The class containing information about the aircraft.
    scenario_angles = [9, 35, 80] : float array
        [deg] The three impact angles for the three descent scenarios. The 80 degrees is not actually used but
        recomputed for each ballistic descent.
    terminal_velocity : float
        [m/s] Terminal velocity for aircraft.
    ballistic_frontal_area : float
        [m^2] Assumed frontal area used in ballistic computations.
    ballistic_drag_coefficient = 0.7 : float
        [-] Drag coefficient used for ballistic descent.
    ballistic_descent_altitude : float
        [m] Assumed altitude for beginning of ballistic descent.
    ballistic_impact_velocity :float
        [m/s] Assumed horizontal velocity for beginning of ballistic descent.
    ballistic_impact_angle : float
        [deg] Computed impact angle with 0 being horizontal.
    ballistic_distance : float
        [m] Computed horizontal distance traveled during ballistic descent.
    ballistic_impact_KE : float
        [J] Computed kinetic energy of aircraft just prior to impact.
    ballistic_descent_time : float
        [s] Computed descent time for ballistic descent.
    impact_angle : float
        [deg] The impact angle of the aircraft when crashing, measure relative to horizontal.
    aircraft_type : :class:`enums.AircraftType`
        The type of aircraft. This parameters is not currently used.
    horizontal_COR : float
        [-] The coefficient of restitution for a near horizontal impact.
    vertical_COR : float
        [-] The coefficient of restitution for a vertical impact. The actual COR is determined
        as a first order interpolation between `horizontal_COR` for 0 degrees and `vertical_COR`
        for 90 degrees.
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
        self.glide_reduce = 0.7
        self.friction_coefficient = 0.5
        self.ballistic_drag_coefficient = 0.7
        self.scenario_angles = np.array([9, 35, 80])

        self.impact_angle = impact_angle

        # Set aircraft type, the type has no effect in this example, but must be given a value.
        self.aircraft_type = enums.AircraftType.GENERIC

        # Setup the parameters used in the plotting.
        self.CA_parms = []
        #                                      Width   CA       Speed    iGRC angle  Drag area   Mass     lethal KE   Altitude
        self.CA_parms.append(self.CAParameters(1,      6.5,     25,      35,         0.1,        3,       290/0.5,    50))
        self.CA_parms.append(self.CAParameters(3,      200,     35,      35,         0.5,        50,      290,        100))
        self.CA_parms.append(self.CAParameters(8,      2000,    75,      35,         2.0,        400,     290,        200))
        self.CA_parms.append(self.CAParameters(20,     20000,   150,     35,         8.0,        5000,    290,        500))
        self.CA_parms.append(self.CAParameters(40,     66000,   200,     35,         14,         10000,   290,        1000))
    
        # Upper and low value for coefficient of restitution (over 9 to 90 degree impact angles).
        self.horizontal_COR = 0.9
        self.vertical_COR = 0.6

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
                # The 1 m column uses 0.9 as CoR in all cases.
                self.CA_parms[k].aircraft.set_coefficient_of_restitution(0.9)
            else:
                # The other columns uses a CoR depending on angle.
                self.CA_parms[k].aircraft.set_coefficient_of_restitution(
                    self.CA_parms[k].aircraft.COR_from_impact_angle(self.impact_angle, [self.scenario_angles[0], 90],
                                                                    [self.horizontal_COR, self.vertical_COR]))

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
    def iGRC(pop_dens, CA, TLOS=1E-6, use_obstacle_reduction = False, use_convervative_reduction = False):
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
        use_convervative_reduction: bool, optional
            if True, the 0.3 reduction in iGRC value is applied.
            
        Returns
        -------
        iGRC : integer
            The intrinsic ground risk class (as an integer). This is the raw value rounded up to nearest integer.
        raw iGRC : float
            The raw iGRC before rounding up.
        """
        if use_obstacle_reduction:
            pop_dens = pop_dens * AnnexFParms.obstacle_reduction_factor(pop_dens, CA)
        
        # Note that the 1E-6 here is the conversion from km^2 to m^2.
        raw_iGRC_value = 1 - math.log10(TLOS / (pop_dens * 1E-6 * CA))
        
        if use_convervative_reduction:
            raw_iGRC_value = raw_iGRC_value - 0.3
            
        # The raw iGRC value may be rounded to one decimal.
        raw_iGRC_value = round(raw_iGRC_value * 10) / 10

        return math.ceil(raw_iGRC_value), raw_iGRC_value

    @staticmethod
    def obstacle_reduction_factor(pop_dens, CA):
        """Compute the obstacle reduction factor used in the iGRC in Annex F :cite:`a-JARUS_AnnexF`.
        
        The obstacle reduction factor is 120/200 when the popuplation density is between 1,500 and 100,000
        and the critical area is between 6.5 and 20,000. Otherwise it is 1.
        
        Parameters
        ----------
        pop_dens : float
            [ppl/km^2] Population density
        CA : float
            [m^2] Size of the critical area.
            
        Returns
        -------
        obstacle_reduction_factor : float
            The reduction factor for use in iGRC.
        """

        obstacle_reduction_factor = 1

        if 1500 <= pop_dens < 100000:
            if 7 < CA <= 2000:
                obstacle_reduction_factor = 120 / 200
            elif 2000 < CA < 20000:
                obstacle_reduction_factor = 700 / 2000
            
        return obstacle_reduction_factor
