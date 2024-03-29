"""
Example 3
---------
This example provides the code for producing a large variety of iGRC tables, including the tables found in Annex F and the SORA.

It can show iGRC for varying population densities, for a specific impact angle or for a ballistic descent, and with and without obstacles.
"""
from casex import AnnexFTables

console_output = AnnexFTables.iGRC_tables(show_with_obstacles = True,
                                          show_ballistic = False,
                                          show_with_conservative_compensation = False,
                                          show_glide_angle = False,
                                          show_additional_pop_density = True)

for s in console_output:
    print(s)
