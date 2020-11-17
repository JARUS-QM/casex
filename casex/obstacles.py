"""
MISSING DOC
"""
import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from scipy import interpolate
from descartes.patch import PolygonPatch
from shapely import affinity
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.strtree import STRtree


class Obstacles:
    """MISSING DOC

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

    def __init__(self, CA_width, CA_length, trial_area_sidelength):
        """Constructor
        
        Parameters
        ----------
        CA_width : float
            [m] Width of the nominal CA.
        CA_length : float
            [m] Length of the nominal CA.
        trial_area_sidelength : float
            [m] Length of each side of the square trial area.
        """
        self.CA_width = CA_width
        self.CA_length = CA_length
        self.trials_count = None
        self.num_of_obstacles = None
        self.intersected_obstacles = None
        self.closest = None
        self.CA_cut_off_coords = None
        self.obstacles_rtree = None
        self.CA_lengths = None
        self.total_obstacle_area = None
        self.total_coverage = None

        self.trial_area_sidelength = trial_area_sidelength

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
        self.YELLOW = '#ffcc33'
        self.GREEN = '#339933'
        self.RED = '#ff3333'
        self.BLACK = '#000000'

    def generate_rectangular_obstacles_normal_distributed(self, num_of_obstacles, width_mu, width_sigma, length_mu,
                                                          length_sigma):
        """Generate a set of uniformly distributed rectangular obstacles.
        
        This method generates a number of rectangular obstacles which a co-linear with the axes, and with width and length
        varying according to normal distributions with the mean and standard deviation as given by input parameters. The position
        of the obstacles are uniformly distributed in 2D in the trial area.

        Parameters
        ----------
        num_of_obstacles : int
            The number of obstacles to generate.
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
        self.num_of_obstacles = num_of_obstacles

        width = stats.norm.rvs(size=num_of_obstacles, loc=width_mu, scale=width_sigma)
        length = stats.norm.rvs(size=num_of_obstacles, loc=length_mu, scale=length_sigma)

        # Create a list of obstacle polygons.
        trans_x = stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)
        trans_y = stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)

        for k in range(0, num_of_obstacles):
            obs = [(0, 0), (length[k], 0), (length[k], width[k]), (0, width[k]), (0, 0)]
            self.obstacles.append(affinity.translate(Polygon(obs), trans_x[k], trans_y[k]))

    def generate_rectangular_obstacles_along_curves(self, width_mu, width_sigma, length_mu, length_sigma, houses_along_street, rows_of_houses, distance_between_two_houses):
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
            [m] The distance between two houses that make up the pair of houses that shares a common border, but are on two different streets (20 m is a good starting number).

        Returns
        -------
        None
        """
        # Number of rows of houses per side length. This is expanded to cover the entire area (because the rows are curved)
        rows_of_houses = 12
        rows_of_houses = round(rows_of_houses * 1.25)

        # Distance between two houses in each set of houses (neighbouring houses from separate streets)
        distance_between_two_houses = 20
        
        self.num_of_obstacles = houses_along_street * 2 * rows_of_houses

        width = stats.norm.rvs(size=self.num_of_obstacles, loc=width_mu, scale=width_sigma)
        length = stats.norm.rvs(size=self.num_of_obstacles, loc=length_mu, scale=length_sigma)

        # Points to create a curvy road
        x_points = np.linspace(0, 1000, 11)
        y_points = np.array([10, 40, 80, 100, 80, 50, 80, 120, 150, 210, 270])
        coefs = interpolate.splrep(x_points, y_points)

        # Compute position and rotation of houses
        x = np.linspace(0, 1000, houses_along_street)
        y = np.linspace(-250, 1000, rows_of_houses)
        x2 = np.full(houses_along_street, 1000 / (houses_along_street + 1))
        y2 = np.diff(interpolate.splev(x, coefs), prepend = -10)
        r = []
        for k in range(22):
            r.append(-math.atan2(y2[k], x2[k]) * 180 / math.pi)

        # Add houses, only those inside the trial area
        counter = 0
        for j in range(0, rows_of_houses):
            for k in range(0, houses_along_street):
                trans_x = interpolate.splev(x[k], coefs) + y[j]
                trans_y = x[k]
                if (trans_x > 0 and trans_y > 0 and trans_x < self.trial_area_sidelength and trans_y < self.trial_area_sidelength):
                    obs = [(0, 0), (length[counter], 0), (length[counter], width[counter]), (0, width[counter]), (0, 0)]
                    self.obstacles.append(affinity.translate(affinity.rotate(Polygon(obs), r[k]), trans_x, trans_y))
                counter = counter + 1
                trans_x = trans_x + distance_between_two_houses
                if (trans_x > 0 and trans_y > 0 and trans_x < self.trial_area_sidelength and trans_y < self.trial_area_sidelength):
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

    def compute_reduced_CAs(self):
        """Compute the reduction for each CA
        
        Any CA that intersects with an obstacles is reduced such as to no longer intersect with any obstacles. This method
        runs through all CAs and all obstacles and produces a list of CAs that

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

                                # Look for the one where the distance to the beginning of the CA is (very close to) zero
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
        of the CA, plus a fourth point that make the polygon a rectangle
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
            warning("Sanity check fail for number of empty CAs.")

    def compute_coverage(self):
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
            area = self.obstacles[k].area
            self.total_obstacle_area = self.total_obstacle_area + area
            self.total_coverage = self.total_coverage + area
            for j in range(k + 1, self.num_of_obstacles):
                if self.obstacles[k].intersects(self.obstacles[j]):
                    self.total_coverage = self.total_coverage - self.obstacles[k].intersection(self.obstacles[j]).area

    def sanity_check(self):
        """Conduct sanity check: No overlapping between any obstacle and any reduced CA.

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
            for o in potentially_intersecting_obstacles:
                if o.intersects(CAr):
                    intersection_area = intersection_area + o.intersection(CAr).area
                    problematic_obstacles.append(o)
                    problematic_CAs.append(CAr)

        return intersection_area, problematic_obstacles, problematic_CAs

    def show_simulation(self, ax, **options):
        """MISSING DOC

        Parameters
        ----------
        ax : MISSING DOC
            MISSING DOC
        options : MISSING DOC
            MISSING DOC

        Returns
        -------
        None
        """
        # Viz all the original CAs
        if options.get("CAs") == "True":
            for CA in self.CAs:
                x, y = CA.exterior.coords.xy
                ax.plot(x, y, '-', color=self.BLACK, linewidth=0.25)
                if options.get("CA_first_point") == "True":
                    ax.plot(x[0], y[0], 'o', color=self.BLACK)

        if options.get("CAs_reduced") == "True":
            for CAr in self.CAs_reduced:
                if not CAr.is_empty:
                    ax.add_patch(
                        PolygonPatch(CAr, facecolor='#6600cc', edgecolor=self.RED, alpha=1, zorder=3, linewidth=0.25))

        if options.get("obstacles_original") == "True":
            for o in self.obstacles:
                ax.add_patch(
                    PolygonPatch(o, facecolor='#00ff00', edgecolor='#000000', alpha=1, zorder=2, linewidth=0.25))

        if options.get("obstacles_intersected") == "True":
            for o in self.intersected_obstacles:
                ax.add_patch(
                    PolygonPatch(o, facecolor='#ff8800', edgecolor='#000000', alpha=1, zorder=2, linewidth=0.25))

        if options.get("debug_points") == "True":
            for p in self.closest:
                ax.plot(p.x, p.y, 'o', color='#ffff00')

            for p in self.CA_cut_off_coords:
                ax.plot(p.x, p.y, 'x', color='#00ffff', zorder=5)

        self.set_limits(ax, -100, self.trial_area_sidelength + 100, -100, self.trial_area_sidelength + 100, 100)
        ax.set_xlabel('Size [m]')
        ax.set_ylabel('Size [m]')
        ax.grid()

    def show_CDF(self, ax, show_CA_as_size):
        """MISSING DOC

        Parameters
        ----------
        ax : MISSING DOC
            MISSING DOC
        show_CA_as_size : MISSING DOC
            MISSING DOC

        Returns
        -------
        None
        """
        F = 1
        if show_CA_as_size:
            F = self.CA_width

        num_bins = int(round(4 * np.sqrt(self.trials_count)))

        ax.hist(np.array(self.CA_lengths) * F, num_bins, density=True, histtype='step', cumulative=True,
                label="Simulated {:1.0f} trials".format(self.trials_count), edgecolor='black', linewidth=1.5)

        if not show_CA_as_size:
            ax.set_xlabel('Length of CA [m]')
        else:
            ax.set_xlabel('Size of CA [m^2]')

        ax.set_ylabel('Accumulated fraction of total')

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
        
        For details on how this is done, see [lacour2021].
        
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

        C = MultiPoint(Cv).convex_hull

        return C

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
        coords = polygon.exterior.coords
        print(coords[0])

        mirrored = Polygon([(-c[0], -c[1]) for c in coords])

        return mirrored

    def cdf(self, x, obstacle_density, obstacle_width_mu, obstacle_width_sigma, obstacle_length_mu,
                  obstacle_length_sigma, pdf_resolution):
        """Compute the CDF for the length of the critical area when rectangular obstacles are present.
        
        This is the CDF for the length of the critical area when there are a given obstacle density of rectangular obstacles with
        dimension given by normal distributions. To draw the full CDF, a typical input for x is an array ranging in value from
        0 to the nominal length of the CA. Since this is usually a rather smooth curve, it can be approximated well by relatively
        few x values (typically 10 or 15).
        
        For a more detailed explanation of the CDF, see [lacour2021]. MISSING DOC.

        Parameters
        ----------
        x : (List of) float(s)
            [m] The length of the critical area for which the CDF is computed. This can be a scalar or an array.
        obstacle_density : float
            [1/m^2] The density of obstacles measured as the number of obstacles per square meter. Note that in many cases, the obstacles density is
            given as obstacles per square kilometer. If so, the user must take care to divide by 1e6 before using this method.
        obstacle_width_mu : float
            The mean of the normal distribution of the width of the obstacles.
        obstacle_width_sigma : float
            The standard deviation of the normal distribution of the width of the obstacles.
        obstacle_length_mu : float
            The mean of the normal distribution of the length of the obstacles.
        obstacle_length_sigma : float
            The standard deviation of the normal distribution of the length of the obstacles.
        pdf_resolution : int
            The number of points for the discretization of the integrals. A good starting value is 15.

        Returns
        -------
        p_x : (List of) float(s)
            The CDF value for the given x. This return parameter has the same type as input x.
        beta : float
            The beta values as computed in [lacour2021]. MISSING DOC
        acc_probability_check : float
            A sanity check on the triple integral. This values should be relatively close to 1, especially for high value of pdf_resolution.
        """
        # Sample the obstacle PDF.
        width = np.linspace(obstacle_width_mu - 3 * obstacle_width_sigma, obstacle_width_mu + 3 * obstacle_width_sigma,
                            pdf_resolution)
        length = np.linspace(obstacle_length_mu - 3 * obstacle_length_sigma,
                             obstacle_length_mu + 3 * obstacle_length_sigma, pdf_resolution)
        CA_orientation = np.linspace(0, 360 - 360 / pdf_resolution, pdf_resolution)

        pdf_width = stats.norm(obstacle_width_mu, obstacle_width_sigma).pdf(width)
        pdf_length = stats.norm(obstacle_length_mu, obstacle_length_sigma).pdf(length)
        pdf_CA_orientation = stats.uniform(0, 360).pdf(CA_orientation)

        # Compute the step length for the integral computation.
        pdf_width_step = (width[-1] - width[0]) / (pdf_resolution - 1)
        pdf_length_step = (length[-1] - length[0]) / (pdf_resolution - 1)
        pdf_CA_orientation_step = (CA_orientation[-1] - CA_orientation[0]) / (pdf_resolution - 1)

        # The assumption is that the input is a list, so if it is scalar, change it to a list
        if not isinstance(x, np.ndarray):
            x = np.array([x])

        x_resolution = len(x)

        # Preset p_x.
        p_x = np.zeros(x_resolution)

        acc_probability_check = 0

        beta_acc = 0

        for idx_x, x_val in enumerate(x):
            # Reset acc for integral.
            accumulator = 0

            CA_polygon = Polygon([(0, 0), (self.CA_width, 0), (self.CA_width, x_val), (0, x_val), (0, 0)])

            for idx_orientation, orientation_val in enumerate(CA_orientation):
                CA_polygon = affinity.rotate(CA_polygon, orientation_val, 'center', use_radians=False)

                for index_w, w in enumerate(width):
                    for index_l, l in enumerate(length):
                        minkowski_area = self.Minkowski_sum_convex_polygons_area(self.CA_width, x_val, w, l,
                                                                                     orientation_val, 0)
                        p_width = pdf_width[index_w] * pdf_width_step
                        p_length = pdf_length[index_l] * pdf_length_step
                        p_orientation = pdf_CA_orientation[idx_orientation] * pdf_CA_orientation_step
                        accumulator = accumulator + minkowski_area * p_width * p_length * p_orientation
                        acc_probability_check = acc_probability_check + p_width * p_length * p_orientation

                        # Compute beta (does not depend on x and orient, so only need to compute once).
                        if idx_x == 0 and idx_orientation == 0:
                            beta_acc = beta_acc + w * l * p_width * p_length

            p_x[idx_x] = 1 - np.exp(-obstacle_density * accumulator)

        beta = 1 - np.exp(-obstacle_density * beta_acc)

        # Divide to account for the accumulator is not reset in the above outer loop.
        acc_probability_check = acc_probability_check / x_resolution

        return p_x, beta, acc_probability_check

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
        ax1.add_patch(PolygonPatch(A, facecolor='#ff0000', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(B, facecolor='#00ff00', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd1, facecolor='#0000ff', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd2, facecolor='#00ffff', edgecolor='#000000', alpha=0.5, zorder=10))
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
            ax1.plot(Ap.x, Ap.y, '.', color='#ff0000')
        for Bp in Blist:
            ax1.plot(Bp.x, Bp.y, '.', color='#00ff00')

        # Manually compute A + B and A - B (the Minkowski way) and show it.
        for Ap in Alist:
            for Bp in Blist:
                ax1.plot(Bp.x - Ap.x, Bp.y - Ap.y, '.', color='#00ffff')
                ax1.plot(Bp.x + Ap.x, Bp.y + Ap.y, '.', color='#0000ff')

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
