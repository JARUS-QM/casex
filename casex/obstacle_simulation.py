"""
MISSING DOC
"""
import time

import matplotlib.pyplot as plt
import numpy as np
from descartes.patch import PolygonPatch

from casex import Obstacles


def obstacle_simulation():
    """MISSING DOC

    Parameters
    ----------

    Returns
    -------
    None
    """
    start_time = time.time()

    ## CA properties.
    CA_width = 0.1
    CA_length = 100
    trials_count = 400
    trial_area_sidelength = 2000
    num_of_obstacles = 3000

    obstacle_width_mu = 25
    obstacle_width_sigma = 8
    obstacle_length_mu = 9
    obstacle_length_sigma = 2

    do_compute_coverage = True
    do_sanity_check = True
    do_theory = True
    do_viz = True

    obstacle_density = num_of_obstacles / trial_area_sidelength / trial_area_sidelength

    OS = Obstacles(trial_area_sidelength)

    gen_polygons_time = time.time()
    OS.generate_rectangular_obstacles_normal_distributed(num_of_obstacles, obstacle_width_mu, obstacle_width_sigma,
                                                         obstacle_length_mu, obstacle_length_sigma)
    OS.generate_CAs(trials_count, CA_width, CA_length)
    print('Generate polygons time:  {:1.3f} sec'.format(time.time() - gen_polygons_time))

    ### Run trials.
    intersection_time = time.time()
    OS.compute_reduced_CAs()
    OS.compute_CA_lengths()
    print('Intersection time:       {:1.3f} sec'.format(time.time() - intersection_time))
    if do_compute_coverage:
        coverage_time = time.time()
        OS.compute_coverage()
        print('Coverage time:           {:1.3f} sec'.format(time.time() - coverage_time))

    if do_sanity_check:
        sanity_check_time = time.time()
        problematic_area, problematic_obstacles, problematic_CAs = OS.sanity_check()
        print('Sanity check time:       {:1.3f} sec'.format(time.time() - sanity_check_time))
    else:
        print('Sanity check time:       None')

    ### Compute the probability based on theory.
    if do_theory:
        theory_time = time.time()
        x_resolution = 50
        x = np.linspace(0, CA_length, x_resolution)
        pdf_resolution = 30
        p_x, beta_analytical, sanity_check = OS.first_pdf(x, obstacle_density, obstacle_width_mu, obstacle_width_sigma,
                                                          obstacle_length_mu, obstacle_length_sigma, pdf_resolution)
        print('Theory time:             {:1.3f} sec'.format(time.time() - theory_time))
        beta_numerical = OS.total_coverage / trial_area_sidelength / trial_area_sidelength

    ### Create figure for visual output.
    viz_time = time.time()
    show_CA_as_size = False
    fig = plt.figure(1, figsize=(12, 8), dpi=90)
    if do_viz:
        ax1 = fig.add_subplot(121)
        OS.show_simulation(ax1, CAs="True", CAs_reduced="True", obstacles_original="True", obstacles_intersected="True",
                           CA_first_point="False", debug_points="False")
        ax2 = fig.add_subplot(122)
    else:
        ax2 = fig.add_subplot(111)

    OS.show_CDF(ax2, show_CA_as_size)

    if do_sanity_check & do_viz:
        for o in problematic_obstacles:
            ax1.add_patch(PolygonPatch(o, facecolor='#ffff00', edgecolor='#000000', alpha=1, zorder=10, linewidth=0.25))
        for CAr in problematic_CAs:
            ax1.add_patch(
                PolygonPatch(CAr, facecolor='#ffff00', edgecolor='#000000', alpha=1, zorder=10, linewidth=0.25))

    print('Visualization time:      {:1.3f} sec'.format(time.time() - viz_time))

    print('Total time:              {:1.3f} sec'.format(time.time() - start_time))

    print('---------------------------')

    print('Original CA:             {:1.0f} m^2'.format(OS.CA_length * OS.CA_width))
    print('Reduced CA:              {:1.0f} m^2 ({:d}%)'.format(np.mean(OS.CA_lengths) * OS.CA_width, int(
        round(100 * np.mean(OS.CA_lengths) / OS.CA_length))))

    print('---------------------------')
    if do_sanity_check:
        print('Total intersection area: {:1.0f} m^2 (should be small or zero)'.format(problematic_area))
    print('Number of CA reduced:    {:d}   ({:d}%)'.format(OS.num_of_reduced_CA,
                                                           int(round(100 * OS.num_of_reduced_CA / OS.trials_count))))
    print('Number of CA empty:      {:d}   ({:d}%)'.format(OS.num_of_empty_CA,
                                                           int(round(100 * OS.num_of_empty_CA / OS.trials_count))))
    print('Obstacle density:        {:1.5f} #/km^2'.format(obstacle_density))
    if do_compute_coverage:
        print('Obstacle total area:     {:1.0f} m^2'.format(OS.total_obstacle_area))
        print('Obstacle coverage (num): {:1.0f} m^2'.format(OS.total_coverage))
        print('Obstacle coverage (ana): {:1.0f} m^2'.format(num_of_obstacles * obstacle_width_mu * obstacle_length_mu))
        print('Coverage ratio:          {:1.3f}'.format(OS.total_coverage / OS.total_obstacle_area))
    if do_theory:
        print('beta (numerical):        {:1.5f}'.format(beta_numerical))
        print('beta (numerical sanity): {:1.5f}'.format(OS.num_of_empty_CA / trials_count))
        print('beta (analytical):       {:1.5f}'.format(beta_analytical))
    if do_sanity_check:
        print('PDF sanity check:        {:1.3f}'.format(sanity_check))

    # Show the curve from theory    
    if do_theory:
        if not show_CA_as_size:
            ax2.plot(x, p_x, '.')
        else:
            ax2.plot(x * OS.CA_width, p_x, '.')
        ax2.plot(0, beta_analytical, 'o', color='#00ff00')
        ax2.plot(0, OS.num_of_empty_CA / trials_count, 'o', color='#0000ff')
        ax2.plot(0, beta_numerical, 'o', color='#ff0000')

    plt.show()

    fig.savefig('Sim.png', format='png', dpi=300)


if __name__ == '__main__':
    obstacle_simulation()
