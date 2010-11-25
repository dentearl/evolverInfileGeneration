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
from optparse import OptionParser
import re
import sys

class BadInputError( ValueError ):
    pass

def usage(s=None):
    if s:
        sys.stderr.write( 'ERROR: %s\n' % s )
    sys.stderr.write( 'USAGE: '+ sys.argv[0] +' --chr 4 --startPosition 101 --endPosition 200 < mcgGenes.gp\n')
    sys.exit(2)
    
def initOptions(parser):
    parser.add_option('-c', '--chr',dest='chr',
                      help='Chromosome')
    parser.add_option('-s', '--startPosition',dest='startPosition',
                      type='int', help='Start position, [1..n] coordinates.')
    parser.add_option('-e', '--endPosition',dest='endPosition',
                      type='int', help='End position, [1..n] coordinates.')

def checkOptions( options ):
    if options.chr == None:
        usage('specify chromosome, --chr')
    if options.startPosition == None:
        usage('specify --startPosition.')
    if options.endPosition == None:
        usage('specify --endPosition.')
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
        raise BadInputError( 'length of exonStarts (%d) not equal to length of exonEnds (%d)' %(len(exonStarts), len(exonEnds)) )
    if len(exonStarts) != int(tData[ -1 ]):
        raise BadInputError('exonCount (%d)not equal to length of exonStarts (%d)' %( int(tData[-1]), len(exonStarts)))
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
        if ( r.group( 1 ) == options.chr) and ( int(data[ 3 ]) >= ( options.startPosition ) ) and ( int(data[ 4 ]) <= options.endPosition ):
            tData = transformCoordinates( data, options )
            print '%s' % '\t'.join( tData )

def main():
    parser=OptionParser()
    initOptions( parser )
    ( options, args ) = parser.parse_args()
    checkOptions( options )
    readAndProcessInput( options )

if __name__ == '__main__':
    main()
