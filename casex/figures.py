"""
Recreates some of the figures in Annex F :cite:`JARUS_AnnexF`.
"""
import matplotlib.pyplot as plt
import numpy as np
import math

# This is used for the colorbar.
from mpl_toolkits.axes_grid1 import make_axes_locatable

from casex import CriticalAreaModels, AnnexFParms, enums, Obstacles


class Figures:
    """
    This class provides some static methods that will were used to make some of the
    figures in Annex F :cite:`JARUS_AnnexF`. The methods take a number of boolean
    variables to control the content of the figures. The specific choice of parameters
    for each figure is shown in example 8.
    """

    @staticmethod
    def figure_obstacle_critical_area_reduction(save_fig=False):
        """Recreates the figure in Annex F Appendix B for the CA reduction used in the iGRC table..

        Parameters
        ----------
        save_fig : bool, optional
            If True save the figure to a PNG (default is False).
            
        Returns
        -------
        None
        """
        # Wingspan and length of CA.
        CA_width = 3
        CA_length = 200 / CA_width

        # Obstacle density in obstacles per square meter.
        obstacle_density = 850 / 1e6

        # Average width and length of house and variation in house width and length.
        obstacle_width_mu = 17
        obstacle_width_sigma = 3
        obstacle_length_mu = 8
        obstacle_length_sigma = 2

        OS = Obstacles(CA_width, CA_length, 0)

        x = np.linspace(0, CA_length, 10)

        CA_of_interest = 120

        # Compute the probability curve.
        p_x, beta_analytical, sanity_check = OS.cdf(x, obstacle_density, obstacle_width_mu, obstacle_width_sigma,
                                                    obstacle_length_mu, obstacle_length_sigma, 25)

        # Compute probability for specific CA size (for graphics).
        p_x2 = OS.cdf(CA_of_interest / CA_width, obstacle_density, obstacle_width_mu, obstacle_width_sigma,
                      obstacle_length_mu, obstacle_length_sigma, 25)

        print('Probability of reduction to at most {:1.0f} m^2 is {:1.0f}%'.format(CA_of_interest, p_x2[0][0] * 100))

        # Plot the curve and the target CA.
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes()
        ax.plot(x * CA_width, p_x, linewidth=3)

        ax.set_xlabel('Critical area [m$^2$]', fontsize=16)
        ax.set_xlim([0, x[-1] * CA_width])

        ax.plot([0, CA_of_interest], [p_x2[0][0], p_x2[0][0]], '--', color='orange', linewidth=3)
        ax.plot([CA_of_interest, CA_of_interest], [p_x[0], p_x2[0][0]], '--', color='orange', linewidth=3)

        ax.set_ylim([p_x[0], math.ceil(p_x[-1] * 10) / 10])
        ax.set_ylabel('Probability', fontsize=16)

        ax.tick_params(axis='both', which='major', labelsize=14)

        plt.grid()
        plt.show()

        # Save the figure to file.
        if save_fig:
            fig.savefig('Obstacles_critical_area_reduction.png', format='png', dpi=300)

    @staticmethod
    def figure_angle_vs_speed(show_matrix=False, show_contours=False, save_fig=False):
        """Recreates the figure in Annex F relating impact angles and impact speed for the different size classes.

        This method also outputs a variety of computations for the ballistic descent as listed in Annex F Appendix A
        :cite:`JARUS_AnnexF`.

        Parameters
        ----------
        show_matrix : bool, optional
            Set to False to get plots in Annex F (the default is False).
        show_contours : bool, optional
            Set to True to see the CA matrix (the default is False).
        save_fig : bool, optional
            If True save the figure to a PNG (default is False).
            
        Returns
        -------
        None
        """
        # Data on person size.
        person_width = 0.3
        person_height = 1.8

        # Instantiate necessary class.
        CA = CriticalAreaModels(person_width, person_height)

        # Sampling density.
        angle_samples = 100
        speed_samples = 100

        # Plotting range for the impact angle.
        impact_angle = np.linspace(1, 80, angle_samples)

        # Plotting range for the speed for each of the four scenarios.
        speed_plot_range = np.array([50, 70, 120, 250, 300])

        # Get the four scenario.
        AFP = AnnexFParms(impact_angle)

        # Contour levels for each plot.
        # Note that the CA target is not included, since it is already listed above (and is plotted in different color).
        contour_levels = []
        contour_levels.append(np.array([5, 10, 30, 50, 100]))
        contour_levels.append(np.array([100, 300, 400, 600]))
        contour_levels.append(np.array([500, 1000, 3000, 5000]))
        contour_levels.append(np.array([5000, 10000, 30000, 50000]))
        contour_levels.append(np.array([5000, 10000, 30000, 50000]))

        # Set to true to plot the COR.
        if show_contours:
            fig, axcor = plt.subplots(1, 1, figsize=(12, 6))

            axcor.plot(impact_angle, AFP.CA_parms[0].aircraft.coefficient_of_restitution)
            axcor.set_ylabel('COR [-]')
            axcor.set_xlabel('Impact angle [deg]')
            axcor.set_title('Coefficient of restitution as a function of impact angle')

        fig, ax = plt.subplots(2, 3, figsize=(13, 7))

        if show_matrix:
            main_color = 'yellow'
            side_color = 'white'
        else:
            main_color = 'black'
            side_color = 'grey'

        print("Ballistic descent computations")
        print("------------------------------")
        print("Class   Init horiz     From     Terminal   Impact   Impact   Distance   Descent      KE")
        print("          speed      altitude   velocity   speed    angle    traveled    time      impact")

        c = 0
        for j in range(2):
            for k in range(3):

                if c > 4:
                    break

                # Speed range for the plot.
                impact_speed = np.linspace(0, speed_plot_range[c], speed_samples)

                # Initialize CA matrix.
                CA_matrix = np.zeros((speed_samples, angle_samples))

                # Compute the CA matrix.
                for i in range(speed_samples):
                    impact_speed_i = impact_speed[i]

                    overlap = 0

                    CA_matrix[i, :] = CA.critical_area(enums.CriticalAreaModel.JARUS, AFP.CA_parms[c].aircraft,
                                                       impact_speed_i, impact_angle, overlap,
                                                       AFP.CA_parms[c].KE_critical)[0]

                # Show the CA matrix.
                if show_matrix:
                    im = ax[j, k].imshow(np.log(CA_matrix),
                                         extent=[impact_angle[0], impact_angle[-1], impact_speed[0], impact_speed[-1]],
                                         aspect='auto', origin='lower')

                    # This is code for getting a colorbar. Not so useful in the combined plot, but can be used if
                    # matrices are plotted individually.
                    # divider = make_axes_locatable(ax[0, 0])
                    # cax = divider.append_axes('right', size='5%', pad=0.05)
                    # fig.colorbar(im, cax=cax, orientation='vertical')

                # Show contours for the CA matrix.
                CS = ax[j, k].contour(impact_angle, impact_speed, CA_matrix, contour_levels[c], colors=side_color)
                ax[j, k].clabel(CS, inline=1, inline_spacing=-7, fontsize=10, fmt="%u m^2")
                CS2 = ax[j, k].contour(impact_angle, impact_speed, CA_matrix, [AFP.CA_parms[c].critical_area_target],
                                       colors=main_color)
                ax[j, k].clabel(CS2, inline=1, inline_spacing=-7, fontsize=10, fmt="%u m^2")

                # Plot the scenario values as dashed lines.
                ax[j, k].plot(np.array([AFP.scenario_angles[0], AFP.scenario_angles[0]]),
                              np.array([impact_speed[0], AFP.CA_parms[c].glide_speed]), 'b--')
                ax[j, k].plot(np.array([AFP.scenario_angles[1], AFP.scenario_angles[1]]),
                              np.array([impact_speed[0], AFP.CA_parms[c].cruise_speed]), 'g--')
                ax[j, k].plot(
                    np.array([AFP.CA_parms[c].ballistic_impact_angle, AFP.CA_parms[c].ballistic_impact_angle]),
                    np.array([impact_speed[0], AFP.CA_parms[c].ballistic_impact_velocity]), 'r--')
                ax[j, k].plot(np.array([0, AFP.scenario_angles[0]]),
                              np.array([AFP.CA_parms[c].glide_speed, AFP.CA_parms[c].glide_speed]), 'b--')
                ax[j, k].plot(np.array([0, AFP.scenario_angles[1]]),
                              np.array([AFP.CA_parms[c].cruise_speed, AFP.CA_parms[c].cruise_speed]), 'g--')
                ax[j, k].plot(np.array([0, AFP.CA_parms[c].ballistic_impact_angle]), np.array(
                    [AFP.CA_parms[c].ballistic_impact_velocity, AFP.CA_parms[c].ballistic_impact_velocity]), 'r--')

                ax[j, k].set_ylabel('Impact speed  [m/s]')
                ax[j, k].set_title('Critical area [m$^2$] for {:d} m'.format(AFP.CA_parms[c].wingspan))

                ax[j, k].set_xlim(0, 80)
                ax[j, k].grid()

                ax[j, k].legend(['9 deg scenario', '35 deg scenario', 'Ballistic scenario'])

                print("{:2d} m      {:3d} m/s     {:4d} m    {:3.0f} m/s   {:3.0f} m/s   {:1.0f} deg    {:4.0f} m     "
                      "{:4.1f} s   {:6.0f} kJ".format(
                    AFP.CA_parms[c].wingspan, AFP.CA_parms[c].cruise_speed, AFP.CA_parms[c].ballistic_descent_altitude,
                    AFP.CA_parms[c].terminal_velocity, AFP.CA_parms[c].ballistic_impact_velocity,
                    AFP.CA_parms[c].ballistic_impact_angle, AFP.CA_parms[c].ballistic_distance,
                    AFP.CA_parms[c].ballistic_descent_time, AFP.CA_parms[c].ballistic_impact_KE / 1000))

                c = c + 1

        # The loop above was interrupted, and c was left one too large.
        c = c - 1

        # Show x axis label only for the two lower plots.
        ax[1, 0].set_xlabel('Impact angle [deg]')
        ax[1, 1].set_xlabel('Impact angle [deg]')
        ax[0, 2].set_xlabel('Impact angle [deg]')

        # Hide the 6th and unused axis.
        ax[1, 2].set_axis_off()

        plt.show()

        # Save the figure to file.
        if save_fig:
            fig.savefig('Descent scenarios - critical area.png', format='png', dpi=300)

    @staticmethod
    def figure_iGRC_CA_vs_PopDensity(filename, show_with_obstacles=False, show_reduced_CA_axis=True,
                                     show_old_quantization=True, show_iGRC_prefix=True, show_additional_grid=False,
                                     show_model_CA=False,
                                     show_colorbar=False, show_x_wingspan=True, show_x_velocity=True, show_x_CA=False,
                                     show_x_CA_above=False, show_title=True, save_fig=False):
        """Recreates the figures showing iGRC values and iGRC table in Annex F Section 1 :cite:`JARUS_AnnexF`.

        Parameters
        ----------
        filename : str
            Name of the output file (only applicable if save_image is True).
        show_with_obstacles : bool, optional
            If True show the calculated iGRC values with a reduction due to obstalces (see Annex F Appendix A)
            (default is False).
        show_reduced_CA_axis : bool, optional
            If True use a reduced granularity on the CA axis (default is True).
        show_old_quantization : bool, optional
            If True uses the SORA V2.0 quantization (only applicable if show_reduced_CA_axis is True)
            (default is True).
        show_iGRC_prefix : bool, optional
            If True show the iGRC numbers as iGRC-X instead of just X (default is True).
        show_additional_grid : bool, optional
            If True show additional grid lines. Makes it a bit cluttered, but assists in reading the table
            (default is False).
        show_colorbar : bool, optional
            If True show colorbar instead of numbers for the background ISO plot (default is False).
        show_x_wingspan : bool, optional
            If True show wingspan on the x axis (default is True).
        show_x_velocity : bool, optional
            If True show velocities on the x axis (default is True).
        show_x_CA : bool, optional
            If True show size of CA on the x axis (default is False).
        show_x_CA_above : bool, optional
            If True and CA is shown, show it above the figure instead of below (default is False).
        show_title : bool, optional
            If True show the title (default is True).
        save_fig : bool, optional
            If True save the figure to a PNG with the given filename (default is False).

        Returns
        -------
        None
        """
        # TODO: Update this when Annex F is finished.

        show_old_quantization = show_old_quantization and show_reduced_CA_axis

        # Instantiate the Annex F class. The impact angle is not relevant for this example, so the value is random.
        impact_angle = 35
        AFP = AnnexFParms(impact_angle)

        # Let CA span from 1 to 66k (we need to add a bit to the upper limit, so the numerics of the log10 does not
        # exclude he value from the axis).
        CA = np.logspace(math.log10(1), math.log10(66e3 + 100), 500)
        # Let pop_density span from 0.01 to 500k.
        pop_density = np.logspace(math.log10(0.01), math.log10(5e5 + 3000), 500)

        M = np.zeros((len(CA), len(pop_density)))

        for pop_density_i in range(len(pop_density)):
            for CA_i in range(len(CA)):
                ReducedCA = 1
                if 500 < pop_density[pop_density_i] < 100000 and 6.5 < CA[CA_i] < 20000 and show_with_obstacles:
                    ReducedCA = 120 / 200
                M[pop_density_i][CA_i] = AFP.iGRC(pop_density[pop_density_i], CA[CA_i] * ReducedCA)[0] - 0.3

        fig = plt.figure(figsize=(16, 9))
        ax = plt.axes()

        # Show the matrix as an image.
        im = ax.imshow(M, extent=[math.log10(CA[0]), math.log10(CA[-1]), math.log10(pop_density[0]),
                                  math.log10(pop_density[-1])], aspect='auto', origin='lower')

        # Change this to true to get a color bar.
        if show_colorbar:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            fig.colorbar(im, cax=cax, orientation='vertical')

        # CA axis tick values in log10.
        CA_ticks = np.array([math.log10(CA[0]), 0.813, 2.3, 3.3, 4.3, 4.82])
        if show_additional_grid:
            CA_ticks_additional = np.log10(np.array([20, 50, 100, 500, 1000, 5E3, 10E3, 4E4, 10E4]))
        else:
            CA_ticks_additional = []

        xtick_actual_values = np.sort(np.concatenate([CA_ticks, CA_ticks_additional]))

        # Add x tick labels.
        xtick_wingspan = ['1', 'n/a', '0.5', '1.2', '3', '1.6', '3.9', '8', '4.5', '9.5', '20', '22', '36']
        xtick_velocity = ['25', 'n/a', '35', '35', '35', '75', '75', '75', '150', '150', '150', '200', '200']
        xtick_CA = [6.5, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 40000, 66000]

        #  Change CA tick labels to accommodate many labels
        for k in range(len(xtick_CA)):
            if show_additional_grid and xtick_CA[k] >= 1000:
                xtick_CA[k] = str(xtick_CA[k] / 1000) + 'k'
            else:
                xtick_CA[k] = str(xtick_CA[k])

        # Add units to x tick labels.
        for k in range(len(xtick_wingspan)):
            xtick_wingspan[k] = xtick_wingspan[k] + ' m'
            xtick_velocity[k] = xtick_velocity[k] + ' m/s'
            xtick_CA[k] = xtick_CA[k] + ' m$^2$'

        # Remove unit on the two n/a
        xtick_wingspan[1] = 'n/a'
        xtick_velocity[1] = 'n/a'

        # Add the requested label types.
        xtick_actual_label = [0] * len(xtick_wingspan)
        for k in range(len(xtick_wingspan)):
            xtick_actual_label[k] = ''
            if show_x_wingspan:
                xtick_actual_label[k] += xtick_wingspan[k]
            if show_x_velocity:
                if show_x_wingspan:
                    xtick_actual_label[k] += '\n'
                xtick_actual_label[k] += xtick_velocity[k]
            if show_x_CA:
                if not show_x_CA_above:
                    if show_x_velocity or show_x_wingspan:
                        xtick_actual_label[k] += '\n'
                    xtick_actual_label[k] += xtick_CA[k]

        # Create the x axis label.
        x_actual_label = ''
        if show_x_wingspan:
            x_actual_label += 'Wingspan'
        if show_x_velocity:
            if show_x_wingspan:
                x_actual_label += ' + '
            x_actual_label += 'Velocity'
        if show_x_CA:
            if show_x_velocity or show_x_wingspan:
                x_actual_label += ' + '
            x_actual_label += 'Critical area'
            if show_x_CA_above:
                x_actual_label += ' (above)'

        # Remove additional xtick labels if they are not requested.
        if not show_additional_grid:
            xtick_actual_label = [xtick_actual_label[i] for i in [0, 4, 7, 10]]
            xtick_CA = [xtick_CA[i] for i in [0, 4, 7, 10]]

        # Add empty labels at both ends.
        xtick_actual_label.insert(0, '')
        xtick_actual_label.append('')
        xtick_CA.insert(0, '')
        xtick_CA.append('')

        # Set tick values and labels
        ax.set_xticks(xtick_actual_values)
        ax.set_xticklabels(xtick_actual_label, fontsize='16')

        if show_x_CA and show_x_CA_above:
            ax2 = ax.twiny()
            ax2.tick_params(labeltop=True)
            ax2.set_xticks(xtick_actual_values)
            ax2.set_xticklabels(xtick_CA, fontsize='16')

        # pop_density axis tick values in log10.
        if show_reduced_CA_axis:
            pop_density_ticks = np.array([-2, -1, np.log10(300), np.log10(15000), 5.7])
        else:
            pop_density_ticks = np.array([-2, -1, 1, 2, 3.167, 4.167, 5, 5.7])
        if show_additional_grid:
            pop_density_ticks_additional = np.log10(np.array([1, 5, 20, 50, 200, 400, 800, 3E3, 8E3, 30E3, 60E3]))
        else:
            pop_density_ticks_additional = []
        ax.set_yticks(np.sort(np.concatenate([pop_density_ticks, pop_density_ticks_additional])))

        # pop_density axis actual names at the ticks.
        if not show_additional_grid:
            if show_reduced_CA_axis:
                ax.set_yticklabels(['', 0.1, 300, '15k', '500k'])
            else:
                ax.set_yticklabels(['', 0.1, 10, 100, 1500, '15k', '100k', '500k'])
        else:
            ax.set_yticklabels(
                ['', 0.1, 1, 5, 10, 20, 50, 100, 200, 400, 800, 1500, '3k', '8k', '15k', '30k', '60k', '100k', '500k'])

        # Show vertical lines.
        for k in CA_ticks:
            if k < math.log10(7) or show_reduced_CA_axis:
                end_pop_density = math.log10(pop_density[-1])
            else:
                end_pop_density = math.log10(1E5)
            ax.plot([k, k], [math.log10(pop_density[0]), end_pop_density], color='white')
        for k in CA_ticks_additional:
            if k < math.log10(7):
                end_pop_density = math.log10(pop_density[-1])
            else:
                end_pop_density = math.log10(1E5)
            ax.plot([k, k], [math.log10(pop_density[0]), end_pop_density], color='black', linestyle='--')

        # Show horizontal lines.
        for k in pop_density_ticks:
            ax.plot([math.log10(CA[0]), math.log10(CA[-1])], [k, k], color='white')
        for k in pop_density_ticks_additional:
            ax.plot([math.log10(CA[0]), math.log10(CA[-1])], [k, k], color='black', linestyle='--')

        # Insert the iGRC table numbers in the middle between the white lines.
        iGRX_prefix = ''
        if show_iGRC_prefix:
            iGRX_prefix = 'iGRC-'

        # Compute placement of iGRC numbers (half way between lines).
        x = np.diff(CA_ticks) / 2 + CA_ticks[0:len(CA_ticks) - 1:1]
        y = np.diff(pop_density_ticks) / 2 + pop_density_ticks[0:len(pop_density_ticks) - 1:1]

        iGRC_fontsize = 14

        if show_reduced_CA_axis:
            # The old iGRC values
            old_iGRC = [
                [1, 2, 3, 4, 0],
                [3, 4, 5, 6, 0],
                [5, 6, 8, 10, 0],
                [8, 0, 0, 0, 0]
            ]
            # The new iGRC values
            new_iGRC = [
                [1, 3, 4, 5, 5],
                [5, 6, 7, 8, 9],
                [6, 8, 9, 10, 10],
                [8, 9, 10, 11, 12]
            ]
            for k in range(5):
                for j in range(4):
                    if show_old_quantization:
                        if old_iGRC[j][k] > 0:
                            ax.text(x[k], y[j], iGRX_prefix + str(old_iGRC[j][k]), ha='center', va='center',
                                    color='white',
                                    weight='bold', fontsize=iGRC_fontsize)
                        else:
                            ax.text(x[k], y[j], "NO GRC", ha='center', va='center', color='black', weight='bold',
                                    fontsize=iGRC_fontsize)
                    else:
                        ax.text(x[k], y[j], iGRX_prefix + str(new_iGRC[j][k]), ha='center', va='center', color='white',
                                weight='bold', fontsize=iGRC_fontsize)
        else:
            for k, xv in enumerate(x, start=2):
                for j, yv in enumerate(y):
                    a = k + j
                    if j == 0:
                        a = a - 1
                    if j < 6:
                        txt = iGRX_prefix + '{}'.format(a)
                    else:
                        if k == 2:
                            txt = iGRX_prefix + '7*'
                        else:
                            txt = ''
                    ax.text(xv, yv, txt, ha='center', va='center', color='white', weight='bold', fontsize=iGRC_fontsize)

            ax.text(2.9, 5.4, "Not in SORA", ha='center', va='center', color='white', weight='bold',
                    fontsize=iGRC_fontsize)

        if not show_colorbar:
            # Locations for the band value numbers.
            bands_x = [0.4, 1.4, 2.5, 3.5, 4.4, 4.4, 4.4, 4.4, 4.4, 4.4, 4.4, 4.4]
            bands_y = [-1.7, -1.7, -1.7, -1.7, -1.7, -0.7, 0.3, 1.3, 2.3, 3.4, 4.4, 5.4]

            # Add values to the bands in the ISO plot.
            for k in range(len(bands_x)):
                if k < 8:
                    clr = 'yellow'
                else:
                    clr = 'mediumblue'
                ax.text(bands_x[k], bands_y[k], '{}'.format(k), color=clr, weight='bold', fontsize=12)

        # Set axes labels.
        ax.set_ylabel('Population density [ppl/km$^2$]', fontsize='18')
        ax.set_xlabel(x_actual_label, fontsize='18')

        # Set axis limits.
        ax.set_xlim(math.log10(CA[0]), math.log10(CA[-1]))
        ax.set_ylim(math.log10(pop_density[-1]), math.log10(pop_density[0]))

        if show_additional_grid:
            ax.tick_params(axis='both', which='major', labelsize=9)
            if show_x_CA_above:
                ax2.tick_params(axis='both', which='major', labelsize=9)
        else:
            ax.tick_params(axis='both', which='major', labelsize=16)
            if show_x_CA_above:
                ax2.tick_params(axis='both', which='major', labelsize=16)

        if show_title:
            title = 'Critical area iso plot'
            if show_old_quantization:
                title += ', old SORA quantization'
            if show_with_obstacles:
                title += ', reduced CA due to obstacles'

            ax.set_title(title, fontsize='20')

        plt.show()

        # Use this to generate a PNG file of the plot.
        if save_fig:
            fig.savefig('iGRC_CA_vs_pop_density' + filename + '.png', format='png', dpi=300)
