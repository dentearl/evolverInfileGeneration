#evolverInfileGeneration

Dent Earl, dearl@soe.ucsc.edu

2009-2011

##Introduction
This repo is intended to assist in the creation of an infile
set for use with the EVOLVER suite of genome evolution tools
written by Robert C. Edgar. George Asimenos, Serafim Batzoglou 
and Arend Sidow. http://www.drive5.com/evolver/

##Dependencies
* Evolver: http://www.drive5.com/evolver/ such that all executables and scripts are preceded with <code>evolver_</code>, e.g. <code>evolver_evo</code>
* The UCSC Genome Browser Kent source tree: <code>git clone git://genome-source.cse.ucsc.edu/kent.git</code> for some utilities used in the infileMakefile
* evolverSimControl: https://github.com/dentearl/evolverSimControl/ for the lib
* TandemRepeatsFinder: trf http://tandem.bu.edu/trf/trf.html

##Installation
1. Download the project.
2. <code>cd</code> into the project directory.
3. Type <code>make</code>.
4. Edit your <code>PYTHONPATH</code> environmental variable to contain the parent directory of the <code>evolverInfileGeneration/</code> directory.

##Operation
1. Copy the <code>bin/infileMakefile</code> into a new directory where you would
like to have all the infiles created.
2. Edit the chromosomes on line 58 from what you see below to whatever you want them to be:

    <code>chrs:= 20 21 22</code>

3. To **test** type <code>make -f infileMakefile testSet=YES</code>
4. To run type <code>make -f infileMakefile</code>

**Pro tip:** The Makefile has been written so that you can use the 
parallel option in make, <code>-j</code>, for a speedup, provided you have a extra processors to spare.

##Extras
* singleRegionGenerator.sh - A shrunken down version of <code>infileMakefile</code>. For when you don't want a full chromosome, but just a small piece of one. Used in the Cactus publication **Cactus: Algorithms for genome multiple sequence alignment** 2011. Paten, Earl, Nguyen, Deikans, Zerbino and Haussler. Genome Research. http://genome.cshlp.org/content/early/2011/06/09/gr.123356.111.abstract .
* splitEvolverInfiles.py - Used to cut a paired FASTA and GFF into smaller FASTAs and GFFs with correct new coordinates for the GFF files.
* src/testSplitEvolverInfiles.py - unittest for splitEvolverInfiles.py, invoke with <code>python src/testSplitEvolverInfiles.py --verbose</code>
* subsetRemapGP.py - Takes a .gp ([genpred](http://genome.ucsc.edu/FAQ/FAQformat.html#format9)) file and arguments to define a subsetted region and returns just the subsetted region with all elements' coordinates transformed to the subset, in .gp format.
