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
        
        self.mainFrame = tk.Frame(self.master, width=700, height=400)
        self.mainFrame.pack_propagate(False)
        #self.mainFrame.grid_propagate(False)
        self.mainFrame.master.title( 'Standardize HIPPNET data')
        self.mainFrame.pack() 

        self.LabelOpts = { 'font':'BOLD', 'background':'darkgreen', 'foreground':'white','relief':tk.RIDGE }
        
        # TEXT VARIABLES
        self.Text_DataBase =  'Not selected.'
        self.Text_PlotCorner =  'Not defined.'
        self.Text_ColSelect =  'Not matched.'
        self.Text_CensusID =  'Not assigned.'
        self.Text_ResolveStatus = 'Unresolved'
        self.Text_ResolveSpecies = 'Unresolved'

        self.censusx0000 = 0
        self.censusy0000 = 0
        self.censusID    = 0
        
        self.DatabaseLoaded = False

        self.makeMainWidgetContainer()
        self.Layout()
    
    def makeMainWidgetContainer(self):
        self.containerFrame = tk.Frame( self.mainFrame)
        self.containerFrame.pack_propagate(False)
        self.containerFrame.pack()
    
    def Layout(self):
        self.containerFrame.destroy()
        self.makeMainWidgetContainer()
        self.ButtonLayout()
        self.LabelLayout()
        self.TextLayout()

    def ButtonLayout(self):
        tk.Button( self.containerFrame, text='Load a HIPPNET MYSQL Database', command = self.LoadDatabase ).grid(row=0, column=2)
        tk.Button(self.containerFrame, text='Define Plot Corner', command=self.plotCorner ).grid(row=1, column=2)
        tk.Button( self.containerFrame, text='Column Selector', command=self.colSelect ).grid(row=2, column=2)
        tk.Button( self.containerFrame, text='Set a CensusID', command = self.setCensusID).grid(row=3,column=2)
        tk.Button( self.containerFrame, text='Resolve Status Column', command = self.resolveStatus).grid(row=4,column=2)
        tk.Button( self.containerFrame, text='Resolve Species Column', command = self.resolveSpecies).grid(row=5,column=2)
    
    def TextLayout(self):
        tk.Label(self.containerFrame, text=self.Text_DataBase).grid( row=0,column=1)
        tk.Label(self.containerFrame, text=self.Text_PlotCorner).grid( row=1,column=1)
        tk.Label(self.containerFrame, text=self.Text_ColSelect).grid( row=2,column=1)
        tk.Label(self.containerFrame, text=self.Text_CensusID).grid( row=3,column=1)
        tk.Label(self.containerFrame, text=self.Text_ResolveStatus).grid( row=4,column=1)
        tk.Label(self.containerFrame, text=self.Text_ResolveSpecies).grid( row=5,column=1)

    def LabelLayout(self):
        tk.Label(self.containerFrame, text='Database Info:',   **self.LabelOpts).grid(row=0,column=0)
        tk.Label(self.containerFrame, text='Plot Corner:',     **self.LabelOpts).grid(row=1,column=0)
        tk.Label(self.containerFrame, text='Columns Matched:', **self.LabelOpts).grid(row=2,column=0)
        tk.Label(self.containerFrame, text='CensusID:',        **self.LabelOpts).grid(row=3,column=0)
        tk.Label(self.containerFrame, text='Status Column:',   **self.LabelOpts).grid(row=4,column=0)
        tk.Label(self.containerFrame, text='Species Column:',  **self.LabelOpts).grid(row=5,column=0)

    def checkDatabaseLoaded(self):
        if not self.DatabaseLoaded:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text='Load a MYSQL database first!', background='red', foreground='white', font='BOLD' ).pack()
            tk.Button( warningWindow, text='OK',command=warningWindow.destroy, relief=tk.RAISED,font='BOLD' ).pack()
            return False
        else:
            return True

    def loadCTFS_standard(self):
        data = np.loadtxt( 
              '/Users/mender/HIPPNET/hippnet/CTFS_tree_column_info.txt', 
              dtype=str,
              delimiter='\t',
              comments='skjdfsakdhfashdfjkhsajdhfkasdfsa' )
        self.ctfs_names = data[:,0]
        self.col_descr  = data[:,1]

#################
# LOAD DATABASE #
#################
    def LoadDatabase(self):
        self.db_select = tk.Toplevel()
        self.db_select.title('Select a MYSQL database')
        tk.Label(  self.db_select,text='MYSQL Database name'  ).grid(row=0)
        tk.Label(  self.db_select,text='Database Table name'  ).grid(row=1)
        self.database = tk.Entry(self.db_select)
        self.database.grid(row=0,column=1)
        self.datatable = tk.Entry(self.db_select)
        self.datatable.grid(row=1,column=1)
        self.database.insert(0,'Palamanui') 
        self.datatable.insert(0,'PN_resurvey_2010_v01') 
        def CMD_LoadDatabase():
            mysql_database = self.database.get()
            mysql_table    = self.datatable.get()
            self.Text_DataBase = '%s; %s'%(mysql_database, mysql_table)
