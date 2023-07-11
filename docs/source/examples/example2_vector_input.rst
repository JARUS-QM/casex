=======================
Example 2: Vector input
=======================

This example shows how to use the JARUS model with a vector input to generate a vector output.
Using this feature it is possible to generate graphs for variations on
one input parameter without resorting to a loop.

This example shows this for the following parameters:

    * width
    * impact angle
    * impact speed
    * lethal area overlap
    * fuel quantity
    * friction coefficient

We begin with setup, which was also done in example 1.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 21-40
    
First, we set the width to an array instead of a scalar. Here we choose the width
to vary from 1 to 5 meters over 100 steps. The input is set via the aircraft class.
We collect the result in the p array.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 53-55

The we set the impact speed as a vector. Since only one parameters at a time can be a vector input, we reset the width to
a scalar value. 

.. literalinclude:: ../../../examples/example3_vector_input.py
    :lines: 58-60

Since the impact angle is not set through the aircraft class, but directly
as an input to `critical_area`, we do not need to reset the impact angle. We
simply use the original variable `impact_angle`. And we set the impact speed
to be an array.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 63-64
    
We do the same with the critical area overlap.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 67-68
    
The fuel quantity is set as an array.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 71-73

And finally, we also set the friction coefficient as an array.

.. literalinclude:: ../../../casex/examples/example2_vector_input.py
    :lines: 76-79

Finally, we plot all the outputs.

.. image:: images/example_2.png
