"""
MISSING DOC
"""
import time

import matplotlib.pyplot as plt
import numpy as np
from descartes.patch import PolygonPatch
from shapely.geometry import Polygon

from casex import Obstacles

def obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        trials_count = 1000,
                        trial_area_sidelength = 1000,
                        obstacle_width_mu = 17,
                        obstacle_width_sigma = 3,
                        obstacle_length_mu = 8,
                        obstacle_length_sigma = 2,
                        CDF_x_resolution = 100,
                        compute_coverage = True,
                        do_problematic_check = True,
                        do_model_CDF = True,
                        model_CDF_high_res = False,
                        visualize_obstacles = True,
                        visualize_CDF = True,
                        show_CAs = True,
                        show_CA_first_point = True,
                        show_CAs_reduced = True,
                        show_obstacles = True,
                        show_obstacles_intersected = True,
                        show_CA_as_size = True,
                        show_legends = True,
                        do_houses_along_roads = False,
                        viz_obstacle_zoom = None,
                        random_generator_seed = None,
                        save_file_name = None):
    """MISSING DOC

    Parameters
    ----------

    Returns
    -------
    None
    """
    start_time = time.time()

    np.random.seed(random_generator_seed)

    OS = Obstacles(CA_width, CA_length, num_of_obstacles, trial_area_sidelength)

    gen_polygons_time = time.time()
    print('Generate polygons time:   ', end='', flush=True)
    if do_houses_along_roads:
        houses_along_street = 30
        rows_of_houses = 15
        distance_between_two_houses = 20
        OS.generate_rectangular_obstacles_along_curves(obstacle_width_mu, obstacle_width_sigma, obstacle_length_mu,
                                                       obstacle_length_sigma, houses_along_street, rows_of_houses,
                                                       distance_between_two_houses)
    else:
        OS.generate_rectangular_obstacles_normal_distributed(obstacle_width_mu, obstacle_width_sigma,
                                                             obstacle_length_mu, obstacle_length_sigma)

    OS.generate_CAs(trials_count)
    print('{:1.1f} sec'.format(time.time() - gen_polygons_time), flush=True)

    # Run trials.
    intersection_time = time.time()
    print('Intersection time:        ', end='', flush=True)
    OS.compute_reduced_CAs()
    OS.compute_CA_lengths()
    print('{:1.1f} sec'.format(time.time() - intersection_time), flush=True)

    # Determine coverage.
    print('Coverage time:            ', end='', flush=True)
    if compute_coverage:
        coverage_time = time.time()
        OS.compute_coverage()
        print('{:1.1f} sec'.format(time.time() - coverage_time), flush=True)
    else:
        print('Not computed', flush=True)

    # Do sanity check (basically checking if the probelmatic areas are sufficiently small)
    print('Problematic obstacles:    ', end='', flush=True)
    if do_problematic_check:
        problematic_check_time = time.time()
        problematic_area, problematic_obstacles, problematic_CAs = OS.missed_obstacle_CA_intersections()
        print('{:1.1f} sec'.format(time.time() - problematic_check_time), flush=True)
    else:
        problematic_obstacles = None
        problematic_CAs = None
        print('Not computed')

    # Compute the probability based on theory.
    print('Theory time:              ', end='', flush=True)
    if do_model_CDF:
        theory_time = time.time()
        x = np.linspace(0, CA_length, CDF_x_resolution)

        if model_CDF_high_res:
            pdf_resolution = 25
        else:
            pdf_resolution = 15

        p_x, EX, beta_analytical, acc_probability_check = OS.cdf(x, pdf_resolution)
        print('{:1.1f} sec'.format(time.time() - theory_time), flush=True)

        if compute_coverage:
            beta_numerical = OS.total_coverage / OS.trial_area_sidelength / OS.trial_area_sidelength
    else:
        print('Not computed')

    # Create figure for visual output.
    print('Visualization time:       ', end='', flush=True)
    if visualize_obstacles or visualize_CDF:
        viz_time = time.time()

        # Set font size on plots
        if visualize_obstacles and visualize_CDF:
            plt.rcParams.update({'font.size': 18})
        else:
            plt.rcParams.update({'font.size': 18})

        fig = plt.figure(1, figsize=(20, 12), dpi=90)

        # Logic to create the appropriate subplots.
        if visualize_obstacles and visualize_CDF:
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
        elif visualize_obstacles and (not visualize_CDF):
            ax1 = fig.add_subplot(111)
        elif (not visualize_obstacles) and visualize_CDF:
            ax2 = fig.add_subplot(111)

        if visualize_obstacles:
            OS.show_simulation(ax1, 
                               problematic_obstacles = problematic_obstacles,
                               problematic_CAs = problematic_CAs,
                               show_CAs = show_CAs, 
                               show_CAs_reduced = show_CAs_reduced, 
                               show_obstacles = show_obstacles,
                               show_obstacles_intersected = show_obstacles_intersected, 
                               show_CA_first_point = show_CA_first_point)

            # If there is request for zoom in this axis.
            if viz_obstacle_zoom is not None:
                ax1.set_xlim(viz_obstacle_zoom[0])
                ax1.set_ylim(viz_obstacle_zoom[1])
    
        if visualize_CDF:
            OS.show_CDF(ax2, 
                        show_CA_as_size = show_CA_as_size, 
                        line_color = 'blue', 
                        line_width = 2.5, 
                        line_label = 'Simulated CDF')

        print('{:1.1f} sec'.format(time.time() - viz_time), flush=True)
    else:
        print('None', flush=True)

    print('Total time:               {:1.1f} sec'.format(time.time() - start_time))

    print('---------------------------')

    print('Original CA:              {:1.0f} m^2'.format(OS.CA_length * OS.CA_width))
    print('Average reduced CA:       {:1.1f} m^2 ({:d}%)'.format(np.mean(OS.CA_lengths) * OS.CA_width, int(
        round(100 * np.mean(OS.CA_lengths) / OS.CA_length))))
    if do_model_CDF:
        print('Analytical reduced CA     {:1.1f} m^2'.format(EX * OS.CA_width))
    else:
        print('Analytical reduced CA     Not computed')

    print('---------------------------')
    print('Number of CA reduced:     {:d}   ({:d}%)'.format(OS.num_of_reduced_CA,
                                                           int(round(100 * OS.num_of_reduced_CA / OS.trials_count))))
    print('Number of CA empty:       {:d}   ({:d}%)'.format(OS.num_of_empty_CA,
                                                           int(round(100 * OS.num_of_empty_CA / OS.trials_count))))
    print('Obstacle density:         {:1.0f} #/km^2'.format(OS.obstacle_density() * 1E6))

    if compute_coverage:
        print('Obstacle total area:      {:1.0f} m^2'.format(OS.total_obstacle_area))
        print('Obstacle coverage (num):  {:1.0f} m^2'.format(OS.total_coverage))
        print('Obstacle coverage (ana):  {:1.0f} m^2 '.format(
            OS.num_of_obstacles * obstacle_width_mu * obstacle_length_mu))
        print('Obstacle coverage ratio:  {:1.3f}'.format(OS.total_coverage / OS.total_obstacle_area))
    else:
        print('Obstacle total area:      Not computed')
        print('Obstacle coverage (num):  Not computed')
        print('Obstacle coverage (ana):  Not computed')
        print('Coverage ratio:           Not computed')

    if do_model_CDF:
        if compute_coverage:
            print('beta (numerical):         {:1.5f}'.format(beta_numerical))
        else:
            print('beta (numerical):         Not computed')
        print('beta (analytical):        {:1.5f}'.format(beta_analytical))
        print('PDF sanity check:         {:1.3f} (should be close to 1)'.format(acc_probability_check))
    else:
        print('beta (numerical):         Not computed')
        print('beta (analytical):        Not computed')
        print('PDF sanity check:         Not computed')

    print('fraction of empty CA):    {:1.3f}'.format(OS.num_of_empty_CA / trials_count))

    if do_problematic_check:
        print('Missed intersection area: {:1.2f} m^2 (should be small or zero)'.format(problematic_area))
        print('Num of involved obstacle: {:d}'.format(len(problematic_obstacles)))
    else:
        print('Missed intersection area: Not computed')
        print('Num of involved obstacle: Not computed')


    # Show the curve from theory    
    if do_model_CDF and visualize_CDF:
        if show_CA_as_size:
            ax2.plot(x * OS.CA_width, p_x, '-', linewidth = 1.5, color = OS.ORANGE, label='Model CDF')
        else:
            ax2.plot(x, p_x, '.', label='Model CDF')

        # Plot CDF of singleton objects
        ax2.plot(x * OS.CA_width, OS.singleton_objects_CDF(x), '-', linewidth = 1.5, color=OS.GREEN, label='Singleton CDF')

        #ax2.plot(0, beta_analytical, 'o', color=OS.GREEN, label='beta analytical')

        #if compute_coverage:
        #    ax2.plot(0, beta_numerical, 'x', color=OS.RED, label='beta numerical')

    if visualize_obstacles:
        ax1.set_title('Obstacles: {:d}  CAs: {:d}   CA nominal size: {:1.0f} m$^2$'.format(OS.num_of_obstacles, trials_count, CA_length * CA_width))

    if visualize_CDF:
        ax2.plot(0, OS.num_of_empty_CA / trials_count, 'o', color=OS.RED, label='Fraction of empty CA')

        if show_legends:
            ax2.legend(loc="upper left", )

        ax2.grid()
        ax2.yaxis.set_ticks(np.arange(0, 1, 0.1))
        ax2.set_title('Obstacle density: {:1.0f}/km$^2$ and {:1.1f} obstacles per CA'.format(OS.obstacle_density() * 1e6, OS.num_of_obstacles / trials_count))

        # Make the second axis square to give it same height as first axis.
        ax2.set_aspect(np.diff(ax2.get_xlim())[0] / np.diff(ax2.get_ylim())[0])

    if visualize_obstacles or visualize_CDF:
        plt.show()

        if save_file_name is not None:
            print('Saving figure:            ', end='', flush=True)
            fig.savefig(save_file_name, format='png', dpi=300, bbox_inches = 'tight')
            print('Done', flush=True)
        
        return fig
    else:
        return None
