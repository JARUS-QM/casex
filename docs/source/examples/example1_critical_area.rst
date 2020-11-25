========================
Example 1: Critical area
========================

This first example demonstrates how to use the CasEx package for computing a critical area for a specific aircraft.
This computation can be used for determining a more accurate iGRC value that what is possible for the iGRC table.

We start by setting two basic parameters required for computing the size of the critical area, namely
the height of a standad person and the "radius" of a standard person. The latter is the radius of a circle circumscribing
a person seen from above.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 6-11
    
Even though these values are relative constant, they are indeed part of the parameter set for this package.

We then instantiate first the class that can provide some friction coefficients, and then the class
that holds the various models for computing the size of the critical area.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 14-15

We then need to decide the impact speed and the impact angle. The former is the speed the aircraft will have along the direction
of travel at the time it impacts the ground. This is used for computing the glide distance after impact. The latter is the angle
of the straight line that the aircraft follows just prior to impact. This is measure from horizontal, so that 10 degrees is a very
shallow impact, while 90 is a vertical impact.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 18-19

We also need to specify some properties of the aircraft. This is done using the :class:`AircraftSpecs` class. But first, we set some of the
parameters used in the instantiation.

We have the wingspan (also known as width or characterstic dimension), the length of the aircraft, the mass, and the coefficient of friction
between the aircraft and the terrain. The latter is in this case captured from the :class:`FrictionCoefficients`, but could also be set
manually. Note that in Annex F this value is always 0.5.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 22-26

Then we instantiate the aircraft class, and set the friction value.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 29-30

The deflagration model can be included by setting the type of fuel and the amount of fuel. Here, we set the amount to 0, which
effectively deactivates the deflagration model. It can be activated by setting a non-zero amount of fuel.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 33-34

The coefficient of restitution is set as a function of the impact angle.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 37

When the deflagratio model is used there will be an overlap between the critical area from the glide and slide and the
critical area from the deflagration (since the deflagration happens to some extend in the same area). We therefore need to
set the fraction of overlap. The total critical area (sum of glide/slide and deflagration) is reduced by the smaller of the two
multiplied with the overlap factor.

Note that this value is not used when there is not fuel onboard, and therefore no deflagration.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 41

During the slide, the aircraft dissepates kinetic energy, which ends at 0 when the aircraft comes to a halt. It is possible to
reduce the size of the critical area by assuming that the aircraft is no longer lethal at a higher kinetic energy than 0. The
chosen value is set here. If the default value is to be used, the value is set to -1.
The documentation for :class:`critical_area_models` have more info on this.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 46

We are now ready to compute the size of the critical area. We do this by calling the `critical_area` method. Here we select to used
the JARUS model, but other models are also available (see example 2).

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 49-50
    
The output from this method a list with 5 values. These are total critical area, glide area, slide area, the inert critical area, and the critical
area from the deflagration. These are shown in the output below along with some of the aircraft parameters.

Finally, we can also compute the raw iGRC as described in Annex F. This is done using the :class:`AnnexFParms` class. Here we need to input
the population density, which is set to 800 here.

.. literalinclude:: ../../../examples/example1_critical_area.py
    :lines: 53

The output of the example is as follows. We see that the raw iGRC is 5.9, which must be rounded up to 6 for the actual iGRC value. This demonstrates
how an aircraft, which belongs in the third column (due to the high impact speed above 35 m/s) can achieve a lower iGRC value that given in the
table (which would be 7) by doing the actual calculations for the critical area.

It is immportant to note that this example uses rubber against concrete as the friction coefficient. This obviously has to be adjusted depending on
the aircraft and the overflown terrain.

.. code-block:: console

    Wingspan:                   1.5 m
    Mass:                       5 kg
    Horizontal impact speed:    36.9 m/s
    Glide area:                 8.9 m^2
    Slide area:                 98.6 m^2
    Critical area inert:        107.5 m^2
    Critical area deflagration: 0.0 m^2
    Total critical area:        107 m^2
    Raw iGRC:                   5.9

