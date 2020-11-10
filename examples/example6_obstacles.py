"""
Example 6
---------
MISSING DOC
"""
import numpy as np
import matplotlib.pyplot as plt

from casex import Obstacles

def example6_obstacles():
    # Wingspan or characteristic dimension of aircraft
    CA_width = 3
    
    # Nominal length (length of CA without obstacles)
    CA_length = 66.7

    houses_per_square_km = 800
    
    # Obtacle density in obstacles per square meter
    obstacle_density = houses_per_square_km / 1e6
    
    # Average width of house
    obstacle_width_mu = 23
    
    # Variation in house width
    obstacle_width_sigma = 6
    
    # Average house length
    obstacle_length_mu = 9
    
    # Variation in house length
    obstacle_length_sigma = 2

    # Target CA size (only used for graphics)
    CA_of_interest = 120

    # Instantiate Obstacles class
    OS = Obstacles(CA_width, CA_length, 0)

    # Set resolution along first axis
    # This does not need to be terribly high, since the resulting curve is always smooth
    x_resolution = 10
    x = np.linspace(0, CA_length, x_resolution)
    
    # Resolution of PDFs in computations. Higher res gives better accuracy, but also longer computation time. Value of 25 is usually good.
    pdf_resolution = 25
    
    # Compute the probability curve
    p_x, beta_analytical, sanity_check = OS.first_pdf(x, obstacle_density, obstacle_width_mu, obstacle_width_sigma, obstacle_length_mu, obstacle_length_sigma, pdf_resolution)
    
    # Compute probability for specific CA size (for graphics)
    p_x2 = OS.first_pdf(CA_of_interest / CA_width, obstacle_density, obstacle_width_mu, obstacle_width_sigma, obstacle_length_mu, obstacle_length_sigma, pdf_resolution)
    
    # Plot the curve and the target CA
    fig = plt.figure(1, figsize=(12, 8), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot(x * CA_width, p_x)
    ax.set_xlabel('Critical area [m$^2$]')
    ax.set_xlim([0, x[-1] * CA_width])
    ax.plot([0, CA_of_interest], [p_x2[0][0], p_x2[0][0]], '--', color='orange')
    ax.plot([CA_of_interest, CA_of_interest], [p_x[0], p_x2[0][0]], '--', color='orange')
    ax.set_ylim([p_x[0], 1])
    ax.set_ylabel('Probability')
    
    print('Probability of reduction to at most {:1.0f} m^2 is {:1.0f}%'.format(CA_of_interest, p_x2[0][0] * 100))
    
    plt.grid()

    plt.show()
    
    fig.savefig('Obstacles_CDF.png', format='png', dpi=300)
    
if __name__ == '__main__':
    example6_obstacles()