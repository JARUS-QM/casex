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
