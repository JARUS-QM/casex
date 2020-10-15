import warnings
import numpy as np
import math

import casex

class CExplosionModels:
    """Explosion and deflagration models.
    
    This class implements a model for the lethal area for an explosition, the lethal thermal area for
    explosion as well as deflagration, and the size of a deflagration fireball (which is also considered lethal).
    
    The main souces for the models are [6]_, [7]_, [8]_, and a brief review of explosion and deflagration is given
    in JARUS SORA annex F [1]_.
    
    The models are all based on TNT equivalent mass, since this is how the literature does it. This means that for any of the models
    it is necessary to convert the fuel amount to a given TNT mass which has the same energy density.
    """
    
    def __init__(self):
        self._self_test()
        
    def lethal_area_explosion(self, TNT_mass, K = 7.14):
        """Compute lethal area for explosion
        
        Determines the lethal area for an explosion. The model used is
        
        .. math:: A_{explosion} = \pi  D^2
            
        where :math:`D` [m] is the distance from the explosion, where it is no longer lethal. It is given as
        
        .. math:: D = K  W^{1/3}
            
        where :math:`K` [m/kg^(1/3)] is a scaling factor for the acceptable risk and W [kg] is the TNT equivalent mass [6]_, [7]_, [8]_.
        
        A recommended value for the scaling factor for 3.5 psi overpressure is 18 ft/lb :math:`^{1/3}` (also called K18, for unprotected persons), which is equal to
        
        .. math:: K = 7.14
            
        For details on this value, see [6]_.
        
        .. note:: The area given by the used model assumes a near-perfect combustion of the fuel, which typically requires a close to ideal mixing of fuel and oxidizer.
                    As this normally do not happen during an aircraft crash, the model tends to be rather conservative in the estimate of the lethal area.
                    For more detail on this, please consult JARUS SORA annex F [1]_.
                
        Parameters
        ----------      
        TNTmass : float
            [kg] Equivalent TNT mass to the explosive material. Use :class:`ComputeTNTEquivalentMass` to determine this value.
            
        K : float, optional
            [kg/m^(1/3)] Scaling factor for acceptable risk. Default value is 7.14.
            
        Returns
        -------      
        area : float
            [m^2] Size of the lethal area, which is in the form of a disc.        
        """
        
        return math.pi * np.power(K * np.power(TNT_mass, 1/3), 2)
    
    def TNT_equivalent_mass(self, type_of_fuel, fuel_quantity):
        """Compute the equivalent mass of TNT for a number of fuels.
        
        Compute the amount of TNT in kg equivalent in energy density to a given type of fuel.
        This value is used for the explosion and deflagration computations.
        
        Available types of fuels are:
        
        +----------------------+----------------------------+-------------------+
        | Fuel type            | Energy density             | Mass density      |
        +======================+============================+===================+
        | TNT                  | 4.184 MJ/kg                | --                |
        +----------------------+----------------------------+-------------------+
        | Gasoline             | 46.4 MJ/L                  | 0.75 kg/L         |
        +----------------------+----------------------------+-------------------+
        | Diesel               | 45.6 MJ/L                  | 0.83 kg/L         |
        +----------------------+----------------------------+-------------------+
        | Jet A1               | 43 MJ/L                    | 0.80 kg/L         |
        +----------------------+----------------------------+-------------------+
        | AvGas                | 44.7 MJ/L                  | 0.69 kg/L         |
        +----------------------+----------------------------+-------------------+
        | Methanol             | 19 MJ/L                    | 0.79 kg/L         |
        +----------------------+----------------------------+-------------------+
        | LiFe batteries       | 1.8 MJ/kg                  | --                |
        +----------------------+----------------------------+-------------------+
        | LiOn batteries       | 0.8 MJ/kg                  | --                |
        +----------------------+----------------------------+-------------------+
        | Liquid hydrogen      | 142 MJ/kg                  | --                |
        +----------------------+----------------------------+-------------------+
        | Liquid butane        | 27.8 MJ/kg                 | --                |
        +----------------------+----------------------------+-------------------+
        
        .. note:: The above coefficients are drawn from a variety of sources of unconfirmed reliability.
                    As such, these are the authors' best guesses at appropriate coefficients.
                    The true coefficient depends on the state of the materials (wet, dry, greased, etc.) and the actual material (e.g. there are numerous types of concrete, soil, etc.).
    
        .. warning:: The values provided are guidance only!
                    Ultimate responsibility for correct choice and use of friction coefficient rests with the user!

        Parameters
        ----------
        type_of_fuel : :class:`EFuelType`
            The type of fuel.
        quantity_in_liters : float
            [L] The amount of fuel.
        
        Returns
        -------
        TNT_mass : float
            [kg] TNT equivalent mass.
        """
        
        # Energy density in MJ/kg
        TNT_energy_density = 4.184
        
        if type_of_fuel == casex.enums.EFuelType.GASOLINE:  # This includes petrol
            relative_density = 46.4 / TNT_energy_density
            kg_per_liter = 0.75
        elif type_of_fuel == casex.enums.EFuelType.DIESEL:
            relative_density = 45.6 / TNT_energy_density
            kg_per_liter = 0.83 
        elif type_of_fuel == casex.enums.EFuelType.JETA1:
            relative_density = 43 / TNT_energy_density
            kg_per_liter = 0.80
        elif type_of_fuel == casex.enums.EFuelType.AVGAS:
            relative_density = 44.7 / TNT_energy_density
            kg_per_liter = 0.69
        elif type_of_fuel == casex.enums.EFuelType.METHANOL:
            relative_density = 19 / TNT_energy_density
            kg_per_liter = 0.79
        elif type_of_fuel == casex.enums.EFuelType.LIQUID_HYDROGEN:
            relative_density = 142 / TNT_energy_density         # NOTE: The energy density is per liter
            kg_per_liter = 1
        elif type_of_fuel == casex.enums.EFuelType.LIQUID_BUTANE:
            relative_density = 27.8 / TNT_energy_density        # NOTE: The energy density is per liter
            kg_per_liter = 1
        elif type_of_fuel == casex.enums.EFuelType.LIFE:
            relative_density = 1.8 / TNT_energy_density         # NOTE: The energy density is per liter
            kg_per_liter = 1                          
        elif type_of_fuel == casex.enums.EFuelType.LION:
            relative_density = 0.8 / TNT_energy_density         # NOTE: The energy density is per liter
            kg_per_liter = 1
        else:
            raise ValueError("Invalid fuel type " + str(type_of_fuel))
        
        return relative_density * kg_per_liter * fuel_quantity    
        
    def lethal_area_thermal(self, TNT_mass, p_lethal):
        """Compute lethal area for thermal radiation (deflagration)
        
        Computes the lethal area for deflagration based on the thermal radiation.
        Model is taken from [7]_ page 61.
        
        .. note:: See note for :class:`lethal_area_explosion`.
        
        Parameters
        ----------
        TNT_mass : float
            [kg] The equivalent TNT mass for the propellant.
        p_lethal : float
            [-] A number between 0 and 1 indicating the target lethality.
            
        Returns
        -------
        area : float
            [m^2] Size of lethal area.
        """
        
        # WARNING: This has still to be checked!!
        # It is a combination of (72) and (74)
        # Compute the lethal distance form deflagration center
        D = -14.8 * np.power(TNT_mass, 1/3) / np.log(- 0.0005493 + 0.000232263 / p_lethal) 
        
        # Return the circular area
        return math.pi * np.power(D, 2)

    def fireball_area(self, TNT_mass):
        """Compute lethal area for fireball (deflagration)
        
        Compute the size of a fireball for a given amount of propellant. The model is found in [7]_ page 62.

        .. note:: See note for :class:`lethal_area_explosion`.
        
        Parameters
        ----------
        TNT_mass : float
            [kg] The equivalent TNT mass for the propellant.

        Returns
        -------
        area : float
            [m^2] Size of area of fireball.
        """
        
        return math.pi * np.power(casex.conversions.CConversion.ft_to_m(2.77 * np.power(casex.conversions.CConversion.kg_to_lbs(TNT_mass), 0.36) / 0.45), 2)

    def _self_test(self):
        """Self test of member functions.
        
        This function can be use to perform a self test of all functions.
        The purpose it make sure that there are not code errors.
        It does not check for equation errors.
        It is not exhaustive, but gives a good indication.
        """
        
        #LethalArea_Explosion(self, TNTmass, K = 7.14):
        self.lethal_area_explosion(20)
        self.lethal_area_explosion(30, 12)
        #TNT_equivalent_mass(self, TypeOfFuel, QuantityInLiters):
        self.TNT_equivalent_mass(casex.enums.EFuelType.GASOLINE, 45)
        #thermal_lethal_area(TNT mass, p_lethal)
        self.lethal_area_thermal(40, 0.1)
        #fireball_area(TNT_mass)        
        self.fireball_area(40)
