import unittest
import os, sys
myBinDir = os.path.normpath(os.path.dirname(sys.argv[0]))
sys.path.append(myBinDir + "/../../..")
os.environ["PATH"] = myBinDir + "/../../../../bin:" + os.environ["PATH"]
from sonLib.bioio import logger

def writeFA_1( faPath ):
    fa = open( faPath, 'w')
    fa.write( '>MyFastaFile blah blah blah\n')
    fa.write( 'AGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n')
    fa.write( 'AGTGTTTCCCCCATTG\n')
    fa.write( 'AGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n')
    fa.close()

def writeAN_1( anPath ):
    an = open( anPath, 'w')
    an.write( 'chr0\tgenncces0\tNGE\t1\t5\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write( 'chr0\tgenncces1\tNGE\t6\t10\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write( 'chr0\tgenncces2\tNGE\t28\t35\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write( 'chr0\tgenncces3\tNGE\t50\t60\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write( 'chr0\tgenncces4\tNGE\t75\t80\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.close()

def extractGffRegionsToList( f ):
    l = []
    for line in f.readlines():
        line.strip()
        data = line.split('\t')
        if len( data ) < 9:
            continue
        l.append( int(data[3]) )
        l.append( int(data[4]) )
    return l
    
class VerifyKnownInput( unittest.TestCase ):
    if not os.path.exists('temp_testFiles'):
        os.mkdir('temp_testFiles')
    def test_fastaLength( self ):
        from splitEvolverInfiles import fastaLength
        """Fasta length should be correctly reported"""
        faPath = os.path.join('temp_testFiles', 'fasta.fa')
        writeFA_1( faPath )
        self.assertEqual( 82, fastaLength( faPath ) )
    def test_fastaSplit( self ):
        import splitEvolverInfiles as SEI
        faPath = os.path.join('temp_testFiles', 'fasta.fa')
        anPath = os.path.join('temp_testFiles', 'annots.gff')
        writeFA_1( faPath )
        writeAN_1( anPath )
        faLength = SEI.fastaLength( faPath )
        splitEvery = int( faLength / 2 )
        SEI.splitFiles( faPath, anPath, splitEvery, 'temp_testFiles' )
        (faOut0, faOut1, anOut0, anOut1) = ('', '', '', '')
        faFiles = [ faOut0, faOut1 ]
        anFiles = [ anOut0, anOut1 ]
        faOutputs = [ '>chr0\nAGTGTTTCCCCCATTGATTTGAATTGATTTAGTAGTGTTTC\n',
                      '>chr1\nCCCCATTGAGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n']
        anRanges  = [ [1, 5, 6, 10, 28, 35],
                      [9, 19, 34, 39] ]
        for i in range(0, len(faFiles) ):
            faFiles[i] = open( os.path.join('temp_testFiles', 'fastaOut%d.fa' % i) )
            anFiles[i] = open( os.path.join('temp_testFiles', 'annotsOut%d.gff' % i) )
            self.assertEqual(''.join( faFiles[i].readlines() ), faOutputs[i] )
            self.assertEqual( extractGffRegionsToList( anFiles[i] ), anRanges[ i ] )
            faFiles[i].close()
            anFiles[i].close()
            
        splitEvery = int( faLength / 3 )
        SEI.splitFiles( faPath, anPath, splitEvery, 'temp_testFiles' )
        (faOut2, faOut3, anOut2, anOut3) = ('', '', '', '')
        faFiles = [ faOut0, faOut1, faOut2, faOut3 ]
        anFiles = [ anOut0, anOut1, anOut2, anOut3 ]
        faOutputs = [ '>chr0\nAGTGTTTCCCCCATTGATTTGAATTGA\n',
                      '>chr1\nTTTAGTAGTGTTTCCCCCATTGAGTGT\n',
                      '>chr2\nTTCCCCCATTGATTTGAATTGATTTAG\n',
                      '>chr3\nT\n']
        anRanges  = [ [1, 5, 6, 10],
                      [1, 8],
                      [21, 26],
                      [] ]
        for i in range(0, len(faFiles) ):
            faFiles[i] = open( os.path.join('temp_testFiles', 'fastaOut%d.fa' % i) )
            anFiles[i] = open( os.path.join('temp_testFiles', 'annotsOut%d.gff' % i) )
            self.assertEqual(''.join( faFiles[i].readlines() ), faOutputs[i] )
            self.assertEqual( extractGffRegionsToList( anFiles[i] ), anRanges[ i ] )
            faFiles[i].close()
            anFiles[i].close()
        
if __name__ == "__main__":
    unittest.main()
