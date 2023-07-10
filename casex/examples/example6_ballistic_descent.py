"""
Example 6
---------
This example shows how to compute a series of values describing a ballistic
descent.
"""
import numpy as np
import matplotlib.pyplot as plt

from casex import BallisticDescent2ndOrderDragApproximation, enums, AircraftSpecs, AnnexFParms


# Instantiate necessary classes.
BDM = BallisticDescent2ndOrderDragApproximation()

# Set aircraft values.
aircraft_type = enums.AircraftType.FIXED_WING
width = 2.8
length = 3.2
mass = 90

# Instantiate and add data to AircraftSpecs class.
aircraft = AircraftSpecs(aircraft_type, width, length, mass)
aircraft.set_ballistic_drag_coefficient(0.8)
aircraft.set_ballistic_frontal_area(0.6 * 0.6)
BDM.set_aircraft(aircraft)

# Set initial values for the descent.
altitude = 100
initial_velocity_x = 28
initial_velocity_y = 0

# Compute ballistic descent values.
# Note that the return in p contains numerous different values.
p = BDM.compute_ballistic_distance(altitude, initial_velocity_x, initial_velocity_y)

print("Distance:     {:1.1f} m    ".format(p[0]))
print("Impact speed: {:1.1f} m/s".format(p[1]))
print("Angle:        {:1.1f} degs".format(p[2] * 180 / np.pi))
print("Time :        {:1.2f} s".format(p[3]))
print("Distances:    {:1.3f}  {:1.3f}  {:1.3f}".format(BDM.distance1, BDM.distance2, BDM.distance3))
print("Times:        {:1.3f}  {:1.3f}  {:1.3f}".format(BDM.time_top, BDM.time_cross, BDM.time_impact))
print("Speeds:       {:1.3f}  {:1.3f}".format(BDM.velocity_x, BDM.velocity_y))
print("")

# In the following, there are three examples, where horizontal velocity (first example), vertical velocity
# (second example), and drag coefficient (third example) are arrays rather than scalar.
altitude = 150
initial_velocity_x = np.linspace(0, 80, 100)
initial_velocity_y = np.linspace(-10, 10, 100)

aircraft.set_mass(100)
BDM.set_aircraft(aircraft)

# Array for horizontal velocity.
p_vel_x = BDM.compute_ballistic_distance(altitude, initial_velocity_x, -2)
# Array for vertical velocity.
p_vel_y = BDM.compute_ballistic_distance(altitude, 30, initial_velocity_y)

# Array for drag coefficient.
drag_coef = np.linspace(0.7, 1, 100)
aircraft.set_ballistic_drag_coefficient(drag_coef)
BDM.set_aircraft(aircraft)
p_drag_coef = BDM.compute_ballistic_distance(altitude, 30, -2)

# Set up figure.
fig, ax = plt.subplots(2, 2, figsize=(12, 6))
plt.style.use('fivethirtyeight')

ax[0, 0].plot(initial_velocity_x, p_vel_x[0], linewidth=2)
ax[0, 0].set_xlabel('Initial velocity X [m/s]', fontsize=12)
ax[0, 0].set_ylabel('Impact distance [m]', fontsize=12)
ax[0, 0].set_title('Impact distance for varying initial horizontal velocity', fontsize=14)

ax[0, 1].plot(initial_velocity_y, p_vel_y[1], linewidth=2)
ax[0, 1].set_xlabel('Initial velocity Y [m/s]', fontsize=12)
ax[0, 1].set_ylabel('Impact velocity [m/s]', fontsize=12)
ax[0, 1].set_title('Impact distance for varying initial vertical velocity', fontsize=14)

ax[1, 0].plot(drag_coef, p_drag_coef[2] * 180 / np.pi, linewidth=2)
ax[1, 0].set_xlabel('Drag coefficient [-]', fontsize=12)
ax[1, 0].set_ylabel('Angle [deg]', fontsize=12)
ax[1, 0].set_title('Impact angle for varying drag coefficient', fontsize=14)

ax[1, 1].plot(initial_velocity_y, p_drag_coef[3], linewidth=2)
ax[1, 1].set_xlabel('Initial velocity X [m/s]', fontsize=12)
ax[1, 1].set_ylabel('Descent time [s]', fontsize=12)
ax[1, 1].set_title('Descent time for varying initial vertical velocity', fontsize=14)

# Get the four scenario.
AFP = AnnexFParms()

print("Ballistic descent computations")
print("------------------------------")
print("Class   Init horiz     From     Terminal   Impact   Impact   Distance   Descent      KE")
print("          speed      altitude   velocity   speed    angle    traveled    time      impact")

for c in range(5):
    print("{:2d} m      {:3d} m/s     {:4d} m    {:3.0f} m/s   {:3.0f} m/s   {:1.0f} deg    {:4.0f} m     "
          "{:4.1f} s   {:6.0f} kJ".format(
        AFP.CA_parms[c].wingspan, AFP.CA_parms[c].cruise_speed, AFP.CA_parms[c].ballistic_descent_altitude,
        AFP.CA_parms[c].terminal_velocity, AFP.CA_parms[c].ballistic_impact_velocity,
        AFP.CA_parms[c].ballistic_impact_angle, AFP.CA_parms[c].ballistic_distance,
        AFP.CA_parms[c].ballistic_descent_time, AFP.CA_parms[c].ballistic_impact_KE / 1000))

plt.show()
