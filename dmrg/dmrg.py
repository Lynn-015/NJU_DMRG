'''
dmrg engine
'''
import numpy as np
from copy import copy,deepcopy

from superblock import SuperBlock
from mps import MPS

class DMRGEngine(object):
	'''
	dmrg engine
	construct:DMRGEngine(lhgen,rhgen)
	
	attributes:
	lhgen:left hamiltonian generator
	rhgen:right hamiltonian generator
	N:length of whole chain
	lblocks:a list to store left generators
	rblocks:a list to store right generators
	sblock:super block	
	'''
	def __init__(self,lhgen,rhgen):
		self.lhgen=lhgen
		self.rhgen=rhgen
		self.L=self.rhgen.L
		self.lblocks=[deepcopy(self.lhgen)]
		self.rblocks=[deepcopy(self.rhgen)]
		self.d=self.lhgen.d
	
	def single_step(self,m): #only for infinite
		'''single dmrg step.m:number of kept states'''
		self.lhgen.enlarge()
		self.rhgen.enlarge()
		self.sblock=SuperBlock(self.lhgen,self.rhgen,joint=True)
		E,psi=self.sblock.eigen()
		print '*'*(self.lhgen.l-1)+'++'+'*'*(self.rhgen.l-1)
		print 'E=',float(E)/self.sblock.L

		U=self.sblock.transmat(m);self.lhgen.U=U
		self.lhgen.transform(U)
		V=self.sblock.rtransmat(m);self.rhgen.V=V
		self.rhgen.transform(V)
		self.lhgen.basis_sector_array=self.sblock.new_sector_array
		self.lhgen.basis_by_sector=self.sblock.new_basis_by_sector
		self.rhgen.basis_sector_array=self.sblock.rnew_sector_array
		self.rhgen.basis_by_sector=self.sblock.rnew_basis_by_sector

		self.lblocks.append(deepcopy(self.lhgen))
		self.rblocks.append(deepcopy(self.rhgen))

	def infinite(self,m):
		'''infinite algorithm'''
		for i in range(self.L/2-1):
			self.single_step(m)
	
	def right_sweep(self,m):
		'''sweep one site towards right'''
		self.rblocks.pop(-1)
		psi0_guess=np.reshape(self.sblock.full_psi0,(self.lblocks[-2].D*self.d,-1))
		psi0_guess=self.lblocks[-1].U.conjugate().transpose().todense().dot(psi0_guess)
		psi0_guess=psi0_guess.reshape(-1,self.rblocks[-1].D)
		psi0_guess=psi0_guess.dot(self.rblocks[-1].V.conjugate().transpose().todense())
		psi0_guess=psi0_guess.reshape(-1,1)
		self.rblocks.pop(-1)
		self.lhgen=deepcopy(self.lblocks[-1])
		self.rhgen=deepcopy(self.rblocks[-1])
		self.lhgen.enlarge();self.rhgen.enlarge()
		self.sblock=SuperBlock(self.lhgen,self.rhgen)
		E,psi=self.sblock.eigen(psi0_guess)
		print '-'*(self.lblocks[-1].l)+'++'+'='*(self.rblocks[-1].l)
		print 'E=',float(E)/self.L
		
		U=self.sblock.transmat(m);self.lhgen.U=U
		V=self.sblock.rtransmat(m);self.rhgen.V=V
		self.lhgen.transform(U)
		self.rhgen.transform(V)
		self.lhgen.basis_sector_array=self.sblock.new_sector_array
		self.lhgen.basis_by_sector=self.sblock.new_basis_by_sector
		self.rhgen.basis_sector_array=self.sblock.rnew_sector_array
		self.rhgen.basis_by_sector=self.sblock.rnew_basis_by_sector
		self.lblocks.append(deepcopy(self.lhgen))
		self.rblocks.append(deepcopy(self.rhgen))

	def left_sweep(self,m):
		'''sweep one site towards left'''
		self.lblocks.pop(-1)
		psi0_guess=np.reshape(self.sblock.full_psi0,(-1,self.rblocks[-2].D*self.d))
		psi0_guess=psi0_guess.dot(self.rblocks[-1].V.todense())
		psi0_guess=psi0_guess.reshape(self.lblocks[-1].D,-1)
		psi0_guess=self.lblocks[-1].U.todense().dot(psi0_guess)
		psi0_guess=psi0_guess.reshape(-1,1)
		self.lblocks.pop(-1)
		self.lhgen=deepcopy(self.lblocks[-1])
		self.rhgen=deepcopy(self.rblocks[-1])
		self.lhgen.enlarge()
		self.rhgen.enlarge()
		self.sblock=SuperBlock(self.lhgen,self.rhgen)
		E,psi=self.sblock.eigen(psi0_guess)
		print '='*(self.lblocks[-1].l)+'++'+'-'*(self.rblocks[-1].l)
		print 'E=',float(E)/self.L
		
		U=self.sblock.transmat(m);self.lhgen.U=U
		V=self.sblock.rtransmat(m);self.rhgen.V=V	
		self.lhgen.transform(U)
		self.rhgen.transform(V)
		self.lhgen.basis_sector_array=self.sblock.new_sector_array
		self.lhgen.basis_by_sector=self.sblock.new_basis_by_sector
		self.rhgen.basis_sector_array=self.sblock.rnew_sector_array
		self.rhgen.basis_by_sector=self.sblock.rnew_basis_by_sector
		self.lblocks.append(deepcopy(self.lhgen))
		self.rblocks.append(deepcopy(self.rhgen))

	def finite(self,mwarmup,mlist):
		'''finite algorithm'''
		self.infinite(mwarmup) #mind the initialize problem
		for m in mlist:
			for i in range(self.L/2,self.L-2):
				self.right_sweep(m)
			for i in range(1,self.L-3):
				self.left_sweep(m)
			for i in range(1,self.L/2-1):
				self.right_sweep(m)
		
	def tomps(self):
		As=[np.array([[1.,0],[0,1.]])]
		As[0]=As[0].reshape(-1,2,As[0].shape[-1])
		Bs=[np.array([[1.,0],[0,1.]])]
		Bs[0]=Bs[0].reshape(Bs[0].shape[0],2,-1)
		for lhgen in self.lblocks[1:]:
			A=copy(lhgen.U)	
			A=A.toarray()
			A=A.reshape(-1,2,A.shape[-1])
			As.append(A)
		for rhgen in self.rblocks[1:]:
			B=copy(rhgen.V)
			B=B.toarray()
			B=B.conjugate().transpose()
			B=B.reshape(B.shape[0],2,-1)
			Bs.append(B)
		Bs.reverse()
		S=self.sblock.s
		
		return MPS(self.d,self.L,As,Bs,S)















