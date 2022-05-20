"""
Example 10
---------
This examples shows the use of the ground risk buffer calculator.
This is still work in progress.
"""
from casex import enums, AircraftSpecs, GroundRiskBuffer
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from shapely.geometry.polygon import LinearRing, Polygon
from descartes import PolygonPatch

# Set aircraft values.
aircraft_type = enums.AircraftType.GENERIC
width = 3.2
length = 1
mass = 150

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, length, mass)
aircraft.set_ballistic_frontal_area(1)
aircraft.set_ballistic_drag_coefficient(0.9)
aircraft.set_cruise_speed(25)

latency = 10 # seconds
behavior = 10 # seconds

GRB = GroundRiskBuffer(latency, behavior)

# The max range in meters divided by the scale
max_range = 180

# The scaling of the distributio matrix (each cell will be scale by scale meters).
scale = 10

wind_max = 5
altitude = 40

# Fraction of cases the "stays" in the corridor
corridor_fraction = 0.8

# Used for finding the distance within which
# this fraction of cases will crash.
fraction_for_dist = [0.9, 0.99]

resolutions = [2, 2, 2, 2]
#resolutions = [8, 2, 8, 8]
#resolutions = [15, 3, 12, 13]
#resolutions = [41, 5, 15, 18]
#resolutions = [90, 7, 80, 40]

if True:
    delay_list = np.array([5, 10, 15, 20, 25, 30])
    aircraft_speed_list = np.array([5, 10, 15, 20, 25, 30, 40, 50])

    M_wc = np.zeros((delay_list.size, aircraft_speed_list.size, 2))
    M_cc = np.zeros((delay_list.size, aircraft_speed_list.size, 2))

    GRB.set_behavior(0)
    for d_idx, delay in enumerate(delay_list):
        GRB.set_latency(delay)
        for a_idx, aircraft_speed in enumerate(aircraft_speed_list):
            aircraft.set_cruise_speed(aircraft_speed)
            M_wc[d_idx][a_idx] = GRB.distance_from_ops_volume(resolutions, max_range, scale, aircraft, altitude, wind_max, 0, fraction_for_dist)[5]
            M_cc[d_idx][a_idx] = GRB.distance_from_ops_volume(resolutions, max_range, scale, aircraft, altitude, wind_max, corridor_fraction, fraction_for_dist)[5]

    print("Standard scenario 90%/99%");
    print("Altitude {:3.0f} m, wind {:2.0f} m/s".format(altitude, wind_max))
    print('     ', end='');
    for k, v in enumerate(aircraft_speed_list):
        print('{:5.0f}'.format(v), end='')
    print(' m/s');
    for k, v in enumerate(delay_list):
        print('{:2.0f} s '.format(v), end = '')
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_wc[k, k2, 0]), end='')
        print('')
        print('     ', end='');
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_wc[k, k2, 1]), end='')
        print('')
        
    print("Corridor scenario 90%/99% (80% corridor + 20% standard)");
    print("Altitude {:3.0f} m, wind {:2.0f} m/s".format(altitude, wind_max))
    print('     ', end='');
    for k, v in enumerate(aircraft_speed_list):
        print('{:5.0f}'.format(v), end='')
    print(' m/s');
    for k, v in enumerate(delay_list):
        print('{:2.0f} s '.format(v), end = '')
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_cc[k, k2, 0]), end='')
        print('')
        print('     ', end='');
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_cc[k, k2, 1]), end='')
        print('')
        
