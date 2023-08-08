"""
Support both computation and simulation of the reduction of critical area.
"""
from dataclasses import dataclass
import math
#from os import waitid_result
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from scipy import interpolate
from descartes.patch import PolygonPatch
from shapely import affinity
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.strtree import STRtree
from enum import Enum


class Obstacles:
    """This class has methods for computing the theoretical reduction in the size of the
    critical area when there are obstacles in the ground area as well as for simulating
    this reduction.
    
    The theoretical reduction is based on the work :cite:`f-lacour2021`.
    
    Examples of how to MISSING DOC

    Attributes
    ----------
    num_of_obstacles : int
        Number of obstacles in the simulation.
    trials_count : int
        Number of trials in the simulation.
    CA_width : float
        [m] Width of critical area.
    CA_length : float
        [m] Length of critical area.
    intersected_obstacles : List of Polygon
        List of all obstacles that have caused reduction in a CA.
    closest : Point
        The point closest to the beginning of a CA for each reduced CA.
    CA_cut_off_coords : List of Point
        Coordinates of CAs where they are cut off as a result of impact with an obstacle.
    obstacles_rtree : STRtree
        Intermediate variables for increasing computations speed. 
    CA_lengths : Array of floats
        List of the length of every CA after reduction
    total_obstacle_area : float
        [m^2] The total area of all obstacles not considering any overlap (sum of the area of every obstacle).
    total_coverage : float
        [m^2] The total area covered by obstacles. This means that overlapping areas are only counted once.
    trial_area_sidelength : float
        [m] Length of each side of the square trial area.
    obstacles : List of Polygon
        A list of all obstacles in the simulation.
    CAs : List of Polygon
        A list of all nominal CAs in the simulation (before potential reduction).
    CAs_reduced : List of Polygon
        A list of all CAs after potential reduction.
    num_of_empty_CA : int
        The count of how many CAs have become empty in the simulation.
    num_of_reduced_CA : int
        The count of how many CAs are reduced in the simulation.
    """

    @dataclass
    class ObstaclesSizeProperties():
        width_mu : float
        width_sigma : float
        length_mu : float
        length_sigma : float

    class ObstacleOrientation(Enum):
        FIXED = 1
        UNIFORM = 2
        NORM = 3

    @dataclass
    class ObstacleOrientationParameters():
        orientation_type : "ObstacleOrientation"
        loc : float = 0.0
        scale : float = 1.0

    def __init__(self, CA_width, CA_length, num_of_obstacles, trial_area_sidelength):
        """ MISSING DOCS

        Parameters
        ----------
        CA_width : float
            [m] Width of the nominal CA.
        CA_length : float
            [m] Length of the nominal CA.
        trials_count : int
            Number of trials in the simulation.
        trial_area_sidelength : float
            [m] Length of each side of the square trial area.
        """
        self.CA_width = CA_width
        self.CA_length = CA_length
        self.num_of_obstacles = num_of_obstacles
        self.trial_area_sidelength = trial_area_sidelength
        self.trials_count = None
        self.intersected_obstacles = None
        self.closest = None
        self.CA_cut_off_coords = None
        self.obstacles_rtree = None
        self.CA_lengths = None
        self.total_obstacle_area = None
        self.total_coverage = None
        self.ObstacleSizes = None
        self.obstacle_orientation_parameters = Obstacles.ObstacleOrientationParameters(Obstacles.ObstacleOrientation.FIXED)


        self.obstacles = []
        self.CAs = []
        self.CAs_reduced = []

        self.num_of_empty_CA = 0
        self.num_of_reduced_CA = 0

        # Smallest distance before we consider two points the same point.
        self.__epsilon = 0.0001

        # Some colors available for drawing obstacles and CAs.
        self.BLUE = '#6699cc'
        self.GRAY = '#999999'
        self.DARKGRAY = '#333333'
        self.YELLOW = '#fff700'
        self.GREEN = '#339933'
        self.RED = '#ff3333'
        self.ORANGE = '#fc6a03'
        self.BLACK = '#000000'
        self.PURPLE = '#CF9FFF'
        self.WHITE = '#FFFFFF'

    def generate_rectangular_obstacles_normal_distributed(self, width_mu, width_sigma, length_mu, length_sigma):
        """Generate a set of uniformly distributed rectangular obstacles.
        
        This method generates a number of rectangular obstacles which a co-linear with the axes, and with width and
        length varying according to normal distributions with the mean and standard deviation as given by input
        parameters. The position of the obstacles are uniformly distributed in 2D in the trial area.

        Parameters
        ----------
        width_mu : float
            The mean of the normal distribution of the width of the obstacles.
        width_sigma : float
            The standard deviation of the normal distribution of the width of the obstacles.
        length_mu : float
            The mean of the normal distribution of the length of the obstacles.
        length_sigma : float
            The standard deviation of the normal distribution of the length of the obstacles.

        Returns
        -------
        None
        """
        self.ObstacleSizes = Obstacles.ObstaclesSizeProperties(width_mu, width_sigma, length_mu, length_sigma)

        width = stats.norm.rvs(size=self.num_of_obstacles, loc=self.ObstacleSizes.width_mu, scale=self.ObstacleSizes.width_sigma)
        length = stats.norm.rvs(size=self.num_of_obstacles, loc=self.ObstacleSizes.length_mu, scale=self.ObstacleSizes.length_sigma)

        if self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.FIXED:
            angle = np.full(self.num_of_obstacles, 0)
        elif self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.UNIFORM:
            angle = stats.uniform.rvs(size=self.num_of_obstacles, loc=self.obstacle_orientation_parameters.loc, scale=self.obstacle_orientation_parameters.scale)
        elif self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.NORM:
            angle = stats.norm.rvs(size=self.num_of_obstacles, loc=self.obstacle_orientation_parameters.loc, scale=self.obstacle_orientation_parameters.scale)
        else:
            warnings.warn("obstacle_orientation_type not recognized.")

        # Create a list of obstacle polygons.
        trans_x = stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)
        trans_y = stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)

        for k in range(0, self.num_of_obstacles):
            obs = [(0, 0), (length[k], 0), (length[k], width[k]), (0, width[k]), (0, 0)]
            self.obstacles.append(affinity.translate(affinity.rotate(Polygon(obs), angle[k], 'center'), trans_x[k], trans_y[k]))

    def set_obstacle_orientation(self, orientation_distribution_type, loc = 0, scale = 1):
        if not isinstance(orientation_distribution_type, Obstacles.ObstacleOrientation):
            warnings.warn("orientation_distribution_type not recognized. Set to FIXED.")
            orientation_distribution_type = Obstacles.ObstacleOrientation.FIXED

        self.obstacle_orientation_parameters = Obstacles.ObstacleOrientationParameters(orientation_distribution_type, loc, scale)

    def generate_rectangular_obstacles_along_curves(self, width_mu, width_sigma, length_mu, length_sigma,
                                                    houses_along_street, rows_of_houses, distance_between_two_houses):
        """Generate a set of obstacles that follows a curve.
        
        Rectangular obstacles are generated so that they follow a vertical curve and located in parts. This is to
        simulate houses along a road. The size and density of houses can be adjusted.
        
        An area larger than the trial area is covered with obstacles, but only the ones inside the trial
        area are preserved. The number of obstacles is set to the number of obstacles preserved.

        Parameters
        ----------
        width_mu : float
            [m] The mean of the normal distribution of the width of the obstacles.
        width_sigma : float
            The standard deviation of the normal distribution of the width of the obstacles.
        length_mu : float
            [m] The mean of the normal distribution of the length of the obstacles.
        length_sigma : float
            The standard deviation of the normal distribution of the length of the obstacles.
        houses_along_street : float
            The number of houses along the road (22 is a good starting number).
        rows_of_houses : float
            The number of rows of houses (12 is a good starting number).
        distance_between_two_houses : float
            [m] The distance between two houses that make up the pair of houses that shares a common border,
            but are on two different streets (20 m is a good starting number).

        Returns
        -------
        None
        """
        self.ObstacleSizes = Obstacles.ObstaclesSizeProperties(width_mu, width_sigma, length_mu, length_sigma)

        # Number of rows of houses per side length. This is expanded to cover the entire area
        # (because the rows are curved).
        rows_of_houses = round(rows_of_houses * 1.25)

        # Distance between two houses in each set of houses (neighbouring houses from separate streets).
        distance_between_two_houses = 20

        self.num_of_obstacles = houses_along_street * 2 * rows_of_houses

        width = stats.norm.rvs(size=self.num_of_obstacles, loc=width_mu, scale=width_sigma)
        length = stats.norm.rvs(size=self.num_of_obstacles, loc=length_mu, scale=length_sigma)

        # Points to create a curvy road.
        x_points = np.linspace(0, 1000, 11)
        y_points = np.array([10, 40, 80, 100, 80, 50, 80, 120, 150, 210, 270])
        coefs = interpolate.splrep(x_points, y_points)

        # Compute position and rotation of houses.
        y = np.linspace(0+0.1, 1000-2*length_mu, houses_along_street)
        x = np.linspace(-250, 1000, rows_of_houses)
        y2 = np.full(houses_along_street, 1000 / (houses_along_street + 1))
        x2 = np.diff(interpolate.splev(y, coefs), prepend=-10)
        r = []
        for k in range(houses_along_street):
            r.append(-math.atan2(x2[k], y2[k]) * 180 / math.pi)

        # Add houses, only those inside the trial area.
        counter = 0
        for j in range(0, rows_of_houses):
            for k in range(0, houses_along_street):
                trans_x = interpolate.splev(y[k], coefs) + x[j]
                trans_y = y[k]
                if 0 < trans_x < self.trial_area_sidelength and 0 < trans_y < self.trial_area_sidelength:
                    obs = [(0, 0), (length[counter], 0), (length[counter], width[counter]), (0, width[counter]), (0, 0)]
                    self.obstacles.append(affinity.translate(affinity.rotate(Polygon(obs), r[k]), trans_x, trans_y))
                counter = counter + 1
                trans_x = trans_x + distance_between_two_houses
                if 0 < trans_x < self.trial_area_sidelength and 0 < trans_y < self.trial_area_sidelength:
                    obs = [(0, 0), (length[counter], 0), (length[counter], width[counter]), (0, width[counter]), (0, 0)]
                    self.obstacles.append(affinity.translate(affinity.rotate(Polygon(obs), r[k]), trans_x, trans_y))
                counter = counter + 1

        self.num_of_obstacles = len(self.obstacles)

    def generate_CAs(self, trials_count):
        """Generate a number of critical areas for simulation.
        
        A number of critical areas are generated with 2D uniformly distributed location and uniformly distributed
        orientation between 0 and 360 degrees. They are have the width and length as set at initialization of the class.

        Parameters
        ----------
        trials_count : int
            Number of trials to perform.

        Returns
        -------
        None
        """
        self.trials_count = trials_count

        # Compute reduction in the translation of the original CA. Since rotation is around the center,
        # the compensation is half the longest length of the CA.
        CA_compensate = np.amax([self.CA_width, self.CA_length]) / 2

        # Uniformly distributed heading from 0 to 180 degrees.
        heading = stats.uniform.rvs(size=self.trials_count, loc=0, scale=360)

        # Uniformly distributed translation from 0 to trial_area_sidelength.
        # We need to compensate for any CAs sticking out of the trial area, and thus cannot intersect obstacles.
        # We do this crudely by forcing the CAs to be sufficiently far from the edge of the trial area.
        CA_trans_x = stats.uniform.rvs(size=self.trials_count, loc=CA_compensate,
                                       scale=self.trial_area_sidelength - 2 * CA_compensate)
        CA_trans_y = stats.uniform.rvs(size=self.trials_count, loc=0,
                                       scale=self.trial_area_sidelength - 2 * CA_compensate)

        CA_coor = [(0, 0), (self.CA_width, 0), (self.CA_width, self.CA_length), (0, self.CA_length), (0, 0)]

        for j in range(0, self.trials_count):
            # Rotate and move CA.
            CA_polygon = affinity.translate(affinity.rotate(Polygon(CA_coor), heading[j], 'center'), CA_trans_x[j],
                                            CA_trans_y[j])

            self.CAs.append(CA_polygon)

    def compute_reduced_CAs(self, show_progress = False):
        """Compute the reduction for each CA
        
        Any CA that intersects with an obstacles is reduced such as to no longer intersect with any obstacles.
        This method runs through all CAs and all obstacles and produces a list of CAs that.

        Parameters
        ----------

        Returns
        -------
        None
        """
        self.CAs_reduced = []
        self.intersected_obstacles = []
        self.closest = []
        self.CA_cut_off_coords = []
        self.num_of_empty_CA = 0

        # Create STRtree for faster intersection detection.
        self.obstacles_rtree = STRtree(self.obstacles)

        # Keep track of reduced obstacles.
        reduced_CA_idxs = []

        for CA_idx, CA_polygon in enumerate(self.CAs):
            if show_progress:
                print('Intersection time:        {:1.0f}%'.format(CA_idx / len(self.CAs) * 100), end='\r', flush=True)

            # Keep track of the starting coordinates of the original CA.
            CA_original_coords = MultiPoint(CA_polygon.exterior.coords)

            # Get a short list of potentially intersecting obstacles.
            potentially_intersecting_obstacles = self.obstacles_rtree.query(CA_polygon)

            # Iterate over those potential obstacles.
            for idx, obstacle in enumerate(potentially_intersecting_obstacles):
                # Check if it intersects any of the obstacles.
                if CA_polygon.intersects(obstacle):

                    # Check if this obstacles has already been reduced once.
                    if CA_idx not in reduced_CA_idxs:
                        # If not, increment the number of reduced obstacles.
                        self.num_of_reduced_CA = self.num_of_reduced_CA + 1
                        # and append it to the list of reduced obstacles.
                        reduced_CA_idxs.append(CA_idx)

                    # Keep a list of the intersected obstacles for later viz.
                    self.intersected_obstacles.append(obstacle)

                    # Figure out how much is left of the CA.

                    # If the beginning of the CA is inside the obstacle, the CA becomes empty.
                    CA_beginning_line = LineString([(CA_original_coords[0].x, CA_original_coords[0].y),
                                                    (CA_original_coords[1].x, CA_original_coords[1].y)])
                    if CA_beginning_line.intersects(obstacle):
                        CA_polygon = Polygon()
                        self.num_of_empty_CA = self.num_of_empty_CA + 1

                        # And we can save a little time by breaking the for loop at this point,
                        # since the CA is reduced as much as it can be, so no need to check more obstacles.
                        break

                    else:
                        # First, subtract the obstacle from the CA.
                        CA_splitted = CA_polygon.difference(obstacle)

                        # If the obstacles splits the CA in multiple polygons, figure out which part we need
                        # (i.e. the one closest to the CA origin).
                        if CA_splitted.geom_type == 'MultiPolygon':

                            # Iterate over all resulting polygons after splitting the CA.
                            for CA_split in CA_splitted:

                                # Look for the one where the distance to the beginning of the CA is (very close to) zero.
                                if (CA_split.distance(CA_original_coords[0]) < self.__epsilon) | (
                                        CA_split.distance(CA_original_coords[1]) < self.__epsilon):
                                    CA_polygon = CA_split
                                    break

                        # The splitting of CA only resulting in one polygon.
                        else:
                            CA_polygon = CA_splitted

                        # After splitting the CA, it is most likely not a rectangle anymore, but we want that.
                        # So, we find all the coordinates of the split CA that were not in the original CA
                        # and that the one closest to the beginning of the CA (called p_closest).
                        # When we compute a new CA polygon consisting of p_closest and the two points at the beginning
                        # of the CA, plus a fourth point that make the polygon a rectangle.
                        CA_polygon = self.__cut_polygon_to_rectangle(CA_polygon, CA_original_coords)

            # Add the resulting CA polygon to the list of reduced CAs.
            self.CAs_reduced.append(CA_polygon)

    def __cut_polygon_to_rectangle(self, CA_polygon, CA_original_coords):
        """
        Create a rectangular polygon that has the same beginning side as the original CA polygon.

        This function finds all the coordinates of the non-rectangular (split) CA that were not in the original CA
        and the one closest to the beginning of the CA (called p_closest) will be used for creating the rectangle.
        When we compute a new CA polygon consisting of p_closest and the two points at the beginning
        of the CA, plus a fourth point that make the polygon a rectangle.
        """
        # Get the coordinates of the input polygon as Points.
        CA_reduced_polygon_coords = MultiPoint(CA_polygon.exterior.coords)

        # Initialize with a sufficiently big number.
        dist = 10 * self.trial_area_sidelength

        # Initialize what point to keep.
        p_closest = CA_reduced_polygon_coords[0]

        # Iterate over the points in the reduced polygon.
        for p in CA_reduced_polygon_coords:

            # Distance to the two coordinates at the beginning of the CA.
            d0 = CA_original_coords[0].distance(p)
            d1 = CA_original_coords[1].distance(p)

            # If p is one of the two original coordinates, move to next for iteration.
            if (d0 < self.__epsilon) | (d1 < self.__epsilon):
                continue

            if d0 < dist:
                p_closest = p
                dist = d0

            if d1 < dist:
                p_closest = p
                dist = d1

        # Figure out the fourth point in the rectangle.
        # 1. Conceptually make a line through p_keep parallel to a line through the two CA coords at the CA beginning,
        #    and find the distance between these two lines.
        # 2. Pick the two points on this line closest to the two CA coords at the CA beginning.

        # Initial computations.
        x = CA_original_coords[1].x - CA_original_coords[0].x
        y = CA_original_coords[1].y - CA_original_coords[0].y

        # This should be equal to w, but just in case.
        d = CA_original_coords[0].distance(CA_original_coords[1])

        # Do the check again w.
        if np.abs(d - self.CA_width) > 10 * self.__epsilon:
            warning.warn("Distance between two CA beginning points not equal to width. This is an internal warning"
                         " showing inconsistency.")

        # Compute step 1
        # Distance from beginning of CA to the closest point.
        dist = np.abs(y * p_closest.x - x * p_closest.y + CA_original_coords[1].x * CA_original_coords[0].y -
                      CA_original_coords[1].y * CA_original_coords[0].x) / d

        # Make this distance a smidging shorter to avoid CA still slightly overlapping obstacle.
        dist = dist - 100 * self.__epsilon

        # Compute step 2
        # Find the two points in addition to the two CA beginning points.
        point1 = Point(-y / d * dist + CA_original_coords[0].x, x / d * dist + CA_original_coords[0].y)
        point2 = affinity.translate(point1, x, y)

        # Record the points for debugging/viz purposes.
        self.closest.append(p_closest)
        self.CA_cut_off_coords.append(point1)
        self.CA_cut_off_coords.append(point2)

        # Generate a new rectangular polygon from the four points.
        CA_polygon = Polygon(
            [[CA_original_coords[0].x, CA_original_coords[0].y], [CA_original_coords[1].x, CA_original_coords[1].y],
             [point2.x, point2.y], [point1.x, point1.y]])

        # Return the new rectangular polygon.
        return CA_polygon

    def compute_CA_lengths(self):
        """Make a list of the actual lengths of the CAs.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # We count the number of empty CAs for comparison with the global num_of_empty_CA for sanity check.
        count_empties = 0

        self.CA_lengths = []
        for CAr in self.CAs_reduced:
            if CAr.is_empty:
                self.CA_lengths.append(0)
                count_empties = count_empties + 1
            else:
                x, y = CAr.exterior.coords.xy
                self.CA_lengths.append(np.sqrt((x[1] - x[2]) * (x[1] - x[2]) + (y[1] - y[2]) * (y[1] - y[2])))

        if not count_empties == self.num_of_empty_CA:
            warning("Sanity check failed for number of empty CAs.")

    def compute_coverage(self, show_progress = False):
        """Determine total obstacle coverage.

        Parameters
        ----------

        Returns
        -------
        None
        """
        self.total_obstacle_area = 0
        self.total_coverage = 0

        for k in range(0, self.num_of_obstacles):
            if show_progress:
                print('Coverage time:            {:1.0f} %'.format(k / self.num_of_obstacles * 100), end='\r', flush=True)

            area = self.obstacles[k].area
            self.total_obstacle_area = self.total_obstacle_area + area
            self.total_coverage = self.total_coverage + area
            for j in range(k + 1, self.num_of_obstacles):
                if self.obstacles[k].intersects(self.obstacles[j]):
                    self.total_coverage = self.total_coverage - self.obstacles[k].intersection(self.obstacles[j]).area

    def missed_obstacle_CA_intersections(self):
        """Identifies missed intersections metween obstacle and reduced CA.

        In the simulation, it may happen that a critical areas is reduced, and the part of the critical area that has
        been reduced away intersects another obstacle that the one causing the reduction. If this overlap is such
        that the nominal critica area is not completely separated in two (i.e., the obstacle has a corner inside
        the CA without going all the way through), the overlapping area will not contribute correctly to the simulation
        results.

        This is a rare event, and is therefore ignore. To visualize these problematic overlaps, this function
        provide a list of the affect obstacles and CAs, plus compute the area missed in the simulation.

        Parameters
        ----------

        Returns
        -------
        intersection area : MISSING DOC
            MISSING DOC
        problematic obstacles : MISSING DOC
            MISSING DOC
        problematic CAs : MISSING DOC
            MISSING DOC
        """
        intersection_area = 0

        # Return all found overlapping polygons.
        problematic_obstacles = []
        problematic_CAs = []

        for CAr in self.CAs_reduced:
            potentially_intersecting_obstacles = self.obstacles_rtree.query(CAr)
            for obstacle in potentially_intersecting_obstacles:
                if obstacle.intersects(CAr):
                    intersection_area = intersection_area + obstacle.intersection(CAr).area
                    problematic_obstacles.append(obstacle)
                    problematic_CAs.append(CAr)

        return intersection_area, problematic_obstacles, problematic_CAs

    def cdf(self, 
            x, 
            obstacle_size_resolution = 10, 
            CA_orientation_resolution = 10,
            obstacle_orientation_resolution = 10,
            probability_threshold = stats.norm.pdf(3),
            show_progress = False):
        """Compute the CDF for the length of the critical area when rectangular obstacles are present.
        
        This is the CDF for the length of the critical area when there are a given obstacle density of rectangular
        obstacles with dimension given by normal distributions. To draw the full CDF, a typical input for x is an array
        ranging in value from 0 to the nominal length of the CA. Since this is usually a rather smooth curve, it can be
        approximated well by relatively few x values (typically 10 or 15).

        The resolution should not be lower than 

        Note that this function relies on a previous call to generate_rectangular_obstacles_normal_distributed().
        
        For a more detailed explanation of the CDF, see :cite:`f-lacour2021`.

        Parameters
        ----------
        x : float array
            [m] The length of the critical area for which the CDF is computed. This can be a scalar or an array.
        obstacle_size_resolution : int (default is 10)
            The number of points for the discretization of the two integrals for width and length of obstacles.
            A good starting value is 10. For high resolution, 20 is an approprite choice.
        CA_orientation_resolution : int (default is 10)
            The number of points for the discretization of integral for CA orientation.
            A good starting value is 10. For high resolution, 20 is an approprite choice.
        obstacle_orientation_resoltion : int (default is 10)
            The number of points for the discretization of the integral over the obstacle orientation.
            The value depends highly on the chosen distribution. If the orientation type is FIXED, this value is not used, as
            the integral does not need to be evaluated.
        probability_threshold : float (default is PDF for normal distribution evaluated at 3 sigma, approx 0.0044)
            This value is used to speed up computation of the integrals. For any probability below this threshold, the contribution 
            to the integrals is ignored.
            To include all values, set this to zero.
            Adjusting this value will affect the sanity checking, so if it becomes too large (i.e., too much of the integral 
            contributions are ignored), a warning will be issued.
        show_progress : bool (default False)
            Write the progress in percent to the prompt for the multple integral computation.

        Returns
        -------
        p_x : float array
            The CDF value for the given x. This return parameter has the same type as input x.
        expected_value : float
            [m] The expected value of the length.
        beta : float
            The beta values as computed in :cite:`f-lacour2021`.
        acc_probability_check : float
            A sanity check on the triple integral. This values should be relatively close to 1, especially for high
            value of pdf_resolution.
        pdf_width : np.array
            The PDF for the obstacle width as used in the integral.
        pdf_length : np.array
            The PDF for the obstacle length as used in the integral.
        pdf_CA_orientation : np.array
            The PDF for the CA orientation as used in the integral.
        """
        # Sample the obstacle PDF.
        width_range = np.linspace(self.ObstacleSizes.width_mu - 3 * self.ObstacleSizes.width_sigma, 
                                  self.ObstacleSizes.width_mu + 3 * self.ObstacleSizes.width_sigma,
                                  obstacle_size_resolution)
        length_range = np.linspace(self.ObstacleSizes.length_mu - 3 * self.ObstacleSizes.length_sigma,
                                   self.ObstacleSizes.length_mu + 3 * self.ObstacleSizes.length_sigma,
                                   obstacle_size_resolution)
        CA_orientation_range = np.linspace(0, 360 - 360 / CA_orientation_resolution, CA_orientation_resolution)


        pdf_width = stats.norm(self.ObstacleSizes.width_mu, self.ObstacleSizes.width_sigma).pdf(width_range)
        pdf_length = stats.norm(self.ObstacleSizes.length_mu, self.ObstacleSizes.length_sigma).pdf(length_range)
        pdf_CA_orientation = stats.uniform(0, 360).pdf(CA_orientation_range)

        # Compute the step length for the integral computation.
        pdf_width_step = (width_range[-1] - width_range[0]) / (obstacle_size_resolution - 1)
        pdf_length_step = (length_range[-1] - length_range[0]) / (obstacle_size_resolution - 1)
        pdf_CA_orientation_step = (CA_orientation_range[-1] - CA_orientation_range[0]) / (CA_orientation_resolution - 1)

        # Handles the various types of obstacle orientations.
        if self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.FIXED:
            obstacle_orientation_range = np.array([0])   # Fixed orientation at 0 degrees.
            pdf_obstacle_orientation_step = 1            # Step-size is 1.
            pdf_obstacle_orientation = np.array([1])         # Probability of orientation is 1.
        else:
            if self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.UNIFORM:
                obstacle_orientation_range = np.linspace(0, 360 - 360 / obstacle_orientation_resolution, obstacle_orientation_resolution)
                pdf_obstacle_orientation = stats.uniform(loc = self.obstacle_orientation_parameters.loc, 
                                                     scale = self.obstacle_orientation_parameters.scale).pdf(obstacle_orientation_range)

                # Due to potentially very low sampling resolution, this PDF may be slightly off in terms of area. So we adjust that.
                pdf_obstacle_orientation = pdf_obstacle_orientation / (np.sum(pdf_obstacle_orientation) * pdf_obstacle_orientation_step)
            elif self.obstacle_orientation_parameters.orientation_type == Obstacles.ObstacleOrientation.NORM:
                obstacle_orientation_range = np.linspace(self.obstacle_orientation_parameters.loc - 3 * self.obstacle_orientation_parameters.scale,
                                   self.obstacle_orientation_parameters.loc + 3 * self.obstacle_orientation_parameters.scale,
                                   obstacle_orientation_resolution)
                pdf_obstacle_orientation = stats.norm(loc = self.obstacle_orientation_parameters.loc, 
                                                  scale = self.obstacle_orientation_parameters.scale).pdf(obstacle_orientation_range)

            pdf_obstacle_orientation_step = (obstacle_orientation_range[-1] - obstacle_orientation_range[0]) / (obstacle_orientation_resolution - 1)


        # The assumption is that the input is an array, so if it is scalar, change it to an array.
        if not isinstance(x, np.ndarray):
            x = np.array([x])

        x_resolution = len(x)
        x_step = 1 if len(x) == 1 else (x[-1] - x[0]) / (len(x) - 1)

        # Preset p_x.
        p_x = np.zeros(x_resolution)

        expected_value = 0
        beta_acc = 0
        acc_probability_check = 0
        obstacle_density = self.obstacle_density()
 
        if show_progress:
            print('', end='\r')

        # Loop over increasing x values to get the full CDF.
        for idx_x, x_val in enumerate(x):
            if show_progress:
                print('Theory time:              {:1.0f}%'.format(idx_x / len(x) * 100), end='\r')

            # Reset acc for integral.
            accumulator = 0

            CA_polygon = Polygon([(0, 0), (self.CA_width, 0), (self.CA_width, x_val), (0, x_val), (0, 0)])

            # Loop over orientations of CA.
            for idx_CA_orientation, CA_orientation_val in enumerate(CA_orientation_range):
                CA_polygon = affinity.rotate(CA_polygon, CA_orientation_val, 'center', use_radians=False)

                p_CA_orientation = pdf_CA_orientation[idx_CA_orientation] * pdf_CA_orientation_step

                if p_CA_orientation <= probability_threshold:
                    continue

                # Loop over orientations of obstacles.
                for idx_obstacle_orientation, obstacle_orientation_val in enumerate(obstacle_orientation_range):

                    p_obstacle_orientation = pdf_obstacle_orientation[idx_obstacle_orientation] * pdf_obstacle_orientation_step

                    if p_obstacle_orientation <= probability_threshold:
                        continue

                    # Loop for obstacle probabilistic properties (called \Phi_i in the paper).
                    for index_w, w in enumerate(width_range):

                        p_width = pdf_width[index_w] * pdf_width_step

                        if p_width <= probability_threshold:
                            continue

                        for index_l, l in enumerate(length_range):
                            p_length = pdf_length[index_l] * pdf_length_step

                            if p_width <= probability_threshold:
                                continue

                            minkowski_area = self.Minkowski_sum_convex_polygons_area(self.CA_width, x_val, w, l,
                                                                                     CA_orientation_val, obstacle_orientation_val)
                            accumulator = accumulator + minkowski_area * p_width * p_length * p_CA_orientation * p_obstacle_orientation
                            acc_probability_check = acc_probability_check + p_width * p_length * p_CA_orientation * p_obstacle_orientation

                            # Compute beta (does not depend on x and orient, so only need to compute once).
                            if idx_x == 0 and idx_CA_orientation == 0 and idx_obstacle_orientation == 0:
                                beta_acc = beta_acc + w * l * p_width * p_length

            p_x[idx_x] = 1 - np.exp(-obstacle_density * accumulator)
            
            # Find expected value from the CDF
            expected_value = expected_value + (1 - p_x[idx_x]) * x_step

        beta = 1 - np.exp(-obstacle_density * beta_acc)
        
        # If x is not an array, the EX does not make sense, so set to zero.
        if len(x) == 1:
            expected_value = 0
                
        # Divide to account for the accumulator is not reset in the above outer loop.
        acc_probability_check = acc_probability_check / x_resolution

        total_integral_ignored = np.array([np.count_nonzero(pdf_CA_orientation * pdf_CA_orientation_step <= probability_threshold) / len(CA_orientation_range),
                                           np.count_nonzero(pdf_obstacle_orientation * pdf_obstacle_orientation_step <= probability_threshold) / len(obstacle_orientation_range),
                                           np.count_nonzero(pdf_width * pdf_width_step <= probability_threshold) / len(width_range),
                                           np.count_nonzero(pdf_length * pdf_length_step <= probability_threshold) / len(length_range)]) * 100

       
        if abs(acc_probability_check - 1) > 0.05:
            warnings.warn("PDF sanity check failed.")
            print('[DEBUG] pdf_width:                {:1.4f}'.format(np.sum(pdf_width) * pdf_width_step),flush = True)
            print('[DEBUG] pdf_length:               {:1.4f}'.format(np.sum(pdf_length) * pdf_length_step),flush = True)
            print('[DEBUG] pdf_CA_orientation:       {:1.4f}'.format(np.sum(pdf_CA_orientation) * pdf_CA_orientation_step),flush = True)
            print('[DEBUG] pdf_obstacle_orientation: {:1.4f}'.format(np.sum(pdf_obstacle_orientation) * pdf_obstacle_orientation_step),flush = True)

        return (p_x, 
                expected_value, 
                beta, 
                {'acc_probability_check' : acc_probability_check, 
                 'total_integral_ignored' : total_integral_ignored,
                 'pdf_width' : pdf_width,
                 'pdf_width_range' : width_range,
                 'pdf_width_step' : pdf_width_step,
                 'pdf_length' : pdf_length,
                 'pdf_length_range' : length_range,
                 'pdf_length_step' : pdf_length_step,
                 'pdf_CA_orientation' : pdf_CA_orientation,
                 'CA_orientation_range' : CA_orientation_range,
                 'pdf_CA_orientation_step' : pdf_CA_orientation_step,
                 'pdf_obstacle_orientation' : pdf_obstacle_orientation,
                 'obstacle_orientation_range' : obstacle_orientation_range,
                 'pdf_obstacle_orientation_step' : pdf_obstacle_orientation_step,
                 })

    def singleton_objects_CDF(self, x):
        """ CDF for singleton objects.

        This implements equation (15) in the paper. MISSING DOCS

        Note that this function requires objects to have been specified first.

        Parameters
        __________
        x : float, scalar or np.array
            The length of the CA, typically starting from 0 to the full length (nominel CA size divded by width)

        Returns
        _______
        CDF with same number of samples as input x (but always as np.array).

        """
        if not isinstance(x, np.ndarray):
            x = np.array([x])

        pdf = 1 - np.exp(-x*self.CA_width*self.obstacle_density())

        return np.cumsum(pdf) / np.sum(pdf)

    def obstacle_density(self):
        """ Return the density of obstacles.
        """
        return self.num_of_obstacles / self.trial_area_sidelength / self.trial_area_sidelength

    def show_simulation(self, ax, problematic_obstacles = None, problematic_CAs = None, show_CAs = True, 
                        show_CA_first_point = False, show_CAs_reduced = True, show_obstacles = True,
                        show_obstacles_intersected = True, show_debug_points = False):
        """Visualize simulation with obstacles and critical areas.

        This functions makes it easy to visualize the result of simulations. It will show the simulated square area with obstacles (possible
        showing which are impacted and which are not), critical areas (both which are "full" and which have been reduced).

        It can also show a list of problematic obstacles and critical areas. For more details on what that is and how to detect them, see
        the help for `sanity_check()`.

        Parameters
        ----------
        ax : axis to plot in
            Handle to the plot axis
        problematic_obstacles : list of polygon (default None)
            Show the provided problematic obstacles (in yellow).
        problematic_CAs : list of polygon (default None)
            Show the provided problematic CAs (in yellow).
        show_CAs : bool (default True)
            Show the nominal critical areas.
        show_CA_first_point : bool (default False)
            Show a point at the starting end of each CA.
        show_CAs_reduced : bool (default True)
            Show the reduced critical areas.
        show_obstacles : bool (default True)
            Show all obstacles (in green).
        show_obstacles_intersected : bool (default True)
            Show the obstacles intersected by critical areas (in orange instead of green).
        show_debug_points : bool (default False)
            Show debug points on the CAs to help verify that intersections and polygonal reduction is corrected.
            Typically only used for debugging.

        Returns
        -------
        None
        """
        # Viz all the original CAs
        if show_CAs:
            for CA in self.CAs:
                x, y = CA.exterior.coords.xy
                ax.plot(x, y, '-', color=self.BLACK, linewidth=0.25)
                if show_CA_first_point:
                    ax.plot((x[0]+x[1])/2, (y[0]+y[1])/2, 'o', color=self.BLACK)
            ax.add_patch(PolygonPatch(Polygon([(0,0), (0,1), (1,0)]), facecolor=self.WHITE, edgecolor=self.BLACK, alpha=1, linewidth=0.25, label="Nominal CA"))

            if show_CA_first_point:
                ax.plot(-10000, -10000, 'o', color=self.BLACK, label="Start of CA")

        if show_CAs_reduced:
            for CAr in self.CAs_reduced:
                if not CAr.is_empty:
                    ax.add_patch(PolygonPatch(CAr, facecolor=self.PURPLE, edgecolor=self.RED, alpha=1, zorder=3, linewidth=0.25))
            ax.add_patch(PolygonPatch(Polygon([(0,0), (0,1), (1,0)]), facecolor=self.PURPLE, edgecolor=self.RED, alpha=1, label="Reduced CA"))

        if show_obstacles:
            for o in self.obstacles:
                ax.add_patch(
                    PolygonPatch(o, facecolor=self.GREEN, edgecolor=self.BLACK, alpha=1, zorder=2, linewidth=0.25))
            if show_obstacles_intersected:
                label_text = "Obstacles (not intersected)"
            else:
                label_text = "Obstacles"
            ax.add_patch(PolygonPatch(Polygon([(0,0), (0,1), (1,0)]), facecolor=self.GREEN, edgecolor=self.BLACK, alpha=1, linewidth=0.25, label=label_text))

        if show_obstacles_intersected:
            for o in self.intersected_obstacles:
                ax.add_patch(
                    PolygonPatch(o, facecolor=self.ORANGE, edgecolor=self.BLACK, alpha=1, zorder=2, linewidth=0.25))
            ax.add_patch(PolygonPatch(Polygon([(0,0), (0,1), (1,0)]), facecolor=self.ORANGE, edgecolor=self.BLACK, alpha=1, linewidth=0.25, label="Obstacles (intersected)"))

        if problematic_obstacles is not None:
            for po in problematic_obstacles:
                ax.add_patch(PolygonPatch(po, facecolor=self.YELLOW, edgecolor=self.BLACK, alpha=1, zorder=10, linewidth=0.25))

        if problematic_CAs is not None:
            for CAr in problematic_CAs:
                ax.add_patch(PolygonPatch(CAr, facecolor=self.YELLOW, edgecolor=self.BLACK, alpha=1, zorder=10, linewidth=0.25))

        if problematic_obstacles is not None or problematic_CAs is not None:
            ax.add_patch(PolygonPatch(Polygon([(0,0), (0.0001,0), (0,0.0001)]), facecolor=self.YELLOW, edgecolor=self.BLACK, 
                                       label='Obstacles with missed area', linewidth=0.25))

        if show_debug_points:
            for p in self.closest:
                ax.plot(p.x, p.y, 'o', color=self.YELLOW)

            for p in self.CA_cut_off_coords:
                ax.plot(p.x, p.y, 'x', color=self.GRAY, zorder=5)

        self.set_limits(ax, -100, self.trial_area_sidelength + 100, -100, self.trial_area_sidelength + 100, 100)
        ax.set_xlabel('Size [m]')
        ax.set_ylabel('Size [m]')
        ax.grid()
        ax.legend(loc="upper left", )

    def show_CDF(self, ax, show_CA_as_size = True, line_label = None, line_color = 'blue', line_width = 3):
        """Plots the CDF

        Plots a histogram of simulation results to the provided axis.

        Parameters
        ----------
        ax : handle
            Handle to the plotting axis.
        show_CA_as_size : bool (default is True)
            If True, show the first axis as size of CA. If False, show the first axis as CA length (i.e., CA size divided by width).
        line_label : text (default is None)
            If None, a label text is generated. If not None, the provided text is used for label text.
        line_color : color (default is 'blue')
            Color of CDF graph (passed directly to plot).
        line_width : float (default 3)
            Width of CDF graph (passed directly to plot).

        Returns
        -------
        None
        """
        F = self.CA_width if show_CA_as_size else 1

        num_bins = int(round(4 * np.sqrt(self.trials_count)))

        if line_label is None:
            lbl = "Simulated {:1.0f} trials".format(self.trials_count)
        else:
            lbl = line_label

        n = ax.hist(np.array(self.CA_lengths) * F, 
                    num_bins, 
                    range = (0, self.CA_length * F + 0.00001), # We need to add a little bit here to get the non-obstacle-intersecting CAs counted correctly
                    density=True, 
                    histtype='step', 
                    cumulative=True,
                    edgecolor=line_color, 
                    linewidth=line_width)

        # We plot a piece of line somewhere outside view to generate a label for the legend.
        # We do not use the histogram, as this will give a rectangle in the legend, and we want a line.
        ax.plot(-1, -1, color=line_color, linewidth=line_width, label=lbl)

        ax.set_ylim([0, 1])

        if show_CA_as_size:
            ax.set_xlabel('Size of CA [m$^2$]')
        else:
            ax.set_xlabel('Length of CA [m]')

        ax.set_ylabel('Accumulated fraction of total')
        
        return n

    @staticmethod
    def set_limits(ax, x0, xN, y0, yN, step=1):
        """Set the axes limits for a axis in a plot.

        Parameters
        ----------
        ax : Handle MISSING DOC
            MISSING DOC
        x0 : float
            MISSING DOC
        xN : float
            MISSING DOC
        y0 : float
            MISSING DOC
        yN : float
            MISSING DOC
        step : int, optional
            MISSING DOC

        Returns
        -------
        None
        """
        ax.set_xlim(x0, xN)
        ax.set_xticks(range(x0, xN + 1, step))
        ax.set_ylim(y0, yN)
        ax.set_yticks(range(y0, yN + 1, step))
        ax.set_aspect("equal")

    @staticmethod
    def Minkowski_sum_convex_polygons(A, B):
        """Compute the polygon that is the Minkowski sum of two convex polygons A and B.

        This methods is based on convex hull for computing the Minkowski sum, and it is
        therefore required that both input polygons are convex, otherwise the result is not correct.

        The result is returned as a MultiPoint type.

        Parameters
        ----------
        A : Polygon
            The one polygon in the Minkowski sum.
        B : Polygon
            The other polygon in the Minkowski sum.

        Returns
        -------
        C : MultiPoint
            The result of the computation as a Multipoint (collection of points) and not a polygon.
        """
        Av = MultiPoint(A.exterior.coords)
        Bv = MultiPoint(B.exterior.coords)
        Cv = []
        for a in Av:
            for b in Bv:
                Cv.append(affinity.translate(a, b.x, b.y))

        C = MultiPoint(Cv).convex_hull

        return C

    @staticmethod
    def Minkowski_sum_convex_polygons_area(w, x, a, b, theta1, theta2):
        """Compute the area of the Minkowski sum of two rectangles polygons.
        
        This is a fast method for computing the Minkowski sum of two polygons that are both rectangles.
        
        For details on how this is done, see :cite:`f-lacour2021`.
        
        Parameters
        ----------
        w : float
            Width of rectangle 1.
        x : float
            Length of rectangle 1.
        a : float
            Width of rectangle 2.
        b : float
            Length of rectangle 2.
        theta1 : float
            [deg] Angle of rectangle 1.
        theta2 : float
            [deg] Angle of rectangle 2.
                
        Returns
        -------
        area : float
            Area of the Minkowski sum of the two rectangles.
        """
        Ct = abs(math.cos(np.radians(theta1 - theta2)))
        St = abs(math.sin(np.radians(theta1 - theta2)))

        return w * x + a * b + w * abs(a * St + b * Ct) + x * abs(a * Ct + b * St)

    @staticmethod
    def Minkowski_difference_convex_polygons(A, B):
        """Compute the polygon that is the Minkowski difference of two convex polygons A and B.

        Compute the Minkowski difference of two convex polygons. This methods is based on the Minkowski sum for
        convex polygons, and it is
        therefore required that both input polygons are convex, otherwise the result is not correct.

        The result is returned as a MultiPoint type.

        Parameters
        ----------
        A : Polygon
            The one polygon in the Minkowski difference.
        B : Polygon
            The other polygon in the Minkowski difference.

        Returns
        -------
        C : MultiPoint
            The result of the computation as a Multipoint (collection of points) and not a polygon.
        """
        Av = MultiPoint(A.exterior.coords)
        Bv = MultiPoint(B.exterior.coords)
        Cv = []
        for a in Av:
            for b in Bv:
                Cv.append(affinity.translate(a, -b.x, -b.y))

        return MultiPoint(Cv).convex_hull

    @staticmethod
    def mirror_polygon_in_origin(polygon):
        """Compute the mirror of a polygon by negative all corner coordinates.

        Parameters
        ----------
        polygon : Polygon
            A polygon to be mirrored.

        Returns
        -------
        m : Polygon
            A polygon that is the mirror of the original polygon
        """
        return Polygon([(-c[0], -c[1]) for c in polygon.exterior.coords])

    def test_Minkowski_sum_diff(self):
        # Create to random convex polygons.
        p1 = [(0, 0), (3, 0), (3, 10), (0, 0)]
        A = affinity.translate(affinity.rotate(Polygon(p1), 35, 'center'), 4, 2)
        p2 = [(0, 0), (4, 0), (4, 8), (0, 8), (0, 0)]
        B = affinity.translate(affinity.rotate(Polygon(p2), 79, 'center'), 10, 5)

        # Find Minkowski sum.
        Cd1 = self.Minkowski_sum_convex_polygons(B, A)

        # Find Minkowski difference.
        Cd2 = self.Minkowski_difference_convex_polygons(B, A)

        # Draw all four polygons.
        fig = plt.figure(1, figsize=(18, 18), dpi=90)
        ax1 = fig.add_subplot(111)
        ax1.add_patch(PolygonPatch(A, facecolor=self.RED, edgecolor=self.BLACK, alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(B, facecolor=self.GREEN, edgecolor=self.BLACK, alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd1, facecolor=self.BLUE, edgecolor=self.BLACK, alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd2, facecolor=self.BLUE, edgecolor=self.BLACK, alpha=0.5, zorder=10))
        ax1.grid()
        self.set_limits(ax1, -10, 30, -10, 30, 10)

        # The the corner pointers for the A and B polygons.
        Ax, Ay = A.exterior.coords.xy
        Bx, By = B.exterior.coords.xy

        # Create sample points covering A and B.
        res = 10
        Ax_sample = np.linspace(np.amin(Ax), np.amax(Ax), res)
        Ay_sample = np.linspace(np.amin(Ay), np.amax(Ay), res)
        Bx_sample = np.linspace(np.amin(Bx), np.amax(Bx), res)
        By_sample = np.linspace(np.amin(By), np.amax(By), res)

        # Grab all the points inside A.
        Alist = []
        for Axv in Ax_sample:
            for Ayv in Ay_sample:
                if A.contains(Point(Axv, Ayv)):
                    Alist.append(Point(Axv, Ayv))

        # and add the corner points, too.
        for k, p in enumerate(Ax):
            Alist.append(Point(Ax[k], Ay[k]))

        # Grab all the points inside B.
        Blist = []
        for Bxv in Bx_sample:
            for Byv in By_sample:
                if B.contains(Point(Bxv, Byv)):
                    Blist.append(Point(Bxv, Byv))

        # and add the corner points, too.
        for k, p in enumerate(Bx):
            Blist.append(Point(Bx[k], By[k]))

        # Show all the points in A and B.
        for Ap in Alist:
            ax1.plot(Ap.x, Ap.y, '.', color=self.RED)
        for Bp in Blist:
            ax1.plot(Bp.x, Bp.y, '.', color=self.GREEN)

        # Manually compute A + B and A - B (the Minkowski way) and show it.
        for Ap in Alist:
            for Bp in Blist:
                ax1.plot(Bp.x - Ap.x, Bp.y - Ap.y, '.', color=self.BLUE)
                ax1.plot(Bp.x + Ap.x, Bp.y + Ap.y, '.', color=self.BLUE)

        plt.show()

    def test_fast_Minkowski_sum(self):
        # Testing Minkowski sum.
        x = 8
        w = 4
        a = 3
        b = 10

        theta2 = 79

        p1 = [(0, 0), (a, 0), (a, b), (0, b), (0, 0)]
        A = affinity.translate(affinity.rotate(Polygon(p1), theta2, 'center'), 4, 2)
        p2 = [(0, 0), (w, 0), (w, x), (0, x), (0, 0)]

        theta_range = np.linspace(0, 360, 100)
        area = []
        fast_area = []
        for theta in theta_range:
            B = affinity.translate(affinity.rotate(Polygon(p2), theta, 'center'), 10, 5)
            Cs = self.Minkowski_sum_convex_polygons(A, B)
            area.append(Cs.area)
            fast_area.append(self.Minkowski_sum_convex_polygons_area(w, x, a, b, theta, theta2))

        fig = plt.figure(1, figsize=(18, 18), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(theta_range, area, label='True Minkowski sum area')
        ax.plot(theta_range, fast_area, '--', label='Fast computed Minkowski sum area')
        ax.legend()
        ax.set_xlabel(r"$\theta$ (deg)")
        plt.show()


