"""
MISSING DOC
"""
import math
import warnings
from collections.abc import Iterable

import numpy as np

from casex import enums, aircraft_specs, explosion_models, Conversion, constants


class CriticalAreaModels:
    """MISSING DOC

    Attributes
    ----------
    buffer : float, optional
        [m] Radius of a standard person as seen from above (default is 0.3 m).
    height : float, optional
        [m] The altitude above the ground at which the aircraft can first impact a person (default is 1.8 m).
    """

    def __init__(self, buffer=0.3, height=1.8):
        """Constructor
        
        Parameters
        ----------          
        buffer : float, optional
            [m] Radius of a standard person as seen from above (default is 0.3 m).
        height : float, optional
            [m] The altitude above the ground at which the aircraft can first impact a person (default is 1.8 m).
        """
        self.buffer = buffer
        self.height = height

    def critical_area(self, critical_area_model, aircraft, impact_speed, impact_angle, critical_areas_overlap, var1=-1):
        """Computes the lethal area as modeled by different models.
        
        The models are described in more detail in SORA Annex F. References for each model is given in the code.
        
        This function supports one of the following input parameters to be a vector, which will give a vector of the
        same size as output:
            
        * impact_speed
        * impact_angle
        * critical_area_overlap
        * aircraft.width
        * aircraft.length
        * aircraft.fuel_quantity
        
        This vector is given as ``numpy.array``, and only one of the parameters can be a vector for each call.
        The return values are then also ``numpy.array`` IF the input parameter that is a ``numpy.array`` is used in the
        computation.

        Parameters
        ----------       
        critical_area_model : :class:`enums.CriticalAreaModel`
            Choice of model (RCC [5]_, RTI [3]_, FAA [2]_, NAWCAD [7]_, JARUS [1]_). See SORA Annex F for details [1]_.
        aircraft : :class:`casex.AircraftSpecs`
            Class with information about the aircraft.
        impact_speed : float
            [m/s] Impact speed of aircraft (this is speed along the velocity vector).
        impact_angle : float
            [deg] Impact angle relative to ground (90 is vertical, straight down).
        critical_areas_overlap : float
            [0 to 1] Fraction of overlap between lethal area from glide and from explosion/deflagration.
        var1 : float, optional
            An additional variable that is used in FAA, NAWCAD, and JARUS models.
            For the FAA model, `var1` = :math:`F_A`, the ratio of secondary debris field to primary debris field. If not
            specified, :math:`F_A` = 4.36 will be used. See [2]_ page 98.

            For the NAWCAD model, `var1` is the lethal kinetic energy threshold in J. If not specified (or set to -1)
            the value 73.2 J is used.

            For the JARUS model, `var1` is the lethal kinetic energy threshold in J. If not specified (or set to -1),
            the following is done (see Annex F section A.5 for details): `var1` is set to 290 J, except when the width
            of the aircraft is <= 1 m, in which case `var1` is set to 2 * 290 J.
        
        Returns
        -------       
        critical area : float
            [m^2] Size of the critical area for the selected model.
        estimated glide area : float
            [m^2] The glide and slide areas are estimated as the relation between the glide and slide distances
            multiplied by the glide+slide area. The glide area is returned as the second output.
        estimated slide area : float
            [m^2] The estimated slide area is returned as the third output.
        critical area inert : float
            [m^2] The inert part of the critical area.
        deflagration area : float
            [m^2] The deflagration area as given by the deflagration model.
        """
        # Check on input argument validity
        if not isinstance(critical_area_model, enums.CriticalAreaModel):
            warnings.warn("Critical area model not recognized. Type set to RCC.")
            critical_area_model = enums.CriticalAreaModel.RCC

        if not isinstance(aircraft, aircraft_specs.AircraftSpecs):
            raise Exception("Aircraft not recognized. Must be of type AircraftSpecs")

        # Instantiate necessary classes.
        exp = explosion_models.ExplosionModels()

        # Compute additional parameters.
        horizontal_impact_speed = self.horizontal_speed_from_angle(impact_angle, impact_speed)
        glide_distance = self.glide_distance(impact_angle)

        # Compute the inert LA.
        if critical_area_model == enums.CriticalAreaModel.RCC:
            # Slide distance based on friction.
            slide_distance_friction = self.slide_distance_friction(horizontal_impact_speed,
                                                                   aircraft.friction_coefficient)
            # [5, p. D-4]
            glide_area = np.multiply(aircraft.length + glide_distance + 2 * self.buffer,
                                     aircraft.width + 2 * self.buffer)
            slide_area = np.multiply(slide_distance_friction, aircraft.width + 2 * self.buffer)

        elif critical_area_model == enums.CriticalAreaModel.RTI:
            # Slide distance based on friction.
            slide_distance_friction = self.slide_distance_friction(
                aircraft.coefficient_of_restitution * horizontal_impact_speed, aircraft.friction_coefficient)

            # [1, p. 6]
            glide_area = 2 * (self.buffer + aircraft.width / 2) * glide_distance + math.pi * np.power(
                self.buffer + aircraft.width / 2, 2)
            slide_area = slide_distance_friction * (2 * self.buffer + aircraft.width)

        elif critical_area_model == enums.CriticalAreaModel.FAA:
            # [2, p. 99]
            r_D = self.buffer + aircraft.width / 2

            # F_A comes from table 6-5 in [2, p. 98]. Here using the median for 20/80 distribution between hard and
            # soft surfaces.
            if var1 == -1:
                F_A = 4.36
            else:
                F_A = var1

            r_Ac = self.buffer + aircraft.width / 2 * np.sqrt(F_A)
            hs = self.height * np.sin(np.deg2rad(90 - impact_angle))
            y2m = np.power(2 * r_Ac * hs, 2) - np.power(np.power(r_Ac, 2) + np.power(hs, 2) - np.power(r_D, 2), 2)

            # If y2m becomes negative, it means that A_C_mark should become zero, because the secondary
            # debris area is larger than the total glide area. This is accomplished by simply setting y2 = 0.
            y2m = np.maximum(0, y2m)
            y2 = np.sqrt(y2m) / (2 * hs)

            A_C_mark = 2 * y2 * hs
            A_C_mark = A_C_mark + (
                    y2 * np.sqrt(np.power(r_D, 2) - np.power(y2, 2)) + np.power(r_D, 2) * np.arcsin(y2 / r_D))
            A_C_mark = A_C_mark - (
                    y2 * np.sqrt(np.power(r_Ac, 2) - np.power(y2, 2)) + np.power(r_Ac, 2) * np.arcsin(y2 / r_Ac))

            # Note that this is not identical to (12), since (12) assumes 0 degrees is vertical and not horizontal.
            LA_inert = math.pi * np.power(self.buffer + aircraft.width / 2 * np.sqrt(F_A), 2) + A_C_mark

            glide_area = math.pi * np.power(self.buffer + aircraft.width / 2, 2)
            slide_area = LA_inert - glide_area

        elif critical_area_model == enums.CriticalAreaModel.NAWCAD:
            # All from [7]
            if var1 == -1:
                KE_lethal = Conversion.ftlb_to_J(54)
            else:
                KE_lethal = var1

            # P. 18 (the following equation is just KE to mass and velocity, not taken from [7])
            velocity_min_kill = np.sqrt(2 * KE_lethal / aircraft.mass)

            # Intermediate variable
            acceleration = aircraft.friction_coefficient * constants.GRAVITY

            # P. 17
            # This is (15), but it seems to be wrong; normally at = v, not 2at = v
            # t_safe = (horizontal_impact_speed - velocity_min_kill) / 2 / aircraft.friction_coefficient / constants.GRAVITATIONAL
            # This seems to be the correct formula
            t_safe = (horizontal_impact_speed - velocity_min_kill) / acceleration

            # Avoid having negative time.
            t_safe = np.maximum(0, t_safe)

            # P. 17
            skid_distance_lethal = (horizontal_impact_speed * t_safe) - (0.5 * acceleration * t_safe * t_safe)

            # P. 25
            glide_area = glide_distance * (2 * self.buffer + aircraft.width)
            slide_area = skid_distance_lethal * (2 * self.buffer + aircraft.width)

        elif critical_area_model == enums.CriticalAreaModel.JARUS:
            if var1 == -1:
                # Set default value for a scalar width.
                if not isinstance(aircraft.width, np.ndarray):
                    if aircraft.width <= 1:
                        KE_lethal = 290
                    else:
                        KE_lethal = 290 * 2
                # Set default value for array width.
                else:
                    KE_lethal = np.full(len(aircraft.width), 290)
                    KE_lethal = np.where(aircraft.width <= 1, KE_lethal, 2 * KE_lethal)
            else:
                KE_lethal = var1

            velocity_min_kill = np.sqrt(2 * KE_lethal / aircraft.mass)
            acceleration = aircraft.friction_coefficient * constants.GRAVITY

            t_safe = (aircraft.coefficient_of_restitution * horizontal_impact_speed - velocity_min_kill) / acceleration
            t_safe = np.maximum(0, t_safe)

            slide_distance_lethal = (aircraft.coefficient_of_restitution * horizontal_impact_speed * t_safe) - (
                    0.5 * acceleration * t_safe * t_safe)

            circular_end = math.pi * np.power(self.buffer + aircraft.width / 2, 2)
            glide_area = 2 * (self.buffer + aircraft.width / 2) * glide_distance + circular_end
            slide_area = slide_distance_lethal * (2 * self.buffer + aircraft.width)

        # Add glide and slide from model.
        LA_inert = glide_area + slide_area

        # Compute deflagration area based on both fireball and thermal lethal area.
        TNT = exp.TNT_equivalent_mass(aircraft.fuel_type, aircraft.fuel_quantity)
        FB = exp.fireball_area(TNT)
        p_lethal = 0.1
        TLA = exp.lethal_area_thermal(TNT, p_lethal)
        LA_deflagration = np.maximum(FB, TLA)

        # Compute the overlapping area between inert and deflagration.
        overlapping_area = np.minimum(LA_inert, LA_deflagration) * np.maximum(0, np.minimum(critical_areas_overlap, 1))

        return LA_inert + LA_deflagration - overlapping_area, glide_area, slide_area, LA_inert, LA_deflagration

    @staticmethod
    def slide_distance_friction(velocity, friction_coefficient):
        """Computes slide distance based on initial velocity and friction.
        
        Sliding distance computed based on the assumption
            
        .. math:: F = -f\cdot w,
            
        where F is the frictional force, f the frictional coefficient, and w the body weight.
        The slide distance is the length of the slide between impact and the body coming to rest.
        
        This is a standard assumption found in most sources that includes friction.
        See for instance [7]_.
        
        Parameters
        ----------
        velocity : float
            [m/s] Horizontal component of the impact velocity.
        friction_coefficient : float
            [] Friction coefficient, typically between 0.4 and 0.7.
        
        Returns
        -------
        distance : float
            [m] Distance from impact to rest.
        """
        return velocity * velocity / 2 / friction_coefficient / constants.GRAVITY

    def glide_distance(self, glide_angle):
        """Compute glide distance based on glide angle.
        
        Glide distance is the distance an aircraft will glide through the air for a given glide angel from altitude
        height until it impacts the ground.
        Thus, the glide starts at altitude Height and continues until the aircraft impacts the ground.
        
        Parameters
        ----------
        glide_angle : float
            [deg] The angle of the aircraft relative to the ground as is impacts the ground. Must be between 1 and 179
            degree. Values above 90 degrees are used as '180 - GlideAngle'.
        
        Returns
        -------
        distance : float
            [m] The glide distance.
        """
        # Height out of range.
        if np.any(self.height < 0):
            warnings.warn("Height in computation of glide distance is less than zero, which does not make sense."
                          " Subsequent computations are not valid.")
            self.height = 0

        # Sanity check on glide angle.
        glide_angle = self.check_glide_angle(glide_angle)

        # This is just triangle standard math.
        return self.height / np.tan(np.radians(glide_angle))

    @staticmethod
    def check_glide_angle(glide_angle):
        """Performs a sanity check on the glide angle.

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        # glide_angle out of range.
        if np.any(glide_angle < 0) or np.any(glide_angle > 180):
            warnings.warn("glide_angle is out of valid range (0 to 180). Subsequent computations are not valid.")
            glide_angle = np.fromiter(map(lambda x: 90 if (x < 0 or x > 180) else x, glide_angle), dtype=np.float)

        # Flip glide angle.
        if isinstance(glide_angle, Iterable):
            glide_angle = np.fromiter(map(lambda x: 180 - x if x > 90 else x, glide_angle), dtype=np.float)
        else:
            if glide_angle > 90:
                glide_angle = 180 - glide_angle

        # If glide_angle is close to zero, we get a division by close to zero, so warn the user.
        # Also avoids an division by zero error.
        if np.any(glide_angle < 1):
            warnings.warn("glide_angle is very small, and may produce numerically unstable results."
                          " Glide angle has been set to 1 degree.")
            glide_angle = np.fromiter(map(lambda x: 1 if x < 1 else x, glide_angle), dtype=np.float)

        return glide_angle

    @staticmethod
    def horizontal_speed_from_angle(impact_angle, impact_speed):
        """Compute horizontal speed component for a given impact angle and impact speed.
        
        Parameters
        ----------
        impact_angle : float
            MISSING DOC
        impact_speed : float
            MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        # Note that we use .abs, since cosine is negative for angles between 90 and 180.
        return np.fabs(np.cos(np.radians(impact_angle))) * impact_speed

    @staticmethod
    def horizontal_speed_from_ratio(glide_ratio, impact_speed):
        """Compute horizontal speed from glide ratio.

        Parameters
        ----------
        glide_ratio : float
            MISSING DOC
        impact_speed : float
            MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        return (glide_ratio / np.power(np.power(glide_ratio, 2) + 1, 0.5)) * impact_speed

    @staticmethod
    def vertical_speed_from_angle(impact_angle, impact_speed):
        """Compute vertical speed from descent angle.

        Parameters
        ----------
        impact_angle : float
            MISSING DOC
        impact_speed : float
            MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        return np.sin(np.radians(impact_angle)) * impact_speed

    @staticmethod
    def glide_angle_from_glide_ratio(glide_ratio):
        """Compute glide angle from glide ratio.

        Parameters
        ----------
        glide_ratio : float
            MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        return np.rad2deg(np.arctan2(1, glide_ratio))

    @staticmethod
    def speed_from_kinetic_energy(KE, mass):
        """Compute speed from kinetic energy.

        Parameters
        ----------
        KE : float
            MISSING DOC
        mass : float
            MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        return np.sqrt(2 * KE / mass)

