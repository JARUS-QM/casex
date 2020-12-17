"""
Class for computing the explosion and deflagration models.
"""
import math

import numpy as np

from casex import enums, Conversion


class ExplosionModels:
    """    
    This class implements a model for the lethal area for an explosion, the lethal thermal area for
    explosion as well as deflagration, and the size of a deflagration fireball (which is also considered lethal).
    
    The main sources for the models are :cite:`d-DepartmentofDefense2012`, :cite:`d-Ball2012`, :cite:`d-Hardwicke2009`, and a
    brief review of explosion and deflagration is given in Annex F :cite:`d-JARUS_AnnexF`.
    
    The models are all based on TNT equivalent mass, since this is how the literature does it. This means that for any
    of the models it is necessary to convert the fuel amount to a given TNT mass which has the same energy density.
    """

    @staticmethod
    def lethal_area_explosion(TNT_mass, K=7.14):
        """Compute lethal area for explosion.
        
        Determines the lethal area for an explosion. The model used is
        
        .. math:: A_{explosion} = \pi  D^2
            
        where :math:`D` [m] is the distance from the explosion, where it is no longer lethal. It is given as
        
        .. math:: D = K  W^{1/3}
            
        where :math:`K` [m/kg :math:`^{1/3}`] is a scaling factor for the acceptable risk and W [kg] is the TNT equivalent mass
        :cite:`DepartmentofDefense2012`, :cite:`Ball2012`, :cite:`Hardwicke2009`.
        
        A recommended value for the scaling factor for 3.5 psi overpressure is 18 ft/lb :math:`^{1/3}` (also called K18,
        for unprotected persons), which is equal to
        
        .. math:: K = 7.14~\mathrm{m/kg}^{1/3}
            
        in SI units. For details on this value, see :cite:`DepartmentofDefense2012`.
        
        .. note:: The area given by the used model assumes a near-perfect combustion of the fuel, which typically
                  requires a close to ideal mixing of fuel and oxidizer. As this normally do not happen during an
                  aircraft crash, the model tends to be rather conservative in the estimate of the lethal area.
                  For more detail on this, please consult Annex F :cite:`JARUS_AnnexF`.
                  
        .. warning:: The model for lethality caused by explosions has not been deeply investigated, and the model
                  is provided as is, with references to it origin. Ultimate responsibility for determining the lethal
                  area at an explosion rests with the user.
                
        Parameters
        ----------      
        TNT_mass : float
            [kg] Equivalent TNT mass to the explosive material.
            Use :class:`TNT_equivalent_mass` to determine this value.
        K : float, optional
            [kg/m^(1/3)] Scaling factor for acceptable risk (the default is 7.14).
            
        Returns
        -------      
        area : float
            [m^2] Size of the lethal area, which is in the form of a disc.        
        """
        return math.pi * np.power(K * np.power(TNT_mass, 1 / 3), 2)

    @staticmethod
    def TNT_equivalent_mass(type_of_fuel, fuel_quantity):
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
        
        .. note:: The above values are drawn from a variety of sources of unconfirmed reliability. As such,
                  these are the authors' best guesses at appropriate values.
    
        Parameters
        ----------
        type_of_fuel : :class:`enums.FuelType`
            The type of fuel.
        fuel_quantity : float
            [L] The amount of fuel.
        
        Returns
        -------
        TNT_mass : float
            [kg] TNT equivalent mass.
        """
        # Energy density in MJ/kg.
        TNT_energy_density = 4.184

        if type_of_fuel == enums.FuelType.GASOLINE:  # This includes petrol.
            relative_density = 46.4 / TNT_energy_density
            kg_per_liter = 0.75
        elif type_of_fuel == enums.FuelType.DIESEL:
            relative_density = 45.6 / TNT_energy_density
            kg_per_liter = 0.83
        elif type_of_fuel == enums.FuelType.JETA1:
            relative_density = 43 / TNT_energy_density
            kg_per_liter = 0.80
        elif type_of_fuel == enums.FuelType.AVGAS:
            relative_density = 44.7 / TNT_energy_density
            kg_per_liter = 0.69
        elif type_of_fuel == enums.FuelType.METHANOL:
            relative_density = 19 / TNT_energy_density
            kg_per_liter = 0.79
        elif type_of_fuel == enums.FuelType.LIQUID_HYDROGEN:
            relative_density = 142 / TNT_energy_density  # NOTE: The energy density is per liter.
            kg_per_liter = 1
        elif type_of_fuel == enums.FuelType.LIQUID_BUTANE:
            relative_density = 27.8 / TNT_energy_density  # NOTE: The energy density is per liter.
            kg_per_liter = 1
        elif type_of_fuel == enums.FuelType.LIFE:
            relative_density = 1.8 / TNT_energy_density  # NOTE: The energy density is per liter.
            kg_per_liter = 1
        elif type_of_fuel == enums.FuelType.LION:
            relative_density = 0.8 / TNT_energy_density  # NOTE: The energy density is per liter.
            kg_per_liter = 1
        else:
            raise ValueError("Invalid fuel type " + str(type_of_fuel))

        return relative_density * kg_per_liter * fuel_quantity

    @staticmethod
    def lethal_area_thermal(TNT_mass, p_lethal):
        """Compute lethal area for thermal radiation (deflagration).
        
        Computes the lethal area for deflagration based on the thermal radiation.
        Model is taken from :cite:`d-Ball2012` page 61.
        
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
        # It is a combination of (72) and (74).
        # Compute the lethal distance form deflagration center.
        D = -14.8 * np.power(TNT_mass, 1 / 3) / np.log(- 0.0005493 + 0.000232263 / p_lethal)

        # Return the circular area.
        return math.pi * np.power(D, 2)

    @staticmethod
    def fireball_area(TNT_mass):
        """Compute lethal area for fireball (deflagration).
        
        Compute the size of a fireball for a given amount of propellant. The model is found in :cite:`d-Ball2012` page 62.

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
        return math.pi * np.power(Conversion.ft_to_m(2.77 * np.power(Conversion.kg_to_lbs(TNT_mass), 0.36) / 0.45), 2)
