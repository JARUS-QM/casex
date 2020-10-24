"""
MISSING DOC
"""
import math
import warnings

import numpy as np
from scipy.stats import norm

from casex import enums


class NormalDistributionParameters:
    """MISSING DOC

    Attributes
    ----------
    MISSING DOC
    """

    def __init__(self, mu=0.0, sigma=1.0, wrapping_type=enums.Wrapping.NONE):
        """Holds the parameters for a normal distribution, and can compute a sampled version of the distribution.
        
        Parameters
        ----------
        mu : double, optional (default is 0)
            Mean of the normal distribution.
        sigma : double, optional (default is 1)
            Standard deviation of the normal distribution.
        wrapping_type : :class:`enums.Wrapping`, optional (default is EWrapping.NONE)
            The wrapping type for mu. When set to EWrapping.PI2PI, mu is wrapped to the interval -pi to pi.
        """
        self.input_set = None
        self.output_set = None

        self.mu = mu
        self.sigma = sigma
        
        self.__reset_values()

        if not isinstance(wrapping_type, enums.Wrapping):
            warnings.warn("Wrapping type not recognized. Wrapping set to NONE.")
            self.wrapping_type = enums.Wrapping.NONE
        else:
            self.wrapping_type = wrapping_type
            
        if self.wrapping_type == enums.Wrapping.PI2PI:
            while self.mu > math.pi:
                self.mu = self.mu - 2 * math.pi
            while self.mu < -math.pi:
                self.mu = self.mu + 2 * math.pi
                
    def __reset_values(self):
        # MISSING DOC
        self.input_set = None
        self.output_set = None
    
    def compute_sampling(self, times_sigma, num_of_samples):
        """Computes a sampling of the normal distribution.
        
        Parameters
        ----------
        times_sigma : double
            This value is multiplied onto sigma and the results plus/minus is the interval for the sampling.
        num_of_samples : int
            Number of samples in the sampling.
            
        Returns
        -------
        input_set : double array
            The domain for the sampling (i.e. the input to the distribution, or the x axis values).
        output_set : double array
            The value set for the sampling (i.e. the output of the distribution, or the y axis values).
            
        The normal distribution can be plotted using output_set against input_set.
        """
        self.input_set = np.linspace(self.mu - times_sigma * self.sigma, self.mu + times_sigma * self.sigma,
                                     num_of_samples)
        self.output_set = norm.pdf(self.input_set, self.mu, self.sigma)


class InitialSpeeds:
    """MISSING DOC

    Attributes
    ----------
    MISSING DOC
    """

    def __init__(self, initial_speed_x_mu, initial_speed_x_sigma, initial_speed_y_mu, initial_speed_y_sigma):
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC
        """
        if initial_speed_x_mu < 0:
            warnings.warn("Initial horizontal speed (along x axis) cannot be negative. Subsequent results are invalid.")
        
        self.initial_speed_x = NormalDistributionParameters(initial_speed_x_mu, initial_speed_x_sigma)
        self.initial_speed_y = NormalDistributionParameters(initial_speed_y_mu, initial_speed_y_sigma)
