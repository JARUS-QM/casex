"""
This class allows for recreating some of the tables in Annex F :cite:`a-JARUS_AnnexF`.
"""
import numpy as np
import math
import warnings
from casex import enums, FrictionCoefficients, CriticalAreaModels, AircraftSpecs, AnnexFParms

class AnnexFTables:
    """This class contains methods for generating a variety of tables in Annex F :cite:`a-JARUS_AnnexF`.

    Parameters
    ----------
    none.

    Attributes
    ----------
    none.
    """
 
    @staticmethod
    def iGRC_tables(show_with_obstacles = True,
                    show_ballistic = False,
                    show_with_conservative_compensation = True,
                    show_glide_angle = False,
                    show_additional_pop_density = False):
        """Compute the iGRC tables Annex F :cite:`a-JARUS_AnnexF`.
        
        Produces console output to show the iGRC tables in a variety of forms.
        The default setup will produce the nominal iGRC table.
        
        Parameters
        ----------
        show_with_obstacles : bool, optional
            If true, show iGRC values when obstacles are present. Default True.
        show_ballistic : bool, optional
            If true, show iGRC values for ballistic descent (typically rotorcraft). This superseeds show_glide_angle.
            Default False.
        show_with_conservative_compensation : bool, optional
            If true, subtract 0.3 from all values. The concept is explained in Annex F. Default True.
        show_glide_angle : bool, optional
            If true, show for 10 degree impact angle instead of 35 degree. Default False.
        show_additional_pop_density : bool, optional
            If true, show additional population density rows. Default False.
            
        Returns
        -------
        console_output : list of strings
            The output to show.
        """
        
        
        # Set impact angle.
        impact_angle = AnnexFParms.scenario_angles[0] if show_glide_angle else AnnexFParms.scenario_angles[1]
        
        # Instantiate necessary classes.
        CA = CriticalAreaModels()
        AFP = AnnexFParms()
        
        # Instantiate and add data to AircraftSpecs class.
        # Values are not relevant here, since they will be changed below.
        aircraft = AircraftSpecs(enums.AircraftType.GENERIC, 1, 1)
        
        # Friction coefficient from Annex F.
        aircraft.set_friction_coefficient(AFP.friction_coefficient)
        
        # Set parameters for fuel
        aircraft.set_fuel_type(enums.FuelType.GASOLINE)
        aircraft.set_fuel_quantity(0)
        
        # Set list of population density bands in the table.
        pop_density = np.array([0.25, 25, 250, 2500, 25000, 250000, 2500000])
        
        if show_additional_pop_density:
            pop_density = np.append(pop_density, [7.5, 75, 750, 7500, 750000, 750000])
        
        pop_density = np.sort(pop_density)
        
        # Initialize variables.,
        iGRC_table = np.zeros((len(pop_density), 5))
        impact_angles = np.zeros((5))
        p = np.zeros((5, 9))
        
        # Loop over columns in the iGRC table.
        for j in range(0, 5):
            
            # Set mass according to Annex F.
            aircraft.set_mass(AFP.CA_parms[j].mass)
        
            # First, set width and speed to nominal values.
            aircraft.set_width(AFP.CA_parms[j].wingspan)
            
            if show_ballistic:
                impact_speed = AFP.CA_parms[j].ballistic_impact_velocity
                impact_angle = AFP.CA_parms[j].ballistic_impact_angle
            else:
                impact_speed = AFP.CA_parms[j].glide_speed if show_glide_angle else AFP.CA_parms[j].cruise_speed
        
            aircraft.set_coefficient_of_restitution(AnnexFParms.CoR_from_impact_angle(impact_angle))
        
            # Compute the CA.
            p[j] = CA.critical_area(aircraft, impact_speed, impact_angle, use_obstacle_reduction = show_with_obstacles)
            
            # Store the impact angle (only relevant for ballistic).
            impact_angles[j] = impact_angle
        
        # Compute the iGRC values.
        for i in range(len(pop_density)):
            for j in range(0, 5):
                iGRC_table[i][j] = AFP.iGRC(pop_density[i],
                                            p[j][0],
                                            width = AFP.CA_parms[j].wingspan,
                                            use_conservative_compensation = show_with_conservative_compensation)[1]
        console_output = []
        
        s = "iGRC table"
        s = s + " (ballistic)" if show_ballistic else s + " ({:d} deg)".format(impact_angle)
        console_output.append(s)
            
        console_output.append("                          1 m       3 m       8 m      20 m      40 m")
        console_output.append("--------------------+-------------------------------------------------")
        
        for i in range(len(pop_density)):
            
            if (pop_density[i] > 1):
                s = "{:7.0f} [ppl/km^2]  | ".format(pop_density[i])
            else:
                s = "Controlled (< 0.25) | "
         
            for j in range(0, 5):
                s = s + "{:7.1f}   ".format(iGRC_table[i][j])
            
            console_output.append(s)
            
        console_output.append("--------------------+-------------------------------------------------")
        
        s = "     CA size [m^2]  |"
        for j in range(0, 5):
            s = s + "{:8.0f}  ".format(p[j][0])
        console_output.append(s)
        
        s = "Slide distance [m]  |"
        for j in range(0, 5):
            s = s + "{:8.0f}  ".format(p[j][2] / AFP.CA_parms[j].wingspan)
        console_output.append(s)
        
        if show_ballistic:
            s = "Impact angle [deg]  |"
            for j in range(0, 5):
                s = s + "{:8.0f}  ".format(impact_angles[j])
            console_output.append(s)
            
            s = "Altitude [m]        |    "
            for k in range(5):
                s = s + "{:4.0f}      ".format(AFP.CA_parms[k].ballistic_descent_altitude)
            console_output.append(s)
            
            s = "Impact angle [deg]  |    "
            for k in range(5):
                s = s + "{:4.1f}      ".format(AFP.CA_parms[k].ballistic_impact_angle)
            console_output.append(s)
        
            s = "Impact vel [m/s]    |   "    
            for k in range(5):
                s = s + "{:5.1f}     ".format(AFP.CA_parms[k].ballistic_impact_velocity)
            console_output.append(s)
        
            s = "Drag area [m^2]     |    "
            for k in range(5):
                s = s + "{:4.1f}      ".format(AFP.CA_parms[k].ballistic_frontal_area)
            console_output.append(s)
                
        console_output.append("--------------------+-------------------------------------------------")
    
        return console_output
    
    
    @staticmethod
    def iGRC_tradeoff_tables(tradeoff_type, show_integer_iGRC, show_relative):
        """Compute the iGRC tradeoff tables Annex F :cite:`a-JARUS_AnnexF`.
        
        Produces console output to show the iGRC tradeoff tables.
        
        The tables can be shown with integer iGRC values (rounded up to nearest integer) and with one
        decimal. The latter makes it easier to determine how close the iGRC value is to the lower integer.
        
        The tables can also be shown relative to the nominal table. Here positive values are iGRC values above the nominal
        and negative below nominal.
        
        Parameters
        ----------
        tradeoff_type : integer
            If 0, produces the nominal iGRC table.
            For n = 1 through 6 produces the corresponding Tn table, as described in Annex F.
            For any other value, an error text is produced.
        show_integer_iGRC : bool
            If True, show the iGRC values rounded up to nearest integer. Otherwise, show with one decimal.
            This only applies to actual iGRC values. Relative values are always shown with one decimal.
        show_relative: bool
            If True, the table shows the difference between nominal iGRC values and values for the tradeoff table.
            The numbers are always shown with one decimal. 
            
        Returns
        -------
        console_output : list of strings
            The output to show.
        """
        
        console_output = []
        
        # Data on person size.
        person_radius = 0.3
        person_height = 1.8
        
        # Instantiate necessary classes.
        CA = CriticalAreaModels(person_radius, person_height)
        
        # Instantiate the Annex F parameter class.
        AFP = AnnexFParms()
        
        # The impact angle is from scenario 2, glide impact
        impact_angle = AnnexFParms.scenario_angles[1]
        
        # Instantiate and add data to AircraftSpecs class.
        # Note that the values here are not important, since they will be changed below.
        aircraft = AircraftSpecs(enums.AircraftType.GENERIC, 1, 1, 1)
        
        # Friction coefficient from Annex F
        aircraft.set_friction_coefficient(AFP.friction_coefficient)
        
        # Set parameters for fuel.
        aircraft.set_fuel_type(enums.FuelType.GASOLINE)
        aircraft.set_fuel_quantity(0)
        
        # Get CoR using the aircraft class.
        aircraft.set_coefficient_of_restitution(AnnexFParms.CoR_from_impact_angle(impact_angle))
        
        # Set the appropriate changes for each type of trade-off.
        if tradeoff_type == 0:
            width_factor        = 1
            impact_speed_factor = 1
            Dpop_factor         = 1
        elif tradeoff_type == 1:
            width_factor        = 1     
            impact_speed_factor = 1.4  
            Dpop_factor         = 0.5                             
        elif tradeoff_type == 2:
            width_factor        = 2   
            impact_speed_factor = 1        
            Dpop_factor         = 0.5                             
        elif tradeoff_type == 3:
            width_factor        = 0.5 
            impact_speed_factor = 1      
            Dpop_factor         = 2                            
        elif tradeoff_type == 4:
            width_factor        = 0.5
            impact_speed_factor = 1.4
            Dpop_factor         = 1                               
        elif tradeoff_type == 5:
            width_factor        = 1      
            impact_speed_factor = 0.75 
            Dpop_factor         = 1.7                       
        elif tradeoff_type == 6:
            width_factor        = 1.7
            impact_speed_factor = 0.75   
            Dpop_factor         = 1                            
        else:
            return "tradeoff_type value not legal."
            
        if tradeoff_type > 0:
            console_output.append("Modified raw iGRC table for trade-off scenario T{:1}".format(tradeoff_type))
        else:
            console_output.append("Original raw iGRC table")
            
        if show_relative:
            console_output.append("Table show difference to the original raw iGRC table.")
        
        s = "             Max dim   |  "
        for j in range(0, 5):
            s = s + "{:4.1f} m    ".format(AFP.CA_parms[j].wingspan * width_factor)
        console_output.append(s)                                                                    
        
        s = "Dpop         Max speed |"        
        for j in range(0, 5):
            s = s + "{:4} m/s  ".format(int(AFP.CA_parms[j].cruise_speed * impact_speed_factor))
        console_output.append(s)
        
        console_output.append("-----------------------+--------------------------------------------------")
        
        for Dpop in [0.25, 25, 250, 2500, 25000, 250000, 250001]:
            
            if (Dpop > 1):
                s = "    {:6} ppl/km^2    |   ".format(int(Dpop * Dpop_factor))
            else:
                s = "         Controlled    |   "
        
            # Loop over columns in the iGRC table.
            for j in range(0, 5):
                
                # Set mass according to Annex F.
                aircraft.set_mass(AFP.CA_parms[j].mass)
        
                # First, set width and speed to nominal values.
                aircraft.set_width(AFP.CA_parms[j].wingspan)
                impact_speed = AFP.CA_parms[j].cruise_speed
        
                # Compute the AC using the angle for scenario 2 (glide impact angle)
                p_original = CA.critical_area(aircraft, impact_speed, impact_angle, use_obstacle_reduction = True)[0]
                
                # Then set to modified values.
                aircraft.set_width(AFP.CA_parms[j].wingspan * width_factor)
                impact_speed = AFP.CA_parms[j].cruise_speed * impact_speed_factor
            
                # And again, compute AC.
                p_trade_off = CA.critical_area(aircraft, impact_speed, impact_angle, use_obstacle_reduction = True)[0]
        
                # Compute the raw iGRC according to Annex F.
                raw_iGRC_original = AnnexFParms.iGRC(Dpop,
                                                     p_original,
                                                     use_conservative_compensation=True,
                                                     width=AFP.CA_parms[j].wingspan) 
                raw_iGRC_trade_off = AnnexFParms.iGRC(Dpop * Dpop_factor,
                                                      p_trade_off,
                                                      use_conservative_compensation=True,
                                                      width=AFP.CA_parms[j].wingspan) 
        
                if Dpop == 250001 and j > 0:
                    s = s + "  n/a     "
                else:                
                    if show_relative:
                        s = s + "{:4.1f}      ".format(raw_iGRC_trade_off[1] - raw_iGRC_original[1])
                    else:
                        if show_integer_iGRC:
                            s = s + "{:4.0f}      ".format(raw_iGRC_trade_off[1] - 0.1) # Subtracting 0.1 to reduce 2.1, 3.1, etc to 2, 3.
                        else:
                            s = s + "{:4.1f}      ".format(raw_iGRC_trade_off[1])
                
            console_output.append(s)
            
        if show_relative:
            console_output.append("Negative number means lower iGRC relative to nominal and positive means higher.")
            
        return console_output
    
    
    @staticmethod
    def ballistic_descent_table():
        """Compute the ballistic descent table in Annex F :cite:`a-JARUS_AnnexF`.
        
        Produces console output to show the ballistic descent table.
        
        Parameters
        ----------
        none.
            
        Returns
        -------
        console_output : list of strings
            The output to show.
        """
        
        console_output = []

        # Impact angle is not used, so just set to 0.
        AFP = AnnexFParms(0)

        console_output.append("Ballistic descent computations")
        console_output.append("---------------------------------------------------------------")

        s = "Class                  "
        for c in range(5):
            s = s + "{:2d} m     ".format(AFP.CA_parms[c].wingspan)
        console_output.append(s)

        s = "Frontal area [m2]      "
        for c in range(5):
            s = s + "{:4.1f}     ".format(AFP.CA_parms[c].ballistic_frontal_area)
        console_output.append(s)

        s = "Mass [kg]             "
        for c in range(5):
            s = s + "{:5d}    ".format(AFP.CA_parms[c].mass)
        console_output.append(s)

        s = "Init alt [m]           "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].ballistic_descent_altitude)
        console_output.append(s)

        s = "Velocity [m/s]         "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].cruise_speed)
        console_output.append(s)

        console_output.append("---------------------------------------------------------------")

        s = "Terminal vel [m/s]     "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].terminal_velocity)
        console_output.append(s)

        s = "Cruise KE [kJ]       "
        for c in range(5):
            s = s + "{:6.0f}   ".format(0.5*AFP.CA_parms[c].mass*AFP.CA_parms[c].cruise_speed*AFP.CA_parms[c].cruise_speed / 1000)
        console_output.append(s)

        s = "Impact velocity [m/s]  "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].ballistic_impact_velocity)
        console_output.append(s)

        s = "Impact angle [deg]     "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].ballistic_impact_angle)
        console_output.append(s)

        s = "Cof of restitution [-] "
        for c in range(5):
            s = s + "{:4.2f}     ".format(AnnexFParms.CoR_from_impact_angle(AFP.CA_parms[c].ballistic_impact_angle))
        console_output.append(s)

        s = "Hor distance [m]       "
        for c in range(5):
            s = s + "{:4.0f}     ".format(AFP.CA_parms[c].ballistic_distance)
        console_output.append(s)

        s = "Descent time [s]       "
        for c in range(5):
            s = s + "{:4.1f}     ".format(AFP.CA_parms[c].ballistic_descent_time)
        console_output.append(s)

        s = "Impact KE [kJ]        "
        for c in range(5):
            s = s + "{:5.0f}    ".format(AFP.CA_parms[c].ballistic_impact_KE / 1000)
        console_output.append(s)

        return console_output
    
    @staticmethod
    def scenario_computation_table(scenario):
        """Compute table of intermediate values for the three descent scenarios in Annex F :cite:`a-JARUS_AnnexF`.
        
        Produces console output.
        
        Parameters
        ----------
        scenario : integer
            Number of scenario, must be either 1, 2, or 3.
            
        Returns
        -------
        console_output : list of strings
            The output to show.
        """
        
        console_output = []
        
        if scenario != 1 and scenario != 2 and scenario != 3:
            warnings.warn("Scenario must be either 1,  2, or 3.")
            return
        
        # This setup cannot use a single impact angle, so it will be adjusted below.
        AFP = AnnexFParms()
        
        impact_speed = [0, 0, 0, 0, 0]
        impact_angle = [0, 0, 0, 0, 0]
        for c in range(5):
            if scenario == 1:
                impact_angle[c] = 10# if c > 0 else 35
                impact_speed[c] = AFP.CA_parms[c].glide_speed
            elif scenario == 2:
                impact_angle[c] = 35
                impact_speed[c] = AFP.CA_parms[c].cruise_speed
            elif scenario == 3:
                impact_angle[c] = AFP.CA_parms[c].ballistic_impact_angle
                impact_speed[c] = AFP.CA_parms[c].ballistic_impact_velocity

        CA = CriticalAreaModels(AFP.person_radius, AFP.person_height)
        p = []
        for c in range(5):
            # Set CoR since it needs to be set manually in this setup.
            AFP.CA_parms[c].aircraft.set_coefficient_of_restitution(AnnexFParms.CoR_from_impact_angle(impact_angle[c]))
            p.append(CA.critical_area(AFP.CA_parms[c].aircraft, impact_speed[c], impact_angle[c]))


        console_output.append("Scenario " + str(scenario) + " critical area calculations")
        console_output.append("Row  Variable                                            Values")
        console_output.append("--------------------------------------------------------------------------------")
        
        s = " 1    Class                         "
        for c in range(5):
            s = s + "{:2d} m      ".format(AFP.CA_parms[c].wingspan)
        console_output.append(s)

        s = " 2    Mass [kg]                    "
        for c in range(5):
            s = s + "{:5d}     ".format(AFP.CA_parms[c].mass)
        console_output.append(s)

        s = " 3    Cruise speed [m/s]            "
        for c in range(5):
            s = s + "{:4.0f}      ".format(AFP.CA_parms[c].cruise_speed)
        console_output.append(s)

        s = " 4    Impact angle [deg]           "
        for c in range(5):
            s = s + "{:5.0f}     ".format(impact_angle[c])
        console_output.append(s)

        s = " 5    Impact velocity [m/s]        "
        for c in range(5):
            s = s + "{:5.0f}     ".format(impact_speed[c])
        console_output.append(s)

        s = " 6    Aircraft width + buffer [m]   "
        rD2 = []
        for c in range(5):
            rD2.append(AFP.CA_parms[c].wingspan + 0.6)
            s = s + "{:4.1f}      ".format(rD2[c])
        console_output.append(s)

        s = " 7    Glide distance [m]            "
        for c in range(5):
            s = s + "{:4.0f}      ".format(p[c][5])
        console_output.append(s)

        s = " 8    Non-lethal speed [m/s]        "
        for c in range(5):
            s = s + "{:4.1f}      ".format(p[c][7])
        console_output.append(s)

        s = " 9    Horz speed at impact [m/s]    "
        for c in range(5):
            s = s + "{:4.0f}      ".format(CA.horizontal_speed_from_angle(impact_angle[c], impact_speed[c])) 
        console_output.append(s)

        s = "10    Coef of resitution [-]        "
        for c in range(5):
            s = s + "{:4.2f}      ".format(AnnexFParms.CoR_from_impact_angle(impact_angle[c])) 
        console_output.append(s)

        s = "11    Horz speed after impact [m/s] "
        for c in range(5):
            s = s + "{:4.0f}      ".format(CA.horizontal_speed_from_angle(impact_angle[c], impact_speed[c]) * AnnexFParms.CoR_from_impact_angle(impact_angle[c]))
        console_output.append(s)

        s = "12    Reduced slide distance [m]    "
        for c in range(5):
            s = s + "{:4.0f}      ".format(p[c][6])
        console_output.append(s)

        s = "13    Time to safe speed [s]        "
        for c in range(5):
            s = s + "{:4.1f}      ".format(p[c][8])
        console_output.append(s)

        s = "14    Raw critical area [m2]       "
        for c in range(5):
            s = s + "{:5.0f}     ".format(p[c][0])
        console_output.append(s)
        
        s = "15    CA reduced by 40%  [m2]      "
        for c in range(5):
            s = s + "{:5.0f}     ".format(p[c][0] * AnnexFParms.obstacle_reduction_factor)
        console_output.append(s)
        
        return console_output


