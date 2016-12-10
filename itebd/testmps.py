import numpy as np
from scipy.linalg import kron
from scipy.sparse import identity
from copy import deepcopy

from mps import MPS,ket2mps#,overlap,expect
from marker import Marker,MarkerGen,sz_in

pmarkers=[sz_in for i in range(4)]
mgen=MarkerGen(pmarkers,4,0)
markers=mgen.markers
#for marker in markers:
	#perm=marker.reorder()
	#print marker.qns,perm

#ket=np.random.rand(2**4)
ket=np.array([0.,0.,0.,1.,0.,1.,1.,0.,0.,1.,1.,0.,1.,0.,0.,0.])
mps=ket2mps(ket,2,4,cano='right',markers=markers,pmarkers=pmarkers)
mps.contract_s()

def shape():
	for M in mps.Ms:
		print M.shape

def qns():
	for M in mps.Ms:
		for marker in M.markers:
			print marker.qns

def cano():
	for M in mps.Ms[:mps.L]:                                                                                                                                                         
		print np.tensordot(M.array,M.array.conjugate().transpose(),axes=([1,2],[1,0]))-identity(M.shape[0])

def toket():
	tket=mps.toket()
	print ket-tket	

def blockize():
	mps.blockize()


if __name__=='__main__':
	#shape()
	#qns()
	#cano()
	#toket()
	blockize()
                                                                                                                                                                                           
'''
class TestMPS(object):
	def __init__(self):
		self.ket=np.random.rand(2**6)
		self.ket2=np.random.rand(2**6)
		self.mps=ket2mps(self.ket,2,6,'right',0,markers=markers)
		self.mps.contract_s()
		self.mps2=ket2mps(self.ket2,2,6,cano='right')
		self.ops=[np.random.random(size=(2,2)) for i in range(6)]

	def check_shape(self):
		for M in self.mps.Ms:
			print M.shape  

	def check_cano(self):
		if self.mps.cano=='left':
			div=self.mps.L
		elif self.mps.cano=='right':
			div=0
		else:
			div=self.mps.div
		for M in self.mps.Ms[:div]:
			print np.tensordot(M.conjugate().transpose(),M,axes=([1,2],[1,0]))-identity(M.shape[2])	
		for M in self.mps.Ms[div+1:self.mps.L]:
			print np.tensordot(M,M.conjugate().transpose(),axes=([1,2],[1,0]))-identity(M.shape[0])
		
	def test_toket(self):
		tket=self.mps.toket()
		print tket-self.ket

	def test_ovlap(self):
		ovlap=overlap(self.mps,self.mps2)
		print ovlap
		ov=self.ket.conjugate().transpose().dot(self.ket2)
		print ov
	
	def test_expect(self):
		exp=expect(self.mps,self.ops)
		OP=self.ops[0]
		for i in range(1,6):
			OP=kron(OP,self.ops[i])
		exp2=self.ket.conjugate().transpose().dot(OP.dot(self.ket))
		print exp
		print exp2
'''
