#!/bin/bash
# singleRegionGenerator.sh
# dent earl, dearl (a) soe ucsc edu
# 19 Oct 2010
#
# This script takes a directory as its first arugment
# and then generates an EVOLVER infile set.
# The directory is required to have a SEQ directory
# that contains a single fasta (*.fa) sequence file
# and an ANNOTATIONS directory that contains the following
# * cpgIslandExt.gp  # cpg Island track from UCSC
# * ensGene.gp       # ensemble gene track from UCSC
# * knownGene.gp     # known genes track from UCSC
# * knownGeneOld2.gp # known genes old 2 track from UCSC
# * mgcGenes.gp      # mammalian gene collection track from UCSC
# and a MODEL dicetory that contains
# * model.txt        # model file.
#
##################################################
# Copyright (C) 2009-2011 by
# Dent Earl (dearl@soe.ucsc.edu, dentearl@gmail.com)
# Benedict Paten (benedict@soe.ucsc.edu, benedictpaten@gmail.com)
# ... and other members of the Reconstruction Team of David Haussler's
# lab (BME Dept. UCSC)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##################################################
usage(){
    echo "Usage: `basename $0` directory label[chr4 or chrX etc...]";
    head -19 `basename $0`;
    exit 2
}
run(){
    # run is used wherever possible, notable exceptions include
    # redirections like | or > .
    echo "$1"
    $1
    if [ $? -ne 0 ];then
        echo "ERROR: '$1' failed with status $?"
        exit 1
    fi
}
runTrf(){
    # trf has a reversed returncode setup.
    # $1 is the directory to run in
    # $2 is the command
    echo "cd $1"
    cd $1
    echo "$2"
    $2
    if [ $? -ne 1 ];then
        echo "ERROR: '$2' failed with status $?"
        exit 1
    fi
}
# check number of arguments
if [ $# -ne 2 ];then
    usage
fi
DIR=$1
DIR=${DIR%/}
DIR=$(readlink -f $DIR)
LABEL=$2
# check argument is a directory
if [ ! -d $DIR  ]; then
    echo "Directory $DIR does not exist."
    usage
fi
# check for SEQ sub directory
if [ ! -d $DIR/SEQ ]; then
    echo "Directory $DIR/SEQ does not exist."
    usage
fi
# check for MODEL sub directory
if [ ! -d $DIR/MODEL ]; then
    echo "Directory $DIR/MODEL does not exist."
    usage
fi
if [ ! -e $DIR/MODEL/model.txt ]; then
    echo "File $DIR/MODEL/model.txt does not exist."
    usage
fi
# check for ANNOTATIONS sub directory
if [ ! -d $DIR/ANNOTATIONS ]; then
    echo "Directory $DIR/ANNOTATIONS does not exist."
    usage
fi
if [ ! -e $DIR/ANNOTATIONS/cpgIslandExt.gp ]; then
    echo "File $DIR/ANNOTATIONS/cpgIslandExt.gp does not exist."
    usage
fi
if [ ! -e $DIR/ANNOTATIONS/ensGene.gp ]; then
    echo "File $DIR/ANNOTATIONS/ensGene.gp does not exist."
    usage
fi
if [ ! -e $DIR/ANNOTATIONS/knownGene.gp ]; then
    echo "File $DIR/ANNOTATIONS/knownGene.gp does not exist."
    usage
fi
if [ ! -e $DIR/ANNOTATIONS/knownGeneOld2.gp ]; then
    echo "File $DIR/ANNOTATIONS/knownGeneOld2.gp does not exist."
    usage
fi
if [ ! -e $DIR/ANNOTATIONS/mgcGenes.gp ]; then
    echo "File $DIR/ANNOTATIONS/mgcGenes.gp does not exist."
    usage
fi
if [ $( ls $DIR/SEQ/*.fa | wc -l ) -ne 1 ]; then
    echo "There should be exactly 1 fasta (*.fa) file in $DIR/SEQ/ ."
    usage
fi
############################################################
############################################################

##############################
# SEQUENCE

FASTA=$DIR/SEQ/*.fa
mkdir -p $DIR/logs/

run "evolver_evo -findns ${FASTA} -out_x $DIR/SEQ/seq.x.fa.tmp -out_gff ${DIR}/SEQ/seq.ns.gff -label_x ${LABEL} -log ${DIR}/logs/seq.findns.log"
run "mv ${DIR}/SEQ/seq.x.fa.tmp ${DIR}/SEQ/seq.x.fa"

run "evolver_cvt -fromfasta ${DIR}/SEQ/seq.x.fa -torev ${DIR}/SEQ/seq.x.seq.rev.tmp -genome root -log ${DIR}/logs/seq.cvtrev.log"
run "evolver_cvt -dumpchrids ${DIR}/SEQ/seq.x.seq.rev.tmp -log ${DIR}/logs/seq.seqlength.log"
run "mv ${DIR}/SEQ/seq.x.seq.rev.tmp ${DIR}/SEQ/seq.x.seq.rev"

run "evolver_cvt -fromfasta ${DIR}/SEQ/seq.x.fa -torev ${DIR}/SEQ/root.seq.rev.tmp -genome root"
run "mv ${DIR}/SEQ/root.seq.rev.tmp ${DIR}/SEQ/root.seq.rev"
run "cp ${DIR}/SEQ/root.seq.rev ${DIR}/seq.rev"

##############################
# ANNOTATIONS

runTrf "${DIR}/SEQ/" "trf seq.x.fa 2 7 7 80 10 50 500 -d -h"
echo ' '
run "mv ${DIR}/SEQ/seq.x.fa.2.7.7.80.10.50.500.dat ${DIR}/SEQ/seq.x.fa.dat.tmp"

evolver_trf2gff.py ${DIR}/SEQ/seq.x.fa.dat.tmp > ${DIR}/SEQ/seq.trfannots.gff.tmp
run "mv ${DIR}/SEQ/seq.trfannots.gff.tmp ${DIR}/SEQ/seq.trfannots.gff"

for a in cpgIslandExt ensGene knownGene knownGeneOld2 mgcGenes; do
    run "genePredToGtf file ${DIR}/ANNOTATIONS/${a}.gp ${DIR}/ANNOTATIONS/${a}.gtf.tmp"
    run "mv ${DIR}/ANNOTATIONS/${a}.gtf.tmp ${DIR}/ANNOTATIONS/${a}.gtf"
done

cat ${DIR}/ANNOTATIONS/knownGene.gtf     | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"ucsc./g"      >   ${DIR}/ANNOTATIONS/genes.unsorted.gtf.tmp
cat ${DIR}/ANNOTATIONS/mgcGenes.gtf      | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"mgc./g"       >>  ${DIR}/ANNOTATIONS/genes.unsorted.gtf.tmp
cat ${DIR}/ANNOTATIONS/knownGeneOld2.gtf | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"oldknown./g"  >>  ${DIR}/ANNOTATIONS/genes.unsorted.gtf.tmp
cat ${DIR}/ANNOTATIONS/ensGene.gtf       | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"ens./g"       >>  ${DIR}/ANNOTATIONS/genes.unsorted.gtf.tmp
run "mv ${DIR}/ANNOTATIONS/genes.unsorted.gtf.tmp ${DIR}/ANNOTATIONS/genes.unsorted.gtf"

evolver_gff_sort.py ${DIR}/ANNOTATIONS/genes.unsorted.gtf > ${DIR}/ANNOTATIONS/genes.gtf.tmp
run "mv ${DIR}/ANNOTATIONS/genes.gtf.tmp ${DIR}/ANNOTATIONS/genes.gtf"

run "evolver_evo -cvtannots ${DIR}/ANNOTATIONS/genes.gtf -out ${DIR}/ANNOTATIONS/genes.x.gff.tmp.tmp -seq ${DIR}/SEQ/seq.x.seq.rev -log ${DIR}/logs/genes.cvtannots.log"
run "mv ${DIR}/ANNOTATIONS/genes.x.gff.tmp.tmp ${DIR}/ANNOTATIONS/genes.x.gff.tmp"

cat ${DIR}/ANNOTATIONS/cpgIslandExt.gtf | sed -e 's/exon/island/' > ${DIR}/ANNOTATIONS/genes.cpg.gff.tmp
run "mv ${DIR}/ANNOTATIONS/genes.cpg.gff.tmp ${DIR}/ANNOTATIONS/genes.cpg.gff"

run "evolver_evo -xgff ${DIR}/ANNOTATIONS/genes.cpg.gff -gff_ns ${DIR}/SEQ/seq.ns.gff -out ${DIR}/ANNOTATIONS/genes.cpg.x.gff.tmp -log ${DIR}/logs/genes.xgffcpg.log"
run "mv ${DIR}/ANNOTATIONS/genes.cpg.x.gff.tmp ${DIR}/ANNOTATIONS/genes.cpg.x.gff"

SEQLEN=$(grep -a "  $LABEL" ${DIR}/logs/seq.seqlength.log | awk '{ print $3 }')
run "evolver_evo -seed $RANDOM -genncces -excl_gff ${DIR}/ANNOTATIONS/genes.x.gff.tmp -length ${SEQLEN} -log ${DIR}/logs/genes.genncces.log -out ${DIR}/ANNOTATIONS/genes.ncces.gff.tmp -model ${DIR}/MODEL/model.txt"
run "mv ${DIR}/ANNOTATIONS/genes.ncces.gff.tmp ${DIR}/ANNOTATIONS/genes.ncces.gff"

run "evolver_evo -seed $RANDOM -assncces ${DIR}/ANNOTATIONS/genes.ncces.gff -genes ${DIR}/ANNOTATIONS/genes.x.gff.tmp -length ${SEQLEN} -log ${DIR}/logs/genes.assncces.log -out ${DIR}/ANNOTATIONS/genes.ncces.ass.gff.tmp -model ${DIR}/MODEL/model.txt"
run "mv ${DIR}/ANNOTATIONS/genes.ncces.ass.gff.tmp ${DIR}/ANNOTATIONS/genes.ncces.ass.gff"

cat ${DIR}/ANNOTATIONS/genes.ncces.ass.gff  ${DIR}/ANNOTATIONS/genes.x.gff.tmp > ${DIR}/ANNOTATIONS/genes.ces.gff.tmp
run "mv ${DIR}/ANNOTATIONS/genes.ces.gff.tmp ${DIR}/ANNOTATIONS/genes.ces.gff"

run "evolver_evo -seed $RANDOM -assprobs ${DIR}/ANNOTATIONS/genes.ces.gff -log ${DIR}/logs/genes.assprobs.log -out ${DIR}/ANNOTATIONS/genes.ces.probs.gff.tmp"
run "mv ${DIR}/ANNOTATIONS/genes.ces.probs.gff.tmp ${DIR}/ANNOTATIONS/genes.ces.probs.gff"

run "evolver_evo -fixcpgs ${DIR}/ANNOTATIONS/genes.cpg.x.gff -cds ${DIR}/ANNOTATIONS/genes.ces.gff -out ${DIR}/ANNOTATIONS/genes.fixedcpg.gff.tmp -log ${DIR}/ANNOTATIONS/genes.fixcpgs.log"
run "mv ${DIR}/ANNOTATIONS/genes.fixedcpg.gff.tmp ${DIR}/ANNOTATIONS/genes.fixedcpg.gff"

cat ${DIR}/ANNOTATIONS/genes.fixedcpg.gff ${DIR}/ANNOTATIONS/genes.ces.probs.gff ${DIR}/SEQ/seq.trfannots.gff > ${DIR}/ANNOTATIONS/genes.unsorted.gff.tmp
run "mv ${DIR}/ANNOTATIONS/genes.unsorted.gff.tmp ${DIR}/ANNOTATIONS/genes.unsorted.gff"

evolver_gff_sort.py ${DIR}/ANNOTATIONS/genes.unsorted.gff > ${DIR}/ANNOTATIONS/genes.x.annots.gff.tmp
run "mv ${DIR}/ANNOTATIONS/genes.x.annots.gff.tmp ${DIR}/ANNOTATIONS/genes.x.annots.gff"

evolver_gff_gene_lengths.py ${DIR}/ANNOTATIONS/genes.x.annots.gff > ${DIR}/ANNOTATIONS/genes.gene_lengths.tmp
run "mv ${DIR}/ANNOTATIONS/genes.gene_lengths.tmp ${DIR}/ANNOTATIONS/genes.gene_lengths"

run "evolver_cvt -gffcover ${DIR}/ANNOTATIONS/genes.gene_lengths -out ${DIR}/ANNOTATIONS/genes.cov.gff.tmp -log ${DIR}/logs/genes.genecover.log"
run "mv ${DIR}/ANNOTATIONS/genes.cov.gff.tmp ${DIR}/ANNOTATIONS/genes.cov.gff"

run "cp ${DIR}/ANNOTATIONS/genes.x.annots.gff ${DIR}/ANNOTATIONS/root.annots.gff"
run "cp ${DIR}/ANNOTATIONS/root.annots.gff ${DIR}/annots.gff"

##############################
# STATS
mkdir -p ${DIR}/stats

touch ${DIR}/stats/merged_root.stats.txt
egrep 'CDS|UTR' ${DIR}/ANNOTATIONS/root.annots.gff > ${DIR}/stats/cds_annots.gff.tmp
run "mv ${DIR}/stats/cds_annots.gff.tmp ${DIR}/stats/cds_annots.gff"

evolver_gff_cdsutr2exons.py ${DIR}/stats/cds_annots.gff > ${DIR}/stats/exons.gff.tmp
run "mv ${DIR}/stats/exons.gff.tmp ${DIR}/stats/exons.gff"

evolver_gff_exons2introns.py ${DIR}/stats/exons.gff > ${DIR}/stats/introns.gff.tmp
run "mv ${DIR}/stats/introns.gff.tmp ${DIR}/stats/introns.gff"

cat ${DIR}/stats/introns.gff ${DIR}/stats/exons.gff ${DIR}/ANNOTATIONS/root.annots.gff > ${DIR}/stats/expanded_annots.gff.tmp
run "mv ${DIR}/stats/expanded_annots.gff.tmp ${DIR}/stats/expanded_annots.gff"

run "evolver_evo -annotstats ${DIR}/annots.gff -seq ${DIR}/seq.rev -log ${DIR}/stats/annotstats.txt.tmp"
run "mv ${DIR}/stats/annotstats.txt.tmp ${DIR}/stats/annotstats.txt"

##############################
# TEST

run "evolver_evo -valgenes ${DIR}/seq.rev -annots ${DIR}/annots.gff"
