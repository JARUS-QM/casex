"""
This class provide methods for computing critical area for a variety of models.
"""
import math
import warnings
from collections.abc import Iterable

import numpy as np

from casex import AnnexFParms, enums, aircraft_specs, explosion_models, Conversion, constants, exceptions

class CriticalAreaModels:
    """
    This class is used for computing the critical area using the JARUS model for a crash when the basic parameters for the
    aircraft is known. The math behind the model is described in
    Appendix B in Annex F :cite:`c-JARUS_AnnexF`.
    
    The main method in this class is `critical_area`, which computes the size of the critical area given
    a number of input arguments relating to the aircraft.
    
    There are two attributes in this class for describing
    a standard person, namely `buffer` and `height`.

    Parameters
    ----------
    buffer : float, optional
        [m] Radius of a standard person as seen from above (the default is 0.3 m).
    height : float, optional
        [m] The altitude above the ground at which the aircraft can first impact a person (the default is 1.8 m).

    Attributes
    ----------
    buffer : float, optional
        [m] Radius of a standard person as seen from above (the default is 0.3 m).
    height : float, optional
        [m] The altitude above the ground at which the aircraft can first impact a person (the default is 1.8 m).
    """

    def __init__(self, buffer = AnnexFParms.person_radius, height = AnnexFParms.person_height):
        self.buffer = buffer
        self.height = height

    def critical_area(self, aircraft, impact_speed, impact_angle, critical_areas_overlap = 0, lethal_kinetic_energy = -1, use_obstacle_reduction = True):
        """Computes the lethal area as modeled by different models.
        
        This function supports one of the following input parameters to be a vector, which will give a vector of the
        same size as output:
            
        * `impact_speed`
        * `impact_angle`
        * `critical_area_overlap`
        * `aircraft.width`
        * `aircraft.fuel_quantity`
        
        This vector is given as ``numpy.array``, and only one of the parameters can be a vector for each call.
        The return values are then also ``numpy.array`` IF the input parameter that is a ``numpy.array`` is used in the
        computation.

        Parameters
        ----------       
        aircraft : :class:`casex.AircraftSpecs`
            Class with information about the aircraft.
        impact_speed : float
            [m/s] Impact speed of aircraft (this is speed along the velocity vector).
        impact_angle : float
            [deg] Impact angle relative to ground (90 is vertical, straight down). Note that when using the JARUS model
            and the width of the aircraft is <= 1 m, the impact angle used is minimum 35 degrees, regardless of input.
            See Appendix A.5 in Annex F :cite:`c-JARUS_AnnexF` for details.
        critical_areas_overlap : float, optional
            [0 to 1] Fraction of overlap between lethal area from glide/slide and from explosion/deflagration. Default is 0.
        lethal_kinetic_energy : float, optional
            The lethal kinetic energy threshold in J. If not specified (or set to -1),
            the standard approach as described in Annex F Appendix A :cite:`c-JARUS_AnnexF` is used.
            If set to a positive value, this value is used independently of all other parameters. If set to a negative value other than -1,
            this value is used following the Annex F standard approach, but with absolute of the given value.
        use_obstacle_reduction : bool, optional
            If set to true, the Annex F obstacle reduction is applied as described in the Annex.
            If set to false, no obstacle reduction is applied.
            Default is true.
        
        Returns
        -------       
        critical area : float
            [:math:`\mathrm{m}^2`] Size of the critical area for the selected model.
        estimated glide area : float
            [:math:`\mathrm{m}^2`] The glide and slide areas are estimated as the relation between the glide and slide
            distances multiplied by the glide+slide area.
        estimated slide area : float
            [:math:`\mathrm{m}^2`] The estimated slide area.
        critical area inert : float
            [:math:`\mathrm{m}^2`] The inert part of the critical area.
        deflagration area : float
            [:math:`\mathrm{m}^2`] The deflagration area as given by the deflagration model. Always 0 for non-JARUS models.
        glide distance : float
            [:math:`\mathrm{m}`] The glide distance.
        slide distance non lethal: float
            [:math:`\mathrm{m}`] The slide distance until non-lethal. Always 0 for non-JARUS models.
        velocity min kill : float
            [:math:`\mathrm{m/s}`] The speed at which the slide is no longer lethal. Always 0 for non-JARUS and NAWCAD models.
        t safe : float
            [:math:`\mathrm{s}`] The time between impact and when slide speed is non-lethal. Always 0 for non-JARUS and NAWCAD models.

        Raises
        ------
        InvalidAircraftError
            If the aircraft is not of type AircraftSpecs.
        OnlyOneVetorInputError
            There is more than one vector input, which is not supported.
        """
        if not isinstance(aircraft, aircraft_specs.AircraftSpecs):
            raise exceptions.InvalidAircraftError("Aircraft not recognized. Must be of type AircraftSpecs.")

        # Instantiate necessary classes.
        exp = explosion_models.ExplosionModels()

        # True if we should use the Annex F approach to applying KE to the crash. False otherwise.
        KE_AnnexF_approach = lethal_kinetic_energy < 0
        
        # Set the correct lethal kinetic energy
        if lethal_kinetic_energy == -1:
            lethal_kinetic_energy = AnnexFParms.lethal_kinetic_energy
        else:
            lethal_kinetic_energy = abs(lethal_kinetic_energy)
            
        # Implement the Annex F approach
        if KE_AnnexF_approach:
            # Set value for a scalar width.
            if not isinstance(aircraft.width, np.ndarray):
                if aircraft.width <= 1:
                    lethal_kinetic_energy = lethal_kinetic_energy * 2
            # Set value for array width.
            else:
                #lethal_kinetic_energy = np.full(len(aircraft.width), lethal_kinetic_energy)
                lethal_kinetic_energy = np.where(aircraft.width <= 1, 2 * lethal_kinetic_energy, lethal_kinetic_energy)

        # Compute additional parameters.
        horizontal_impact_speed = self.horizontal_speed_from_angle(impact_angle, impact_speed)
        glide_distance = self.glide_distance(impact_angle)
        
        # Default to zero.
        slide_distance_non_lethal = 0
        velocity_min_kill = 0
        t_safe = 0

        default_impact_angle = AnnexFParms.scenario_angles[1]
        
        # Get the obstacle reduction factor as described in Annex F.
        obstacle_reduction_factor = AnnexFParms.applied_obstacle_reduction_factor(aircraft.width)
        
        # Special concession on impact angle for below 1 m.
        if isinstance(aircraft.width, np.ndarray):
            if isinstance(impact_angle, np.ndarray):
                raise Exception("impact_angle and aircraft.width cannot both be vectors.")
            impact_angle = np.where(aircraft.width <= 1, max(default_impact_angle, impact_angle), impact_angle)
        else:
            if aircraft.width <= 1:
                if not isinstance(impact_angle, np.ndarray):
                    impact_angle = max(default_impact_angle, impact_angle)
                else:
                    impact_angle = np.where(impact_angle < default_impact_angle, default_impact_angle, impact_angle)                 

        velocity_min_kill = np.sqrt(2 * lethal_kinetic_energy / aircraft.mass)
        acceleration = aircraft.friction_coefficient * constants.GRAVITY
        
        t_safe = (aircraft.coefficient_of_restitution * horizontal_impact_speed - velocity_min_kill) / acceleration
        t_safe = np.maximum(0, t_safe)

        slide_distance_non_lethal = (aircraft.coefficient_of_restitution * horizontal_impact_speed * t_safe) - (
                0.5 * acceleration * t_safe * t_safe)

        # Compute a half disc to attach to one end of glide and slide.
        circular_end = math.pi * np.power(self.buffer + aircraft.width / 2, 2) / 2
        
        glide_area = 2 * (self.buffer + aircraft.width / 2) * glide_distance + circular_end
        slide_area = slide_distance_non_lethal * (2 * self.buffer + aircraft.width) + circular_end

        # Concession for aircraft below 1 m.
        if not isinstance(aircraft.width, np.ndarray):
            if aircraft.width <= 1:
                if not isinstance(slide_distance_non_lethal, np.ndarray):
                    slide_distance_non_lethal = 0
                else:
                    slide_distance_non_lethal = np.full(len(slide_distance_non_lethal), 0)
                if not isinstance(slide_area, np.ndarray):
                    slide_area = 0
                else:
                    slide_area = np.full(len(slide_area), 0)
        else:
            slide_distance_non_lethal[aircraft.width <= 1] = 0
            slide_area[aircraft.width <= 1] = 0

        # Obstacle reduction is applied to the right variables
        if use_obstacle_reduction:
            glide_area = glide_area * obstacle_reduction_factor
            slide_area = slide_area * obstacle_reduction_factor
            glide_distance = glide_distance * obstacle_reduction_factor

        # Add glide and slide from model.
        CA_inert = glide_area + slide_area

        # Compute deflagration area based on both fireball and thermal lethal area.
        TNT = exp.TNT_equivalent_mass(aircraft.fuel_type, aircraft.fuel_quantity)
        FB = exp.fireball_area(TNT)
        p_lethal = 0.1
        TLA = exp.lethal_area_thermal(TNT, p_lethal)
        CA_deflagration = np.maximum(FB, TLA)

        # Compute the overlapping area between inert and deflagration.
        if np.any(critical_areas_overlap) < 0 or np.any(critical_areas_overlap) > 1:
            warnings.warn("Critical area overlap must be between 0 and 1. Subsequent computations are not valid.")
        overlapping_area = np.minimum(CA_inert, CA_deflagration) * critical_areas_overlap

        return CA_inert + CA_deflagration - overlapping_area, \
                glide_area, \
                slide_area, \
                CA_inert, \
                CA_deflagration, \
                glide_distance, \
                slide_distance_non_lethal, \
                velocity_min_kill, \
                t_safe

    @staticmethod
    def slide_distance_friction(velocity, friction_coefficient):
        """Computes slide distance based on initial velocity and friction.
        
        Sliding distance computed based on the assumption
            
        .. math:: F = -f \cdot w,
            
        where :math:`F` is the frictional force, :math:`f` the frictional coefficient,
        and :math:`w` the body weight.
        The slide distance is the length of the slide between impact and the body coming to rest.
        
        This is a standard assumption found in most sources that includes friction.
        See for instance :cite:`c-Ball2012`.
        
        Parameters
        ----------
        velocity : float
            [m/s] Horizontal component of the impact velocity.
        friction_coefficient : float
            [-] Friction coefficient, typically between 0.4 and 0.7.
        
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
        """Checks the glide angle.
        
        Issues a warning if the glide angle is out of range, or close to zero (which produces unrealistic results in the
        CA model). It also flips the glide angle if it is between 90 and 180 degrees.

        Parameters
        ----------
        glide_angle : float
            [deg] The glide angle to be checked.

        Returns
        -------
        glide_angle : float
            [deg] The glide angle, which is either the same as the input, or flipped if needed.
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
            [deg] Impact angle of the aircraft.
        impact_speed : float
            [m/s] Impact speed of the aircraft (speed in the direction of travel).

        Returns
        -------
        horizontal_speed : float
            [m/s] The horizontal compotent of the impact speed.
        """
        # Note that we use .abs, since cosine is negative for angles between 90 and 180.
        return np.fabs(np.cos(np.radians(impact_angle))) * impact_speed

    @staticmethod
    def horizontal_speed_from_ratio(glide_ratio, impact_speed):
        """Compute horizontal speed from glide ratio.

        Parameters
        ----------
        glide_ratio : float
            [-] The ratio between vertical and horizontal speed during glide.
        impact_speed : float
            [m/s] The impact speed of the aircraft (in the direction of travel).

        Returns
        -------
        horizontal_speed : float
            [m/s] The horizontal compotent of the impact speed.
        """
        return (glide_ratio / np.power(np.power(glide_ratio, 2) + 1, 0.5)) * impact_speed

    @staticmethod
    def vertical_speed_from_angle(impact_angle, impact_speed):
        """Compute vertical speed from impact angle.

        Parameters
        ----------
        impact_angle : float
            [deg] Impact angle of the aircraft.
        impact_speed : float
            [m/s] Impact speed of the aircraft (speed in the direction of travel).

        Returns
        -------
        vertical_speed : float
            [m/s] The vertical compotent of the impact speed.
        """
        return np.sin(np.radians(impact_angle)) * impact_speed

    @staticmethod
    def glide_angle_from_glide_ratio(glide_ratio):
        """Compute glide angle from glide ratio.

        Parameters
        ----------
        glide_ratio : float
            [-] The ratio between vertical and horizontal speed during glide.

        Returns
        -------
        glide_angle : float
            [deg] The glide angle for the given glide ratio.
        """
        return np.rad2deg(np.arctan2(1, glide_ratio))

    @staticmethod
    def speed_from_kinetic_energy(KE, mass):
        """Compute speed from kinetic energy.

        Parameters
        ----------
        KE : float
            [J] Kinetic energy of the aircraft.
        mass : float
            [kg] Mass of the aircraft.

        Returns
        -------
        speed : float
            [m/s] The speed associated with the given kinetic energy and mass.
        """
        return np.sqrt(2 * KE / mass)
