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
from optparse import OptionParser
import os
import re
import sys

def initOptions(parser):
    parser.add_option('-f', '--fasta',dest='fasta',
                      help='fasta file input')
    parser.add_option('-a', '--annots',dest='annots',
                      help='annotation file input.')
    parser.add_option('-n', '--numFiles',dest='numFiles',
                      type='int', default=2,
                      help='number of files to split input into. default=%default')
    parser.add_option('-o', '--outDir',dest='outDir',
                      help='directory in which to write output.')
    parser.add_option('--maxLineLength', dest='maxLineLength',
                      default=50, type='int',
                      help='Length of the fasta output lines. default=%default')

def checkOptions( parser, options ):
    if options.fasta is None or not os.path.exists(options.fasta):
        parser.error('specify fasta input, --fasta')
    if options.annots is None or not os.path.exists(options.annots):
        parser.error('specify annotation input, --annots.')
    if not options.outDir:
        options.outDir = os.getcwd()
    if not os.path.isdir( options.outDir ):
        parser.error('output directory "%s" is not a directory, --outDir.' % options.outDir )
    options.outDir = os.path.abspath( options.outDir )
    if maxLineLength < 1:
        parser.error('--maxLineLength < 1. %d is not a valid value.' % options.maxLineLength)

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

def splitFiles( fa, annots, splitEvery, outDir, maxLineLength ):
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
            if cNumLine == maxLineLength:
                faOut.write('\n')
                cNumLine = 0
            if c == splitEvery:
                c = 0
                cNumLine = 0
                anOut.write( transformedAnnotsList[i-1] )
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
    usage=('usage: %prog --fasta=file.fa --annots=file.gff --outDir=path/to/dir [options]\n'
           'For cutting a paired fasta and gff into\n'
           'smaller fastas and gffs, with correct new\n'
           'coordinates for the gff files.\n\n'
           'At the moment, annotations that range between\n'
           'a split are simply dropped from the output.')
    parser=OptionParser( usage=usage )
    initOptions( parser )
    ( options, args ) = parser.parse_args()
    checkOptions( parser, options )
    faLength = fastaLength( options.fasta )
    splitEvery = int( faLength / options.numFiles )
    splitFiles( options.fasta, options.annots, splitEvery, options.outDir, options.maxLineLength )
    

if __name__ == '__main__':
    main()