#           read HIPPNET TSV file into pandas
            datatype, self.hippnet_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )
            self.hippnet_col_names  = list(self.hippnet_data)
            self.db_select.destroy()
            self.Layout()
        
        tk.Button(self.db_select, text="Load MYSQL Database", command= CMD_LoadDatabase).grid(row=2,columnspan=2)
        self.DatabaseLoaded = True

##########################
# PLOT CORNER DEFINITION #
##########################
    def plotCorner(self):
        self.cornerFrameTop = tk.Toplevel()
        def CMD_plotCornerManual():
            self.cornerFrame = tk.Toplevel()
            self.cornerFrameTop.destroy()
            tk.Label(master=self.cornerFrame, text='Plot SW corner (x coordinate UTM)').grid(row=0)
            tk.Label(master=self.cornerFrame, text='Plot SW corner (y coordinate UTM)').grid(row=1)
            self.x_entry = tk.Entry(self.cornerFrame)
            self.y_entry = tk.Entry(self.cornerFrame)
            self.x_entry.grid(row=0,column=1)
            self.y_entry.grid(row=1,column=1)
            
            def getCornersManual():
                self.censusx0000 = self.x_entry.getdouble()
                self.censusy0000 = self.y_entry.getdouble()
                self.cornerFrame.destroy()
                self.Text_PlotCorner= "x= %.2f; y=%.2f"%(self.censusx0000, self.censusy0000)
                self.Layout()

            tk.Button(self.cornerFrame, text='Apply', command=getCornersManual ).grid(row=3,columnspan=2)

        def CMD_plotCornerSelect():
            self.cornerFrame = tk.Toplevel()
            self.cornerFrameTop.destroy()
            tk.Label( self.cornerFrame , text='Plot name:',background='darkgreen',foreground='white', font='BOLD',relief=tk.RIDGE).grid(row=0,column=0)
            self.cornerVar = tk.StringVar()
            tk.OptionMenu(self.cornerFrame, self.cornerVar,  *[ 'Palamanui', 'Laupahoehoe' ] ).grid( row=0, column=1 ) 
            def getCornersList():
                if self.cornerVar.get() == 'Palamanui':
                    self.censusx0000 = 185950.006
                    self.censusy0000 = 2185419.984
                elif self.cornerVar.get() == 'Laupahoehoe':
                    self.censusx0000 = 260420.001
                    self.censusy0000 = 2205378.002
                self.Text_PlotCorner= "x= %.2f; y=%.2f"%(self.censusx0000, self.censusy0000)
                self.Layout()
                self.cornerFrame.destroy()

            tk.Button(self.cornerFrame, text='Apply',   command=getCornersList   ).grid(row=1,columnspan=2)

        tk.Button( master=self.cornerFrameTop, text='define manually', command=CMD_plotCornerManual  ).grid(row=0)
        tk.Button( master=self.cornerFrameTop, text='select from list', command=CMD_plotCornerSelect ).grid(row=1)

####################
# COLUMN SELECTION #
####################
    def colSelect(self):
        if not self.checkDatabaseLoaded():
            return

        self.colWin = tk.Toplevel()
      
        self.loadCTFS_standard()
       
        tk.Label( master=self.colWin, text='CTFS column', font='BOLD', relief=tk.RIDGE, width=15).grid( row=0, column=0)
        tk.Label( master=self.colWin, text='description',  relief=tk.RIDGE, width=120).grid( row=0, column=1)
        tk.Label( master=self.colWin, text='census column', relief=tk.RIDGE, width=20).grid( row=0, column=2)

        # initialize each match as "missing"
        self.matches = [ tk.StringVar() for c in self.ctfs_names ]
        for m in self.matches:
            m.set('*MISSING*')

        # fill in the table
        for i,n in enumerate( self.ctfs_names ) : 
            d = self.col_descr[i]
            tk.Label( master=self.colWin, text=n, relief=tk.RIDGE, width=15).grid( row=i+1, column=0)
            tk.Label( master=self.colWin, text=d, relief=tk.RIDGE, width=120).grid( row=i+1, column=1)
            tk.OptionMenu(self.colWin, self.matches[i],  *self.hippnet_col_names ).grid( row=i+1, column=2 )  
        
        def CMD_colSelect(): 
            matched_cols = { m.get():self.ctfs_names[i]  for i,m in enumerate(self.matches) }
            self.hippnet_data.rename(columns=matched_cols, inplace=True)
            
#           ~~~~ SPECIES ~~~
            self.hippnet_data['sp'] = self.hippnet_data['sp'].map( lambda x:x.upper() )
            #self.hippnet_data.loc[ self.hippnet_data['sp'] == 'COPSP', 'sp'] = 'COPRHY'
#           ~~~~ DATE ~~~
            datetime_stamp = pandas.DatetimeIndex( self.hippnet_data ['ExactDate'] )
            self.hippnet_data ['ExactDate'] = datetime_stamp
            self.hippnet_data ['date']      = datetime_stamp.to_julian_date()
