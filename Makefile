# This Makefile by dent earl, dearl(a) soe ucsc edu
# 31 March 2010
# 
# This Makefile is used to generate an infile set used as the 
# ancestor or root genome for an evolver genome simulation run.
#
# This Makefile assumes you have the kent source tree compiled. Specifically
# we assume the installation and configuration of
# *hgsql
# *bedToGenePred
# *genePredToGtf
##############################
SHELL:= /bin/bash
rawPath:= raw
intPath:= intermediates
rootPath:= root
logPath:= logs
statsPath:= stats
MODEL:= /cluster/home/dearl/evolver/myToy/gParams/model.txt
GENOME:= root #$(shell basename $$(pwd))
.SECONDARY: # leave this blank to force make to keep intermediate files
##############################
# MAKE EDITS TO THE chr VARIABLE TO CHANGE THE
# INFILE GENOME
##############################
testSet:=NO
##############################
ifeq ($(testSet), YES)
	chrs:= 22_random
	gtfs:= mgcGenes cpgIslandExt
else
	chrs:= 20 21 22
	gtfs:= mgcGenes knownGene knownGeneOld2 cpgIslandExt ensGene
endif
#
# DO NOT EDIT BELOW THIS LINE
##################################################
all: rawData sequence annotations stats
	@echo ALL WORK COMPLETE
##################################################

stats: ${statsPath}/expanded_annots.gff
	@echo STATS COMPLETE
##################################################
# This section takes the gtf files and creates the 
# first set of stats files.
${statsPath}/expanded_annots.gff: ${statsPath}/introns.gff ${statsPath}/exons.gff ${rootPath}/root.annots.gff
	cat $^ > $@.tmp
	mv $@.tmp $@
${statsPath}/introns.gff: ${statsPath}/exons.gff ${statsPath}/cds_annots.gff ${rootPath}/root.annots.gff
	evolver_gff_exons2introns.py $< > $@.tmp
	mv $@.tmp $@
${statsPath}/exons.gff: ${statsPath}/cds_annots.gff ${rootPath}/root.annots.gff
	evolver_gff_cdsutr2exons.py $< > $@.tmp
	mv $@.tmp $@
${statsPath}/cds_annots.gff: ${rootPath}/root.annots.gff ${statsPath}/merged_root.stats
	egrep 'CDS|UTR' ${rootPath}/root.annots.gff > $@.tmp
	mv $@.tmp $@
${statsPath}/merged_root.stats:
	touch $@

annotations: $(foreach chr, $(chrs), $(join ${intPath}/chr${chr},.genes.cov.gff)) annots.gff
	@echo ANNOTATIONS COMPLETE
##################################################
# This section takes the gtf files, corrects for the new
# N-less coordinate space, merges the gtfs, and creates a 
# single gtf annotation
annots.gff: ${rootPath}/root.annots.gff
	cp $< $@
${rootPath}/root.annots.gff: $(foreach chr, $(chrs), $(join ${intPath}/chr${chr},.x.annots.gff)) #.genes.cov.gff))
	cat $^ > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.genes.cov.gff: ${intPath}/chr%.gene_lengths
	evolver_cvt -gffcover ${intPath}/chr$*.gene_lengths -out $@.tmp -log ${logPath}/chr$*.genecover.log
	mv $@.tmp $@
${intPath}/chr%.gene_lengths: ${intPath}/chr%.x.annots.gff
	evolver_gff_gene_lengths.py $< > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.x.annots.gff: ${intPath}/chr%.unsorted.gff
	evolver_gff_sort.py $< > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.unsorted.gff: ${intPath}/chr%.fixedcpg.gff ${intPath}/chr%.ces.probs.gff ${intPath}/chr%.trfannots.gff
	cat $^ > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.fixedcpg.gff: ${intPath}/chr%.cpg.x.gff ${intPath}/chr%.ces.gff
	evolver_evo -fixcpgs $< -cds ${intPath}/chr$*.ces.gff -out $@.tmp -log ${logPath}/chr$*.fixcpgs.log
	mv $@.tmp $@
