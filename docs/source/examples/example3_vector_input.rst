=======================
Example 3: Vector input
=======================

This example shows how to use the models using vector input to generate a vector output.
Using this feature it is possible to generate graphs for variations on one input parameter.

This example shows this for the following parameters:
    * width
    * length
    * impact angle
    * impact speed
    * lethal area overlap
    * fuel quantity
    * friction coefficient

Note that not all models include all of the above parameters. If a model does not include a
specific parameters, it does not produce a vector output, even if a vector input is given
for that parameter.

.. literalinclude:: ../../../examples/example3_vector_input.py
    :lines: 20-151

*Text explaining the output*

.. image:: images/example_3.png
