=====================================
Example 4: iGRC tradeoff tables
=====================================

This example produces the tradeoff tables in Annex F :cite:`j-JARUS_AnnexF`.

We want to see the T2 tradeoff table in rounded up integers. First, we set the tradeoff value

.. literalinclude:: ../../../casex/examples/example4_tradeoffs.py
    :lines: 14

and request integers

.. literalinclude:: ../../../casex/examples/example4_tradeoffs.py
    :lines: 17

and not relative values

.. literalinclude:: ../../../casex/examples/example4_tradeoffs.py
    :lines: 20
    
If showing relative values, the table will show the difference to the nominal iGRC table. This feature is primarily for developers
that want to see how big the difference is when using trade-offs. It does not have any bearing on the use of the trade-off
tables.

We then call the AnnexFTables method

.. literalinclude:: ../../../casex/examples/example4_tradeoffs.py
    :lines: 22-23

and run

.. literalinclude:: ../../../casex/examples/example4_tradeoffs.py
    :lines: 25-26

to show the result

.. code-block:: console

    Modified raw iGRC table for trade-off scenario T2
                 Max dim   |   2.0 m     6.0 m    16.0 m    40.0 m    80.0 m    
    Dpop         Max speed |  25 m/s    35 m/s    75 m/s   150 m/s   200 m/s  
    -----------------------+--------------------------------------------------
             Controlled    |      1         2         3         4         5      
            12 ppl/km^2    |      3         4         5         6         7      
           125 ppl/km^2    |      4         5         6         7         8      
          1250 ppl/km^2    |      5         6         7         8         9      
         12500 ppl/km^2    |      6         7         8         9        10      
        125000 ppl/km^2    |      7         8         9        10        11      
        125000 ppl/km^2    |      7        n/a       n/a       n/a       n/a  

.. bibliography::
   :keyprefix: j-
