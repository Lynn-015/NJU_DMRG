from numpy import *
from numpy.linalg import *
from scipy.misc import factorial
from utils import ind2c,c2ind
from matplotlib.pyplot import *
from itertools import combinations
import pdb
class SpaceConfig(object):
    '''Space configuration class.
    A typical hamiltonian space config consist of 4 part:

        1. Use Nambu space?
        2. How many spins?
        3. Number of sites.
            the sites in a unit cell for momentum being a good quantum number.
            the total sites for k not a good quantum number.
        4. How many orbital to be considerd.

    config:
        an len-4 array/list, the elements are:

        1. nnambu, 2 if use Nambu space else 1.
        2. nspin, number of spins.
        3. natom, number of atoms.
        4. norbit, number of orbits.
    kspace:
        True if k is a good quantum number and you decided to work in k space.
    spinless:
        infers a spinless system if True. default is False.
    '''
    def __init__(self,config,kspace=True,spinless=False):
        self.config=array(config)
        self.kspace=kspace
        self.spinless=spinless
        self.cache={}

    def __str__(self):
        return str(self.nnambu)+'(nambu) X '+str(self.nspin)+'(spin) X '+str(self.natom)+'(atom) X '+str(self.norbit)+'(orbit)'

    def __getattr__(self,name):
        if name=='nflv':
            return self.ndim/self.nnambu
        elif name=='nnambu':
            return self.config[0]
        elif name=='nspin':
            return self.config[1]
        elif name=='natom':
            return self.config[2]
        elif name=='norbit':
            return self.config[3]
        elif name=='smallnambu':
            return self.nnambu==2 and self.nspin==1 and (not self.spinless)
        elif name=='superconduct':
            return self.nnambu==2
        elif name=='nambuindexer':
            if self.cache.has_key('nambuindexer'):
                nambuindexer=self.cache['nambuindexer']
            else:
                nambuindexer=kron(arange(self.nnambu),ones(self.nflv))
                self.cache['nambuindexer']=nambuindexer
            return nambuindexer
        elif name=='atomindexer':
            if self.cache.has_key('atomindexer'):
                atomindexer=self.cache['atomindexer']
            else:
                atomindexer=kron(ones(self.nnambu*self.nspin,dtype='int32'),kron(arange(self.natom),ones(self.norbit,dtype='int32')))
                self.cache['atomindexer']=atomindexer
            return atomindexer
        elif name=='spinindexer':
            if self.cache.has_key('spinindexer'):
                spinindexer=self.cache['spinindexer']
            else:
                spinindexer=kron(ones(self.nnambu,dtype='int32'),kron(arange(self.nspin),ones(self.natom*self.norbit,dtype='int32')))
                self.cache['spinindexer']=spinindexer
            return spinindexer
        elif name=='orbitindexer':
            if self.cache.has_key('orbitindexer'):
                orbitindexer=self.cache['orbitindexer']
            else:
                orbitindexer=kron(ones(self.nnambu*self.nspin*self.natom,dtype='int32'),arange(self.norbit))
                self.cache['orbitindexer']=orbitindexer
            return orbitindexer
        else:
            super(SpaceConfig,self).__getattr__(name)


    def clearcache(self,*args):
        '''
        Clear items in cache.

        *args: 
            name of cached item.
        '''
        if len(args)==0:
            self.cache={}
            return
        for name in args:
            if self.cache.has_key(name):
                del(self.cache[name])
            else:
                print 'Warning, item %s to delete not in cache.'%name

    @property
    def ndim(self):
        '''
        The dimension of space.
        '''
        return self.config.prod()

    @property
    def hndim(self):
        '''
        The dimension of hamiltonian.
        '''
        return self.ndim

    def setnatom(self,N):
        '''
        Set atom number.

        N:
            the new atom number.
        '''
        self.config[-2]=N
        self.clearcache()

    def ind2c(self,index):
        '''
        Parse index into space len-4 config indices like (nambui,spini,atomi,orbiti).

        index:
            the index(0 ~ ndim-1).
        '''
        return ind2c(index,N=self.config)

    def c2ind(self,indices=None,nambuindex=0,spinindex=0,atomindex=0,orbitindex=0):
        '''
        Parse space config index into index.

        indices:
            a len-4 array for all the above indices.
        nambuindex/spinindex/atomindex/orbitindex:
            index for nambuspace/spinspace/atomspace/orbitspace
        '''
        if self.smallnambu:
            spinindex=0
        if indices==None:
            indices=[nambuindex,spinindex,atomindex,orbitindex]
        return c2ind(indices,N=self.config)

    def subspace2(self,nambus=None,spins=None,atoms=None,orbits=None):
        '''
        Get a matrix of mask on a subspace.

        nambus/spins/atoms/orbits:
            array as indices of nambu/spin/atom/orbit, default is all indices.
        '''
        if nambus==None:
            nambus=arange(self.nnambu)
        if spins==None:
            spins=arange(self.nspin)
        if atoms==None:
            atoms=arange(self.natom)
        if orbits==None:
            orbits=arange(self.norbit)
        if self.smallnambu:
            spins=[0]
        subspace=zeros(self.config,dtype='bool')
        subspace[ix_(nambus,spins,atoms,orbits)]=True
        subspace=subspace.ravel()
        return subspace

    def subspace(self,nambuindex=None,spinindex=None,atomindex=None,orbitindex=None):
        '''
        Get the subspace mask. the single index version of subspace2.

        nambuindex/spinindex/atomindex/orbitindex:
            nambu/spin/atomindex/orbitindex index, default is all indices.
        '''
        if self.smallnambu:
            spinindex=0
        mask=ones(self.ndim,dtype='bool')
        if nambuindex!=None:
            mask=mask & (self.nambuindexer==nambuindex)
        if spinindex!=None:
            mask=mask & (self.spinindexer==spinindex)
        if atomindex!=None:
            mask=mask & (self.atomindexer==atomindex)
        if orbitindex!=None:
            mask=mask & (self.orbitindexer==orbitindex)
        return mask

    def sigma(self,index,onlye=False):
        '''
        Pauli matrices for spin.
        It is defined in whole space by default, which makes a different in superconductng case.

        index: 
            = 1,2,3 for spin x/y/z.
        onlye:
            return a spin operator define in eletron space only if True.
        '''
        nl=1
        if not onlye:
            nl*=self.config[0]
        nr=self.config[-1]*self.config[-2]
        return kron(kron(identity(nl),s[index]),identity(nr))

    def tau(self,index):
        '''
        Pauli matrices for nambu.

        index:
            = 1,2,3 for tau_x/y/z.
        '''
        nl=1
        nr=self.nflv
        return kron(kron(identity(nl),s[index]),identity(nr))

    @property
    def I(self):
        '''
        Identity matrix.
        '''
        dim=self.hndim
        return identity(dim)

