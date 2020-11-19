"""
MISSING DOC
"""
import matplotlib.pyplot as plt
import numpy as np

from casex import CriticalAreaModels, AnnexFParms, enums


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
    ax.text(0.5, 3.2 * 50000, '6+7', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)

    ax.text(2.4, 0.05, '2', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(2.4, 3.2 * 5, '3+4', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(2.4, 5000, '5+6', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(2.4, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)

    ax.text(6, 0.05, '3', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(6, 3.2 * 5, '4+5', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(6, 5000, '6+8', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(6, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)

    ax.text(10.5, 0.05, '4', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(10.5, 3.2 * 5, '5+6', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(10.5, 5000, '8+10', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)
    ax.text(10.5, 3.2 * 50000, 'xxx', horizontalalignment='center', verticalalignment='center', fontsize=FS, color=clr)

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
    ax.set_title(
        'GRC comparison (angle = {:d} deg, impact speed = 0.7 x max cruise, 1 m no slide)'.format(impact_angle))

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


if __name__ == '__main__':
    figure_GRC_model_vs_iGRC()
