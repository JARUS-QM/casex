Bug fixes and updates
=====================

Version 1.2.2
-------------

* Updated documentation for examples. Still not complete.

Known issues still to be fixed:

* figures.py still needs more work to fit SORA 2.5.
* Documentation has only partially been updated to fit all the changes following SORA 2.5.


Version 1.2.1
-------------

* Removed models for RTI, RCC, NAVCAD, and FAA. These are no longer avaiable for computation. Also removed the associated enum.
* Length has been removed from AircraftSpecs, since it is no longer needed.
* Changed gravity from 9.82 to 9.81 to comply with MKS system.
* Rearrange the order of the examples.


Version 1.2.0
-------------

* Updated Casex to correspond to SORA 2.5. Most the following updates are adjustments to SORA 2.5, while most of the bug fixes are resulting from a general update of CasEx.
* Changed numerous values in annex_f_tables.py to correspond to the coming public version of SORA 2.5.
* Added ballistic_descent_table() to annex_f_tables.py (originally in figures.py) and expanded to show the full table.

Smaller changes

* Change upper proper CoF value in aircraft_specs.py from 1.5 to 1.0.
* Moved COR_from_impact_angle() from aircraft_specs.py to annex_f_parms.py and made it static.
* Added default values for person_radius (0.3) and person_height (1.8) to AnnexFParms.
* Change LA_inert to CA_inert and LA_deflagration to CA_deflagration in critical_area() method to reflect critial area instead of lethal area.
* Change slide_distance_lethal to slide_distance_non_lethal in critical_area() method, since it is in fact the non-lethal distance.
* Updated example 1 to comply with changes.
* Deleted example 2.
* Updated example 3 to comply with changes.
* Updated example 4 to include obstacle reduction.
* Updated example 7 to match new population bands.
* Updated JARUS model equations in critical_area() to accommodate concession of 35 degree impact angle.
* Added population bands to AnnexFParms.
* Development status change from beta to production/stable.

Version 1.1.11
--------------

* The disc-shaped end of the critical area was counted double, i.e., a full disc was added to both glide and slide. Now only half a disc is added to glide and slide.
* In the web interface for the online tool "Person width" is changed to "Person radius".
* Updated values for calculation of CoR to fit SORA 2.5.
* The Obstacles simulation currently does not work. A fix is in progress.
* Thanks to Janis Mauch for point out these bugs.

Version 1.1.10
--------------
* First deployed version.