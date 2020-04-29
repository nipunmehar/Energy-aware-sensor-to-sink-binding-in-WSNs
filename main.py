# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 21:20:45 2020

@author: ww
"""
import numpy as np
import gurobipy as gp
import Topology, Point, EnergyOptimizer
from scipy.spatial import distance



if __name__ == '__main__':
    
    params= [(15,3)]
    for param in params:
        iter = 0
        while iter < 1:
            num_nodes = param[0]
            num_sinks = param[1]
            num_nodes_per_sink_avg = num_nodes/num_sinks
            width = 200
            length = 200
        
            r = 8000
            alpha_t = 50*10**(-6)
            alpha_r = 50*10**(-6)
            alpha_a = 10*10**(-9)
            R_sink, R_node = 100, 50
            alphas = [3]
    
            t1 = Topology.Topology(num_nodes, num_sinks, width, length)
            sensors, sinks = t1.deploy()
            dist1 = t1.calc_dist(sensors, sinks)    #sensor-sink distance
            dist2 = t1.calc_dist(sensors, sensors)  #sensor-sensor distance
            
            empty_nodes = t1.unreachable_nodes(dist1, R_node, R_sink)
                        
            #dist1 = np.reshape(dist1, (num_nodes*num_sinks)) # reshape it for convenient computations during optimization
            C = t1.comm_cost(r, alpha_t, alpha_r, alpha_a, dist1)
            C = np.reshape(C, (num_nodes*num_sinks))
            
            """Multi-hop code START"""
            
            lvl_num = 1
            levels = [[sinks]] #sinks are level 0
            row_num = [list(range(num_sinks))]
            lines = []
            num_sen = num_nodes
            
            while num_sen > 0:
                sack = []
                arr = []
                if lvl_num == 1:
                    """level 1 sensors"""
                    d = R_sink
                    dist = dist1
                    for ii in range(len(dist[:,0])):
                        temp = np.min(dist[ii,:])
                        col_num = np.where(dist[ii,:]==temp)
                        if temp <= d and temp <= R_node:  
                            sack.append(sensors[ii,:])
                            arr.append(ii) 
                            lines.append([ii,col_num])
                    num_sen -= len(arr)        
                    levels.append(sack)
                    row_num.append(arr) #keep track of sensor numbers
                    lvl_num += 1
                else:
                    """level 2,3,4... sensors"""
                    d = R_node
                    dist = dist2
                    for ii in range(len(dist[:,0])):
                        flag = False
                        #Check if the sensor is not in the levels above
                        for kk in range(1,len(row_num)):
                            if row_num[kk].__contains__(ii):
                                flag = True
                        if flag:
                            continue
                        sens_dist = []
                        for jj in range(len(dist[0,:])):  
                            euc_dist = distance.euclidean(sensors[ii],sensors[jj])
                            if row_num[lvl_num-1].__contains__(jj) and euc_dist <= d:
                                sens_dist.append(euc_dist)
                        try:
                            jj = np.where(dist[0,:]==np.min(sens_dist))        
                            sack.append(sensors[ii,:])
                            arr.append(ii)
                            lines.append([ii,jj])
                        except:
                            print("No sensor found in row " + str(ii))     
                    if len(sack) > 0:
                        num_sen -= len(arr)
                        levels.append(sack)
                        row_num.append(arr)
                        lvl_num += 1
                    else:
                        break
            p = Point.Point(sensors, sinks, R_sink)
            p.plot_points()
                    
            """Multi-hop code END"""
            
            x_iter = []
            for k in range(len(row_num)-1):
                
                num_sinks = len(row_num[k])
                num_nodes = len(row_num[k+1])
                num_nodes_per_sink_avg = num_nodes/num_sinks
                dist_temp = np.zeros((len(row_num[k+1]),len(row_num[k])))
                
                for kk in range(len(row_num[k+1])):   #iterate over sensors
                    for jj in range(len(row_num[k])): #iterate over sinks
                        if k == 0:
                            dist_temp[kk,jj] = dist1[row_num[k+1][kk],row_num[k][jj]]
                        else:
                            dist_temp[kk,jj] = dist2[row_num[k+1][kk],row_num[k][jj]]

                dist_temp = np.reshape(dist_temp, (num_nodes*num_sinks))
                C = t1.comm_cost(r, alpha_t, alpha_r, alpha_a, dist_temp)
                C = np.reshape(C, (num_nodes*num_sinks)) 
                e1 = EnergyOptimizer.EnergyOptimizer('Binary', num_nodes, num_sinks)
                m = e1.optimize(C, dist_temp, alphas, R_node=100, R_sink=100)
                
                x_iter.append(m.X)
                
            iter = iter + 1 
            if m.status == gp.GRB.OPTIMAL:
                print("\nX (length of " + str(len(x_iter)) + ") for each iteration in the list form: \n")
                print(x_iter)
                print("\nNumber of levels obtained (except for level 0, i.e. true sinks): " + str(len(levels)-1))
                print("\nNumber of unreachable nodes in single-hop case: " + str(empty_nodes))
                print("Number of unreachable nodes in multi-hop case: " + str(num_sen))
                p.connect_dots(row_num, x_iter, levels)
                