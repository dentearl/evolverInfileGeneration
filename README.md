#evolverInfileGeneration

Dent Earl, dearl@soe.ucsc.edu
2009-2011

##Introduction
This repo is intended to assist in the creation of an infile
set for use with the EVOLVER suite of genome evolution tools
written by Robert C. Edgar. George Asimenos, Serafim Batzoglou 
and Arend Sidow.
(http://www.drive5.com/evolver/)

##Operation
1. Copy the infileMakefile into a new directory where you would
like to have all the infiles created.
2. Edit the infileMakefile line 57 from what you see below:

    chrs:= 20 21 22

3. To **test** type <code>make -f infileMakefile testSet=YES</code>
4. To run type <code>make -f infileMakefile</code>

**Pro tip:** The Makefile has been written so that you can use the 
parallel option in make, <code>-j</code>, for a speedup.

##Dependencies
*EVOLVER http://www.drive5.com/evolver/ such that all executables and scripts
are preceded with <code>evolver_</code>, e.g. <code>evolver_evo</code>
*The Kent source tree http://moma.ki.au.dk/genome-mirror/admin/git.html
*evolverSimControl https://github.com/dentearl/evolverSimControl/ for the lib
*TandemRepeatsFinder, trf http://tandem.bu.edu/trf/trf.html