${intPath}/chr%.ces.probs.gff: ${intPath}/chr%.ces.gff
	evolver_evo -assprobs ${intPath}/chr$*.ces.gff -log ${logPath}/chr$*.assprobs.log -out $@.tmp
	mv $@.tmp $@
${intPath}/chr%.ces.gff: ${intPath}/chr%.ncces.ass.gff
	cat $<  ${intPath}/chr$*.genes.x.gff.tmp > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.ncces.ass.gff: ${intPath}/chr%.ncces.gff
	SEQLEN=$$(grep -a "  chr$*" ${logPath}/chr$*.seqlength.log | awk '{ print $$3 }'); \
	evolver_evo -assncces $< -genes ${intPath}/chr$*.genes.x.gff.tmp -length $$SEQLEN -log ${logPath}/chr$*.assncces.log -out $@.tmp -model $(MODEL)
	mv $@.tmp $@
${intPath}/chr%.ncces.gff: ${intPath}/chr%.genes.x.gff.tmp
	SEQLEN=$$(grep -a "  chr$*" ${logPath}/chr$*.seqlength.log | awk '{ print $$3 }'); \
	evolver_evo -genncces -excl_gff $< -length $$SEQLEN -log ${logPath}/chr$*.genncces.log -out $@.tmp -model $(MODEL)
	mv $@.tmp $@
${intPath}/chr%.cpg.x.gff: ${intPath}/chr%.cpg.gff
	evolver_evo -xgff $< -gff_ns ${intPath}/chr$*.ns.gff -out $@.tmp -log ${logPath}/chr$*.xgffcpg.log
	mv $@.tmp $@
${intPath}/chr%.cpg.gff: ${rawPath}/cpgIslandExt.gtf
	grep -Pa '^chr$*\t' $< | sed -e 's/exon/island/' > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.genes.x.gff.tmp: ${intPath}/chr%.genes.x.gff
	evolver_evo -cvtannots $< -out $@.tmp -seq ${intPath}/chr$*.x.seq.rev -log ${logPath}/chr$*.cvtannots.log
	mv $@.tmp $@
${intPath}/chr%.genes.x.gff: ${intPath}/chr%.genes.gtf
	evolver_evo -xgff $< -gff_ns ${intPath}/chr$*.ns.gff -out $@.tmp -log ${logPath}/chr$*.xgff.log
	mv $@.tmp $@
${intPath}/chr%.genes.gtf: ${intPath}/chr%.genes.unsorted.gtf
	evolver_gff_sort.py $< > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.genes.unsorted.gtf: $(foreach gtf, $(gtfs), $(join ${rawPath}/${gtf}, .gtf)) 
	grep -Pa '^chr$*\t' ${rawPath}/knownGene.gtf     | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"ucsc./g"     >  $@.tmp
	grep -Pa '^chr$*\t' ${rawPath}/mgcGenes.gtf      | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"mgc./g"      >> $@.tmp
	grep -Pa '^chr$*\t' ${rawPath}/knownGeneOld2.gtf | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"oldknown./g" >> $@.tmp
	grep -Pa '^chr$*\t' ${rawPath}/ensGene.gtf       | evolver_gtfStopCodonMerger.py | sed -e "s/_id \"/_id \"ens./g"      >> $@.tmp
	mv $@.tmp $@
${intPath}/chr%.trfannots.gff: ${intPath}/chr%.x.fa.dat.tmp
	evolver_trf2gff.py $< > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.x.fa.dat.tmp: ${intPath}/chr%.x.fa
	LOCALDIR=$$(pwd);\
	simCtrl_wrapperTRF.py $$LOCALDIR/${intPath}/chr$*.x.fa 2 7 7 80 10 50 500 -d -h
	mv ${intPath}/chr$*.x.fa.2.7.7.80.10.50.500.dat $@

sequence: $(foreach chr, $(chrs), $(join ${intPath}/chr${chr},.x.seq.rev)) seq.rev
	@echo SEQUENCES COMPLETE
##################################################
# This section takes the fasta files, finds all the Ns
# and then removes them, and then creates the .rev files.
seq.rev: ${rootPath}/root.seq.rev
	cp $< $@
