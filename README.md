#evolverInfileGeneration

Dent Earl, dearl@soe.ucsc.edu

2009-2011

##Introduction
This repo is intended to assist in the creation of an infile
set for use with the EVOLVER suite of genome evolution tools
written by Robert C. Edgar. George Asimenos, Serafim Batzoglou 
and Arend Sidow. http://www.drive5.com/evolver/

##Operation
1. Copy the <code>src/infileMakefile</code> into a new directory where you would
like to have all the infiles created.
2. Edit the chromosomes on line 58 from what you see below to whatever you want them to be:

    <code>chrs:= 20 21 22</code>

3. To **test** type <code>make -f infileMakefile testSet=YES</code>
4. To run type <code>make -f infileMakefile</code>

**Pro tip:** The Makefile has been written so that you can use the 
parallel option in make, <code>-j</code>, for a speedup, provided you have a extra processors to spare.

##Extras
* singleRegionGenerator.sh - A shrunken down version of <code>infileMakefile</code>. For when you don't want a full chromosome, but just a small piece of one. Used in a publication.
* splitEvolverInfiles.py - Used to cut a paired FASTA and GFF into smaller FASTAs and GFFs with correct new coordinates for the GFF files.
* testSplitEvolverInfiles.py - unittest for splitEvolverInfiles.py, invoke with <code>python testSplitEvolverInfiles.py --verbose</code>
* subsetRemapGP.py - Takes a .gp (genpred) file and arguments to define a subsetted region and returns just the subsetted region with all elements' coordinates transformed to the subset, in .gp format.

##Dependencies
* EVOLVER: http://www.drive5.com/evolver/ such that all executables and scripts are preceded with <code>evolver_</code>, e.g. <code>evolver_evo</code>
* The UCSC Genome Browser Kent source tree: http://genome.ucsc.edu/admin/git.html for some utilities used in the infileMakefile
* evolverSimControl: https://github.com/dentearl/evolverSimControl/ for the lib
* TandemRepeatsFinder: trf http://tandem.bu.edu/trf/trf.html
