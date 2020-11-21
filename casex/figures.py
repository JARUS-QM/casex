"""
MISSING DOC
"""
import matplotlib.pyplot as plt
import numpy as np

from casex import CriticalAreaModels, AnnexFParms, enums


class Figures:
    """MISSING DOC

    """

    @staticmethod
    def figure_angle_vs_speed(show_matrix=False, show_contours=False):
        """MISSING DOC

        Parameters
        ----------
        show_matrix : bool, optional
            Set to False to get plots in Annex F (the default is False).
        show_contours : bool, optional
            Set to True to see the CA matrix (the default is False).

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
        fig.savefig('Descent scenarios - critical area.png', format='png', dpi=300)

    @staticmethod
    def figure_GRC_model_vs_iGRC():
        """MISSING DOC

        Parameters
        ----------

        Returns
        -------
        None
        """
        # Data on person size.
        person_width = 0.3
        person_height = 1.8
        impact_angle = 9

        # Instantiate necessary classes.
        CA = CriticalAreaModels(person_width, person_height)

        # Sampling density.
        pop_density_samples = 400
        wingspan_samples = 200

        # Plotting range for the impact angle.
        wingspan = np.linspace(0, 12, wingspan_samples)

        # Get the five scenario.
        AFP = AnnexFParms(impact_angle)

        fig, ax = plt.subplots(1, 1, figsize=(13, 7))

        # Speed range for the plot.
        pop_density = np.logspace(-3 + np.log10(5), 5 + np.log10(5), pop_density_samples)

        # Initialize CA matrix.
        GRC_matrix = np.zeros((pop_density_samples, wingspan_samples))

        # Compute the CA matrix.
        for j in range(len(wingspan)):

            # Set impact speed in correspondence with wingspan.
            if wingspan[j] <= AFP.CA_parms[0].wingspan:
                column = 0
            elif wingspan[j] <= AFP.CA_parms[1].wingspan:
                column = 1
            elif wingspan[j] <= AFP.CA_parms[2].wingspan:
                column = 2
            else:
                column = 3

            impact_speed = AFP.CA_parms[column].cruise_speed * 0.7
            # impact_speed = AFP.CA_parms[column].ballistic_impact_velocity.

            AFP.CA_parms[column].aircraft.width = wingspan[j]

            M = 1e-6 * CA.critical_area(enums.CriticalAreaModel.JARUS, AFP.CA_parms[column].aircraft, impact_speed,
                                        impact_angle, 0, 0)[0]

            for i in range(len(pop_density)):
                GRC_matrix[i, j] = 1 - np.log10(1e-6 / (pop_density[i] * M))

        ax2 = ax.twinx()
        im = ax2.imshow(np.ceil(GRC_matrix), extent=[wingspan[0], wingspan[-1], pop_density[0], pop_density[-1]],
                        aspect='auto', origin='upper')

        ax.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_visible(False)
        ax2.yaxis.set_major_locator(plt.NullLocator())

        ax.plot([wingspan[0], wingspan[-1]], [.05, .05], '--', color='lightgrey', linewidth=0.5)
        ax.plot([wingspan[0], wingspan[-1]], [0.5, 0.5], 'w--')
        ax.plot([wingspan[0], wingspan[-1]], [5, 5], '--', color='lightgrey', linewidth=0.5)
        ax.plot([wingspan[0], wingspan[-1]], [50, 50], '--', color='lightgrey', linewidth=0.5)
        ax.plot([wingspan[0], wingspan[-1]], [500, 500], 'w--')
        ax.plot([wingspan[0], wingspan[-1]], [5000, 5000], '--', color='lightgrey', linewidth=0.5)
        ax.plot([wingspan[0], wingspan[-1]], [50000, 50000], 'w--')
        ax.plot(np.array([1, 1]), np.array([pop_density[0], pop_density[-1]]), 'w--')
        ax.plot(np.array([3, 3]), np.array([pop_density[0], pop_density[-1]]), 'w--')
        ax.plot(np.array([8, 8]), np.array([pop_density[0], pop_density[-1]]), 'w--')

        for i in range(8):
            if i == 3 or i == 7:
                m = 1.8
            else:
                m = 3.2
            ax.text(0.5, m * 0.005 * np.power(10, i), i + 1, horizontalalignment='center', verticalalignment='center',
                    fontsize=12, color='lightgray')
            ax.text(1.6, 3.2 * 0.005 * np.power(10, i), i + 2, horizontalalignment='center', verticalalignment='center',
                    fontsize=12, color='lightgray')
            ax.text(4.5, 3.2 * 0.005 * np.power(10, i), i + 3, horizontalalignment='center', verticalalignment='center',
                    fontsize=12, color='lightgray')
            ax.text(9.5, 3.2 * 0.005 * np.power(10, i), i + 4, horizontalalignment='center', verticalalignment='center',
                    fontsize=12, color='lightgray')

        ax.text(12.2, 0.05, 'Controlled', fontsize=14, rotation=90, verticalalignment='center')
        ax.text(12.2, 3.2 * 5, 'Sparsely populated', fontsize=14, rotation=90, verticalalignment='center')
        ax.text(12.2, 5000, 'Populated', fontsize=14, rotation=90, verticalalignment='center')
        ax.text(12.2, 3.2 * 50000, 'Gath', fontsize=14, rotation=90, verticalalignment='center')

        FS = 16
        clr = 'white'

        ax.text(0.5, 0.05, '1', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(0.5, 3.2 * 5, '2+3', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(0.5, 5000, '4+5', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(0.5, 3.2 * 50000, '6+7', horizontalalignment='center', verticalalignment='center', fontsize=FS,
                color=clr)

        ax.text(2.4, 0.05, '2', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(2.4, 3.2 * 5, '3+4', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(2.4, 5000, '5+6', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(2.4, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS,
                color=clr)

        ax.text(6, 0.05, '3', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(6, 3.2 * 5, '4+5', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(6, 5000, '6+8', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(6, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)

        ax.text(10.5, 0.05, '4', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(10.5, 3.2 * 5, '5+6', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(10.5, 5000, '8+10', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
        ax.text(10.5, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS,
                color=clr)

        ax.text(12.9, 3.2 * 0.0005, 'DK dens', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 0.005, '0.0%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 0.05, '3.1%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 0.5, '11.7%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 5, '57.2%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 50, '20.0%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 500, '7.4%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 5000, '0.5%', horizontalalignment='center', verticalalignment='center', fontsize=12)
        ax.text(12.9, 3.2 * 50000, '0.0%', horizontalalignment='center', verticalalignment='center', fontsize=12)

        # Show contours for the CA matrix.
        CS = ax.contour(wingspan, pop_density, GRC_matrix, np.arange(1, 18), colors='black')
        ax.clabel(CS, inline=1, fontsize=12, fmt="GRC %u")

        ax.set_ylabel('Population density [ppl/km^2]')
        ax.set_xlabel('Wingspan [m]')
        ax.set_yscale('log')
        ax.set_title('GRC comparison (angle = {:d} deg, impact speed = 0.7 x max cruise, 1 m no slide)'.format(
            impact_angle))

        y = np.array([0.005, 0.05, 0.5, 5, 50, 5e2, 5e3, 5e4, 5e5])
        ax.yaxis.set_major_locator(plt.FixedLocator(y))
        ax.set_yticklabels(y)
        ax.yaxis.set_minor_locator(plt.NullLocator())
        ax.xaxis.set_major_locator(plt.FixedLocator([1, 3, 8]))
        ax.set_xticklabels([1, 3, 8])

        ax.set_xlim(wingspan[0], wingspan[-1])
        ax.set_ylim(pop_density[-1], pop_density[0])
        # ax.grid()

        plt.show()

        # Save the figure to file.
        fig.savefig('GRC comparison, {:d} degrees.png'.format(impact_angle), format='png', dpi=300)
