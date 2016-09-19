'''
one-dimensional hamiltonian generator for dmrg
'''
import numpy as np
from scipy.sparse import kron,identity
from copy import deepcopy

class HGen(object):
	'''
	father class of LHGen and RHGen
	
	attributes:
	l:length of chain
	d:dimension of single site hilbert space
	D:dimension of total hibert space
	H:hamiltonian matrix
	pterms:terms need to be handled
	terms:hamiltonian terms
	'''
	def __init__(self,terms,d):
		self.l=1
		self.d=d
		self.D=self.d
		self.H=np.zeros([self.d,self.d])
		self.terms=terms
		self.pterms=[]

class LHGen(HGen):
	'''
	left hamiltonian generator
	construct:LHGen(terms,d)

	attributes:
	same as HGen
	'''
	def __init__(self,terms,d):
		HGen.__init__(self,terms,d)
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==1): #onsite term
				self.H=self.H+term.op1*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==1):
				pterm=deepcopy(term)
				pterm.site1=1
				pterm.site2=1+pterm.dist
				self.pterms.append(pterm)

	def enlarge(self):
		'''enlarge one site towards right'''
		self.l=self.l+1
		self.H=kron(self.H,identity(self.d))
		pts=[]
		for pterm in self.pterms:
			if pterm.site2==self.l:
				self.H=self.H+kron(pterm.op1,pterm.op2)*pterm.param
			else:
				pterm.op1=kron(pterm.op1,identity(self.d))
				pts.append(pterm)
		self.pterms=deepcopy(pts)
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==self.l):
				self.H=self.H+kron(identity(D),term.op1)*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==self.l):
				pterm=deepcopy(term)
				pterm.op1=kron(identity(self.D),pterm.op1)
				pterm.site1=self.l
				pterm.site2=self.l+pterm.dist
				self.pterms.append(pterm)
		self.D=self.D*self.d

	def truncate(self,U):
		'''truncate H and part_terms with U'''
		self.H=U.conjugate().transpose().dot(self.H.dot(U))
		for pterm in self.pterms:
			pterm.op1=U.conjugate().transpose().dot(pterm.op1.dot(U))
		self.D=self.H.shape[0] 

class RHGen(HGen):
	'''
	right hamiltonian generator
	construct:RHGen(terms,d,N)

	attributes:
	N:length of whole chain
	same as HGen 
	'''
	def __init__(self,terms,d,N): #mirror image not used
		HGen.__init__(self,terms,d)
		self.N=N
		for term in self.terms:
			if term.op1 is None and (term.site2 is None or term.site2==N):
				self.H=self.H+term.op2*term.param
			elif term.op1 is not None and (term.site2 is None or term.site2==N):
				pterm=deepcopy(term)
				pterm.site2=N
				pterm.site1=N-pterm.dist
				self.pterms.append(pterm)

	def enlarge(self):
		self.l=self.l+1
		self.H=kron(identity(self.d),self.H)
		pts=[]
		for pterm in self.pterms:
			if pterm.site1==self.N-self.l+1:
				self.H=self.H+kron(pterm.op1,pterm.op2)*pterm.param
			else:
				pterm.op2=kron(identity(self.d),pterm.op2)
				pts.append(pterm)
		self.pterms=deepcopy(pts)
		for term in self.terms:
			if term.op1 is None and (term.site2 is None or term.site2==self.N-self.l+1):
				self.H=self.H+kron(term.op2,identity(self.D))*term.param
			elif term.op1 is not None and (term.site2 is None or term.site2==self.N-self.l+1):
				pterm=deepcopy(term)
				pterm.op2=kron(pterm.op2,identity(self.D))
				pterm.site2=self.N-self.l+1
				pterm.site1=self.N-self.l+1-pterm.dist
				self.pterms.append(pterm)
		self.D=self.D*self.d
	
	def truncate(self,V):
		self.H=V.conjugate().transpose().dot(self.H.dot(V))
		for pterm in self.pterms:
			pterm.op2=V.conjugate().transpose().dot(pterm.op2.dot(V))
		self.D=self.H.shape[0]

class SuperBlock(object):
	'''
	super block hamiltonian generator

	attributes:
	lhgen:left hamiltonian generator
	rhgen:right hamiltonian generator
	H:super block hamiltonian matrix
	'''
	def __init__(self,lhgen,rhgen):
		self.lhgen=deepcopy(lhgen)
		self.rhgen=deepcopy(rhgen)
		self.L=self.lhgen.l+self.rhgen.l
		self.H=kron(self.lhgen.H,identity(self.rhgen.D))+kron(identity(self.lhgen.D),self.rhgen.H)
		for lpterm in self.lhgen.pterms:
			for rpterm in self.rhgen.pterms:
				if all(lpterm.label)==all(rpterm.label) and (lpterm.site1+self.rhgen.N-self.L,lpterm.site2+self.rhgen.N-self.L)==(rpterm.site1,rpterm.site2): 
					#this doesn't work in mirror image
					self.H=self.H+kron(lpterm.op1,rpterm.op2)*lpterm.param

class SpinTerm(object):
	'''
	two site spin-spin term
	support operators on every site and on specific sites

	attributes:
	op1/2:left and right operator 
	dist:site distance between op1 and op2
	param:interaction parameter
	site1/2:site of op1/2
	label:['op1','op2'],used to form superblock
	'''
	def __init__(self,param=1.,label=['',''],op1=None,op2=None,site1=None,site2=None,dist=1):
		self.param=param
		self.label=label
		self.op1=op1
		self.op2=op2
		self.site1=site1
		self.site2=site2
		self.dist=dist
		self.dist=dist
