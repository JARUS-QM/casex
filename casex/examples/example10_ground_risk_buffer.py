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
from scipy.optimize import curve_fit

def evaluate_polynomial_2nd_order(x, *coeffs):
    """
    Evaluate a 2nd order polynomial in two variables.

    Args:
        x (float): The value of the first variable.
        y (float): The value of the second variable.
        coeffs (list): The coefficients of the polynomial in the form [c00, c10, c01, c20, c11, c02, c21, c12, c22],
                       where cij represents the coefficient of x^i * y^j.

    Returns:
        float: The value of the polynomial at the given (x, y) coordinates.
    """
    c00, c10, c01, c20, c11, c02, c21, c12, c22 = coeffs
    return c00 + c10 * x[0] + c01 * x[1] + c20 * x[0]**2 + c11 * x[0] * x[1] + c02 * x[1]**2 + c21 * x[0]**2 * x[1] + c12 * x[0] * x[1]**2 + c22 * x[0]**2 * x[1]**2
    
def evaluate_multivariate_polynomial(variables, *coefficients):
    """
    Evaluates a second-order multivariate polynomial in four variables.

    Arguments:
    coefficients -- a list of coefficients in the following order: [c, cx, cy, cz, cw, cxx, cyy, czz, cww, cxy, cxz, cyz, cxw, cyw, czw]
    variables -- a list of variable values in the following order: [x, y, z, w]

    Returns:
    The evaluated result of the multivariate polynomial.
    """
    c, cx, cy, cz, cw, cxx, cyy, czz, cww, cxy, cxz, cyz, cxw, cyw, czw = coefficients
    x, y, z, w = variables

    result = c + cx * x + cy * y + cz * z + cw * w + cxx * (x ** 2) + cyy * (y ** 2) + czz * (z ** 2) + cww * (w ** 2) + cxy * x * y + cxz * x * z + cyz * y * z + cxw * x * w + cyw * y * w + czw * z * w
    return result

def GRB_estimator(delay, speed, altitude, wind):
    coeffs = np.array([-5.07952058e+01,  4.80032525e+00,  2.93940667e+00 , 1.17064114e-01,
        -8.22230251e-01, -3.14982379e-02, -1.30952381e-02, -4.70085472e-04,
        -1.25000000e-02,  4.96649846e-01,  4.59578387e-03, -4.36964714e-03,
        -7.01991008e-02,  2.98333333e-01,  1.14583333e-02])
    y_eval = evaluate_multivariate_polynomial((delay, speed, altitude, wind), *coeffs)
    return y_eval

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

# The scaling of the distribution matrix (each cell will be scale by scale meters).
scale = 10

#wind_max_list = np.array([5, 7.5, 10, 12.5, 15])
#altitude_list = np.array([40, 70, 100, 200, 300])

wind_max_list = np.array([12])
altitude_list = np.array([10])

# Fraction of cases the "stays" in the corridor
corridor_fraction = 0.8

# Used for finding the distance within which
# this fraction of cases will crash.
fraction_for_dist = [0.9, 0.99]

#resolutions = [2, 2, 2, 2]
resolutions = [8, 2, 8, 8]
#resolutions = [15, 3, 12, 13]
#resolutions = [41, 5, 15, 18]
#resolutions = [90, 7, 80, 40]


