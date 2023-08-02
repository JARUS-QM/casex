#from casex import Obstacle
from obstacle_simulation import *

CA_width = 3
CA_length = 80 / 3
num_of_obstacles = 800

if False:
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = False,
                        trials_count = 1000,
                        trial_area_sidelength = 1000,
                        viz_obstacle_zoom = None,
                        random_generator_seed = 12345,
                        save_file_name = 'fig1.png')

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_CDF = False,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 1000,
                        trial_area_sidelength = 1000,
                        viz_obstacle_zoom = [[200, 400], [200, 400]],
                        random_generator_seed = 12345,
                        save_file_name = 'fig2.png')

if False:
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_obstacles = False,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 100000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12345,
                        save_file_name = 'fig3.png')

if True:
    CA_width = 3
    CA_length = 90

    num_of_obstacles = 100
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_obstacles = False,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        save_file_name = 'fig_100obs.png')

    num_of_obstacles = 500
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_obstacles = False,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        save_file_name = 'fig_500obs.png')

    num_of_obstacles = 2500
    obstacle_simulation(CA_width,
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_obstacles = False,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        save_file_name = 'fig_2500obs.png')

    num_of_obstacles = 10000
    obstacle_simulation(CA_width,
                        CA_length, 
                        num_of_obstacles, 
                        do_theory = True, 
                        do_compute_coverage=True,
                        do_viz_obstacles = False,
                        do_viz_CDF = True,
                        do_problematic_check = False,
                        do_show_CA_first_point = True,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        save_file_name = 'fig_10000obs.png')
