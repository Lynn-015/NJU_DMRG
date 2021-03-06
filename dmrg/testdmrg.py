from __future__ import division

import numpy as np
from copy import copy,deepcopy

from hgen import HGen
from dmrg import DMRGEngine
from ops import Op,Term,FTerm,SFTerm,oplib

J=1.
t=-0.1
U=1.
sterms=[Term([oplib['s+'],oplib['s-']],param=J/2,label='S+*S-'),Term([oplib['s-'],oplib['s+']],param=J/2,label='S-*S+'),Term([oplib['sz'],oplib['sz']],param=J,label='Sz*Sz')]
lhgen=HGen(sterms,10,part='left')
rhgen=HGen(sterms,10,part='right')

fterms=[FTerm([oplib['c+'],oplib['c']],param=t,label='C+*C'),FTerm([oplib['c'],oplib['c+']],param=-t,label='C*C+')]
flhgen=HGen(fterms,10,part='left',fermi=True)
frhgen=HGen(fterms,10,part='right',fermi=True)

fsterms=[SFTerm([oplib['Cup+'],oplib['Cup']],param=t,label='Cup+*Cup'),SFTerm([oplib['Cup'],oplib['Cup+']],param=-t,label='Cup*Cup+'),SFTerm([oplib['Cdn+'],oplib['Cdn']],param=t,label='Cdn+*Cdn'),SFTerm([oplib['Cdn'],oplib['Cdn+']],param=-t,label='Cdn*Cdn+')]
fslhgen=HGen(fsterms,10,d=4,part='left',sfermi=True,sectors=np.array([1.,0.,0.,-1.]))
fsrhgen=HGen(fsterms,10,d=4,part='right',sfermi=True,sectors=np.array([1.,0.,0.,-1.]))

def test_ispin():
	dmrg=DMRGEngine(lhgen,rhgen)
	dmrg.infinite(m=20)

def test_fspin():
	dmrg=DMRGEngine(lhgen,rhgen)
	dmrg.finite(mwarmup=10,mlist=[10,20,30,40,40])
	
def test_ifermi():
	dmrg=DMRGEngine(flhgen,frhgen)
	dmrg.infinite(m=40)

def test_ffermi():	
	dmrg=DMRGEngine(flhgen,frhgen)	
	dmrg.finite(mwarmup=10,mlist=[10,20,30,40,40])

def test_isfermi():
	dmrg=DMRGEngine(fslhgen,fsrhgen)
	dmrg.infinite(m=40)
	
def test_fsfermi():
	dmrg=DMRGEngine(fslhgen,fsrhgen)	
	dmrg.finite(mwarmup=10,mlist=[10,20,30,40,40])

if __name__=='__main__':
	#test_ispin()
	#test_fspin()
	#test_ifermi()
	#test_ffermi()
	#test_isfermi()
	test_fsfermi()