if True:
    delay_list = np.array([5, 10, 15, 20, 25, 30])
    aircraft_speed_list = np.array([5, 10, 15, 20, 25, 30, 40, 50])

    GRB.set_behavior(0)
    delay = 25
    speed = 40
    altitude = 300
    wind = 5
    print(GRB_estimator(delay, speed, altitude, wind))
    aircraft.set_cruise_speed(speed)
    GRB.set_latency(delay)
    print(GRB.distance_from_ops_volume(resolutions, max_range, scale, aircraft, altitude, wind, 0, fraction_for_dist)[5])
    #quit()

    M_wc = np.zeros((delay_list.size, aircraft_speed_list.size, altitude_list.size, wind_max_list.size, 2))
    M_cc = np.zeros((delay_list.size, aircraft_speed_list.size, altitude_list.size, wind_max_list.size, 2))

    for d_idx, delay in enumerate(delay_list):
        GRB.set_latency(delay)
        for s_idx, aircraft_speed in enumerate(aircraft_speed_list):
            aircraft.set_cruise_speed(aircraft_speed)
            for a_idx, altitude in enumerate(altitude_list):
                for w_idx, wind_max in enumerate(wind_max_list):
                    M_wc[d_idx][s_idx][a_idx][w_idx] = GRB.distance_from_ops_volume(resolutions, max_range, scale, aircraft, altitude, wind_max, 0, fraction_for_dist)[5]
                    M_cc[d_idx][s_idx][a_idx][w_idx] = GRB.distance_from_ops_volume(resolutions, max_range, scale, aircraft, altitude, wind_max, corridor_fraction, fraction_for_dist)[5]

    print("Standard scenario 90%/99%");
    print("Altitude {:3.0f} m, wind {:2.0f} m/s".format(altitude_list[0], wind_max_list[0]))
    print('     ', end='');
    for k, v in enumerate(aircraft_speed_list):
        print('{:5.0f}'.format(v), end='')
    print(' m/s');
    for k, v in enumerate(delay_list):
        print('{:2.0f} s '.format(v), end = '')
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_wc[k, k2, 0, 0, 0]), end='')
        print('')
        print('     ', end='');
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_wc[k, k2, 0, 0, 1]), end='')
        print('')
        
    print("Corridor scenario 90%/99% (80% corridor + 20% standard)");
    print("Altitude {:3.0f} m, wind {:2.0f} m/s".format(altitude_list[0], wind_max_list[0]))
    print('     ', end='');
    for k, v in enumerate(aircraft_speed_list):
        print('{:5.0f}'.format(v), end='')
    print(' m/s');
    for k, v in enumerate(delay_list):
        print('{:2.0f} s '.format(v), end = '')
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_cc[k, k2, 0, 0, 0]), end='')
        print('')
        print('     ', end='');
        for k2, v2 in enumerate(aircraft_speed_list):
            print('{:5.0f}'.format(M_cc[k, k2, 0, 0, 1]), end='')
        print('')
        
    X1, X2, X3, X4 = np.meshgrid(aircraft_speed_list, delay_list, altitude_list, wind_max_list)
    
    # Flatten the input variables
    x1_flat = X1.flatten()
    x2_flat = X2.flatten()        
    x3_flat = X3.flatten()
    x4_flat = X4.flatten()        
    y_flat = M_cc[:, :, :, :, 0].flatten()

    initial_guess = [1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # Initial guess for the coefficients
    popt, pcov = curve_fit(evaluate_multivariate_polynomial, (x1_flat, x2_flat, x3_flat, x4_flat), y_flat, p0=initial_guess)    

    # Print the fitted coefficients
    #print("Fitted coefficients:")
    #for i, coeff in enumerate(popt):
    #    indices = np.unravel_index(i, (3, 3))
    #    print(f"Coefficient for x1^{indices[0]} * x2^{indices[1]} * x3^{indices[2]} * x4^{indices[3]}: {coeff}")
    
    print(popt)
    
    # Make a grid for the resulting polynomial and evaluate in the grid (for plotting a surface).
    X1_data, X2_data = np.meshgrid(aircraft_speed_list, delay_list)
    X1_eval, X2_eval = np.meshgrid(np.linspace(aircraft_speed_list[0], aircraft_speed_list[-1], 100), np.linspace(delay_list[0], delay_list[-1], 100))

    y_eval = evaluate_multivariate_polynomial((X1_eval.flatten(), X2_eval.flatten(), altitude_list[0], wind_max_list[0]), *popt)
    Y_eval = y_eval.reshape(X1_eval.shape)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(X1_data, X2_data, M_cc[:, :, 0, 0, 0], c="b", label="Original data")
    ax.plot_surface(X1_eval, X2_eval, Y_eval, color="r", alpha=0.5, label="Fitted polynomial")
    ax.set_xlabel("Speed (m/s)")
    ax.set_ylabel("Delay (s)")
    ax.set_zlabel("Y")
    plt.show()

    X1_data, X2_data = np.meshgrid(altitude_list, wind_max_list)
    X1_eval, X2_eval = np.meshgrid(np.linspace(altitude_list[0], altitude_list[-1], 100), np.linspace(wind_max_list[0], wind_max_list[-1], 100))

    y_eval = evaluate_multivariate_polynomial((delay_list[4], aircraft_speed_list[6], X1_eval.flatten(), X2_eval.flatten()), *popt)
    Y_eval = y_eval.reshape(X1_eval.shape)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(X1_data, X2_data, M_cc[4, 6, :, :, 0], c="b", label="Original data")
    ax.plot_surface(X1_eval, X2_eval, Y_eval, color="r", alpha=0.5, label="Fitted polynomial")
    ax.set_xlabel("Altitude (m)")
    ax.set_ylabel("Wind (m/s)")
    ax.set_zlabel("Y")
    plt.show()

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

