===========================
Example 2: Model comparison
===========================

This example shows the basics of using the different models in casex.
It shows how to set up the necessary parameters and variables, and how
to call the lethal_model function to calculate lethal areas for the
models. It also shows how to modify an existing setup to change from one aircraft
to another.

As in example 1, we start by setting up a few standard parameters, and
instantiate classes for friction coefficient and critical area.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 18-24

We choose a fixed wing aircraft (although at this stage of development, CasEx
does not use this information) with a width of 4 meters and length of 3.2 meters.
The mass is 25 kg, and the friction coefficient is aluminum against concrete.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 27-31

We then instantiate the class for the aircraft, and set fuel type and quantity,
friction coefficient, and coefficient of restitution.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 34-38

The impact speed is chosen such as to be equivalent to a kinetic energy of
34 kJ.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 42
    
The impact angle is chose to be 25 degrees.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 45

The overlap betweeb inert and deflagration critical areas is set at 50%.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 48

We want to compare models, and we add the result from the same computation for
each model to a list `p`.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 51-55
    
We do the computation one more time, except we change the impact angle to 65 degrees.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 58-60

We then redo the computations with a different size aircraft, again with an impact
angle of 25 degrees.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 53-71

And finally, we redo the computations are 65 degree impact angle.

.. literalinclude:: ../../../examples/example2_model_comparison.py
    :lines: 74-76

Note that `p` now is a 2 dimensional list, with different computations
along the first axis and the 5 different outputs from the critical area
model along the second axis. Since in this example we are only interested in
the total critical area, all use of `p` is on the form `p[x][0]`.

The result of the computations are shown in the figure below.

*Text explaining the output*

.. image:: images/example_2.png
