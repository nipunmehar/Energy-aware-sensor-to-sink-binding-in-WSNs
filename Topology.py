# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 00:50:47 2020

@author: ww
"""

"""Note that width is treated as X and length as Y coordinate"""
import numpy as np
from scipy.spatial.distance import cdist

class Topology:
    
    def __init__(self, num_sen, num_sink, width, length):
        self.num_sen = num_sen
        self.num_sink = num_sink
        self.width = width
        self.length = length
        
    def deploy(self):
        """create matrix with sensors' Cartesian coordinates"""
        sensors = np.zeros([self.num_sen,2]) 
        sinks = np.zeros([self.num_sink,2]) 
        for i in range(self.num_sen):
            """Randomly pick INTEGER coordinates for sensor i"""
            sensors[i,:] = [np.random.uniform(0,self.width),np.random.uniform(0,self.length)]
        for j in range(self.num_sink):
            sinks[j,:] = [np.random.uniform(0,self.width),np.random.uniform(0,self.length)]
        return sensors,sinks
    
    def calc_dist(self, sensors, sinks):
        """calculate distance between each sensor and sink"""
        dist = cdist(sensors,sinks,metric='euclidean')
        return dist
    
    def comm_cost(self, r, alpha_t, alpha_r, alpha_a, dist):
        """r - no. of bits
           alpha_t - energy/bit consumed by the transmitter
           alpha_r - energy/bit consumed by the receiver
           alpha_a - energy dissipated in the transmit op-amp
           dist - distance from sender to receiver"""
        Et = (alpha_t + alpha_a * dist**2) * r
        Er = alpha_r * r
        """Communication cost matrix of size (num_sen, num_sink)"""
        C = Et + Er
        return C
    
    def comm_load(self, C, X):
        """Communication load of all sinks, matrix of size (1, num_sink)"""
        L_sink = np.sum(np.multiply(C,X),axis=0)
        return L_sink
    
    def unreachable_nodes(self, dist, R_node, R_sink):
        count = 0
        for k in range(self.num_sen):
            if(np.min(dist[k,:]) > R_node) or (np.min(dist[k,:]) > R_sink):
                count = count + 1
        return count
    
        