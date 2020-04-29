# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 00:51:17 2020

@author: ww
"""

"""Plots the sensors and sinks in Cartesian coordinate plane"""

import matplotlib.pyplot as plt  
import numpy as np 
   
class Point:
    
    def __init__(self, sensors, sinks, radius):
        self.sensors = sensors
        self.sinks = sinks
        self.radius = radius
    
    def plot_points(self):
        x1 = self.sensors[:,0]
        y1 = self.sensors[:,1]
        x2 = self.sinks[:,0]
        y2 = self.sinks[:,1]
        """BLUE are sensors, RED are sinks"""
        plt.scatter(x1,y1, c='b', marker='.', label='1')
        plt.scatter(x2,y2, c='r', marker='s', label='-1')
        ax=plt.gca()
        for i in range(len(self.sinks[:,0])):
            circle1=plt.Circle((self.sinks[i,:][0],self.sinks[i,:][1]),self.radius,color='r',fill=False)
            ax.add_patch(circle1)
        plt.axis('scaled')
        #plt.show()  
        plt.savefig('1.png', format = 'png', dpi=1200)
              
    def connect_dots(self, row_num, x_iter, levels):
        x1 = self.sensors[:,0]
        y1 = self.sensors[:,1]
        x2 = self.sinks[:,0]
        y2 = self.sinks[:,1]
        """BLUE are sensors, RED are sinks"""
        plt.scatter(x1,y1, c='b', marker='.', label='1')
        plt.scatter(x2,y2, c='r', marker='s', label='-1')
        ax=plt.gca()
        for i in range(len(self.sinks[:,0])):
            circle1=plt.Circle((self.sinks[i,:][0],self.sinks[i,:][1]),self.radius,color='r',fill=False)
            ax.add_patch(circle1)
        plt.axis('scaled')      
        #Add lines
        for i in range(1,len(levels)):
            count = 0
            index = np.zeros(int(len(row_num[i])))
            #print("\n\n\nHELLO! i = " + str(i))
            for k in range(0,len(x_iter[i-1]),len(row_num[i-1])):
                index[count] = x_iter[i-1][k:(k+len(row_num[i-1]))].index(1)
                count += 1
            for j in range(len(row_num[i])):
                #print("\n\n\nHELLO! j = " + str(j))
                if i == 1:
                    temp = int(index[j].item())
                    x2 = levels[i-1][0][temp][0].item()
                    y2 = levels[i-1][0][temp][1].item()
                else:
                    temp = int(index[j].item())
                    x2 = levels[i-1][temp][0].item()
                    y2 = levels[i-1][temp][1].item()
                xcor = [levels[i][j][0].item(), x2]
                ycor = [levels[i][j][1].item(), y2]
                plt.gcf().gca().plot(xcor,ycor,'--',color='g')              
        #plt.show()
        plt.savefig('2.png', format = 'png', dpi=1200)