import os
import sys

import ttk 
import Tkinter as tk
from pylab import *
import numpy as np

sys.path.append('/Users/mender/HIPPNET/hippnet')
import helper 

mysql_database = "Palamanui"
mysql_table    = "PN_resurvey_2010_v01"

# ~~~~ read HIPPNET TSV file into pandas ~~~~~~~
datatype, hippnet_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )

#hippnet_data.rename(columns = lambda x:x.lower(), inplace=True )
names  = list(hippnet_data)
hippnet_num_rows   = len( hippnet_data )

names = np.insert( names, 0, '*MISSING*' )

# GLOBALS
gx = 0
gy = 0
col_matches = []

class ColumnSelect:
    def __init__(self, master):
        columnFrame = tk.Frame( master)
        columnFrame.pack_propagate(0)
        columnFrame.pack(fill=tk.BOTH)
#######################
# LOAD CTFS INFO PAGE #
#######################
        data = np.loadtxt( 
              '/Users/mender/HIPPNET/hippnet/CTFS_tree_column_info.txt', 
              dtype=str,
              delimiter='\t',
              comments='skjdfsakdhfashdfjkhsajdhfkasdfsa' )
        ctfs_names = data[:,0]
        self.col_descr = data[:,1]

        tk.Label( master=columnFrame, text='CTFS column', font='BOLD', relief=tk.RIDGE, width=15).grid( row=0, column=0)
        tk.Label( master=columnFrame, text='description',  relief=tk.RIDGE, width=120).grid( row=0, column=1)
        tk.Label( master=columnFrame, text='census column', relief=tk.RIDGE, width=20).grid( row=0, column=2)

        # initialize each match as "missing"
        matches = [ tk.StringVar() for c in ctfs_names ]
        for m in matches:
            m.set('*MISSING*')

        # fill in the table
        for i,n in enumerate( ctfs_names ) : 
            d = self.col_descr[i]
            tk.Label( master=columnFrame, text=n, relief=tk.RIDGE, width=15).grid( row=i+1, column=0)
            tk.Label( master=columnFrame, text=d, relief=tk.RIDGE, width=120).grid( row=i+1, column=1)
            tk.OptionMenu(columnFrame, matches[i],  *names ).grid( row=i+1, column=2 )  
       
        # button action for after columns are matched 
        def matchCols():
            matched_cols = { m.get().title():ctfs_names[i]  for i,m in enumerate(matches) }
            hippnet_data.rename(columns=matched_cols, inplace=True)
            print list(hippnet_data) 
            columnFrame.destroy()
            App(root)
        # button 
        self.done_button = tk.Button(columnFrame, text='Done', command=matchCols )
        self.done_button.pack( fill=tk.X, side=tk.BOTTOM)

class PlotCorner:
    def __init__( self, master):
        cornerFrame = tk.Frame(master)
        cornerFrame.pack_propagate(0)
        cornerFrame.pack(fill=tk.BOTH)
        
        tk.Label(master=cornerFrame, text='Plot SW corner (x coordinate UTM)').grid(row=0)
        tk.Label(master=cornerFrame, text='Plot SW corner (y coordinate UTM)').grid(row=1)

        x_entry = tk.Entry(cornerFrame)
        y_entry = tk.Entry(cornerFrame)

        x_entry.grid(row=0,column=1)
        y_entry.grid(row=1,column=1)

        def getCorners():
            gx = x_entry.get()
            gy = y_entry.get()
            print gx,gy
            cornerFrame.destroy()
            App(root)
        
        tk.Button(cornerFrame, text='Set coordinates', command=getCorners ).pack()

class App:
    def __init__ (self, master):
        self.mainFrame = tk.Frame(master, name = 'main-frame', width=1000, height=700)
        self.mainFrame.master.title( 'Standardize HIPPNET data')
        self.mainFrame.pack_propagate(0)
        self.mainFrame.pack(fill=tk.BOTH) 
        
        startFrame = tk.Frame( self.mainFrame , width=200, height=100)
        startFrame.pack_propagate(0)
        startFrame.pack(fill=tk.BOTH)
        tk.Label(startFrame, text='Welcome to the HIPPNET data standardizer').pack()
        tk.Button(startFrame, text='Column Selector', command=self.launchColumnSelect).pack(fill=tk.BOTH)
        
        tk.Button(startFrame, text='Define Plot Corner', command=self.launchPlotCorner ).pack(fill=tk.BOTH)
        
        self.startFrame = startFrame
        
    def launchColumnSelect(self):
        self.startFrame.destroy() 
        ColumnSelect(self.mainFrame)

    def launchPlotCorner(self):
        self.startFrame.destroy()
        newPage = PlotCorner( self.mainFrame)


root    = tk.Tk()
launch  = App( root )

root.mainloop()

#root = tk.Tk()
#app = App1( root )
#root.mainloop()


