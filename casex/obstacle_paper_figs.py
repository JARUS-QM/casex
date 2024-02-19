#from casex import Obstacle
from obstacle_simulation import *

if False:
    CA_width = 3
    CA_length = 80 / 3
    num_of_obstacles = 1800

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = False,
                        visualize_obstacles = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = True,
                        obstacle_orientation = Obstacles.DistributionType.UNIFORM,
                        obstacle_orientation_loc = 0,
                        obstacle_orientation_scale = 19,
                        obstacle_orientation_resolution = 100,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12346,
                        show_pdf_density_functions = True,
                        force_fixed_obstacle_orientation_in_CDF = False,
                        save_file_name = 'fig_test_UNIFORM_0_19.png')

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = False,
                        visualize_obstacles = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = True,
                        obstacle_orientation = Obstacles.DistributionType.UNIFORM,
                        obstacle_orientation_loc = 0,
                        obstacle_orientation_scale = 19,
                        obstacle_orientation_resolution = 100,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12346,
                        show_pdf_density_functions = True,
                        force_fixed_obstacle_orientation_in_CDF = True,
                        save_file_name = None # 'fig_test_UNIFORM_0_19_no_obs_orient_integral.png'
                        )

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = False,
                        visualize_obstacles = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = True,
                        obstacle_orientation = Obstacles.DistributionType.UNIFORM,
                        obstacle_orientation_loc = 67,
                        obstacle_orientation_scale = 256,
                        obstacle_orientation_resolution = 100,
                        trials_count = 2000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12346,
                        show_pdf_density_functions = True,
                        force_fixed_obstacle_orientation_in_CDF = True,
                        save_file_name = None # 'fig_test_UNIFORM_67_256.png'
                        )

if True:
    CA_width = 3
    CA_length = 80 / 3
    num_of_obstacles = 1800

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = False,
                        visualize_obstacles = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = True,
                        obstacle_orientation = Obstacles.DistributionType.NORM,
                        obstacle_orientation_loc = 34,
                        obstacle_orientation_scale = 30,
                        obstacle_orientation_resolution = 25,
                        trials_count = 5000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12346,
                        show_pdf_density_functions = True,
                        force_fixed_obstacle_orientation_in_CDF = False,
                        save_file_name = 'fig_test_NORM_34_30.png'
                        )

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = False,
                        visualize_obstacles = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = True,
                        obstacle_orientation = Obstacles.DistributionType.NORM,
                        obstacle_orientation_loc = 34,
                        obstacle_orientation_scale = 30,
                        obstacle_orientation_resolution = 25,
                        trials_count = 5000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12346,
                        show_pdf_density_functions = True,
                        force_fixed_obstacle_orientation_in_CDF = True,
                        save_file_name = 'fig_test_NORM_34_30_no_obs_orient_integral.png'
                        )


if False:
    print('--- CASE 1 ---')
    CA_width = 3
    CA_length = 80 / 3
    num_of_obstacles = 1800

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage=True,
                        visualize_CDF = True,
                        do_problematic_check = False,
                        show_CA_first_point = False,
                        model_CDF_high_res = False,
                        trials_count = 1000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 12345,
                        save_file_name = 'fig_init_example.png')

    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage=True,
                        visualize_CDF = False,
                        do_problematic_check = False,
                        show_CA_first_point = True,
                        trials_count = 1000,
                        trial_area_sidelength = 1000,
                        viz_obstacle_zoom = [[200, 400], [200, 400]],
                        random_generator_seed = 12345,
                        save_file_name = 'fig_init_example_zoom.png')

if False:
    CA_width = 3
    CA_length = 90

    print('--- CASE 2 ---')
    num_of_obstacles = 100
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        compute_coverage = True,
                        visualize_obstacles = False,
                        visualize_CDF = True,
                        do_problematic_check = False,
                        trials_count = 10000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        save_file_name = 'fig_100obs.png')

    print('--- CASE 3 ---')
    num_of_obstacles = 500
    obstacle_simulation(CA_width, 
                        CA_length, 
                        num_of_obstacles, 
                        compute_coverage = True,
                        visualize_obstacles = False,
                        visualize_CDF = True,
                        do_problematic_check = False,
                        trials_count = 10000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        show_legends = False,
                        save_file_name = 'fig_500obs.png')

    print('--- CASE 4 ---')
    num_of_obstacles = 2500
    obstacle_simulation(CA_width,
                        CA_length, 
                        num_of_obstacles, 
                        compute_coverage = True,
                        visualize_obstacles = False,
                        visualize_CDF = True,
                        do_problematic_check = False,
                        trials_count = 10000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        show_legends = False,
                        save_file_name = 'fig_2500obs.png')

    print('--- CASE 5 ---')
    num_of_obstacles = 10000
    obstacle_simulation(CA_width,
                        CA_length, 
                        num_of_obstacles, 
                        compute_coverage = True,
                        visualize_obstacles = False,
                        visualize_CDF = True,
                        do_problematic_check = False,
                        trials_count = 10000,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1234,
                        show_legends = False,
                        save_file_name = 'fig_10000obs.png')

if False:
    print('--- CASE 6 ---')
    CA_width = 3
    CA_length = 90

    num_of_obstacles = 1000
    obstacle_simulation(CA_width,
                        CA_length, 
                        num_of_obstacles, 
                        do_model_CDF = True, 
                        compute_coverage = True,
                        visualize_obstacles = True,
                        visualize_CDF = True,
                        do_houses_along_roads = True,
                        do_problematic_check = True,
                        show_CA_first_point = False,
                        trials_count = 500,
                        trial_area_sidelength = 1000,
                        random_generator_seed = 1235,
                        save_file_name = 'fig_along_rods.png')