else:
    distribution, PDF_dist, CDF_dist, x_axis_PDF, x_axis_CDF, dist_fraction, \
        distribution_wc, distribution_cc = GRB.distance_from_ops_volume(resolutions, max_range,
        scale, aircraft, altitude, wind_max, corridor_fraction, fraction_for_dist)

    fig, axs = plt.subplots(1)
    axs.imshow(distribution, extent=np.array([-max_range, max_range, max_range, -max_range]) * scale)
    plt.show()
   
    fig, axs = plt.subplots(1, 2)
    for j in range(2):
        for label in (axs[j].get_xticklabels() + axs[j].get_yticklabels()):
            label.set_fontsize(14)

    if (corridor_fraction == 0):
        [FG, CV, Buffer1, Buffer2] = GRB.AreaPolygons(np.amax(PDF_dist), max_range * scale, dist_fraction, corridor_fraction)
        axs[0].add_patch(PolygonPatch(Buffer1, fc='#ff0000', ec='#ff0000', alpha=0.5, linewidth = 0))
        axs[0].add_patch(PolygonPatch(Buffer2, fc='#ff0000', ec='#ff0000', alpha=0.8))
        axs[0].add_patch(PolygonPatch(CV, fc='#ffff00', ec='#ffff00', alpha=0.7))
        axs[0].add_patch(PolygonPatch(FG, fc='#00ff00', ec='#00ff00', alpha=0.7))
        [FG, CV, Buffer1, Buffer2] = GRB.AreaPolygons(1, max_range * scale, dist_fraction, corridor_fraction)
        axs[1].add_patch(PolygonPatch(Buffer1, fc='#ff0000', ec='#ff0000', alpha=0.5))
        axs[1].add_patch(PolygonPatch(Buffer2, fc='#ff0000', ec='#ff0000', alpha=0.8))
        axs[1].add_patch(PolygonPatch(CV, fc='#ffff00', ec='#ffff00', alpha=0.7))
        axs[1].add_patch(PolygonPatch(FG, fc='#00ff00', ec='#00ff00', alpha=0.7))
    else:
        [FG, CV, Buffer1, Buffer2] = GRB.AreaPolygons(np.amax(PDF_dist), max_range * scale, dist_fraction, 1)
        axs[0].add_patch(PolygonPatch(Buffer1, fc='#ff0000', ec='#ff0000', alpha=0.5, linewidth = 0))
        axs[0].add_patch(PolygonPatch(Buffer2, fc='#ff0000', ec='#ff0000', alpha=0.8, linewidth = 0))
        axs[0].add_patch(PolygonPatch(CV, fc='#ffff00', ec='#ffff00', alpha=0.7, linewidth = 0))
        axs[0].add_patch(PolygonPatch(FG, fc='#00ff00', ec='#00ff00', alpha=0.7, linewidth = 0))
        [FG, CV, Buffer1, Buffer2] = GRB.AreaPolygons(np.amax(PDF_dist), max_range * scale, dist_fraction, -1)
        axs[0].add_patch(PolygonPatch(Buffer1, fc='#ff0000', ec='#ff0000', alpha=0.5, linewidth = 0))
        axs[0].add_patch(PolygonPatch(Buffer2, fc='#ff0000', ec='#ff0000', alpha=0.8, linewidth = 0))
        axs[0].add_patch(PolygonPatch(CV, fc='#ffff00', ec='#ffff00', alpha=0.7, linewidth = 0))
        axs[0].add_patch(PolygonPatch(FG, fc='#00ff00', ec='#00ff00', alpha=0.7, linewidth = 0))
        [FG, CV, Buffer1, Buffer2] = GRB.AreaPolygons(1, max_range * scale, dist_fraction, 1)
        axs[1].add_patch(PolygonPatch(Buffer1, fc='#ff0000', ec='#ff0000', alpha=0.5, linewidth = 0))
        axs[1].add_patch(PolygonPatch(Buffer2, fc='#ff0000', ec='#ff0000', alpha=0.8, linewidth = 0))
        axs[1].add_patch(PolygonPatch(CV, fc='#ffff00', ec='#ffff00', alpha=0.7, linewidth = 0))
        axs[1].add_patch(PolygonPatch(FG, fc='#00ff00', ec='#00ff00', alpha=0.7, linewidth = 0))
        
    axs[0].plot(x_axis_PDF, PDF_dist, linewidth=3, label = "Distribution of crashes")
    axs[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
    axs[0].legend(loc="upper right", fontsize=14)
    axs[0].set_ylabel("Fraction of total crashes", fontsize = 16)
    axs[0].set_xlabel("Distance from flyaway point [m]", fontsize = 16)
    
    axs[1].plot(x_axis_CDF, CDF_dist, 'b', label = "Accumulated distribution", linewidth=3)
    axs[1].plot([x_axis_CDF[0], dist_fraction[0]], np.array([1, 1]) * fraction_for_dist[0],'k--', linewidth=2, label = "{:1.0f}% of all cases at {:1.0f} m".format(fraction_for_dist[0] * 100, dist_fraction[0]))
    axs[1].plot([x_axis_CDF[0], dist_fraction[1]], np.array([1, 1]) * fraction_for_dist[1],'k-.', linewidth=2, label = "{:1.0f}% of all cases at {:1.0f} m".format(fraction_for_dist[1] * 100, dist_fraction[1]))
    axs[1].plot([dist_fraction[0], dist_fraction[0]], [0, fraction_for_dist[0]], 'k--', linewidth=2)
    axs[1].plot([dist_fraction[1], dist_fraction[1]], [0, fraction_for_dist[1]], 'k-.', linewidth=2)
    axs[1].legend(loc="lower right", fontsize=14)
    axs[1].set_yticks(np.linspace(0, 1, 11))
    axs[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axs[1].set_xlabel("Distance from flyaway point [m]", fontsize = 16)
    axs[1].set_ylabel("Fraction of total crashes", fontsize = 16)
    plt.show()
    
    if (corridor_fraction > 0):
        fig.suptitle('Crash distribution for corridor', fontsize = 20)
        fig.savefig('Flyaway and crash - corridor.png', format='png', dpi=300)
    else:
        fig.suptitle('Crash distribution for standard', fontsize = 20)
        fig.savefig('Flyaway and crash - standard.png', format='png', dpi=300)
