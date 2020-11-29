=========================================
Example 7: JARUS model vs the iGRC values
=========================================

In this example we compare the iGRC table in Annex F with the actual output of the JARUS model. This is done by plotting
the critical area for a variety of wingspan and population densities. This is similar to the iGRC figures that can be
computed with the :class:`Figures` class, which do the same thing, but for the simplified model.

We start with setting standard person parameters.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 17-18
    
and then we need to decide the impact angle. This is not used in the
simplified model, where the impact angle has been simplified away. However,
for the JARUS model we need to set this, since the critical area depends on it.
Here we choose 35 degrees, but any angle will do (but obviously produce a slightly
different plot).

We also need to set an impact speed for the JARUS mode, and here we choose to
use the values from the :class:`AnnexFParms` class, possibly reduced, since this
is what is assumed in Annex F for the 9 degree glide angle. Here we do not reduce
the speed, since we have 35 degrees impact angle.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 19-20
    
We instantiate the CA model class.    

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 23
    
We set the sampling density for the two axes.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 26-27
    
We set the arrays for the sampling on the two axis. Note that the wingspan
axis is linear, while the population density axis is logarithmic.

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 30-31
    

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 17-18
    

.. literalinclude:: ../../../examples/example7_JARUS_model_vs_iGRC.py
    :lines: 17-18


.. image:: images/example_7.png
