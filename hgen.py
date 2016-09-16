'''
one-dimensional hamiltonian generator used for nrg and dmrg
may be wrong orz...
'''
import numpy as np
from scipy.sparse import kron,identity
from copy import deepcopy

class NRGHGen(object):
	'''
	one dimensional hamiltonian generator for nrg,without considering fermion sign problem 
	
	attributes:
	l:length of chain
	d:dimension of single site hilbert space
	D:dimension of total hilbert space
	H:hamiltonian matrix
	part_terms:terms need to be handled
	terms:all terms	
	'''
	def __init__(self,terms):
		self.l=1
		self.d=terms[0].op1.shape[0]
		self.D=self.d
		self.H=np.zeros([self.d,self.d])
		self.part_terms=[]
		self.terms=terms
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==1):
				self.H=self.H+term.op1*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==1):
				pterm=deepcopy(term)
				pterm.site1=1
				pterm.site2=1+pterm.dist
				self.part_terms.append(pterm)	
		
	def enlarge(self):
		self.l=self.l+1	
		self.H=kron(self.H,identity(self.d))
		pts=[]
		for pterm in self.part_terms:
			if pterm.site2==self.l:
				self.H=self.H+kron(pterm.op1,pterm.op2)*pterm.param
			else:
				pterm.op1=kron(pterm.op1,identity(self.d))
				pts.append(pterm)
		self.part_terms=deepcopy(pts)
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==self.l):
				self.H=self.H+kron(identity(D),term.op1)*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==self.l):
				pterm=deepcopy(term)
				pterm.op1=kron(identity(self.D),pterm.op1)
				pterm.site1=self.l
				pterm.site2=self.l+pterm.dist
				self.part_terms.append(pterm)
		self.D=self.D*self.d
		
	def truncate(self,U):
		self.H=U.conjugate().transpose().dot(self.H.dot(U))
		for pterm in self.part_terms:
			pterm.op1=U.conjugate().transpose().dot(pterm.op1.dot(U))
		self.D=self.H.shape[0]

class LHGen(object):
	'''
	left dmrg hamiltonian generator,basically same as NRGHGen
	'''
	def __init__(self,terms):
		self.l=1
		self.d=terms[0].op1.shape[0]
		self.D=self.d
		self.H=np.zeros([self.d,self.d])
		self.part_terms=[]
		self.terms=terms
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==1):
				self.H=self.H+term.op1*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==1):
				pterm=deepcopy(term)
				pterm.site1=1
				pterm.site2=1+pterm.dist
				self.part_terms.append(pterm)

	def enlarge(self):
		self.l=self.l+1
		self.H=kron(self.H,identity(self.d))
		pts=[]
		for pterm in self.part_terms:
			if pterm.site2==self.l:
				self.H=self.H+kron(pterm.op1,pterm.op2)*pterm.param
			else:
				pterm.op1=kron(pterm.op1,identity(self.d))
				pts.append(pterm)
		self.part_terms=deepcopy(pts)
		for term in self.terms:
			if term.op2 is None and (term.site1 is None or term.site1==self.l):
				self.H=self.H+kron(identity(D),term.op1)*term.param
			elif term.op2 is not None and (term.site1 is None or term.site1==self.l):
				pterm=deepcopy(term)
				pterm.op1=kron(identity(self.D),pterm.op1)
				pterm.site1=self.l
				pterm.site2=self.l+pterm.dist
				self.part_terms.append(pterm)
		self.D=self.D*self.d

	def truncate(self,U):
		self.H=U.conjugate().transpose().dot(self.H.dot(U))
		for pterm in self.part_terms:
			pterm.op1=U.conjugate().transpose().dot(pterm.op1.dot(U))
		self.D=self.H.shape[0] 

class RHGen(object):
	def __init__(self,terms,N): #only used in finite algorithm.in infinite algorithm,rhgen is just a copy of lhgeni
		pass

class SuperBlock(object):
	def __init__(self,lhgen,rhgen):
		self.lpterms=deepcopy(lhgen.part_terms)
		self.rpterms=deepcopy(rhgen.part_terms)
		self.H=kron(lhgen.H,identity(rhgen.D))+kron(identity(lhgen.D),rhgen.H)
		for lpterm in self.lpterms:
			for rpterm in self.rpterms:
				if lpterm.label[0]==rpterm.label[1] and lpterm.label[1]==rpterm.label[0] and \
					lpterm.site1==rpterm.site1 and lpterm.site2==rpterm.site2: #for infinite algorithm,this works only in special condition!
					self.H=self.H+kron(lpterm.op1,rpterm.op1)*lpterm.param

class Term(object):
	'''
	a class to store hamiltonian terms.just support simple one and two site operator at now
	besides,it support operators on every site and on specific sites
	for now,site1 is the current site,site2 is next site

	attributes:
	op1/2:operator on site1/2 
	dist:site distance between op1 and op2
	param:interaction parameter
	site1/2:site of op1/2
	'''
	def __init__(self,op1=None,op2=None,site1=None,site2=None,dist=None,param=1.,label=''):
		self.op1=op1
		self.op2=op2 #if op2==None,it's an onsite term
		self.dist=dist
		self.param=param
		self.site1=site1 #if site1 and site2 are all None,it means that this term is on every site
		self.site2=site2
		self.label=label
