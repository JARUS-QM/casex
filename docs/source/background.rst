Background
==========

From the summer 2019 and until early 2021, a small group of people have been working under
the auspice of `JARUS <http://jarus-rpas.org>`_ on developing guidance material for use
to determine the ground risk associated with operations of unmanned aircraft.
This group is called the Quantitative Methods subgroup. The developed concept had to
be applicable to most types of UAS and it has to be relatively simple to allow for everyday use by
operators and authorities.

The result of this development is described in Annex F :cite:`JARUS_AnnexF`
in the SORA set of document developed and published by 
JARUS. This Annex provide a elaborate explanation of how to determine the ground risk
for a given operation, where a number of aircraft parameters and the density of people on the ground is known.

As part of the development of Annex F, the group has gone through quite a lot of programming in Matlab and Python
to test out difference ideas, verifying assumptions, plotting graphs, etc. Some of this work might be useful to
other people, and may also serve to document how the various models and math implementation have been used in
the development of Annex F.

Therefor, the group decided to spent the effort to convert some of the code into a publicly available toolbox
that can be used to apply the methods described in Annex F without having to implement it all from scratch.
The toolbox also reproduces some of the figures in the Annex.

CasEx is the result of this implementation. It is intended only as a supplement to Annex F, and it is still
the responsibility of the operator or authority using the toolbox to make sure that any computed value
and use of such values is in compliance with Annex F and any other requirements.

Still, we hope that the toolbox can be useful. Comments and queries related to the
implementation and use can be submitted to the main author Anders la Cour-Harbo at at alc(a)es.aau.dk.
