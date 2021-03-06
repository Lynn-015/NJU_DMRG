import numpy as np
from scipy.sparse import identity,kron
from scipy.sparse.linalg import eigsh
from copy import deepcopy

t=-0.1

Cp=np.array([[0,1],[0,0]]) #cant represent boson
Cm=np.array([[0,0],[1,0]])
Z=np.array([[-1,0],[0,1]])

Zs=np.array([[1,0,0,0],[0,-1,0,0],[0,0,-1,0],[0,0,0,1]])
Cp_up=np.array([[0,0,1,0],[0,0,0,1],[0,0,0,0],[0,0,0,0]])
Cm_up=np.array([[0,0,0,0],[0,0,0,0],[1,0,0,0],[0,1,0,0]])
Cp_dn=np.array([[0,-1,0,0],[0,0,0,0],[0,0,0,1],[0,0,0,0]])
Cm_dn=np.array([[0,0,0,0],[-1,0,0,0],[0,0,0,0],[0,0,1,0]])

def fermion(L):
	H=np.zeros((2,2))
	cp=Cp.dot(Z)
	cm=Cm.dot(Z)
	z=deepcopy(Z)
	d=2
	for i in range(L-1):
		H=kron(H,identity(2))+t*kron(identity(d/2),np.dot(kron(Cp,identity(2)),kron(Z,Cm)))-t*kron(identity(d/2),np.dot(kron(Cm,identity(2)),kron(Z,Cp)))
		#H=kron(H,identity(2))+t*kron(cp,Cm)+t*kron(Cp,cm)
		cp=kron(identity(d),Cp.dot(Z))
		cm=kron(identity(d),Cm.dot(Z))
		z=kron(identity(d),Z)
		d*=2
	E0,psi0=eigsh(H,k=1,which='SA')
	print E0/L	
	print H.dot(psi0)-E0*psi0
	print (H.conjugate().transpose()-H).todense()
	
def sfermion(L):
	H=np.zeros((4,4))
	d=1
	for i in range(L-1):
		H=kron(H,identity(4))+t*kron(kron(identity(d),Cp_up.dot(Zs)),Cm_up)-t*kron(kron(identity(d),Cm_up.dot(Zs)),Cp_up)+t*kron(kron(identity(d),Cp_dn.dot(Zs)),Cm_dn)-t*kron(kron(identity(d),Cm_dn.dot(Zs)),Cp_dn)
		d*=4
	E0,psi0=eigsh(H,k=1,which='SA')
	print E0/L		

def expect():
	pass

if __name__=="__main__":
	#fermion(10)
	sfermion(10)