${rootPath}/root.seq.rev: ${intPath}/root.fa
	evolver_cvt -fromfasta $< -torev $@.tmp -genome ${GENOME}
	mv $@.tmp $@
${intPath}/root.fa: $(foreach chr, $(chrs), $(join ${intPath}/chr${chr},.x.fa))
	cat $^ > $@.tmp
	mv $@.tmp $@
${intPath}/chr%.x.seq.rev: ${intPath}/chr%.x.fa
	evolver_cvt -fromfasta $< -torev $@.tmp -genome ${GENOME} -log ${logPath}/chr$*.cvtrev.log
	evolver_cvt -dumpchrids $@.tmp -log ${logPath}/chr$*.seqlength.log
	mv $@.tmp $@
${intPath}/chr%.x.fa: ${rawPath}/chr%.fa
	evolver_evo -findns $< -out_x $@.tmp -out_gff ${intPath}/chr$*.ns.gff -label_x chr$* -log ${logPath}/chr$*.findns.log
	mv $@.tmp $@

rawData: $(foreach chr, $(chrs), $(join ${rawPath}/chr${chr}, .fa)) $(foreach gtf, $(gtfs), $(join ${rawPath}/${gtf}, .gtf))
	@echo RAW DATA COMPLETE
##################################################
# This section extracts data from UCSC and prepares it
# to be used to generate infiles.
${rawPath}/chr%.fa: ${rawPath}/chr%.fa.gz
	gunzip -c $<  > $@.tmp
	mv $@.tmp $@
${rawPath}/chr%.fa.gz: ${rawPath}/
	curl http://hgdownload.cse.ucsc.edu/goldenPath/hg18/chromosomes/chr$*.fa.gz --create-dirs -o $@.tmp
	mv $@.tmp $@
${rawPath}/:
	mkdir -p ${rawPath} ${logPath} ${intPath} ${rootPath} ${statsPath}
${rawPath}/%.gtf: ${rawPath}/%.gp
	genePredToGtf file $< $@.tmp
	mv $@.tmp $@
ifeq ($(testSet),YES)
${rawPath}/mgcGenes.gp:
	hgsql -Ne 'select * from mgcGenes' hg18 | cut -f 2- | grep -a 'chr22_random' > $@.tmp
	mv $@.tmp $@
${rawPath}/knownGene.gp:
	touch $@
${rawPath}/knownGeneOld2.gp:
	touch $@
${rawPath}/cpgIslandExt.gp: ${rawPath}/cpgIslandExt.bed
	bedToGenePred $< $@.tmp
	mv $@.tmp $@
${rawPath}/cpgIslandExt.bed: 
	hgsql -Ne 'select * from cpgIslandExt' hg18 |  cut -f 1-4 | grep -a 'chr22_random'> $@.tmp
	mv $@.tmp $@
${rawPath}/ensGene.gp:
	touch $@
else
${rawPath}/mgcGenes.gp:
	hgsql -Ne 'select * from mgcGenes' hg18 | cut -f 2- > $@.tmp
	mv $@.tmp $@
${rawPath}/knownGene.gp:
	hgsql -Ne 'select * from knownGene' hg18 | cut -f 1-10 > $@.tmp
	mv $@.tmp $@
${rawPath}/knownGeneOld2.gp:
	hgsql -Ne 'select * from knownGeneOld2' hg18 | cut -f 1-10 > $@.tmp
	mv $@.tmp $@
${rawPath}/cpgIslandExt.gp: ${rawPath}/cpgIslandExt.bed
	bedToGenePred $< $@.tmp
	mv $@.tmp $@
${rawPath}/cpgIslandExt.bed: 
	hgsql -Ne 'select * from cpgIslandExt' hg18 |  cut -f 1-4 > $@.tmp
	mv $@.tmp $@
${rawPath}/ensGene.gp:
	hgsql -Ne 'select * from ensGene' hg18 | cut -f 2- > $@.tmp
	mv $@.tmp $@
endif

clean:
	rm -rf ${rawPath}/ ${logPath}/ ${intPath}/ ${rootPath}/ ${statsPath}/ seq.rev
