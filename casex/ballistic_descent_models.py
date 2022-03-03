"""
Class supports computation of a ballistic descent under the influence of gravity and drag.
"""
import warnings

import numpy as np

from casex import constants, exceptions


class BallisticDescent2ndOrderDragApproximation:
    """    
    This class allows for computation of ballistic descent using a variation of the standard
    second order drag model. In this implementation it has been modified to support
    fast calculations. Details on this can be found in :cite:`b-lacour2021`.

    Attributes
    ----------
    aircraft : :class:'AircraftSpecs'
        Class holding information about the aircraft.
    distance1 : float
        [m] Horizontal distance travelled between start time of descent and time `time_top`.
    distance2 : float
        [m] Horizontal distance travelled between time `time_top` and time `time_cross`.
    distance3 : float
        [m] Horizontal distance travelled between time `time_cross` and time `time_impact`.
    velocity_x : float
        [m/s] Horizontal part of the impact velocity.
    velocity_y : float
        [m/s] Vertical part of the impact velocity.
    time_top : float
        [s] Time from start of descent to reaching the top of the descent curve. This is 0 if the descent starts with a
        descent.
    time_cross : float
        [s] Time from start of descent to reaching the point, where the vertical velocity exceeds the horizontal
        velocity.
    time_impact : float
        [s] Time from start of descent to impact.
    c : float
        This represents the multiplication of frontal area, air density, and drag coefficient, which often appears
        together in the computations. The `c` attribute is just a placeholder for this multiplication.
    gamma : float
        A placeholder for :math:`\sqrt{m \cdot g / c}`, where :math:`m` is the mass
        of the aircraft, and :math:`g` is the gravitational constant.
    """
    def __init__(self):
        self.aircraft = None
        self.distance_impact = None
        self.distance1 = None
        self.distance2 = None
        self.distance3 = None
        self.velocity_impact = None
        self.velocity_x = None
        self.velocity_y = None
        self.angle_impact = None
        self.time_top = None
        self.time_cross = None
        self.time_impact = None
        self.c = None
        self.gamma = None

    def set_aircraft(self, aircraft):
        """Set the aircraft.

        Parameters
        ----------
        aircraft : :class:`AircraftSpecs`
            Class holding information about the aircraft.

        Returns
        -------
        None
        """
        self.aircraft = aircraft

    def compute_ballistic_distance(self, altitude, initial_velocity_x, initial_velocity_y):
        """Compute the distance, time, angle, and velocity of a ballistic descent impact.
    
        One of the following parameters can be an :class:`numpy.array`
        
        * `altitude`
        * `initial_velocity_x`
        * `initial_velocity_y`
        * `aircraft.ballistic_drag_coefficient`
        * `aircraft.ballistic_frontal_area`
        
        and the output will also be an :class:`numpy.array` for the outputs that depends on the parameters given as an
        :class:`numpy.array`. Note that `aircraft` refers to the variable set with the methods
        :class:`set_aircraft`.
        
        Requirements
        ------------
        The following requirements apply to the inputs
        
        * `initial_velocity_x` must be positive.
        * `initial_velocity_x` must be larger than `initial_velocity_y`.
        * absolute value of `initial_velocity_y` must be less than the terminal velocity.
        
        Parameters
        ----------
        altitude : float
            [m] Altitude of aircraft at time of event.
        initial_velocity_x : float
            [m/s] Horizontal velocity as time of event.
        initial_velocity_y : float
            [m/s] Vertical velocity as time of event.
            
        Returns
        -------
        distance_impact : float
            [m] Horizontal distance for impact relative to event point.
        velocity_impact: float
            [m/s] The impact velocity.
        angle_impact : float
            [rad] The impact angle (relative to horizontal).
        time_impact: float
            [s] Time from event to impact.

        Raises
        ------
        NegativeHorizontalVelocityError
            If the initial horizontal velocity is negative.
        HorizontalSmallerThanVerticalVelocityError
            If the initial horizontal velocity is smaller than the initial vertical velocity.
        """
        # Update Gamma and c based on the drag coefficient(s).
        self.__compute_gamma_and_c()

        if np.any(self.gamma < initial_velocity_y):
            warnings.warn("Vertical velocities exceed terminal velocity and has been thresholded by smallest gamma. "
                          "Consider reducing initial_velocity_y.")
            initial_velocity_y = np.minimum(np.amin(self.gamma) * 0.999, initial_velocity_y)

        vi_y_m = np.where(initial_velocity_y < 0, 0, initial_velocity_y)
        vi_y_n = np.where(initial_velocity_y >= 0, 0, initial_velocity_y)

        Hd = self.__compute_H_d(vi_y_m)
        Gd = self.__compute_G_d(vi_y_m)

        if np.any(initial_velocity_x < 0):
            raise exceptions.NegativeHorizontalVelocityError(
                "This function does not support negative initial horizontal velocity.")
        if np.any(initial_velocity_x < initial_velocity_y):
            raise exceptions.HorizontalSmallerThanVerticalVelocityError(
                "This function does not yet support initial horizontal velocity smaller than initial vertical velocity.")

        # Time of top point.
        t_top = self.__compute_t_top(vi_y_n)

        # Horizontal distance travelled until top point.
        x1 = self.__compute_x_before(t_top, initial_velocity_x)

        # Time (from event) to x_vy takes over.
        t_c = self.__compute_t_cross(t_top, initial_velocity_x, Hd)

        # In extreme cases the continued fraction approximation on which t_c is based can go haywire. This is an attempt
        # to solve that problem.
        t_c = np.where(t_c < 0, np.inf, t_c)

        # Altitude of top point (negative value).
        y_t = self.__compute_y_top(vi_y_n)

        # Time to drop from top point.
        t_d = self.__compute_t_drop(altitude - y_t, Hd, Gd)

        # Time of impact.
        t_i = t_top + t_d

        # Initial horizontal speed at top point.
        vx_top = self.__compute_vx_before(t_top, initial_velocity_x)

        x2 = self.__compute_x_before(np.minimum(t_i, t_c) - t_top, vx_top)

        # Initial speeds at time of crossing (x and y are not the same, since the crossing is approximated).
        vix_c = self.__compute_vx_before(t_c, initial_velocity_x)

        # Note that viy_c should not reach Gamma, since it will cause problems for x3.
        viy_c = np.minimum(self.gamma * 0.999, self.__compute_vy_down(t_c - t_top, Hd))

        # Horizontal distance after crossing vy = vx.
        # This is a fix to give same length as t_i - t_c rather than length 1 (from the 0).
        mx = np.maximum(0, t_i - t_c)
        # x_after gives zero for t_i < t_c.
        x3 = self.__compute_x_after(mx, vix_c, viy_c, self.__compute_H_d(viy_c), self.__compute_G_d(viy_c))

        # The condition "if t_i < t_c" is implemented through logical indexing.
        v_tx = np.where(t_i > t_c,
                        self.__compute_vx_after(t_i - t_c, vix_c, self.__compute_H_d(viy_c), self.__compute_G_d(viy_c)),
                        self.__compute_vx_before(t_i, initial_velocity_x))

        # Terminal vertical speed.
        v_ty = self.__compute_vy_down(t_i - t_top, Hd)

        # Return values.
        distance_impact = x1 + x2 + x3
        velocity_impact = np.sqrt(np.power(v_tx, 2) + np.power(v_ty, 2))
        angle_impact = np.arctan2(v_ty, v_tx)

        # Additional values that may be of interest to the user.
        # Then accessible as parameters.
        self.distance1 = x1
        self.distance2 = x2
        self.distance3 = x3
        self.velocity_x = v_tx
        self.velocity_y = v_ty
        self.time_top = t_top
        self.time_cross = t_c
        self.time_impact = t_i

        return distance_impact, velocity_impact, angle_impact, self.time_impact

    def __compute_gamma_and_c(self):
        self.c = 0.5 * self.aircraft.ballistic_frontal_area * constants.AIR_DENSITY * self.aircraft.ballistic_drag_coefficient
        self.gamma = np.sqrt(self.aircraft.mass * constants.GRAVITY / self.c)

    def __compute_t_top(self, init_v_y):
        return - self.gamma / constants.GRAVITY * np.arctan(init_v_y / self.gamma)

    def __compute_t_cross(self, tt, init_v_x, Hd):
        return (self.aircraft.mass * (constants.GRAVITY * tt - self.gamma * Hd + init_v_x * (
                1 + np.power(Hd - constants.GRAVITY / self.gamma * tt, 2)))) / (
                       self.aircraft.mass * constants.GRAVITY + init_v_x * self.c *
                       (constants.GRAVITY * tt - self.gamma * Hd))

    def __compute_t_drop(self, y, Hd, Gd):
        return self.gamma / constants.GRAVITY * (np.arccosh(np.exp(self.c * y / self.aircraft.mass + Gd)) - Hd)

    def __compute_H_u(self, init_v_y):
        return np.arctan2(init_v_y, self.gamma)

    def __compute_H_d(self, init_v_y):
        return np.arctanh(init_v_y / self.gamma)

    def __compute_G_u(self, init_v_y):
        return -1 / 2 * np.log(1 + np.power(init_v_y, 2) / np.power(self.gamma, 2))

    def __compute_G_d(self, init_v_y):
        return -1 / 2 * np.log(1 - np.power(init_v_y, 2) / np.power(self.gamma, 2))

    def __compute_vy_up(self, t, Hu):
        return self.gamma * np.tan(constants.GRAVITY * t / self.gamma + Hu)

    def __compute_vy_down(self, t, Hd):
        return self.gamma * np.tanh(constants.GRAVITY * t / self.gamma + Hd)

    def __compute_vx_before(self, t, vix):
        return vix / (1 + (t * vix) / (self.aircraft.mass / self.c))

    def __compute_vx_after(self, t, init_v_x, Hd, Gd):
        return init_v_x * np.exp(Gd) / np.cosh(constants.GRAVITY * t / self.gamma + Hd)

    def __compute_y_up(self, t, Hu, Gu):
        return -self.aircraft.mass / self.c * (np.log(np.cos(constants.GRAVITY * t / self.gamma + Hu)) - Gu)

    def __compute_y_down(self, t, Hd, Gd):
        return self.aircraft.mass / self.c * (np.log(np.cosh(constants.GRAVITY * t / self.gamma + Hd)) - Gd)

    def __compute_x_before(self, t, init_v_x):
        return self.aircraft.mass / self.c * np.log(1 + init_v_x * self.c * t / self.aircraft.mass)

    def __compute_x_after(self, t, init_v_x, init_v_y, Hd, Gd):
        return init_v_x * np.exp(Gd) * self.gamma / constants.GRAVITY * (
                np.arctan(np.sinh(constants.GRAVITY * t / self.gamma + Hd)) - np.arcsin(init_v_y / self.gamma))

    def __compute_y_top(self, init_v_y):
        return self.__compute_G_u(init_v_y) * self.aircraft.mass / self.c
