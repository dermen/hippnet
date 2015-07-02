import os
import sys

import ttk 
import Tkinter as tk
from pylab import *
import numpy as np

sys.path.append('/Users/mender/HIPPNET/hippnet')
import helper 

#mysql_database = "Palamanui"
#mysql_table    = "PN_resurvey_2010_v01"

# ~~~~ read HIPPNET TSV file into pandas ~~~~~~~
#datatype, hippnet_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )

#hippnet_data.rename(columns = lambda x:x.lower(), inplace=True )
#names  = list(hippnet_data)
#hippnet_num_rows   = len( hippnet_data )

#names = np.insert( names, 0, '*MISSING*' )

class App:
    def __init__ (self, master):
        self.master = master
        self.mainFrame = tk.Frame(self.master, width=400, height=300)
        self.mainFrame.master.title( 'Standardize HIPPNET data')
        self.mainFrame.pack_propagate(False)
        self.mainFrame.grid_propagate(False)
        self.mainFrame.pack() 
               
        self.mysqlButton = tk.Button( self.mainFrame, text='Load a HIPPNET MYSQL Database', command = self.selectDatabase )
        self.mysqlButton.grid(row=0)

##############
# INITIALIZE #
##############
    def selectDatabase(self):   
        db_select = tk.Toplevel()
        db_select.title('Select a MYSQL database')
        
        tk.Label(  db_select,text='MYSQL Database name'  ).grid(row=0)
        tk.Label(  db_select,text='Database Table name'  ).grid(row=1)
        
        self.database = tk.Entry(db_select)
        self.database.grid(row=0,column=1)
        
        self.datatable = tk.Entry(db_select)
        self.datatable.grid(row=1,column=1)

        self.database.insert(0,'Palamanui') 
        self.datatable.insert(0,'PN_resurvey_2010_v01') 
        
        self.db_select = db_select
        
        button = tk.Button(self.db_select, text="Load MYSQL Database", command= self.launchLoader)
        button.grid(row=2,columnspan=2)
    
    def launchLoader(self):
        mysql_database = self.database.get()
        mysql_table    = self.datatable.get()

#       read HIPPNET TSV file into pandas
        datatype, self.hippnet_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )

        self.hippnet_col_names  = list(self.hippnet_data)

        self.db_select.destroy()
        self.mysqlButton.destroy()
        
        tk.Button(self.mainFrame, text='Define Plot Corner', command=self.plotCorner ).grid(row=1)


##########################
# PLOT CORNER DEFINITION #
##########################
    def plotCorner(self):
        self.cornerFrameTop = tk.Toplevel()
        tk.Button( master=self.cornerFrameTop, text='define manually', command=self.plotCornerManual  ).grid(row=0)
        tk.Button( master=self.cornerFrameTop, text='select from list', command=self.plotCornerSelect ).grid(row=1)

    def plotCornerManual(self):
        self.cornerFrameTop.destroy()
        self.cornerFrame = tk.Toplevel()

        tk.Label(master=self.cornerFrame, text='Plot SW corner (x coordinate UTM)').grid(row=0)
        tk.Label(master=self.cornerFrame, text='Plot SW corner (y coordinate UTM)').grid(row=1)

        self.x_entry = tk.Entry(self.cornerFrame)
        self.y_entry = tk.Entry(self.cornerFrame)

        self.x_entry.grid(row=0,column=1)
        self.y_entry.grid(row=1,column=1)
        
        tk.Button(self.cornerFrame, text='Apply', command=self.getCornersManual ).grid(row=3,columnspan=2)
    def plotCornerSelect(self):
        self.cornerFrameTop.destroy()
        self.cornerFrame = tk.Toplevel(width=100)
        tk.Label( self.cornerFrame , text='Plot name:', width=50, relief=tk.RIDGE).grid(row=0,column=0)
        self.cornerVar = tk.StringVar()
        tk.OptionMenu(self.cornerFrame, self.cornerVar,  *[ 'Palamanui', 'Laupahoehoe' ] ).grid( row=0, column=1 ) 
        tk.Button(self.cornerFrame, text='Apply',   command=self.getCornersList   ).grid(row=1,columnspan=2)
 
    def getCornersManual(self):
        self.censusx0000 = self.x_entry.getdouble()
        self.censusy0000 = self.y_entry.getdouble()
        self.cornerFrame.destroy()
        tk.Button( self.mainFrame, text='Column Selector', command=self.colSelect ).grid(row=2)
    
    def getCornersList(self):
        if self.cornerVar == 'Palamanui':
            self.censusx0000 = 185950.006
            self.censusy0000 = 2185419.984
        elif self.cornerVar == 'Laupahoehoe':
            self.censusx0000 = 260420.001
            self.censusy0000 = 2205378.002
        
        self.cornerFrame.destroy()
        tk.Button( self.mainFrame, text='Column Selector', command=self.colSelect ).grid(row=2)