class SuperSpaceConfig(SpaceConfig):
    '''
    Space config in the occupation representation.
    Note that the dimension of space here are different from dimension of hamiltonian.
    Notice, Notice, Notice -> we arange space as |0,1,2,3 ... >, here higher number means lower power.
    e.g.
        |up=0,dn=0> -> 0
        |up=1,dn=0> -> 1
        |up=0,dn=1> -> 2
        |up=1,dn=1> -> 3

    ne_conserve:
        True(default) if electron numbers are conserved else False.
    '''
    def __init__(self,config,ne_conserve=False,*args,**kwargs):
        super(SuperSpaceConfig,self).__init__(config,kspace=False,*args,**kwargs)
        self.ne_conserve=ne_conserve
        self.cache={}
        self.ne=0
        if ne_conserve and config[0]==2:
            print 'Warning! Please Don\'t Use Nambu Space to Cope With Electron Non-conserved System. Setting ne_conserve False and Continue ...'
            self.ne_conserve=False

            #use a table to convert index to "True index - id"
            self.table=sum(2**array(list(combinations(arange(self.nsite),ne))),axis=-1)

        #binaryparser is a parser from config to index, use '&' operation to parse.
        self.binaryparser=1 << arange(self.nsite)#-1,-1,-1)


    def __str__(self):
        return super(SuperSpaceConfig,self).__str__()+(', with %s electrons.'%self.ne if self.ne_conserve else '')

    def __getattr__(self,name):
        return super(SuperSpaceConfig,self).__getattr__(name)

    @property
    def nsite(self):
        '''
        The number of sites, note that it equivalent to nflv, superconducting space is needless.
        '''
        #return prod(self.config[1:])
        res=self.ndim
        if self.nnambu==2 and (not self.smallnambu):
            res/=2
        return res

    @property
    def hndim(self):
        '''
        The dimension of hamiltonian.
        '''
        if self.cache.has_key('hndim'):
            return self.cache['hndim']
        nsite=self.nsite
        ne=self.ne
        if self.ne_conserve:
            hndim=factorial(nsite)/factorial(ne)/factorial(nsite-ne)
        else:
            hndim=pow(2,nsite)
        self.cache['hndim']=hndim
        return hndim

    def setnatom(self,natom):
        '''
        Set the number of atoms.

        natom:
            the number of atoms.
        '''
        super(SuperSpaceConfig,self).setnatom(natom)
        self.binaryparser=1 << np.arange(self.nsite) #-1,-1,-1)

    def setne(self,N):
        '''
        Set eletron number.

        N: 
            the new eletron number.
        '''
        self.ne=N
        self.table=sum(2**array(list(combinations(arange(self.nsite),N))),axis=-1)

    def ind2config(self,index):
        '''
        Parse index into eletron configuration.

        index:
            the index(0 ~ hndim-1).
        output:
            A electron configuration, which is a len-nsite array with items 0,1(state without/with electron).
        '''
        if self.ne_conserve:
            id=self.table[index]
            return self.id2config(id)
        else:
            return self.id2config(index)

    def config2ind(self,config):
        '''
        Parse eletron configuration to index.

        config:
            A electron configuration is len-nsite array with items 0,1(state without/with electron).
        output: 
            a index(0 ~ hndim-1).
        '''
        if self.ne_conserve:
            #parse config to id - the number representation
            id=self.config2id(config)
            return searchsorted(self.table,id)
        else:
            return self.config2id(config)

    def plotconfig(self,config,offset=zeros(2)):
        '''
        Display a config of electron.

        config:
            len-nsite array with items 0,1(state without/with electron).
        '''
        cfg=config.reshape(self.config)
        cfg=swapaxes(cfg,-1,-2).reshape([-1,self.natom])
        x,y=meshgrid(self.atomindexer,arange(self.nsite/self.natom))
        colors=cm.get_cmap('rainbow')(float64(cfg))
        scatter(x+offset[0],y+offset[1],s=20,c=colors.reshape([-1,4]))

    def config2id(self,config):
        '''
        Convert config to id

        config:
            an array of 0 and 1 that indicates the config of electrons.
        '''
        return sum(config*self.binaryparser,axis=-1)

    def id2config(self,id):
        '''
        Convert id to config.

        id:
            a number indicate the whole space index.
        '''
        if ndim(id)>0:
            id=id[...,newaxis]
        return (id & self.binaryparser)>0

    def indices_occ(self,occ=[],unocc=[],getreverse=False,count_e=False):
        '''
        Find the indices with specific sites occupied.

        occ:
            the sites with electron. default is no site.
        unocc:
            unoccupied sites. default is no site.
        getreverse:
            get a reversed state(with occ unoccupied and unocc occupied) at the same time.
        count_e:
            count electron numbers between two indices ind1 < site < ind2.
        output:
            a list of indices.

        return:
            [states meets requirements, final states(if get reverse), electrons between these(valid for 1,2) sites(or before this site)]
        '''
        occ=unique(occ).astype('int32')
        unocc=unique(unocc).astype('int32')
        no=len(occ)
        nn=len(unocc)
        #get remained sites
        usedsites=sort(concatenate([occ,unocc]))
        remainsites=delete(arange(self.nsite),usedsites)
        if no+nn!=self.nsite-len(remainsites):
            raise Exception('Error','Warning, no match for indices %s,%s! @indices_occ'%(occ,unocc))
            #return array([],dtype='int32')
        if count_e:
            assert(no+nn<=2)
            if no+nn<2:
                ecounter=array([],dtype='int32')
        #get possible combinations
        if self.ne_conserve:
            #assert(nn==no)
            distri=array(list(combinations(remainsites,self.ne-no)))
            if count_e and no+nn==2:
                ecounter=((usedsites[0]<distri) & (distri<usedsites[1])).sum(axis=-1)
            #turn into indices.
            ids0=(2**distri).sum(axis=-1)
            ids=ids0+(2**occ).sum()
            indices=searchsorted(self.table,ids)
            res=[indices]
            if getreverse:
                rids=ids0+(2**unocc).sum()
                res.append(searchsorted(self.table,rids))
            if count_e:
                res.append(ecounter)
            return tuple(res)
        else:
            distri=self.id2config(arange(2**(self.nsite-no-nn)))[...,:-no-nn]
            if count_e:
                if no+nn==2:
                    ecounter=distri[...,usedsites[0]:usedsites[1]-1].sum(axis=-1)
                elif no+nn==1:
                    ecounter=distri[...,:usedsites[0]].sum(axis=-1)
            parser=delete(self.binaryparser,usedsites)
            ids0=(distri*parser).sum(axis=-1)
            ids=ids0+(2**occ).sum()
            res=[ids]
            if getreverse:
                res.append(ids0+(2**unocc).sum())
            if count_e:
                res.append(ecounter)
            return tuple(res)

    def show_basis(self):
        '''
        display the whole basis.
        '''
        for i in xrange(self.hndim):
            print self.ind2config(i).astype(uint8)
