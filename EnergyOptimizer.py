# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 00:51:24 2020

@author: ww
"""

"""Note: ALL CALCULATIONS are performed according to SI Units"""
import numpy as np
import gurobipy as gp


class EnergyOptimizer:

    '''
    Optimizer class which implements optimization.
    
    '''
    def __init__(self, variable_type = 'Binary', 
                       num_nodes=100, 
                       num_sinks=5):
        if variable_type == 'Binary':
            self.vtype = gp.GRB.BINARY
        else:
            self.vtype = gp.GRB.CONTINUOUS
        self.lb = 0.0
        self.ub = 1.0
        self.num_nodes = num_nodes
        self.num_sinks = num_sinks
        
    def create_M_matrix(self):
        '''
        This method created the M matrix
        needed for the first constraint
        Size: (n, m*n)

        Input: 
        - self, the instance itself, but num_nodes and num_sinks are used
        Return: 
        - M matrix of size (n, m*n)
        '''
        M = np.zeros((self.num_nodes, self.num_nodes*self.num_sinks))
        for ii in range(self.num_nodes):
            M[ii, ii*self.num_sinks:ii*self.num_sinks+self.num_sinks] = 1
        return M
    
    def optimize(self, C, dist, alphas, R_node=100, R_sink=100):
        '''
        This method solves the quadratic optimization problem
        using Gurobi tool's Python Interface.
        
        Input:
        - self - use num_nodes and num_sinks attributes of the instance
        - C - node-to-sink communication cost matrix of shape (m*n,)
        - dist - node-to-sink distance, size (m*n,)
        - num_nodes_per_sink_avg - average number of nodes per sink (num_nodes/num_sinks)
        - alphas - thresold for a second constraint, also hyperparameter to tune,
        supplied as a list of possible values of alpha, e.g. [3,5,7,9]
        - R_node, R_sink - maximum distances between nodes and sinks, default 100

        Return:
        -
        '''
        num_nodes_per_sink_avg = self.num_nodes/self.num_sinks
        try:
            for alpha in alphas:
                # model declaration, name: BinaryWSN
                m = gp.Model("BinaryWSN")

                # variable declaration, size (n*m,)
                X = []
                for jj in range(self.num_nodes*self.num_sinks):
                    X.append(m.addVar(lb=self.lb, ub=self.ub, vtype=self.vtype))
                
                # defining the objective function
                L_sinks = [0]*self.num_sinks
                obj =  gp.QuadExpr()
                for jj in range(self.num_sinks):
                    for ii in range(self.num_nodes):
                        L_sinks[jj] = C[self.num_nodes*jj + ii]*X[self.num_nodes*jj + ii]

                L_avg = sum(L_sinks)*(1/self.num_sinks)

                for jj in range(self.num_sinks):
                    obj += (L_sinks[jj] - L_avg)*(L_sinks[jj] - L_avg)
                obj = (1/self.num_sinks)*obj
                m.setObjective(obj, gp.GRB.MINIMIZE) # minimization problem

                # create M matrix of size (n, n*m)
                M = self.create_M_matrix()

                # first constraint: ensuring Mx = 1
                Mx = [0]*self.num_nodes
                for ii in range(self.num_nodes):
                    for jj in range(self.num_nodes*self.num_sinks):
                        Mx[ii] += M[ii,jj]*X[jj]
                m.addConstrs(Mx[ii] == 1 for ii in range(self.num_nodes))

                # addding other constraint: ensure |nj - n_avg| < alpha, where j is a jth sink
                n_nodes_per_sink = [0]*self.num_sinks
                for jj in range(self.num_sinks):
                    for ii in range(self.num_nodes):
                        n_nodes_per_sink[jj] += X[self.num_nodes*jj + ii]

                # |abs| < alpha we define as abs < alpha and abs > - alpha
                m.addConstrs((n_nodes_per_sink[jj] - num_nodes_per_sink_avg <= alpha for jj in range(self.num_sinks)))
                m.addConstrs((n_nodes_per_sink[jj] - num_nodes_per_sink_avg >= -alpha for jj in range(self.num_sinks)))

                # last two constraints: ensure both node and sink are within the required distance
                m.addConstrs(dist[ii]*X[ii] <= R_sink for ii in range(self.num_nodes*self.num_sinks))
                m.addConstrs(dist[ii]*X[ii] <= R_node for ii in range(self.num_nodes*self.num_sinks))

                # update the model on pending changes
                m.update()

                # optimize model: solve the problem
                m.optimize()

        except gp.GurobiError as e:
            print('Error code ' + str(e.errno) + ": " + str(e))
        
        except AttributeError:
            print('Encountered an attribute error')

        return m