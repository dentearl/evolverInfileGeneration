#!/usr/bin/env python
"""
subsetRemapGP.py
dent earl, dearl (a) soe ucsc edu
19 Oct 2010

Takes as its input a .gp file, a --chr, --positionStart and
--positionEnd with positions [1..n] . It returns a parsed down
.gp with only annotations that were in the range specified,
and it remaps the annotations to positions [0..n).

So if you wanted to subset positions 101..150, and there
was a gene at 110..120 it would become
gene 9..19

Confusing, I know, but that's how it is.

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
import re
import sys

class BadInputError( ValueError ):
    pass
    
def initOptions(parser):
    parser.add_option('-c', '--chr',dest='chr',
                      help='Chromosome')
    parser.add_option('-s', '--startPosition',dest='startPosition',
                      type='int', help='Start position, [1..n] coordinates.')
    parser.add_option('-e', '--endPosition',dest='endPosition',
                      type='int', help='End position, [1..n] coordinates.')

def checkOptions( parser, options ):
    if options.chr is None:
        parser.error('specify chromosome, --chr')
    if options.startPosition is None:
        parser.error('specify --startPosition.')
    if options.endPosition is None:
        parser.error('specify --endPosition.')
    options.startPosition -= 1

def transformCoordinates( data, options ):
    """ takes one line and transforms the coordinates from [0..n) to [1..n]
    and then 
    """
    tData = []
    tData[0:3] = data[0:3]
    for i in range(3, 7):
        tData.append( str ( int(data[i]) - options.startPosition ) )
    tData.append( data[ 7 ] )
    exonStarts = data[ 8 ].strip(',').split(',')
    exonEnds   = data[ 9 ].strip(',').split(',')
    if len(exonStarts) != len(exonEnds):
        raise BadInputError( 'length of exonStarts (%d) not equal to length of exonEnds (%d)' %
                             (len(exonStarts), len(exonEnds)) )
    if len(exonStarts) != int(tData[ -1 ]):
        raise BadInputError('exonCount (%d)not equal to length of exonStarts (%d)' %
                            ( int(tData[-1]), len(exonStarts)) )
    xFormExonStarts = []
    xFormExonEnds = []
    for i in range( 0, len(exonStarts) ):
        xFormExonStarts.append( str( int(exonStarts[ i ]) - options.startPosition ) )
        xFormExonEnds.append( str( int(exonEnds[ i ])   - options.startPosition ) )
    tData.append( ','.join( xFormExonStarts ) )
    tData.append( ','.join( xFormExonEnds ) )
    tData[ 10: ] = data[ 10: ]
    return tData


def readAndProcessInput( options ):
    pat = re.compile('chr(.+)')
    for line in sys.stdin:
        line = line.strip()
        data = line.split('\t')
        r = re.match( pat, data[ 1 ] )
        if (( r.group( 1 ) == options.chr) and ( int(data[ 3 ]) >= ( options.startPosition ) ) and 
            ( int(data[ 4 ]) <= options.endPosition )):
            tData = transformCoordinates( data, options )
            print '%s' % '\t'.join( tData )

def main():
    usage=( 'usage: %prog --chr=N --positionStart=X --positionEnd=Y\n'
            'Takes as its input a .gp file, a --chr, --positionStart=X and\n'
            '--positionEnd=Y with positions [X..Y] . It returns a parsed down\n'
            '.gp with only annotations that were in the range specified,\n'
            'and it remaps the annotations to positions [X-1..Y).\n\n'
            'So if you wanted to subset positions 101..150, and there\n'
            'was a gene at 110..120 it would become\n'
            'gene 9..19' )
    parser=OptionParser(usage=usage)
    initOptions( parser )
    options, args = parser.parse_args()
    checkOptions( parser, options )
    readAndProcessInput( options )

if __name__ == '__main__':
    main()
