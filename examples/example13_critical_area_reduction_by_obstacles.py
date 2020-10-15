import platform
import matplotlib.pyplot as plt
import numpy as np

import casex

# Abbreviate this, as it is used several times
from casex.enums import ECriticalAreaModel as Model

def example13_critical_area_reduction_by_obstacles():
    
    # Data on person size
    person_width = 0.3
    person_height = 1.8
    
    CA = casex.critical_area_models.CCriticalAreaModels(person_width, person_height)
    
    width = 2
    obstacles_per_CA = np.array([0.5,1,3,5])
    distance_glide_slide = 100
    trials_count = 10000
    resolution = 100

    #obstacle_density = np.array([50000, 100000, 200000, 300000])
    obstacle_density = obstacles_per_CA * 1000000 / width / distance_glide_slide
 
    num_bins = int(round(4 * np.sqrt(trials_count)))
    bins = np.linspace(0, distance_glide_slide, num_bins)
   
    fig, ax = plt.subplots(2, 2, figsize=(12,6))
    
    c = 0
    for k in range(2):
        for j in range (2):
            y, no_obstacles_in_CA = CA.simulate_minimum_CDF(obstacle_density[c], width, distance_glide_slide, trials_count)
            y2, x, p_none, Ac_reduced = CA.compute_minimum_CDF(obstacle_density[c], width, distance_glide_slide, resolution, 0.8)
            
            # Possion
            y3, x2, p_none2 = CA.compute_Poisson_CDF(obstacle_density[c], width, distance_glide_slide, resolution)
            print(obstacle_density[c]/1e6)
        
            ax[k,j].hist(y, bins, density=True, histtype='step', cumulative=True, label="Simulated {:1.0f} trials".format(trials_count), edgecolor='black', linewidth=2)
        
            ax[k,j].plot(x,  y3, '--', linewidth=1.5, label='Poisson')
            ax[k,j].plot(x,  y2, '--', linewidth=1.5, label='Minimum of uniforms')
        
            ax[k,j].set_title("Obstacle density: {:1.0f} per km^2 / {:1.1f} obstacles per CA".format(obstacle_density[c], obstacle_density[c] / 1e6 * width * distance_glide_slide), fontsize=11)
                
            c = c + 1
        
    ax[0,0].legend()
    ax[1,0].set_xlabel('Critical glide + slide length [m]')
    ax[1,1].set_xlabel('Critical glide + slide length [m]')
    ax[0,0].set_ylabel('Probability')
    ax[1,0].set_ylabel('Probability')
        
    fig.suptitle('Comparison of simulated and approximated CDF for CA of {:1.0f} m$^2$'.format(distance_glide_slide * width), fontsize=14)
        
    plt.show()

    fig.savefig('CA reduction simulation vs approximation examples.png', format='png', dpi=300)
    
if __name__ == '__main__':
    example13_critical_area_reduction_by_obstacles()
