"""
Example 4
---------
This example basically recreates Figure 2 in Annex F. This figure shows the iGRC integer values
for a range of critical areas and population densities that span what the iGRC table has, that is,
CA values from 1 m^2 to 66k m^2, and population densities from 0.01 to 500k ppl/km^2.

Note that in the final iGRC table, the columns are aircraft dimension instead of CA, and the
population densities has "controlled" instead of 0.1 and >100.000 instead of 500.000.
"""
import matplotlib.pyplot as plt
import numpy as np
import math

# This is used for the colorbar
from mpl_toolkits.axes_grid1 import make_axes_locatable

import casex

def figure_iGRC_CA_vs_PopDensity():
    show_reduced_pop_dens = True
    show_additional_grid = False
    show_colorbar = False

    # Data on person size
    person_width = 0.3
    person_height = 1.8

    # Instantiate necessary classes    
    FC = casex.friction_coefficient.FrictionCoefficients()
    CA = casex.critical_area_models.CriticalAreaModels(person_width, person_height)
    
    # Instantiate the Annex F class. The impact angle is not relevant for this example, so the value is random.
    impact_angle = 35;
    AFP = casex.annex_f_parms.AnnexFParms(impact_angle)
    
    # Let CA span from 1 to 66k (we need to add a bit to the upper limit, so the numerics of the log10 does not exclude he value from the axis)
    CA = np.logspace(math.log10(1), math.log10(66e3+100), 500)
    # Let pop_density span from 0.01 to 500k
    pop_density = np.logspace(math.log10(0.01), math.log10(5e5+3000), 500)
    
    # Create the matrix of iGRC values
    M = np.zeros((len(CA),len(pop_density)))
    for pop_density_i in range(len(pop_density)):
        for CA_i in range(len(CA)):
            ReducedCA = 1
            if (pop_density[pop_density_i] > 500 and pop_density[pop_density_i] < 100000 and CA[CA_i] > 6.5 and CA[CA_i] < 20000 and show_reduced_pop_dens):
                ReducedCA = 120/200
            M[pop_density_i][CA_i] = AFP.iGRC(pop_density[pop_density_i], CA[CA_i] * ReducedCA)[0] - 0.3
        
    fig = plt.figure(figsize=(16,9))  
    ax = plt.axes()
      
    # Show the matrix as an image
    im = ax.imshow(M, extent=[math.log10(CA[0]), math.log10(CA[-1]), math.log10(pop_density[0]), math.log10(pop_density[-1])], aspect='auto', origin='lower')

    # Change this to true to get a color bar
    if show_colorbar:    
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        fig.colorbar(im, cax=cax, orientation='vertical')
    
    # CA axis tick values in log10
    CA_ticks = np.array([math.log10(CA[0]), 0.813, 2.3, 3.3,  4.3,  4.82])
    if show_additional_grid:
        CA_ticks_additional = np.log10(np.array([20, 50, 100, 500, 1000, 5E3, 10E3, 4E4, 10E4]))
    else:
        CA_ticks_additional = []
    ax.set_xticks(np.sort(np.concatenate([CA_ticks, CA_ticks_additional])))
    # CA axis actual names at the ticks
    if show_reduced_pop_dens:
        ax.set_xticklabels(['', 1, 3, 8, 20, ''])        
    elif not show_additional_grid:
        ax.set_xticklabels(['', 6.5,   200, 2000, '20k', '66k'])
    else:
        ax.set_xticklabels(['', '6.5\n1 m\n25 m/s', '20\nCannot be\nachieved', '50\n0.5 m\n35 m/s', '100\n1.2 m\n35 m/s', '200\n3 m\n35 m/s', '500\n1.6 m\n75 m/s', '1k\n3.9 m\n75 m/s', '2k\n8 m\n75 m/s', '5k\n4.5 m\n150 m/s', '10k\n9.5 m\n150 m/s', '20k\n20 m\n150 m/s', '40k\n22 m\n200 m/s', '66k\n36 m\n200 m/s'])

    # pop_density axis tick values in log10
    if show_reduced_pop_dens:
        pop_density_ticks = np.array([-2, -1, np.log10(300), np.log10(15000), 5.7])
    else:
        pop_density_ticks = np.array([-2, -1, 1,    2,   3.167,  4.167,       5,    5.7])
    if show_additional_grid:
        pop_density_ticks_additional = np.log10(np.array([1, 5, 20, 50, 200, 400, 800, 3E3, 8E3, 30E3, 60E3]))
    else:
        pop_density_ticks_additional = []
    ax.set_yticks(np.sort(np.concatenate([pop_density_ticks, pop_density_ticks_additional])))
    # pop_density axis actual names at the ticks
    if not show_additional_grid:
        if show_reduced_pop_dens:
            ax.set_yticklabels(['', 0.1, 300, '15k', '500k'])
        else:
            ax.set_yticklabels(['', 0.1,       10,         100,                1500,             '15k',               '100k', '500k'])
    else:
        ax.set_yticklabels(['', 0.1, 1, 5, 10, 20, 50, 100, 200, 400, 800, 1500, '3k', '8k', '15k', '30k', '60k', '100k', '500k'])
    
    if show_additional_grid:
        ax.tick_params(axis='both', which='major', labelsize=7)
    else:
        ax.tick_params(axis='both', which='major', labelsize=9)

    # Show vertical and horizontal lines corresponding to the tick marks
    for k in CA_ticks:
        if k < math.log10(7) or show_reduced_pop_dens:
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
    #    ax.plot([math.log10(6.5), math.log10(6.5)], [math.log10(pop_density[0]), math.log10(pop_density[-1])], color='white')
    #    ax.plot([math.log10(200), math.log10(200), math.log10(120), math.log10(120), math.log10(200), math.log10(200)], [math.log10(pop_density[0]), math.log10(500), math.log10(500), math.log10(100000), math.log10(100000), math.log10(500000)], color='white')
    #    ax.plot([math.log10(2000), math.log10(2000), math.log10(700), math.log10(700), math.log10(2000), math.log10(2000)], [math.log10(pop_density[0]), math.log10(500), math.log10(500), math.log10(100000), math.log10(100000), math.log10(500000)], color='white')
    #    ax.plot([math.log10(20000), math.log10(20000), math.log10(7000), math.log10(7000), math.log10(20000), math.log10(20000)], [math.log10(pop_density[0]), math.log10(500), math.log10(500), math.log10(100000), math.log10(100000), math.log10(500000)], color='white')
    #    ax.plot([math.log10(66000), math.log10(66000)], [math.log10(pop_density[0]), math.log10(pop_density[-1])], color='white')

    for k in pop_density_ticks:
        ax.plot([math.log10(CA[0]), math.log10(CA[-1])], [k, k], color='white')
    for k in pop_density_ticks_additional:
        ax.plot([math.log10(CA[0]), math.log10(CA[-1])], [k, k], color='black', linestyle='--')

    # Insert the iGRC table numbers in the middle between the white lines
    if not show_reduced_pop_dens:
        x = np.diff(CA_ticks) / 2 + CA_ticks[0:5:1]
        y = np.diff(pop_density_ticks) / 2 + pop_density_ticks[0:7:1]

        for k, xv in enumerate(x, start=2):
            for j, yv in enumerate(y):
                a = k+j
                if (j == 0):
                    a = a - 1
                if (j < 6):
                    txt = '{}'.format(a)
                else:
                    if (k == 2):
                        txt = '7*'
                    else:
                        txt = ''
                ax.text(xv, yv, txt, ha='center', va='center', color='white', weight='bold', fontsize='9')

        ax.text(2.9, 5.4, "Not in SORA", ha='center', va='center', color='white', weight='bold', fontsize='9')


    # Locations for the band value numbers
    bands_x = [ 0.4,  1.4,  2.5,  3.5,  4.4, 4.4, 4.4, 4.4, 4.4, 4.4, 4.4, 4.4]
    bands_y = [-1.7, -1.7, -1.7, -1.7, -1.7,-0.7, 0.3, 1.3, 2.3, 3.4, 4.4, 5.4]

    for k in range(len(bands_x)):
        if k < 8:
            clr = 'yellow'
        else:
            clr = 'black'
        ax.text(bands_x[k], bands_y[k], '{}'.format(k), color=clr, weight='bold', fontsize='8')

    ax.set_ylabel('Population density [ppl/km$^2$]', fontsize='11')
    if show_reduced_pop_dens:
        ax.set_xlabel('Wingspan [m]', fontsize='11')
    elif not show_additional_grid:
        ax.set_xlabel('Critical area [m$^2$]', fontsize='11')
    else:
        ax.set_xlabel('Critical area [m$^2$]\nWing span [m ]\nSpeed [m/s]', fontsize='11')

    # Set axis limits
    ax.set_xlim(math.log10(CA[0]), math.log10(CA[-1]))
    ax.set_ylim(math.log10(pop_density[-1]), math.log10(pop_density[0]))

    plt.show()
    
    # Use this to generate a PNG file of the plot
    if show_additional_grid:
        fig.savefig('iGRC_CA_vs_pop_density_additional_grid.png', format='png', dpi=300)
    else:
        fig.savefig('iGRC_CA_vs_pop_density.png', format='png', dpi=300)

if __name__ == '__main__':
    figure_iGRC_CA_vs_PopDensity()
