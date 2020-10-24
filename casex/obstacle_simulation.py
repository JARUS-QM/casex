"""
MISSING DOC
"""
import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from descartes.patch import PolygonPatch
from shapely import affinity
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.strtree import STRtree


class ObstacleSimulation:
    """MISSING DOC

    Attributes
    ----------
    MISSING DOC
    """

    def __init__(self, trial_area_sidelength):
        """Constructor
        
        Parameters
        ----------
        trial_area_sidelength : float
            [m] Length of each side of the square trial area
        """
        self.num_of_obstacles = None
        self.trials_count = None
        self.CA_width = None
        self.CA_length = None
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

        # Smallest distance before we consider two points the same point
        self.__epsilon = 0.0001

        # Some colors available for drawing obstacles and CAs
        self.BLUE = '#6699cc'
        self.GRAY = '#999999'
        self.DARKGRAY = '#333333'
        self.YELLOW = '#ffcc33'
        self.GREEN = '#339933'
        self.RED = '#ff3333'
        self.BLACK = '#000000'

    def generate_rectangular_obstacles_normal_distributed(self, num_of_obstacles, width_mu, width_sigma, length_mu,
                                                          length_sigma):
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        """
        self.num_of_obstacles = num_of_obstacles

        width = sp.stats.norm.rvs(size=num_of_obstacles, loc=width_mu, scale=width_sigma)
        length = sp.stats.norm.rvs(size=num_of_obstacles, loc=length_mu, scale=length_sigma)

        # Create a list of obstacle polygons
        trans_x = sp.stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)
        trans_y = sp.stats.uniform.rvs(size=self.num_of_obstacles, loc=0, scale=self.trial_area_sidelength)

        for k in range(0, num_of_obstacles):
            obs = [(0, 0), (length[k], 0), (length[k], width[k]), (0, width[k]), (0, 0)]
            self.obstacles.append(affinity.translate(Polygon(obs), trans_x[k], trans_y[k]))

    def generate_CAs(self, trials_count, CA_width, CA_length):
        """MISSING DOC

        Parameters
        ----------
        trials_count : int
            Number of trials to perform
        CA_width : float
            [m] Width of the nominal CA
        CA_length : float
            [m] Length of the nominal CA

        Returns
        -------
        """
        self.trials_count = trials_count
        self.CA_width = CA_width
        self.CA_length = CA_length

        # Compute reduction in the translation of the original CA. Since rotation is around the center,
        # the compensation is half the longest length of the CA.
        CA_compensate = np.amax([CA_width, CA_length]) / 2

        # Uniformly distributed heading from 0 to 180 degrees
        heading = sp.stats.uniform.rvs(size=self.trials_count, loc=0, scale=360)

        # Uniformly distributed translation from 0 to trial_area_sidelength.
        # We need to compensate for any CAs sticking out of the trial area, and thus cannot intersect obstacles.
        # We do this crudely by forcing the CAs to be sufficiently far from the edge of the trial area.
        CA_trans_x = sp.stats.uniform.rvs(size=self.trials_count, loc=CA_compensate,
                                          scale=self.trial_area_sidelength - 2 * CA_compensate)
        CA_trans_y = sp.stats.uniform.rvs(size=self.trials_count, loc=0,
                                          scale=self.trial_area_sidelength - 2 * CA_compensate)

        CA_coor = [(0, 0), (self.CA_width, 0), (self.CA_width, self.CA_length), (0, self.CA_length), (0, 0)]

        for j in range(0, self.trials_count):
            # Rotate and move CA
            CA_polygon = affinity.translate(affinity.rotate(Polygon(CA_coor), heading[j], 'center'), CA_trans_x[j],
                                            CA_trans_y[j])

            self.CAs.append(CA_polygon)

    def compute_reduced_CAs(self):
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        """
        self.CAs_reduced = []
        self.intersected_obstacles = []
        self.closest = []
        self.CA_cut_off_coords = []

        # Create STRtree for faster intersection detection
        self.obstacles_rtree = STRtree(self.obstacles)

        # Keep track of reduced obstacles
        reduced_CA_idxs = []

        for CA_idx, CA_polygon in enumerate(self.CAs):
            # Keep track of the starting coordinates of the original CA
            CA_original_coords = MultiPoint(CA_polygon.exterior.coords)

            # Get a short list of potentially intersecting obstacles
            potentially_intersecting_obstacles = self.obstacles_rtree.query(CA_polygon)

            # Iterate over those potential obstacles
            for idx, obstacle in enumerate(potentially_intersecting_obstacles):
                # Check if it intersects any of the obstacles
                if CA_polygon.intersects(obstacle):

                    # Check if this obstacles has already been reduced once
                    if CA_idx not in reduced_CA_idxs:
                        self.num_of_reduced_CA = self.num_of_reduced_CA + 1
                        reduced_CA_idxs.append(CA_idx)

                    # Keep a list of the intersected obstacles for later viz
                    self.intersected_obstacles.append(obstacle)

                    # Figure out how much is left of the CA
                    # If the beginning of the CA is inside the obstacle, the CA becomes empty
                    CA_beginning_line = LineString([(CA_original_coords[0].x, CA_original_coords[0].y),
                                                    (CA_original_coords[1].x, CA_original_coords[1].y)])
                    if CA_beginning_line.intersects(obstacle):
                        CA_polygon = Polygon()
                        self.num_of_empty_CA = self.num_of_empty_CA + 1

                        # And we can save a little time by breaking the for loop at this point,
                        # since the CA is reduced as much as it can be, so no need to check more obstacles
                        break
                    else:
                        # First, subtract the obstacle from the CA
                        CA_splitted = CA_polygon.difference(obstacle)

                        # If the obstacles splits the CA in multiple polygons, figure out which part we need
                        # (i.e. the one closest to the CA origin)
                        if CA_splitted.geom_type == 'MultiPolygon':
                            dist = 10 * self.trial_area_sidelength  # Just a number sufficiently big

                            # Iterate over all resulting polygons after splitting the CA
                            for CA_split in CA_splitted:

                                # Look for the one where the distance to the beginning of the CA is (very close to) zero
                                if (CA_split.distance(CA_original_coords[0]) < self.__epsilon) | (
                                        CA_split.distance(CA_original_coords[1]) < self.__epsilon):
                                    CA_polygon = CA_split
                                    break

                        # The splitting of CA only resulting in one polygon            
                        else:
                            CA_polygon = CA_splitted

                        # After splitting the CA, it is most likely not a rectangle anymore, but we want that.
                        # So, we find all the coordinates of the split CA that were not in the original CA
                        # and that the one closest to the beginning of the CA (called p_closest)
                        # When we compute a new CA polygon consisting of p_closest and the two points at the beginning
                        # of the CA, plus a fourth point that make the polygon a rectangle
                        CA_polygon = self.__cut_polygon_to_rectangle(CA_polygon, CA_original_coords)

            # Add the resulting CA polygon to the list of reduced CAs
            self.CAs_reduced.append(CA_polygon)

    def __cut_polygon_to_rectangle(self, CA_polygon, CA_original_coords):
        """
        Create a rectangular polygon that has the same beginning side as the original CA polygon

        This function finds all the coordinates of the non-rectangular (split) CA that were not in the original CA
        and the one closest to the beginning of the CA (called p_closest) will be used for creating the rectangle.
        When we compute a new CA polygon consisting of p_closest and the two points at the beginning
        of the CA, plus a fourth point that make the polygon a rectangle
        """
        # Get the coordinates of the input polygon as Points
        CA_reduced_polygon_coords = MultiPoint(CA_polygon.exterior.coords)

        # Initialize with a sufficiently big number
        dist = 10 * self.trial_area_sidelength

        # Initialize what point to keep
        p_closest = CA_reduced_polygon_coords[0]

        # Iterate over the points in the reduced polygon
        for p in CA_reduced_polygon_coords:

            # Distance to the two coordinates at the beginning of the CA
            d0 = CA_original_coords[0].distance(p)
            d1 = CA_original_coords[1].distance(p)

            # If p is one of the two original coordinates, move to next for iteration
            if (d0 < self.__epsilon) | (d1 < self.__epsilon):
                continue

            if d0 < dist:
                p_closest = p
                dist = d0

            if d1 < dist:
                p_closest = p
                dist = d1

        # Figure out the fourth point in the rectangle
        # 1. Conceptually make a line through p_keep parallel to a line through the two CA coords at the CA beginning,
        #    and find the distance between these two lines
        # 2. Pick the two points on this line closest to the two CA coords at the CA beginning.

        # Initial computations
        x = CA_original_coords[1].x - CA_original_coords[0].x
        y = CA_original_coords[1].y - CA_original_coords[0].y

        # This should be equal to w, but just in case
        d = CA_original_coords[0].distance(CA_original_coords[1])

        # Do the check again w
        if np.abs(d - self.CA_width) > 10 * self.__epsilon:
            warnings.warn("Distance  between two CA beginning points not equal to width. "
                          "This is an internal warning showing inconsistency.")

        ### Compute step 1
        # Distance from beginning of CA to the closest point
        dist = np.abs(
            y * p_closest.x - x * p_closest.y + CA_original_coords[1].x * CA_original_coords[0].y - CA_original_coords[
                1].y * CA_original_coords[0].x) / d

        # Make this distance a smidging shorter to avoid CA still slightly overlapping obstacle
        dist = dist - 100 * self.__epsilon

        # Compute step 2
        # Find the two points in addition to the two CA beginning points
        point1 = Point(-y / d * dist + CA_original_coords[0].x, x / d * dist + CA_original_coords[0].y)
        point2 = affinity.translate(point1, x, y)

        # Record the points for debugging/viz purposes
        self.closest.append(p_closest)
        self.CA_cut_off_coords.append(point1)
        self.CA_cut_off_coords.append(point2)

        # Generate a new rectangular polygon from the four points
        CA_polygon = Polygon(
            [[CA_original_coords[0].x, CA_original_coords[0].y], [CA_original_coords[1].x, CA_original_coords[1].y],
             [point2.x, point2.y], [point1.x, point1.y]])

        # Return the new rectangular polygon
        return CA_polygon

    def compute_CA_lengths(self):
        """Make a list of the actual lengths of the CAs.

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        """
        self.CA_lengths = []
        for CAr in self.CAs_reduced:
            if CAr.is_empty:
                self.CA_lengths.append(0)
            else:
                x, y = CAr.exterior.coords.xy
                self.CA_lengths.append(np.sqrt((x[1] - x[2]) * (x[1] - x[2]) + (y[1] - y[2]) * (y[1] - y[2])))

    def compute_coverage(self):
        """Determine total obstacle coverage

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
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
        MISSING DOC

        Returns
        -------
        """
        intersection_area = 0

        # Return all found overlapping polygons
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
        MISSING DOC

        Returns
        -------
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
        MISSING DOC

        Returns
        -------
        """
        F = 1
        if show_CA_as_size:
            F = self.CA_width

        num_bins = int(round(4 * np.sqrt(self.trials_count)))
        bins = np.linspace(0, self.CA_length * F, num_bins)

        ax.hist(np.array(self.CA_lengths) * F, bins, density=True, histtype='step', cumulative=True,
                label="Simulated {:1.0f} trials".format(self.trials_count), edgecolor='black', linewidth=1.5)

        if not show_CA_as_size:
            ax.set_xlabel('Length of CA [m]')
        else:
            ax.set_xlabel('Size of CA [m^2]')

        ax.set_ylabel('Accumulated fraction of total')

    @staticmethod
    def set_limits(ax, x0, xN, y0, yN, step=1):
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        """
        ax.set_xlim(x0, xN)
        ax.set_xticks(range(x0, xN + 1, step))
        ax.set_ylim(y0, yN)
        ax.set_yticks(range(y0, yN + 1, step))
        ax.set_aspect("equal")

    @staticmethod
    def Minkowski_sum_convex_polygons(A, B):
        """Compute the polygon that is the Minkowski sum of two convex polygons A and B.

        The result is returned as a MultiPoint type

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        MISSING DOC
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
    def Minkowski_sum_convex_polygons_area(w, x, a, b, theta, theta2):
        """Compute the area of the Minkowski sum of two rectangles polygons
        
        Parameters
        -----------
        w : float
            Width of rectangle 1
        x : float
            Length of rectangle 1
        a : float
            Width of rectangle 2
        b : float
            Length of rectangle 2
        theta : float
            [deg] Angle of rectangle 1
        theta2 : float
            [deg] Angle of rectangle 2
                
        Returns
        -------
        area : float
            Area of the Minkowski sum of the two rectangles
        """
        Ct = abs(math.cos(np.radians(theta - theta2)))
        St = abs(math.sin(np.radians(theta - theta2)))

        return w * x + a * b + w * abs(a * St + b * Ct) + x * abs(a * Ct + b * St)

    @staticmethod
    def Minkowski_difference_convex_polygons(A, B):
        """Compute the polygon that is the Minkowski difference of two convex polygons A and B.

        The result is returned as a MultiPoint type

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        MISSING DOC
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
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        coords = polygon.exterior.coords
        print(coords[0])

        m = Polygon([(-c[0], -c[1]) for c in coords])

        return m

    def first_pdf(self, x, obstacle_density, obstacle_width_mu, obstacle_width_sigma, obstacle_length_mu,
                  obstacle_length_sigma, pdf_resolution):
        """MISSING DOC

        Parameters
        ----------
        MISSING DOC

        Returns
        -------
        MISSING DOC
        """
        # Sample the obstacle PDF
        width = np.linspace(obstacle_width_mu - 3 * obstacle_width_sigma, obstacle_width_mu + 3 * obstacle_width_sigma,
                            pdf_resolution)
        length = np.linspace(obstacle_length_mu - 3 * obstacle_length_sigma,
                             obstacle_length_mu + 3 * obstacle_length_sigma, pdf_resolution)
        CA_orientation = np.linspace(0, 360 - 360 / pdf_resolution, pdf_resolution)

        pdf_width = sp.stats.norm(obstacle_width_mu, obstacle_width_sigma).pdf(width)
        pdf_length = sp.stats.norm(obstacle_length_mu, obstacle_length_sigma).pdf(length)
        pdf_CA_orientation = sp.stats.uniform(0, 360).pdf(CA_orientation)

        # Compute the step length for the integral computation
        pdf_width_step = (width[-1] - width[0]) / (pdf_resolution - 1)
        pdf_length_step = (length[-1] - length[0]) / (pdf_resolution - 1)
        pdf_CA_orientation_step = (CA_orientation[-1] - CA_orientation[0]) / (pdf_resolution - 1)

        x_resolution = len(x)

        # Preset p_x
        p_x = np.zeros(x_resolution)

        acc_probability_check = 0

        for idx_x, x_val in enumerate(x):
            # Reset acc for integral        
            accumulator = 0

            CA_polygon = Polygon([(0, 0), (self.CA_width, 0), (self.CA_width, x_val), (0, x_val), (0, 0)])

            for idx_orientation, orientation_val in enumerate(CA_orientation):
                CA_polygon = affinity.rotate(CA_polygon, orientation_val, 'center', use_radians=False)

                for index_w, w in enumerate(width):
                    for index_l, l in enumerate(length):
                        if False:
                            obstacle = Polygon([(0, 0), (w, 0), (w, l), (0, l), (0, 0)])
                            M = self.Minkowski_sum_convex_polygons(CA_polygon, obstacle)
                            area = M.area
                        else:
                            area = self.Minkowski_sum_convex_polygons_area(self.CA_width, x_val, w, l, orientation_val,
                                                                           0)
                        p_width = pdf_width[index_w] * pdf_width_step
                        p_length = pdf_length[index_l] * pdf_length_step
                        p_orientation = pdf_CA_orientation[idx_orientation] * pdf_CA_orientation_step
                        accumulator = accumulator + area * p_width * p_length * p_orientation
                        acc_probability_check = acc_probability_check + p_width * p_length * p_orientation

            p_x[idx_x] = 1 - np.exp(-obstacle_density * accumulator)

        acc_probability_check = acc_probability_check / x_resolution

        return p_x, acc_probability_check

    def test1_Minkowski_sum(self):
        # Testing Minkowski sum
        p1 = [(0, 0), (3, 0), (3, 10), (0, 0)]
        A = affinity.translate(affinity.rotate(Polygon(p1), 35, 'center'), 4, 2)
        p2 = [(0, 0), (4, 0), (4, 8), (0, 8), (0, 0)]
        B = affinity.translate(affinity.rotate(Polygon(p2), 79, 'center'), 10, 5)
        Cs = OS.Minkowski_sum_convex_polygons(B, A)
        Cd = OS.Minkowski_difference_convex_polygons(B, A)
        fig = plt.figure(1, figsize=SIZE, dpi=90)
        ax1 = fig.add_subplot(121)
        ax1.add_patch(PolygonPatch(A, facecolor='#ff0000', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(B, facecolor='#00ff00', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cs, facecolor='#0000ff', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd, facecolor='#00ffff', edgecolor='#000000', alpha=0.5, zorder=10))
        Am = OS.mirror_polygon_in_origin(A)
        ax1.add_patch(PolygonPatch(Am, facecolor='#44ff99', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.grid()
        self.set_limits(ax1, -30, 30, -30, 30, 10)
        plt.show()

    def test2_Minkowski_sum(self):
        # Testing Minkowski sum
        p1 = [(0, 0), (3, 0), (3, 10), (0, 0)]
        A = affinity.translate(affinity.rotate(Polygon(p1), 35, 'center'), 4, 2)
        p2 = [(0, 0), (4, 0), (4, 8), (0, 8), (0, 0)]
        B = affinity.translate(affinity.rotate(Polygon(p2), 79, 'center'), 10, 5)
        Cd1 = self.Minkowski_sum_convex_polygons(A, B)
        Cd2 = self.Minkowski_difference_convex_polygons(A, B)
        fig = plt.figure(1, figsize=(18, 18), dpi=90)
        ax1 = fig.add_subplot(111)
        ax1.add_patch(PolygonPatch(A, facecolor='#ff0000', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(B, facecolor='#00ff00', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd1, facecolor='#0000ff', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.add_patch(PolygonPatch(Cd2, facecolor='#00ffff', edgecolor='#000000', alpha=0.5, zorder=10))
        ax1.grid()
        self.set_limits(ax1, -30, 30, -10, 30, 10)

        Ax, Ay = A.exterior.coords.xy
        Bx, By = B.exterior.coords.xy

        res = 10
        Ax_sample = np.linspace(np.amin(Ax), np.amax(Ax), res)
        Ay_sample = np.linspace(np.amin(Ay), np.amax(Ay), res)
        Bx_sample = np.linspace(np.amin(Bx), np.amax(Bx), res)
        By_sample = np.linspace(np.amin(By), np.amax(By), res)

        Alist = []
        for Axv in Ax_sample:
            for Ayv in Ay_sample:
                if A.contains(Point(Axv, Ayv)):
                    Alist.append(Point(Axv, Ayv))

        for k, p in enumerate(Ax):
            Alist.append(Point(Ax[k], Ay[k]))

        Blist = []
        for Bxv in Bx_sample:
            for Byv in By_sample:
                if B.contains(Point(Bxv, Byv)):
                    Blist.append(Point(Bxv, Byv))

        for k, p in enumerate(Bx):
            Blist.append(Point(Bx[k], By[k]))

        C = []
        Anew = True
        for Ap in Alist:
            ax1.plot(Ap.x, Ap.y, '.', color='#ff0000')
            for Bp in Blist:
                if Anew:
                    ax1.plot(Bp.x, Bp.y, '.', color='#00ff00')

                ax1.plot(Ap.x - Bp.x, Ap.y - Bp.y, '.', color='#00ffff')
                ax1.plot(Ap.x + Bp.x, Ap.y + Bp.y, '.', color='#0000ff')
                # C.append(Point(Ax_sample[k] - Bx_sample[k], Ay_sample[k] - By_sample[k]))
            Anew = False

        plt.show()

    def test3_Minkowski_sum(self):
        # Testing Minkowski sum
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
        
#            Ct = abs(math.cos(np.radians(theta-theta2)))
#            St = abs(math.sin(np.radians(theta-theta2)))
#            tmp = w*x + a*b + w*abs(a*St + b*Ct) + x * abs(a*Ct + b*St)
#            fast_area.append(tmp)
            fast_area.append(self.Minkowski_sum_convex_polygons_area(w, x, a, b, theta, theta2))        
        
        fig = plt.figure(1, figsize=(18,18), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(theta_range, area, label='True Minkowski sum area')
        ax.plot(theta_range, fast_area, '--', label='Fast computed Minkowski sum area')
        ax.legend()
        ax.set_xlabel(r"$\theta$ (deg)")
        plt.show()

        fig.savefig('test3_out.png', format='png', dpi=300)

    def _self_test(self):
        """Runs a test on all implemented functions. Debug function.
        
        This function can be use to perform a self test of all functions.
        The purpose it make sure that there are no obvious code errors.
        It does not check for equation errors.
        It is not exhaustive, but gives a good indication.
        """
