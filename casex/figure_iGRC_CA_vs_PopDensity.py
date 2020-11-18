"""
MISSING DOC:
This example basically recreates Figure 2 in Annex F. This figure shows the iGRC integer values
for a range of critical areas and population densities that span what the iGRC table has, that is,
CA values from 1 m^2 to 66k m^2, and population densities from 0.01 to 500k ppl/km^2.

Note that in the final iGRC table, the columns are aircraft dimension instead of CA, and the
population densities has "controlled" instead of 0.1 and >100.000 instead of 500.000.
"""
import matplotlib.pyplot as plt
import numpy as np
import math

# This is used for the colorbar.
from mpl_toolkits.axes_grid1 import make_axes_locatable

import casex


def figure_iGRC_CA_vs_PopDensity():
    """MISSING DOC

    Parameters
    ----------

    Returns
    -------
    None
    """
    # TODO: Update this when Annex F is finished.
    # Show the calculated iGRC values with a reduction as shown in Annex F Table 17.
    show_with_obstacles = False

    # Use a reduced granularity on the CA axis.
    show_reduced_CA_axis = True

    # Uses the old SORA quantization (only applicable if show_reduced_CA_axis is True).
    show_old_quantization = True
    show_old_quantization = show_old_quantization and show_reduced_CA_axis

    # Show the iGRC numbers as iGRC-X instead of just X.
    show_iGRC_prefix = True

    # Show additional grid lines. Makes it a bit cluttered, but assist in reading the table.
    show_additional_grid = False

    # Show colorbar instead of numbers for the background ISO plot.
    show_colorbar = False

    # Turn on/off three different labels on the x axis.
    show_x_wingspan = True
    show_x_velocity = True
    show_x_CA = False

    # Instantiate the Annex F class. The impact angle is not relevant for this example, so the value is random.
    impact_angle = 35
    AFP = casex.annex_f_parms.AnnexFParms(impact_angle)

    # Let CA span from 1 to 66k (we need to add a bit to the upper limit, so the numerics of the log10 does not
    # exclude he value from the axis).
    CA = np.logspace(math.log10(1), math.log10(66e3 + 100), 500)
    # Let pop_density span from 0.01 to 500k.
    pop_density = np.logspace(math.log10(0.01), math.log10(5e5 + 3000), 500)

    # Create the matrix of iGRC values.
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
    ax.set_xticks(np.sort(np.concatenate([CA_ticks, CA_ticks_additional])))

    # Add x tick labels.
    xtick_wingspan = ['1', 'n/a', '0.5', '1.2', '3', '1.6', '3.9', '8', '4.5', '9.5', '20', '22', '36']
    xtick_velocity = ['25', 'n/a', '35', '35', '35', '75', '75', '75', '150', '150', '150', '200', '200']
    xtick_CA = ['6.5', '20', '50', '10', '200', '500', '1k', '2k', '5k', '10k', '20k', '40k', '66k']

    # Add units to x tick labels.
    for k in range(len(xtick_wingspan)):
        xtick_wingspan[k] = xtick_wingspan[k] + ' m'
        xtick_velocity[k] = xtick_velocity[k] + ' m/s'
        xtick_CA[k] = xtick_CA[k] + ' m$^2$'

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

    # Remove additional xtick labels is they are not requested.
    if not show_additional_grid:
        xtick_actual_label = [xtick_actual_label[i] for i in [0, 4, 7, 10]]

    # Add empty labels at both ends.
    xtick_actual_label.insert(0, '')
    xtick_actual_label.append('')

    ax.set_xticklabels(xtick_actual_label, fontsize='16')

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

    if show_additional_grid:
        ax.tick_params(axis='both', which='major', labelsize=7)
    else:
        ax.tick_params(axis='both', which='major', labelsize=9)

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

    iGRC_fontsize = 12

    if show_reduced_CA_axis:
        old_iGRC = [
            [1, 2, 3, 4, 0],
            [3, 4, 5, 6, 0],
            [5, 6, 8, 10, 0],
            [8, 0, 0, 0, 0]
        ]
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
                        ax.text(x[k], y[j], iGRX_prefix + str(old_iGRC[j][k]), ha='center', va='center', color='white',
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

        ax.text(2.9, 5.4, "Not in SORA", ha='center', va='center', color='white', weight='bold', fontsize=iGRC_fontsize)

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
            ax.text(bands_x[k], bands_y[k], '{}'.format(k), color=clr, weight='bold', fontsize=10)

    # Set axes labels.
    ax.set_ylabel('Population density [ppl/km$^2$]', fontsize='16')
    ax.set_xlabel(x_actual_label, fontsize='16')

    # Set axis limits.
    ax.set_xlim(math.log10(CA[0]), math.log10(CA[-1]))
    ax.set_ylim(math.log10(pop_density[-1]), math.log10(pop_density[0]))

    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)

    title = 'Critical area iso plot'
    if show_old_quantization:
        title += ', old SORA quantization'
    if show_with_obstacles:
        title += ', reduced CA due to obstacles'

    ax.set_title(title, fontsize='20')

    plt.show()

    # Use this to generate a PNG file of the plot.
    fig.savefig('iGRC_CA_vs_pop_density_img4.png', format='png', dpi=300)


if __name__ == '__main__':
    figure_iGRC_CA_vs_PopDensity()
