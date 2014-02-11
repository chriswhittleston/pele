from __future__ import division
import numpy as np
import random
from mpi4py import MPI

class MPI_Parallel_Tempering(object):
    def __init__(self, mc_runner, Tmax, Tmin, mciter = 100):
        self.mcrunner = mc_runner
        self.comm = MPI.COMM_WORLD
        self.nproc = self.comm.Get_size() #total number of processors (replicas)
        self.rank = self.comm.Get_rank() #this is the unique identifier for the process  
        self.Tmax = Tmax
        self.Tmin = Tmin
        self.exchange_dic = {1:'right',-1:'left'}
        self.exchange_choice = random.choice(self.exchange_pattern.keys())
        self.ex_outstream = open("exchanges", "w")
        self.pt_niter = 0
        self.no_exchange_int = 1000000 #this number in exchange pattern means that no exchange should be attempted
        
    def _get_temps(self):
        """
        set up the temperatures
        distribute them exponentially
        """
        if (self.rank == 0):
            CTE = np.exp( np.log( self.Tmax / self.Tmin ) / (self.nproc-1) )
            Tarray = np.array([self.Tmin * CTE**i for i in range(self.nproc)],dtype='d')
        else:
            Tarray = None
        return Tarray
    
    def _scatter_data(self, in_send_array):
        """
        function to scatter data in equal ordered chunks among replica (it relies on the rank of the replica) 
        """
        if (self.rank == 0):
            assert(len(in_send_array) % self.nproc == 0) 
            send_array = in_send_array
        else:
            send_array = None
        
        recv_array = np.zeros(len(send_array) /self.nproc,dtype='d')
        self.comm.Scatter(send_array, recv_array, root=0) 
        return recv_array 
    
    def _scatter_single_value(self, send_array):
        """
        returns the a signel value for each replica (e.g. Temperature or swap partner)
        """
        T = self._scatter_data(send_array)
        assert(len(T) == 1)
        return T[0]
    
    def _broadcast_data(self, in_data):
        """
        identical data are broadcasted from root to all other processes
        """
        if(self.rank == 0):
            bcast_data = in_data
        else:
            bcast_data = None
        bcast_data = self.comm.Bcast(bcast_data, root=0)
        return bcast_data
    
    def _gather_data(self, in_send_array):
        """
        function to gather data in equal ordered chunks from replicas (it relies on the rank of the replica) 
        """
        if (self.rank == 0):
            recv_array = np.zeros(len(in_send_array) * self.nproc,dtype='d')
        else:
            recv_array = None
        
        self.comm.Gather(in_send_array, recv_array, root=0)
        
        if (self.rank != 0):
            assert(recv_array == None)
        
        return recv_array
    
    def _gather_energies(self, E):
        """
        gather energy configurations from all processors
        """
        send_Earray = np.array([E],dtype='d')
        recv_Earray = self._gather_data(send_Earray)
        return recv_Earray
    
    def _point_to_point_exchange_replace(self, dest, source, data):
        """
        swap data between two processors, the message sent buffer is replaced with the received message
        """
        assert(self.rank == dest or self.rank == source)
        old_data = data.copy() #this is for a test that has to be removed after initial implementation
        self.comm.Sendrecv_replace(data, dest=dest,source=source)
        assert(data != old_data) #this is a test that has to be removed after initial implementation
        return data
    
    def _find_exchange_pairs(self, Earray, Tarray):
        """
        This function determines the exchange pattern alternating swaps with right and left neighbours.
        An exchange pattern array is constructed, filled with self.no_exchange_int which
        signifies that no exchange should be attempted. This value is replaced with the
        rank of the processor with which to perform the swap is the swap attempt is successful.
        The exchange partner is then scattered to the other processors.
        """        
        if (self.rank == 0):
            assert(len(Earray)==len(Tarray))
            exchange_pattern = np.array([self.no_exchange_int for i in xrange(len(Earray))],dtype='i')
            for i in xrange(0,self.nproc,2):
                print 'exchange choice: ',self.exchange_pattern[self.exchange_choice] #this is a print statement that has to be removed after initial implementation
                E1 = Earray[i]
                T1 = Tarray[i]
                E2 = Earray[i+self.exchange_choice]
                T2 = Tarray[i+self.exchange_choice]
                deltaE = E1 - E2
                deltabeta = 1./T1 - 1./T2
                w = min( 1. , np.exp( deltaE * deltabeta ) )
                rand = np.random.rand()
                if w > rand:
                    #accept exchange
                    self.ex_outstream.write("accepting exchange %d %d %g %g %g %g %d\n" % (i, i+self.exchange_choice, E1, E2, T1, T2, self.pt_niter))
                    assert(exchange_pattern[i] == self.no_exchange_int)                      #verify that is not using the same processor twice for swaps
                    assert(exchange_pattern[i+self.exchange_choice] == self.no_exchange_int) #verify that is not using the same processor twice for swaps
                    exchange_pattern[i] = i+self.exchange_choice
                    exchange_pattern[i+self.exchange_choice] = i
            ############end of for loop###############
        else:
            exchange_pattern = None
            
        self.exchange_choice *= -1 #swap direction of exchange choice
        return exchange_pattern
        
    def _exchange_pairs(self, Earray, Tarray, data):
        """
        return data from the pair exchange
        """
        exchange_pattern = self._find_exchange_pairs(Earray, Tarray)
        exchange_buddy = self._scatter_single_value(exchange_pattern)
        if (exchange_buddy != self.no_exchange_int):
            #the replica sends to exchange_partner and receives from it (replacing source with self.rank would cause a deadlock)
            data = self._point_to_point_exchange_replace(exchange_buddy, exchange_buddy, data) 
        return data
    
        
                
            
              
                
                
                