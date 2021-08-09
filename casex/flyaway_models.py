"""
Class for computing probabilities associated with flyaways.
"""
import math

import numpy as np

from casex import enums, Conversion


class FlyawayModels:
    """    
    """

    def __init__(self, max_range=1000):
        self.max_range = max_range


    def concentric_area(o):
        """Compute something
        
        
        Parameters
        ----------

        Returns
        -------
        """

        # Random directions
        direction = stats.uniform.rvs(size=100, loc=0, scale=2*math.PI)
        
        # Random distance
        distance = stats.uniform.rvs(size=100, loc=0, scale=self.max_range)
        
        
        


        return 

