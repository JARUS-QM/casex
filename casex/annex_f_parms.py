"""
MISSING DOC
"""
import math
from dataclasses import dataclass

import numpy as np

from casex import AircraftSpecs, enums, BallisticDescent2ndOrderDragApproximation


class AnnexFParms:
    """This class provides support for redoing some of the computations found in Annex F.
    
    It contains the following parameters for the 5 size classes in the iGRC table:
    
    +----------------------------------+----------------------------------------------------------------------+
    | wingspan                         | Same as width                                                        |
    +----------------------------------+----------------------------------------------------------------------+
    | critical_area_target             | Size of the largest critical area for each size class                |
    +----------------------------------+----------------------------------------------------------------------+
    | cruise_speed                     | Maximum cruise speed for each size class                             |
    +----------------------------------+----------------------------------------------------------------------+
    | mass                             | Assumed biggest mass for each size class                             |
    +----------------------------------+----------------------------------------------------------------------+
    | KE_critical                      | Non-lethal energy during slide                                       |
    +----------------------------------+----------------------------------------------------------------------+
    | friction_coefficient = 0.5       | The friction coefficient is assumed constant throughout Annex F      |
    +----------------------------------+----------------------------------------------------------------------+
    | glide_reduce = 0.7               | Reduction in glide speed relative to cruise speed                    |
    +----------------------------------+----------------------------------------------------------------------+
    | scenario_angles = [9, 35, 80]    | The three impact angles for the three descent scenarios.             |
    |                                  | The 80 degrees is recomputed for each ballistic descent.             |
    +----------------------------------+----------------------------------------------------------------------+
    | terminal_velocity                | Terminal velocity for aircraft                                       |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_frontal_area           | Assumed frontal area used in ballistic computations                  |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_drag_coefficient = 0.7 | Drag coefficient used for ballistic descent                          |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_descent_altitude       | Assumed altitude for beginning of ballistic descent                  |
    +----------------------------------+---------------------------------------------------- -----------------+
    | ballistic_impact_velocity        | Assumed horizontal velocity for beginning of ballistic descent       |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_impact_angle           | Computed impact angle                                                |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_distance               | Computed horizontal distance traveled during ballistic descent       |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_impact_KE              | Computed kinetic energy of aircraft just prior to impact             |
    +----------------------------------+----------------------------------------------------------------------+
    | ballistic_descent_time           | Computed descent time for ballistic descent                          |
    +----------------------------------+----------------------------------------------------------------------+
    | rho = 1.225                      | Density of air [kg/m^3]                                              |
    +----------------------------------+----------------------------------------------------------------------+

    """
    # This dataclass make the programming and plotting more smooth in allowing for looping for virtually all values.
    @dataclass
    class CAParameters:
        wingspan: float
        critical_area_target: float
        cruise_speed: float
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
        """Constructor
        
        Parameters
        ----------
        impact_angle : float
            The impact angle of the descending aircraft, measured relative to the ground [deg].
        """
        self.glide_reduce = 0.7
        self.friction_coefficient = 0.5
        self.rho = 1.225
        self.ballistic_drag_coefficient = 0.7
        self.scenario_angles = np.array([9, 35, 80])

        self.impact_angle = impact_angle

        # Set aircraft type, the type has no effect in this example, but must be given a value.
        self.aircraft_type = enums.AircraftType.GENERIC

        # Setup the parameters used in the plotting.
        self.CA_parms = []
        #                                      Width   CA       Speed    Drag area   Mass     lethal KE   Altitude
        self.CA_parms.append(self.CAParameters(1,      6.5,     25,      0.1,        4,       290/0.5,    75))
        self.CA_parms.append(self.CAParameters(3,      200,     35,      0.5,        50,      290,        100))
        self.CA_parms.append(self.CAParameters(8,      2000,    75,      2.5,        400,     290,        200))
        self.CA_parms.append(self.CAParameters(20,     20000,   150,     12.5,       5000,    290,        500))
        self.CA_parms.append(self.CAParameters(40,     66000,   200,     20,         10000,   290,        1000))
    
        # Upper and low value for coefficient of restitution (over 9 to 90 degree impact angles).
        self.horizontal_COR = 0.9
        self.vertical_COR = 0.6

        BDM = BallisticDescent2ndOrderDragApproximation(self.friction_coefficient)

        # Compute the parameters for each of the 5 size classes.
        for k in range(5):
            self.CA_parms[k].glide_speed = self.glide_reduce * self.CA_parms[k].cruise_speed

            # Define the aircraft.
            self.CA_parms[k].aircraft = AircraftSpecs(self.aircraft_type, self.CA_parms[k].wingspan, 1,
                                                      self.CA_parms[k].mass)

            # Set parameters into aircraft.
            self.CA_parms[k].aircraft.set_ballistic_frontal_area(self.CA_parms[k].ballistic_frontal_area)
            self.CA_parms[k].aircraft.set_ballistic_drag_coefficient(self.ballistic_drag_coefficient)
            self.CA_parms[k].aircraft.set_friction_coefficient(self.friction_coefficient)

            # The 1 m column uses 0.9 as CoR in all cases.
            if k == 0:
                self.CA_parms[k].aircraft.set_coefficient_of_restitution(0.9)
            else:
                self.CA_parms[k].aircraft.set_coefficient_of_restitution(
                    self.CA_parms[k].aircraft.COR_from_impact_angle(self.impact_angle, [self.scenario_angles[0], 90],
                                                                    [self.horizontal_COR, self.vertical_COR]))

            # Compute terminal velocity.
            self.CA_parms[k].terminal_velocity = self.CA_parms[k].aircraft.terminal_velocity(self.rho)

            BDM.set_aircraft(self.CA_parms[k].aircraft)
            p = BDM.compute_ballistic_distance(self.CA_parms[k].ballistic_descent_altitude,
                                               self.CA_parms[k].cruise_speed, 0)
            self.CA_parms[k].ballistic_impact_velocity = p[1]
            self.CA_parms[k].ballistic_impact_angle = p[2] * 180 / np.pi
            self.CA_parms[k].ballistic_distance = p[0]
            self.CA_parms[k].ballistic_descent_time = p[3]
            self.CA_parms[k].ballistic_impact_KE = 0.5 * self.CA_parms[k].mass * np.power(p[1], 2)

    @staticmethod
    def iGRC(pop_dens, CA, TLOS=1E-6):
        """Compute the finale integer iGRC as described in Annex F.
        
        Parameters
        ----------
        pop_dens : float
            Population density [ppl/km^2] (Note that this function converts the density to ppl/m^2
            as needed for the equation).
        CA : float
            Size of the critical area [m^2].
        TLOS : float, optional (default is 1e-6)
            Target level of safety [fatalities per flight hour].
            
        Returns
        -------
        iGRC : integer
            The intrinsic ground risk class (as an integer).
        raw iGRC : float
            The raw iGRC before rounding up.
        """
        raw_iGRC_value = 1 - math.log10(TLOS / (pop_dens * 1E-6 * CA))

        return math.ceil(raw_iGRC_value), raw_iGRC_value
