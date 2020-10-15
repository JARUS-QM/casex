import warnings
import math
import numpy as np
from scipy.stats import norm
import warnings

from casex.enums import EWrapping, EAircraftType, EFuelType

class CNormalDistributionParameters:

    def __init__(self, mu = 0.0, sigma = 1.0, wrapping_type = EWrapping.NONE):
        """
        CNormalDistributionParameters(mu = 0, sigma = 1, wrapping_type = EWrapping.NONE
        
        Holds the parameters for a normal distribution, and can compute a sampled version of the distribution.
        
        Parameters
        ----------
       
            mu : double
                Mean of the normal distribution (default 0)
            
            sigma : double
                Standard deviation of the normal distribution (default 1)
            
            wrapping_type : EWrapping
                The wrapping type for mu. When set to EWrapping.PI2PI, mu is wrapped to the interval -pi to pi.
                Default EWrapping.NONE
        """
        self.mu = mu
        self.sigma = sigma
        
        self._reset_values()

        if not isinstance(wrapping_type, EWrapping):
            warnings.warn("Wrapping type not recognized. Wrapping set to NONE.")
            self.wrapping_type = EWrapping.NONE
        else:
            self.wrapping_type = wrapping_type
            
        if self.wrapping_type == EWrapping.PI2PI:
            while self.mu > math.pi:
                self.mu = self.mu - 2 * math.pi
            while self.mu < -math.pi:
                self.mu = self.mu + 2 * math.pi
                
    def _reset_values(self):
        self.input_set= None
        self.output_set = None
    
    def compute_sampling(self, times_sigma, num_of_samples):
        """
        compute_sampling(TimesSigma, NumOfSamples)
        
        Computes a sampling of the normal distribution
        
        Parameters
        ----------
        
            TimesSigma : double
                This value is multiplied onto sigma and the results plus/minus is the interval for the sampling
                
            NumOfSamples : int
                Number of samples in the sampling
            
        Returns
        -------
        
            InputSet : double array
                The domain for the sampling (i.e. the input to the distribution, or the x axis values)
                
            OutputSet : double array
                The value set for the sampling (i.e. the output of the distribution, or the y axis values)
            
        The normal distribution can be plotted using OutputSet against InputSet
        """
        self.input_set = np.linspace(self.mu - times_sigma * self.sigma, self.mu + times_sigma * self.sigma, num_of_samples)
        self.output_set = norm.pdf(self.input_set, self.mu, self.sigma)
        
    def self_test(self):
        self.compute_sampling(3, 100)
        
        
class CInitialSpeeds:
    """
    """
    
    def __init__(self, initial_speed_x_mu, initial_speed_x_sigma, initial_speed_y_mu, initial_speed_y_sigma):
        
        if initial_speed_x_mu < 0:
            warnings.warn("Initial horizontal speed (along x axis) cannot be negative. Subsequent results are invalid.")
        
        self.initial_speed_x = CNormalDistributionParameters(initial_speed_x_mu, initial_speed_x_sigma)
        self.initial_speed_y = CNormalDistributionParameters(initial_speed_y_mu, initial_speed_y_sigma)
        
