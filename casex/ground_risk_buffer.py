"""
This class supports computation for determining the properties of the ground risk buffer
according to the M1 mitigation at medium level.

"""
import numpy as np
import math
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.affinity import scale

from casex import AircraftSpecs, BallisticDescent2ndOrderDragApproximation, constants

class GroundRiskBuffer:
    """This class contains the following parameters for the 5 size classes in the iGRC table:

    Parameters
    ----------
    xx : float
        [deg] The impa

    Attributes
    ----------
    xx : float
        Characteristic d
    """
    
    def __init__(self, latency_time, behavior_time):
        self.latency_time = latency_time
        self.behavior_time = behavior_time

    def set_latency(self, latency_time):
        self.latency_time = latency_time

    def set_behavior(self, behavior_time):
        self.behavior_time = behavior_time

    def distance_from_ops_volume(self, resolutions, max_range, scale, aircraft, altitude, wind_max, corridor_fraction, fraction_for_dist):
        
        dir_hor_resolution = resolutions[0]
        dir_ver_resolution = resolutions[1]
        wind_resolution = resolutions[2]
        aircraft_speed_resolution = resolutions[3]
        
        # Uniform distribution of flyaway direction horizontally relative to direction of
        # the border of the ops volume.
        direction_horizontal = np.linspace(math.pi, 3/2*math.pi, dir_hor_resolution, endpoint = False)
        direction_horizontal_cos = np.cos(direction_horizontal)
        direction_horizontal_sin = np.sin(direction_horizontal)
        
        # Uniform distribution of flyaway direction vertically relative to horizontal.
        direction_vertical_cos = np.cos(np.linspace(0, math.pi / 2 - 0.1, dir_ver_resolution, endpoint = False))

        # Uniform distribution of wind speed and direction.
        wind_speed = np.linspace(1, wind_max, wind_resolution)
        wind_dir = np.linspace(0+0.5, 2 * math.pi + 0.5, wind_resolution, endpoint = False)
        
        # Uniform distribution of the speed of the aircraft.
        aircraft_speed = np.linspace(aircraft.cruise_speed / 4, aircraft.cruise_speed, aircraft_speed_resolution)
        
        BD = BallisticDescent2ndOrderDragApproximation()
        BD.set_aircraft(aircraft)
        
        # Initialize matrix with 0's.
        distribution_wc = np.zeros([2*max_range + 1, 2 * max_range + 1])
        distribution_cc = np.zeros([2*max_range + 1, 2 * max_range + 1])
        
        delay = self.latency_time + self.behavior_time

        # Descent time (irrespective of flight speed when flight is horizontal)
        bal_time = BD.compute_ballistic_distance(altitude, 0.8 * aircraft.cruise_speed, 0)[3]

        # Loops for the WC scenario
        for v in aircraft_speed:
            
            # Ballistic descent in standard scenario
            bal_distance_std = BD.compute_ballistic_distance(altitude, v, 0)[0]
            
            for idx, dir_h in enumerate(direction_horizontal):
                
                cossin_dir_h = np.array([direction_horizontal_cos[idx], direction_horizontal_sin[idx]])
                
                for dir_w in wind_dir:
                    
                    cossin_dir_w_bal_time = np.array([math.cos(dir_w), math.sin(dir_w)]) * bal_time

                    for dir_v_cos in direction_vertical_cos:

                        for w in wind_speed:
    
                            loc_ballistic = cossin_dir_w_bal_time * w
                            
                            # Compute the worst case
                            dist_wc = (v + w) * delay * dir_v_cos + bal_distance_std
                            loc_wc = dist_wc * cossin_dir_h + loc_ballistic
    
                            x_wc = min(2 * max_range, max(0, max_range + int(loc_wc[0] / scale + 0.5)))
                            y_wc = min(2 * max_range, max(0, max_range + int(loc_wc[1] / scale + 0.5)))
                            
                            distribution_wc[x_wc][y_wc] = distribution_wc[x_wc][y_wc] + 1
                         
        # Copy the result to all four quadrants
        distribution_wc = (distribution_wc + np.rot90(distribution_wc, k = 1, axes=(0, 1)) + np.rot90(distribution_wc, k = 2, axes=(0, 1)) + np.rot90(distribution_wc, k = 3, axes=(0, 1)))/4
                         
        # Ballistic descent in corridor scenario
        bal_distance_cor = BD.compute_ballistic_distance(altitude, 0.8 * aircraft.cruise_speed, 0)[0]
        
        # Compute the corridor case
        dist_cc = np.array([0.8 * aircraft.cruise_speed * delay + bal_distance_cor, 0])
        
        # Loop for CC scenario   
        for dir_w in wind_dir:
            
            cossin_dir_w_bal_time = np.array([math.cos(dir_w), math.sin(dir_w)]) * bal_time

            for w in wind_speed:

                loc_ballistic = cossin_dir_w_bal_time * w
                
                loc_cc = dist_cc + loc_ballistic
            
                x_cc = min(2 * max_range, max(0, max_range + int(loc_cc[0] / scale + 0.5)))
                y_cc = min(2 * max_range, max(0, max_range + int(loc_cc[1] / scale + 0.5)))
                
                distribution_cc[x_cc][y_cc] = distribution_cc[x_cc][y_cc] + 1
        
        # Adjust CC scenario to have the same number of samples as WC
        distribution_cc = distribution_cc / np.sum(np.sum(distribution_cc, axis = 0)) * np.sum(np.sum(distribution_wc, axis = 0))
        
        # Sum over rows to get 1D distribution of distance to corridor/ops volume.
        PDF_dist_wc = np.sum(distribution_wc, axis = 0)
        PDF_dist_cc = np.sum(distribution_cc, axis = 0)
        
        # Joint distribution.
        PDF_dist = PDF_dist_cc * corridor_fraction + PDF_dist_wc * (1 - corridor_fraction)

        PDF_dist[max_range] = PDF_dist[max_range + 1]
        
        # Normalize distribution.
        PDF_dist = PDF_dist / np.sum(PDF_dist)
        
        # Create the associated x axis.
        x_axis_PDF = np.linspace(-max_range * scale, max_range * scale, 2 * max_range + 1)

        # Initialize.
        dist_fraction = [0, 0]

        if (corridor_fraction == 0):
            # Get the accumulated sum (CDF).
            CDF_dist = np.cumsum(PDF_dist)
            
            # Create the axis that fits the CDF.
            x_axis_CDF = x_axis_PDF

            # For what distance does the cumsum reach a given fraction of totals?
            dist_fraction[0] = (np.argmin(np.abs(CDF_dist - CDF_dist[-1]*fraction_for_dist[0])) - max_range)* scale

            # For what distance does the cumsum reach a given fraction of totals?
            dist_fraction[1] = (np.argmin(np.abs(CDF_dist - CDF_dist[-1]*fraction_for_dist[1])) - max_range)* scale

        else:
            # Get the accumulated sum (CDF) only to one side and double it.
            CDF_dist = 2 * np.cumsum(PDF_dist[max_range:0:-1]) - PDF_dist[max_range] / 2
            
            # Normalize; should not be necessary, but for low res computations the PDF may not be entirely symmetric.
            CDF_dist = CDF_dist / CDF_dist[-1]            
            
            # Create the axis the fits the CDF.
            x_axis_CDF = np.linspace(0, max_range * scale, max_range)

            # For what distance does the cumsum reach a given fraction of totals?
            dist_fraction[0] = np.argmin(np.abs(CDF_dist - CDF_dist[-1]*fraction_for_dist[0])) * scale

            # For what distance does the cumsum reach a given fraction of totals?
            dist_fraction[1] = np.argmin(np.abs(CDF_dist - CDF_dist[-1]*fraction_for_dist[1])) * scale

        # For the visuals of joint corridor/non-corridor distribution.
        distribution = distribution_cc * corridor_fraction + distribution_wc * (1 - corridor_fraction);
        
        return distribution, PDF_dist, CDF_dist, x_axis_PDF, x_axis_CDF, dist_fraction, distribution_wc, distribution_cc
        
    def reflection(self):
        return lambda x, y: (- x, y)
    
    def AreaPolygons(self, H, max_range, dist_fraction, corridor):

        if (corridor == 0):
            Buffer1 = Polygon([(0, 0), (dist_fraction[0], 0), (dist_fraction[0], H), (0, H), (0, 0)])
            Buffer2 = Polygon([(dist_fraction[0], 0), (dist_fraction[1], 0), (dist_fraction[1], H), (dist_fraction[0], H), (dist_fraction[0], 0)])
            CV = Polygon([(0, 0), (-0.3 * max_range, 0), (-0.3 * max_range, H), (0, H), (0, 0)])
            FG = Polygon([(-0.3 * max_range, 0), (-max_range, 0), (-max_range, H), (-0.3 * max_range, H), (-0.3 * max_range, 0)])
        else:
            Buffer1 = Polygon([(0.1 * max_range, 0), (dist_fraction[0], 0), (dist_fraction[0], H), (0.1 * max_range, H), (0.1 * max_range, 0)])
            Buffer2 = Polygon([(dist_fraction[0], 0), (dist_fraction[1], 0), (dist_fraction[1], H), (dist_fraction[0], H), (dist_fraction[0], 0)])
            CV = Polygon([(0.05 * max_range, 0), (0.1 * max_range, 0), (0.1 * max_range, H), (0.05 * max_range, H), (0.05 * max_range, 0)])
            FG = Polygon([(0, 0), (0.05 * max_range, 0), (0.05 * max_range, H), (0, H), (0, 0)])
            
            if (corridor < 0):
                Buffer1 = scale(Buffer1, xfact = -1, origin = (0, H/2))
                Buffer2 = scale(Buffer2, xfact = -1, origin = (0, H/2))
                CV = scale(CV, xfact = -1, origin = (0, H/2))
                FG = scale(FG, xfact = -1, origin = (0, H/2))
           
        return FG, CV, Buffer1, Buffer2
        
