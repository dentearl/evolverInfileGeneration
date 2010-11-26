#!/usr/bin/env python
"""
splitEvolverInfiles.py
dent earl, dearl (a) soe ucsc edu
Thanksgiving day, 2010 :(

For cutting a paired fasta and gff into
smaller fastas and gffs, with correct new
coordinates for the gff files.

At the moment, annotations that range between
a split are simply dropped from the output. 

"""
from optparse import OptionParser
import os
import re
import sys

MAX_FASTA_LINE_LENGTH = 50

def usage(s=None):
    if s:
        sys.stderr.write( 'ERROR: %s\n' % s )
    sys.stderr.write( 'USAGE: '+ sys.argv[0] +' --fasta seq.fa --annots annots.gff [--numFiles 2] [--outDir path/to/dir/ ]\n')
    sys.exit(2)

def initOptions(parser):
    parser.add_option('-f', '--fasta',dest='fasta',
                      help='fasta file input')
    parser.add_option('-a', '--annots',dest='annots',
                      help='annotation file input.')
    parser.add_option('-n', '--numFiles',dest='numFiles',
                      type='int', default=2,
                      help='number of files to split input into.')
    parser.add_option('-o', '--outDir',dest='outDir',
                      help='directory in which to write output.')

def checkOptions( options ):
    if (options.fasta == None) or (not os.path.exists(options.fasta)):
        usage('specify fasta input, --fasta')
    if (options.annots == None) or (not os.path.exists(options.annots)):
        usage('specify annotation input, --annots.')
    if not options.outDir:
        options.outDir = os.getcwd()
    if not os.path.isDir(options.outDir):
        usage('output directory "%s" is not a directory, --outDir.' % options.outDir )
    options.outDir = os.path.abspath( options.outDir )

def fastaLength( fa ):
    f = open(fa)
    c = 0
    for line in f.readlines():
        if line[0] == '>':
            continue
        line = line.strip()
        c += len( line )
    return c

def newOuts( outDir, i ):
    faOut = open( os.path.join( outDir, 'fastaOut%d.fa' % i), 'w' )
    faOut.write( '>chr%d\n' % i )
    anOut = open( os.path.join( outDir, 'annotsOut%d.gff' % i), 'w' )
    i += 1
    return (faOut, anOut, i)

def splitTransformAnnots( annots, splitEvery ):
    aList = []
    an = open( annots )
    offset = 0
    chr = 0
    thisSet = ''
    for line in an.readlines():
        line = line.strip()
        data = line.split('\t')
        while int( data[4] ) - offset >= splitEvery:
            offset += splitEvery
            chr += 1
            aList.append( thisSet )
            thisSet = ''
        if int( data[3] ) < 1 + offset:
            continue
        data[0] = 'chr%d' % chr
        data[3] = str( int( data[3] ) - offset )
        data[4] = str( int( data[4] ) - offset )
        thisSet += '\t'.join(data)
        thisSet += '\n'
    aList.append( thisSet )
    return aList

def splitFiles( fa, annots, splitEvery, outDir ):
    i = 0 # i is the number of the current output file
    c = 0 # c is the total number of characters processed so far
    ( faOut, anOut, i ) = newOuts( outDir, i )
    f = open( fa )
    a = open( annots )
    cNumLine = 0

    transformedAnnotsList = splitTransformAnnots( annots, splitEvery )
    for line in f.readlines():
        if line[0] == '>':
            continue
        line = line.strip()
        for l in line:
            faOut.write(l)
            c += 1
            cNumLine += 1
            if cNumLine == MAX_FASTA_LINE_LENGTH:
                faOut.write('\n')
                cNumLine = 0
            if c == splitEvery:
                c = 0
                cNumLine = 0
                anOut.write( '%s\n' % transformedAnnotsList[i-1] )
                anOut.close()
                faOut.write('\n')
                faOut.close()
                ( faOut, anOut, i ) = newOuts( outDir, i )
    if faOut:
        anOut.close()
        faOut.write('\n')
        faOut.close()
    if not cNumLine:
        # if the split fell right on the end of the fasta we can end up with blank files.
        os.remove( os.path.join(outDir, 'fastaOut%d.fa' % (i-1) ) )
        os.remove( os.path.join(outDir, 'annotsOut%d.gff' % (i-1) ) )
        
def main():
    parser=OptionParser()
    initOptions( parser )
    ( options, args ) = parser.parse_args()
    checkOptions( options )
    faLength = fastaLength( options.fasta )
    splitEvery = int( faLength / options.numFiles )
    splitFiles( options.fasta, options.annots, splitEvery, options.outDir )
    

if __name__ == '__main__':
    main()

