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
import os
import sys
import unittest

myBinDir = os.path.normpath(os.path.dirname(sys.argv[0]))
sys.path.append(myBinDir + "/../../..")
os.environ["PATH"] = myBinDir + "/../../../../bin:" + os.environ["PATH"]

def writeFA_1(faPath):
    fa = open(faPath, 'w')
    fa.write('>MyFastaFile blah blah blah\n')
    fa.write('AGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n')
    fa.write('AGTGTTTCCCCCATTG\n')
    fa.write('AGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n')
    fa.close()

def writeAN_1(anPath):
    an = open(anPath, 'w')
    an.write('chr0\tgenncces0\tNGE\t1\t5\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write('chr0\tgenncces1\tNGE\t6\t10\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write('chr0\tgenncces2\tNGE\t28\t35\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write('chr0\tgenncces3\tNGE\t50\t60\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.write('chr0\tgenncces4\tNGE\t75\t80\t0\t+\t.\tavgprob "0.5176"; probs "a8ac489e5a";\n')
    an.close()

def extractGffRegionsToList(f):
    l = []
    for line in f.readlines():
        line.strip()
        data = line.split('\t')
        if len(data) < 9:
            continue
        l.append(int(data[3]))
        l.append(int(data[4]))
    return l
    
class VerifyKnownInput(unittest.TestCase):
    if not os.path.exists('temp_testFiles'):
        os.mkdir('temp_testFiles')
    def test_fastaLength(self):
        from evolverInfileGeneration.bin.splitEvolverInfiles import fastaLength
        """Fasta length should be correctly reported"""
        faPath = os.path.join('temp_testFiles', 'fasta.fa')
        writeFA_1(faPath)
        self.assertEqual(82, fastaLength(faPath))
    def test_fastaSplit(self):
        import splitEvolverInfiles as SEI
        faPath = os.path.join('temp_testFiles', 'fasta.fa')
        anPath = os.path.join('temp_testFiles', 'annots.gff')
        writeFA_1(faPath)
        writeAN_1(anPath)
        faLength = SEI.fastaLength(faPath)
        splitEvery = int(faLength / 2)
        SEI.splitFiles(faPath, anPath, splitEvery, 'temp_testFiles', 50)
        (faOut0, faOut1, anOut0, anOut1) = ('', '', '', '')
        faFiles = [faOut0, faOut1]
        anFiles = [anOut0, anOut1]
        faOutputs = ['>chr0\nAGTGTTTCCCCCATTGATTTGAATTGATTTAGTAGTGTTTC\n',
                      '>chr1\nCCCCATTGAGTGTTTCCCCCATTGATTTGAATTGATTTAGT\n']
        anRanges  = [[1, 5, 6, 10, 28, 35],
                      [9, 19, 34, 39]]
        for i in range(0, len(faFiles)):
            faFiles[i] = open(os.path.join('temp_testFiles', 'fastaOut%d.fa' % i))
            anFiles[i] = open(os.path.join('temp_testFiles', 'annotsOut%d.gff' % i))
            self.assertEqual(''.join(faFiles[i].readlines()), faOutputs[i])
            self.assertEqual(extractGffRegionsToList(anFiles[i]), anRanges[i])
            faFiles[i].close()
            anFiles[i].close()
            
        splitEvery = int(faLength / 3)
        SEI.splitFiles(faPath, anPath, splitEvery, 'temp_testFiles', 50)
        (faOut2, faOut3, anOut2, anOut3) = ('', '', '', '')
        faFiles = [faOut0, faOut1, faOut2, faOut3]
        anFiles = [anOut0, anOut1, anOut2, anOut3]
        faOutputs = ['>chr0\nAGTGTTTCCCCCATTGATTTGAATTGA\n',
                      '>chr1\nTTTAGTAGTGTTTCCCCCATTGAGTGT\n',
                      '>chr2\nTTCCCCCATTGATTTGAATTGATTTAG\n',
                      '>chr3\nT\n']
        anRanges  = [[1, 5, 6, 10],
                      [1, 8],
                      [21, 26],
                      []]
        for i in range(0, len(faFiles)):
            faFiles[i] = open(os.path.join('temp_testFiles', 'fastaOut%d.fa' % i))
            anFiles[i] = open(os.path.join('temp_testFiles', 'annotsOut%d.gff' % i))
            self.assertEqual(''.join(faFiles[i].readlines()), faOutputs[i])
            self.assertEqual(extractGffRegionsToList(anFiles[i]), anRanges[i])
            faFiles[i].close()
            anFiles[i].close()
        
if __name__ == "__main__":
    unittest.main()