####################
# COLUMN SELECTION #
####################
    def colSelect(self):
        self.colWin = tk.Toplevel(width=400,height=300)
        #######################
        # LOAD CTFS INFO PAGE #
        #######################
        data = np.loadtxt( 
              '/Users/mender/HIPPNET/hippnet/CTFS_tree_column_info.txt', 
              dtype=str,
              delimiter='\t',
              comments='skjdfsakdhfashdfjkhsajdhfkasdfsa' )
        self.ctfs_names = data[:,0]
        col_descr = data[:,1]

        tk.Label( master=self.colWin, text='CTFS column', font='BOLD', relief=tk.RIDGE, width=15).grid( row=0, column=0)
        tk.Label( master=self.colWin, text='description',  relief=tk.RIDGE, width=120).grid( row=0, column=1)
        tk.Label( master=self.colWin, text='census column', relief=tk.RIDGE, width=20).grid( row=0, column=2)

        # initialize each match as "missing"
        self.matches = [ tk.StringVar() for c in self.ctfs_names ]
        for m in self.matches:
            m.set('*MISSING*')

        # fill in the table
        for i,n in enumerate( self.ctfs_names ) : 
            d = col_descr[i]
            tk.Label( master=self.colWin, text=n, relief=tk.RIDGE, width=15).grid( row=i+1, column=0)
            tk.Label( master=self.colWin, text=d, relief=tk.RIDGE, width=120).grid( row=i+1, column=1)
            tk.OptionMenu(self.colWin, self.matches[i],  *self.hippnet_col_names ).grid( row=i+1, column=2 )  

        tk.Button(self.colWin, text='Done', command=self.matchCols ).grid(row=len(self.ctfs_names)+1, columnspan=3 )

    def matchCols(self):
        matched_cols = { m.get():self.ctfs_names[i]  for i,m in enumerate(self.matches) }
        self.hippnet_data.rename(columns=matched_cols, inplace=True)
        
#       ~~~~ SPECIES ~~~
        self.hippnet_data['sp'] = self.hippnet_data['sp'].map( lambda x:x.upper() )
        #self.hippnet_data.loc[ self.hippnet_data['sp'] == 'COPSP', 'sp'] = 'COPRHY'

#       ~~~~ DATE ~~~
        datetime_stamp = pandas.DatetimeIndex( self.hippnet_data ['ExactDate'] )
        self.hippnet_data ['ExactDate'] = datetime_stamp
        self.hippnet_data ['date']      = datetime_stamp.to_julian_date()

#       ~~~ GPS ~~~~
        self.hippnet_data ['gx']       = np.round(self.hippnet_data['x'] - self.census_x0000, decimals=3)
        self.hippnet_data ['gy']       = np.round(self.hippnet_data['y'] - self.census_y0000, decimals=3)

#       ~~~ NULL columns which are required for CTFS formatting but dont apply to HIPPNET data 
        self.hippnet_data ['StemTag']  = np.nan
        self.hippnet_data ['stemID']   = np.nan
        self.hippnet_data ['codes']    = np.nan
        self.hippnet_data ['agb']      = np.nan

        self.colWin.destroy()
        


root    = tk.Tk()
launch  = App( root  )
root.mainloop()


#