#           ~~~ GPS ~~~~
            self.hippnet_data ['gx']       = np.round(self.hippnet_data['x'] - self.census_x0000, decimals=3)
            self.hippnet_data ['gy']       = np.round(self.hippnet_data['y'] - self.census_y0000, decimals=3)
#           ~~~ NULL columns which are required for CTFS formatting but dont apply to HIPPNET data 
            self.hippnet_data ['StemTag']  = np.nan
            self.hippnet_data ['stemID']   = np.nan
            self.hippnet_data ['codes']    = np.nan
            self.hippnet_data ['agb']      = np.nan
#           ~~~ CENSUS ID label ~~~
            hippnet_data ['CensusID'] = census_num 
            
            self.colWin.destroy()

            self.Text_ColSelect = 'Matched!'
            self.Layout()        

        tk.Button(self.colWin, text='Done', foreground='white', background='darkgreen',
                font='BOLD', command=CMD_colSelect, relief=tk.RAISED).grid(row=len(self.ctfs_names)+1, columnspan=3 )

#############
# CENSUS ID #
#############
    def setCensusID( self ):
        censusID_window = tk.Toplevel()
        tk.Label( censusID_window, text='Enter a unique ID integer for this census:', foreground='white', background='darkgreen', font='BOLD').grid(row=0)
        self.censusID_entry = tk.Entry( censusID_window  )
        self.censusID_entry.grid(row=1)
        def CMD_setCensusID():
            self.censusID = int( self.censusID_entry.get() )
            self.Text_CensusID = '%d'%self.censusID
            self.Layout()
            censusID_window.destroy()

        tk.Button( censusID_window, text='Apply', command=CMD_setCensusID ).grid(row=2)

    def resolveStatus( self):
        if not self.checkDatabaseLoaded():
            return
        
        self.statusWin = tk.Toplevel()
        
        #self.unique_status = {  stat:tk.StringVar() for stat in  np.unique( self.hippnet_data['RawStatus'])  }
        self.unique_status = {  stat:tk.StringVar() for stat in  set( self.hippnet_data['Status'])  }
    
        dfstat = [ 'alive', 'dead', 'missing', 'gone' ]
        
        tk.Label( self.statusWin, text='Assign a CTFS DFstatus based on the RawStatus', **self.LabelOpts).grid( row=0,columnspan=2 ) 
        
        for i,stat in enumerate( self.unique_status ):
            tk.Label( self.statusWin, text=stat, relief=tk.RIDGE).grid( row=i+1, column=0)
            tk.OptionMenu( self.statusWin, self.unique_status[stat],  *dfstat ).grid( row=i+1 , column=1)
    
        def CMD_resolveStatus():
            self.hippnet_data['DFstatus'] = self.hippnet_data['RawStatus']
            #self.hippnet_data['DFstatus'] = self.hippnet_data['Status']
            self.DFstatus_map = { stat:val.get() for stat,val in self.unique_status.items() if stat != val.get() }
            if self.DFstatus_map:
                self.hippnet_data.replace( to_replace={'DFstatus': self.DFstatus_map} , inplace=True )
            
            # make the status column as well, which is an abbeviated DFstatus column
            self.hippnet_data['status']   = self.hippnet_data['DFstatus'].map(lambda x:x.upper()[0])
            self.statusWin.destroy() 
            self.Text_ResolveStatus = 'Resolved!'
            self.Layout()
            
        tk.Button( self.statusWin, text='Apply', relief=tk.RAISED , font='BOLD',command=CMD_resolveStatus).grid( row=len(self.unique_status)+1, columnspan=2)

    def resolveSpecies( self):
        if not self.checkDatabaseLoaded():
            return
        self.spWin = tk.Toplevel()
        
        self.unique_sp = { sp:tk.Entry(self.spWin) for sp in set( self.hippnet_data['SPECIES'])  }
    
        tk.Label( self.spWin, text='Correct species mistakes if necessary', **self.LabelOpts).grid( row=0,columnspan=2 ) 
        tk.Label( self.spWin, text='Raw',).grid( row=1,column=0 ) 
        tk.Label( self.spWin, text='Enter Corrections',).grid( row=1,column=1 ) 
        
        for i,sp in enumerate( self.unique_sp ):
            tk.Label( self.spWin, text=sp, relief=tk.RIDGE).grid( row=i+2, column=0)
            sp_entry = self.unique_sp[ sp ] 
            sp_entry.grid( row=i+2 , column=1)
            sp_entry.insert(0, sp)

        def CMD_resolveSpecies():
            self.sp_map = { sp:val.get() for sp,val in self.unique_sp.items() if sp != val.get() }
            if self.sp_map:
                self.hippnet_data.replace( to_replace={'SPECIES': self.sp_map} , inplace=True )

            self.spWin.destroy() 
            self.Text_ResolveSpecies = 'Resolved!'
            self.Layout()
            
        tk.Button( self.spWin, text='Apply', relief=tk.RAISED , font='BOLD',command=CMD_resolveSpecies).grid( row=len(self.unique_sp)+2, columnspan=2)




        return

root    = tk.Tk()
launch  = App( root  )
root.mainloop()
