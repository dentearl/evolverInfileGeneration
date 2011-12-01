#!/usr/bin/env python
"""
trfWrapper.py, 17 February 2009
 dent earl, dearl (a) soe ucsc edu

trfWrapper.py takes all the the same arguments that
trf takes and passes them to trf. trfWrapper then checks the
return code and acts appropriately.

trf has issues with return codes and this is a simple way around
some of the issues.

the return code for trf  is the number of seqs it masked, or 255
if there was an error, [-1 is turned into an unsigned int] (if
you tried to mask 255 seqs you're out of luck. We only do one
at a time, so we expect a retcode of 1.)

"""
########################################
import glob
import os
import subprocess 
import sys

def usage():
    print "USAGE: %s [trf options]" %(sys.argv[0])
    print __doc__
    sys.exit(2)

def verifyPrograms(programs, verbose = False):
    """verifyPrograms(programs) takes a list of executable names, and acts on the list object
    to look up the full path to the executables, or if they are not found it raises an exeption
    """
    from libSimControl import which
    if not isinstance(programs, list):
       raise TypeError('verifyPrograms takes a list of program '
                       'names, not %s.' % programs.__class__)
    for i, prog in enumerate(programs, 0):
       if not isinstance(prog, str):
          raise TypeError('verifyPrograms list members should all be strings, '
                          '"%s" not a string, is a %s.' %(str(prog), prog.__class__))
       p = which(prog)
       if p is None:
           raise RuntimeError('verifyPrograms(): Could not locate "%s" '
                              'in PATH.' % prog)
       else:
           if verbose:
               print '   located executable %s %s OK' % (p, (90 - len(p)) * '.')
           if prog.endswith('.py') or prog.endswith('.pl') or prog.endswith('.sh'):
               verifyUnixLineEndings(prog, verbose = verbose)
           programs[i] = p

def verifyUnixLineEndings(prog, verbose = False):
    """ verifyUnixLineEndngs takes a program (no path) and checks the line endings to
    verify that they are unix (LF). If they are not, it raises a RuntimeError.
    """
    from libSimControl import which
    if not isinstance(prog, str):
        raise TypeError('verifyUnixLineEndings takes a string, not %s.' % prog.__class__)
    p = which(prog)
    if p is None:
        raise RuntimeError('verifyUnixLineEndings(): '
                           'Could not locate "%s" in PATH' % prog)
    else:
        dat = open(p, 'rb').read()
        if '\0' in dat:
            # binary
            return
        newDat = dat.replace("\r\n", "\n") # replace CRLF with LF
        if newDat != dat:
            raise RuntimeError('verifyUnixLineEndings(): %s '
                               'contains CRLF line endings.' % p)
        else:
            if verbose:
                print '   unix line endings %s %s OK' % (p, (90 - len(p)) * '.')

def main(argv):
    programs = ['trf']
    verifyPrograms(programs)
    TRF_BIN = programs[0]
    cmd = [TRF_BIN]
    cmd.extend(argv[1:])
    localDir = os.path.dirname(argv[1])
    p = subprocess.Popen(cmd, cwd = localDir)
    p.wait()
    if p.returncode != 1:
        if p.returncode < 0:
            sys.stderr.write('%s: Experienced an error while trying to '
                             'execute: %s SIGNAL:%d\n' %(sys.argv[0], ' '.join(cmd), -(p.returncode)))
        else:
            sys.stderr.write('%s: Experienced an error while trying to '
                             'execute: %s retcode:%d\n' %(sys.argv[0], ' '.join(cmd), p.returncode))
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
