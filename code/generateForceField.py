#!/usr/bin/python
import sys
import numpy as np
import basUtils
import elements
import GridUtils     as GU
import ProbeParticle as PP;    PPU = PP.PPU;
import libFFTfin     as LFF
from optparse import OptionParser

parser = OptionParser()
parser.add_option( "-i", "--input", action="store", type="string", help="format of input file", default='vasp.locpot.xsf')
(options, args) = parser.parse_args()

num = len(sys.argv)
if (num < 2):
    sys.exit("Number of arguments = "+str(num-1)+". This script should have at least one argument. I am terminating...")
finput = sys.argv[num-1]

# --- initialization ---

sigma  = 1.0 # [ Angstroem ] 

print " ========= get electrostatic force field from hartree "

# TODO with time implement reading a hartree potential generated by different software
print " loading Hartree potential from disk "
if(options.input == 'vasp.locpot.xsf'):
    V, lvec, nDim, head = GU.loadXSF(finput)
elif(options.input == 'aims.cube'):
    V, lvec, nDim, head = GU.loadCUBE(finput)

print " computing convolution with tip by FFT "
Fel_x,Fel_y,Fel_z = LFF. potential2forces( V, lvec, nDim, sigma = sigma )

print " saving electrostatic force field "
GU.saveXSF('FFel_x.xsf', Fel_x, lvec, head)
GU.saveXSF('FFel_y.xsf', Fel_y, lvec, head)
GU.saveXSF('FFel_z.xsf', Fel_z, lvec, head)

del Fel_x,Fel_y,Fel_z,V


print " ========= get Lenard-Jones force field "

PPU.params['gridA'] = lvec[ 1,:  ].copy()
PPU.params['gridB'] = lvec[ 2,:  ].copy()
PPU.params['gridC'] = lvec[ 3,:  ].copy()
PPU.params['gridN'] = nDim.copy()

atoms     = basUtils.loadAtoms('input.xyz', elements.ELEMENT_DICT )
iZs,Rs,Qs = PP.parseAtoms( atoms, autogeom = False, PBC = True )
FFLJ      = PP.computeLJ( Rs, iZs, FFLJ=None, FFparams=None)

print " trimming Lenard-Jones force field"
GU.limit_vec_field( FFLJ, Fmax=100.0 ) # remove too large values; keeps the same direction; good for visualization 

print " saving Lenard-Jones force field"
GU.saveVecFieldXsf( 'FFLJ', FFLJ, lvec, head)

