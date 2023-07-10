=====================================
Example 4: iGRC tradeoff tables
=====================================

NOT YET UPDATED TO SORA 2.5

This example produces the tradeoff tables in Annex F :cite:`j-JARUS_AnnexF`.

We want to see the T2 tradeoff table in rounded integers. First, we set the tradeoff value

.. literalinclude:: ../../../casex/examples/example9_tradeoffs.py
    :lines: 14

and request integers

.. literalinclude:: ../../../casex/examples/example9_tradeoffs.py
    :lines: 17

and not relative values

.. literalinclude:: ../../../casex/examples/example9_tradeoffs.py
    :lines: 20

We call the AnnexFTables method

.. literalinclude:: ../../../casex/examples/example9_tradeoffs.py
    :lines: 22

and run

.. literalinclude:: ../../../casex/examples/example9_tradeoffs.py
    :lines: 24-25

to show the result

.. code-block:: console

    Modified raw iGRC table for trade-off scenario T2
                 Max dim   |   2.0 m     6.0 m    16.0 m    40.0 m    80.0 m    
    Dpop         Max speed |  25 m/s    35 m/s    75 m/s   150 m/s   200 m/s  
    -----------------------+--------------------------------------------------
          Controlled       |      1         2         4         4         5      
          5 ppl/km^2       |      3         4         6         6         7      
         50 ppl/km^2       |      4         5         7         7         8      
        750 ppl/km^2       |      6         7         8         9         9      
       7500 ppl/km^2       |      7         7         8         9        10      
      50000 ppl/km^2       |      7         8         9        10        11      
     500000 ppl/km^2       |      8         9        11        11        12 

.. bibliography::
   :keyprefix: j-
