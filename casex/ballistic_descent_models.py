import numpy as np

import casex

class CBallisticDescent_2ndOrderDrag_Approximation:
    """
    """
    
    def __init__(self, rho):
        self.rho = rho
        self.aircraft = None
        
    def set_aircraft(self, aircraft):
        self.aircraft = aircraft
     
    def compute_ballistic_distance(self, altitude, initial_velocity_x, initial_velocity_y):
        """ Compute the distance, time, angle, and velocity of a ballistic descent impact
    
        One following parameters can be an :class:`numpy.array`
        
        * altitude
        * initial_velocity_x
        * initial_velocity_y
        * aircraft.ballistic_drag_coefficient
        * aircraft.ballistic_frontal_area
        
        and the output will also be an :class:`numpy.array` for the outputs that depends on the parameters given as an :class:`numpy.array`.
        Note that :class:`aircraft` refers to the variable set with the methods :class:`set_aircraft`.
        
        Requirements
        ------------
        The following requires apply to the inputs
        
        * :class:`initial_velocity_x` must be positive.
        * :class:`initial_velocity_x` must be larger than :class:`initial_velocity_y`.
        * absolute value of :class:`initial_velocity_y` must be less than the terminal velocity.
        
        Parameters
        ----------
        MISSING DOC
        altutide : float
            [m] Altitude of aircraft at time of event.
        initial_velocity_x : float
            [m/s] Horizontal velocity as time of event.
        initial_velocity_y : float
            [m/s] Vertical velocity as time of event.
        drag_coef : float, optional
            [-] Drag coefficient.
            
        Returns
        -------
        distance : float
            [m] Horizontal distance for impact relative to event point.
        time : float
            [s] Time from event to impact.
        impact_velocity : float
            [m/s] Impact velocity.
        MISSING DOC
        """
            
        # Update Gamma and c based on the drag coefficient(s)
        self.compute_gamma_and_c()
               
        if np.any(self.gamma < initial_velocity_y):
            warnings.warn("Vertical velocities exceed terminal velocity and has been thresholded by smallest gamma. Consider reducing initial_velocity_y.")
            initial_velocity_y = np.minimum(np.amin(self.gamma) * 0.999, initial_velocity_y)
            
        vi_y_m = np.where(initial_velocity_y < 0, 0, initial_velocity_y)
        vi_y_n = np.where(initial_velocity_y >= 0, 0, initial_velocity_y)
            
        Hd = self.compute_H_d(vi_y_m)
        Gd = self.compute_G_d(vi_y_m)
            
        if np.any(initial_velocity_x < 0):
            raise NameError('This function does not support negative initial horizontal velocity.')
        if np.any(initial_velocity_x < initial_velocity_y):
            raise NameError('This function does not yet support initial horizontal velocity smaller than initial vertical velocity.')
            
        # Time of top point
        t_top = self.compute_t_top(vi_y_n)
            
        # Horizontal distance travelled until top point
        x1 = self.compute_x_before(t_top, initial_velocity_x)
            
        # Time (from event) to x_vy takes over
        t_c = self.compute_t_cross(t_top, initial_velocity_x, Hd)
            
        # In extreme cases the continued fraction approximation on
        # which t_c is based can go haywire. This is an attempt to
        # solve that problem
        t_c = np.where(t_c < 0, np.inf, t_c)
            
        # Altitude of top point (negative value)
        y_t = self.compute_y_top(vi_y_n)
            
        # Time to drop from top point
        t_d = self.compute_t_drop(altitude - y_t, Hd, Gd)
            
        # Time of impact
        t_i = t_top + t_d
            
        # Initial horizontal speed at top point
        vx_top = self.compute_vx_before(t_top, initial_velocity_x)
            
        x2 = self.compute_x_before(np.minimum(t_i, t_c) - t_top, vx_top)
        
        # Initial speeds at time of crossing (x and y are not the same,
        # since the crossing is approximated)
        vix_c = self.compute_vx_before(t_c, initial_velocity_x)
        viy_c = np.minimum(self.gamma * 0.999, self.compute_vy_down(t_c - t_top, Hd)) # Note that viy_c should not reach Gamma, since it will cause problems for x3
            
        # Horizontal distance after crossing vy = vx
        # x_after gives zero for t_i < t_c
        mx = np.maximum(0, t_i - t_c) # This is a fix to give same length as t_i - t_c rather than length 1 (from the 0)
        x3 = self.compute_x_after(mx, vix_c, viy_c, self.compute_H_d(viy_c), self.compute_G_d(viy_c))
            
        # The condition "if t_i < t_c" is implemented through logical indexing
        v_tx = np.where(t_i > t_c,
                 self.compute_vx_after(t_i - t_c, vix_c, self.compute_H_d(viy_c), self.compute_G_d(viy_c)),
                 self.compute_vx_before(t_i, initial_velocity_x))
            
        # Terminal vertical speed
        v_ty = self.compute_vy_down(t_i - t_top, Hd)
            
        # Return values
        self.distance_impact = x1 + x2 + x3
        self.distance1 = x1
        self.distance2 = x2
        self.distance3 = x3
        self.velocity_impact = np.sqrt(np.power(v_tx, 2) + np.power(v_ty, 2))
        self.velocity_x = v_tx 
        self.velocity_y = v_ty
        self.angle_impact = np.arctan2(v_ty, v_tx)
        self.time_top = t_top
        self.time_cross = t_c
        self.time_impact = t_i
        
        return self.distance_impact, self.velocity_impact, self.angle_impact, self.time_impact
            
    def compute_gamma_and_c(self):
        self.c = 0.5 * self.aircraft.ballistic_frontal_area * self.rho * self.aircraft.ballistic_drag_coefficient
        self.gamma = np.sqrt(self.aircraft.mass * casex.constants.GRAVITY / self.c)

    def compute_t_top(self, init_v_y):
        return -self.gamma / casex.constants.GRAVITY * np.arctan(init_v_y / self.gamma)
    
    def compute_t_cross(self, tt, init_v_x, Hd):
        return (self.aircraft.mass * (casex.constants.GRAVITY * tt - self.gamma * Hd + init_v_x * (1 + np.power(Hd - casex.constants.GRAVITY / self.gamma * tt, 2)))) / (self.aircraft.mass * casex.constants.GRAVITY + init_v_x * self.c * (casex.constants.GRAVITY * tt - self.gamma * Hd))
        
    def compute_t_drop(self, y, Hd, Gd):
        return self.gamma / casex.constants.GRAVITY * (np.arccosh(np.exp(self.c * y / self.aircraft.mass + Gd)) - Hd)
        
    def compute_H_u(self, init_v_y):
        return np.arctan2(init_v_y, self.gamma)

    def compute_H_d(self, init_v_y):
        return np.arctanh(init_v_y / self.gamma)
        
    def compute_G_u(self, init_v_y):
        return -1/2 * np.log(1 + np.power(init_v_y, 2) / np.power(self.gamma, 2))

    def compute_G_d(self, init_v_y):
        return -1/2 * np.log(1 - np.power(init_v_y, 2) / np.power(self.gamma, 2))

    def compute_vy_up(self, t, Hu):
        return self.gamma * np.tan(casex.constants.GRAVITY * t / self.gamma + Hu)

    def compute_vy_down(self, t, Hd):
        return self.gamma * np.tanh(casex.constants.GRAVITY * t / self.gamma + Hd)

    def compute_vx_before(self, t, vix):
        return vix / (1 + (t * vix) / (self.aircraft.mass / self.c))

    def compute_vx_after(self, t, init_v_x, Hd, Gd):
        return init_v_x * np.exp(Gd) / np.cosh(casex.constants.GRAVITY * t / self.gamma + Hd)
   
    def compute_y_up(self, t, Hu, Gu):
        return -self.aircraft.mass / self.c * (np.log(np.cos(casex.constants.GRAVITY * t / self.gamma + Hu)) - Gu)

    def compute_y_down(self, t, Hd, Gd):
        return self.aircraft.mass / self.c * (np.log(np.cosh(casex.constants.GRAVITY * t / self.gamma + Hd)) - Gd)

    def compute_x_before(self, t, init_v_x):
        return self.aircraft.mass / self.c * np.log(1 + init_v_x * self.c * t / self.aircraft.mass)

    def compute_x_after(self, t, init_v_x, init_v_y, Hd, Gd):
        return init_v_x * np.exp(Gd) * self.gamma / casex.constants.GRAVITY * (np.arctan(np.sinh(casex.constants.GRAVITY * t / self.gamma + Hd)) - np.arcsin(init_v_y / self.gamma))
      
    def compute_y_top(self, init_v_y):
        return self.compute_G_u(init_v_y) * self.aircraft.mass / self.c

      