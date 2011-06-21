SHELL:=/bin/bash -e
export SHELLOPTS=pipefail

.PHONY: all clean test

binPath = bin
progs = infileMakefile singleRegionGenerator.sh splitEvolverInfiles.py subsetRemapGP.py

all: ${progs:%=${binPath}/%}

${binPath}/infileMakefile: src/infileMakefile
	@mkdir -p $(dir $@)
	cp -f $< $@.tmp
	mv $@.tmp $@

${binPath}/%: src/% __init__.py
	@mkdir -p $(dir $@)
	touch ${binPath}/__init__.py
	cp -f $< $@.tmp
	chmod 755 $@.tmp
	mv $@.tmp $@

__init__.py:
	touch $@

clean:
	rm -rf ${binPath} temp_testFiles/ testSplitEvolverInfiles.pyc __init__.py

test:
	python src/testSplitEvolverInfiles.py --verbose
	rm -rf src/testSplitEvolverInfiles.pyc temp_testFiles/
