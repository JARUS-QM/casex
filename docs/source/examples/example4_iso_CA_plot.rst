======================
Example 4: iso CA plot
======================

This example makes a colored plot of the lethal area for varying impact angle and impact speed. The size of the aircraft
as well as the other parameters are fixed. The target is the first column in the iGRC table, where the lethal area
is 10 m^2. Therefore, the iso-curve for to 10 m^2 is shown (in yellow) along with other iso curves for comparison
(in white).

The purpose is to give a relation between angle and speed for impacts to uncover any potential relation between angle
and speed in terms of fixed lethal area.

The JARUS model is used throughout this example.

.. literalinclude:: ../../../examples/example4_iso_CA_plot.py
    :lines: 14-71

*Text explaining the output*

.. image:: images/example_4.png
