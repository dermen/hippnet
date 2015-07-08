import os
import sys
import re
import Tkinter as tk

import numpy as np
import pandas

sys.path.append('/Users/mender/HIPPNET/hippnet')
import helper 

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
        self.Text_MultiStem    = 'Unresolved'
        self.Text_MoreMultiStem = 'Unresolved'

        self.censusx0000 = 0
        self.censusy0000 = 0
        self.censusID    = 0
        self.multi_stem_names = []
        
        self.DatabaseLoaded = False
        self.ColumnsMatched = False
        self.CensusNumSet = False
        self.PlotCornerSet = False

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
        tk.Button( self.containerFrame, text='Select Multiple Stems Columns', command = self.multiStem).grid(row=6,column=2)
        tk.Button( self.containerFrame, text='Select More Multiple Stem Data', command = self.moreMultiStem).grid(row=7,column=2)
#       finished button
        tk.Button( self.containerFrame, text='Finished', command = self.Finish, background='blue',foreground='white').grid( row=8, column=1)
    
    def TextLayout(self):
        tk.Label(self.containerFrame, text=self.Text_DataBase).grid( row=0,column=1)
        tk.Label(self.containerFrame, text=self.Text_PlotCorner).grid( row=1,column=1)
        tk.Label(self.containerFrame, text=self.Text_ColSelect).grid( row=2,column=1)
        tk.Label(self.containerFrame, text=self.Text_CensusID).grid( row=3,column=1)
        tk.Label(self.containerFrame, text=self.Text_ResolveStatus).grid( row=4,column=1)
        tk.Label(self.containerFrame, text=self.Text_ResolveSpecies).grid( row=5,column=1)
        tk.Label(self.containerFrame, text=self.Text_MultiStem).grid( row=6,column=1)
        tk.Label(self.containerFrame, text=self.Text_MoreMultiStem).grid( row=7,column=1)

    def LabelLayout(self):
        tk.Label(self.containerFrame, text='Database Info:',   **self.LabelOpts).grid(row=0,column=0)
        tk.Label(self.containerFrame, text='Plot Corner:',     **self.LabelOpts).grid(row=1,column=0)
        tk.Label(self.containerFrame, text='Columns Matched:', **self.LabelOpts).grid(row=2,column=0)
        tk.Label(self.containerFrame, text='CensusID:',        **self.LabelOpts).grid(row=3,column=0)
        tk.Label(self.containerFrame, text='Status Column:',   **self.LabelOpts).grid(row=4,column=0)
        tk.Label(self.containerFrame, text='Species Column:',  **self.LabelOpts).grid(row=5,column=0)
        tk.Label(self.containerFrame, text='Multiple Stems:',  **self.LabelOpts).grid(row=6,column=0)
        tk.Label(self.containerFrame, text='More Multiple Stems:',  **self.LabelOpts).grid(row=7,column=0)

    def checkDatabaseLoaded(self):
        if not self.DatabaseLoaded:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text='Load a MYSQL database first!', background='red', foreground='white', font='BOLD' ).pack()
            tk.Button( warningWindow, text='OK',command=warningWindow.destroy, relief=tk.RAISED,font='BOLD' ).pack()
            return False
        else:
            return True

    def checkColumnsMatched(self):
        if not self.ColumnsMatched:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text='Match columns first!', background='red', foreground='white', font='BOLD' ).pack()
            tk.Button( warningWindow, text='OK',command=warningWindow.destroy, relief=tk.RAISED,font='BOLD' ).pack()
            return False
        else:
            return True
    
    def checkCensusNum(self):
        if not self.CensusNumSet:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text='Specify a unique census number first!', background='red', foreground='white', font='BOLD' ).pack()
            tk.Button( warningWindow, text='OK',command=warningWindow.destroy, relief=tk.RAISED,font='BOLD' ).pack()
            return False
        else:
            return True
    
    def checkPlotCorner(self):
        if not self.PlotCornerSet:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text='Select plot corner first!', background='red', foreground='white', font='BOLD' ).pack()
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
            self.datatype, self.hippnet_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )
            self.hippnet_col_names  = list(self.hippnet_data)
            self.db_select.destroy()
            self.Layout()
        
        tk.Button(self.db_select, text="Load MYSQL Database", command= CMD_LoadDatabase).grid(row=2,columnspan=2)
        self.DatabaseLoaded = True

##########################
# PLOT CORNER DEFINITION #
##########################
    def plotCorner(self):
        self.cornerFrame = tk.Toplevel(width=400,height=200)
        self.cornerFrame.title('Plot Corner definition')
        self.cornerFrame.grid_propagate(False)
        def CMD_plotCornerManual():
            self.cornerButton1.destroy()
            self.cornerButton2.destroy()
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
                self.PlotCornerSet = True
                self.Text_PlotCorner= "x= %.2f; y=%.2f"%(self.censusx0000, self.censusy0000)
                self.Layout()

            tk.Button(self.cornerFrame, text='Apply', command=getCornersManual ).grid(row=3,columnspan=2)

        def CMD_plotCornerSelect():
            self.cornerButton1.destroy()
            self.cornerButton2.destroy()
            tk.Label( self.cornerFrame , text='Plot name:',background='darkgreen',foreground='white', 
                        font='BOLD',relief=tk.RIDGE).grid(row=0,column=0)
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
                self.PlotCornerSet = True
                self.Layout()
                self.cornerFrame.destroy()

            tk.Button(self.cornerFrame, text='Apply', command=getCornersList).grid(row=1,columnspan=2)

        self.cornerButton1 = tk.Button( master=self.cornerFrame, text='define manually', command=CMD_plotCornerManual  )
        self.cornerButton1.grid(row=0)
        self.cornerButton2 = tk.Button( master=self.cornerFrame, text='select from list', command=CMD_plotCornerSelect )
        self.cornerButton2.grid(row=1)

####################
# COLUMN SELECTION #
####################
    def colSelect(self):
        if not self.checkDatabaseLoaded():
            return
        if not self.checkCensusNum():
            return
        if not self.checkPlotCorner():
            return
        self.loadCTFS_standard()

#       SOME COLUMNS ARE MANDATORY            
        self.mandatory_cols = ['sp', 'ExactDate', 'x', 'y', 'dbh', 'RawStatus', 'tag', 'nostems' ]
        self.non_mandatory_cols = [ col_name for col_name in self.ctfs_names if col_name not in self.mandatory_cols ]
        
        self.colWin = tk.Toplevel()
        self.colWin.title('Match Columns to CTFS standards')
        tk.Label( master=self.colWin, text='CTFS column', font='BOLD', relief=tk.RIDGE, width=15).grid( row=0, column=0)
        tk.Label( master=self.colWin, text='description',  relief=tk.RIDGE, width=120).grid( row=0, column=1)
        tk.Label( master=self.colWin, text='census column', relief=tk.RIDGE, width=20).grid( row=0, column=2)

        # initialize each match as "missing"
        self.matches = [ tk.StringVar() for c in self.ctfs_names ]
        for i,c in enumerate( self.ctfs_names) : # in self.matches:
            if c == 'sp':
                self.matches[i].set( 'SPECIES')
            elif c == 'tag':
                self.matches[i].set( 'TAG')
            elif c == 'RawStatus':
                self.matches[i].set( 'Status')
            elif c == 'nostems':
                self.matches[i].set( 'number_of_stems')
            elif c == 'dbh':
                self.matches[i].set( 'DBH_2010')
            elif c == 'ExactDate':
                self.matches[i].set( 'Date_')
            elif c == 'x':
                self.matches[i].set( 'x')
            elif c == 'y':
                self.matches[i].set( 'y')
            else:
                self.matches[i].set('*MISSING*')

        # fill in the table
        for i,n in enumerate( self.ctfs_names ) : 
            d = self.col_descr[i]
            if n in self.mandatory_cols:
                tk.Label( master=self.colWin, text=n, relief=tk.RIDGE, width=15, background='red',foreground='white').grid( row=i+1, column=0)
            else:
                tk.Label( master=self.colWin, text=n, relief=tk.RIDGE, width=15).grid( row=i+1, column=0)
            tk.Label( master=self.colWin, text=d, relief=tk.RIDGE, width=120).grid( row=i+1, column=1)
            col_choices =['*MISSING*']+ self.hippnet_col_names
            tk.OptionMenu(self.colWin, self.matches[i],  *col_choices).grid( row=i+1, column=2 )  
        
        def CMD_colSelect(): 
            matched_cols = { self.ctfs_names[i]:m.get()  for i,m in enumerate(self.matches) }
            
            rename_map = { m.get():self.ctfs_names[i] for i,m in enumerate(self.matches) if m.get() != '*MISSING*' }
            self.hippnet_data.rename(columns=rename_map, inplace=True)
           
            for col in self.mandatory_cols: 
                assert( matched_cols[col] != '*MISSING*' )

#           ~~~~ SPECIES ~~~
            self.hippnet_data['sp'] = self.hippnet_data['sp'].map( lambda x:x.upper() )
#           ~~~~ DATE ~~~
            datetime_stamp = pandas.DatetimeIndex( self.hippnet_data ['ExactDate'] )
            self.hippnet_data ['ExactDate'] = datetime_stamp
            self.hippnet_data ['date']      = datetime_stamp.to_julian_date()
#           ~~~ GPS ~~~~
            self.hippnet_data ['gx']       = np.round(self.hippnet_data['x'] - self.censusx0000, decimals=3)
            self.hippnet_data ['gy']       = np.round(self.hippnet_data['y'] - self.censusy0000, decimals=3)
#           ~~~ NULL columns which are required for CTFS formatting but dont apply to HIPPNET data 
            self.hippnet_data ['StemTag']  = np.nan
            self.hippnet_data ['stemID']   = np.nan
            self.hippnet_data ['codes']    = np.nan
            self.hippnet_data ['agb']      = np.nan
#           ~~~ CENSUS ID label ~~~
            self.hippnet_data ['CensusID'] = self.censusID 
#           ~~~~ POINT OF MEASUREMENT related ~~~~~
            if matched_cols['pom'] != '*MISSING*':
                self.hippnet_data[ 'hom'] = self.hippnet_data[ 'pom'].map(lambda x:'%.2f'%x)
            else:
                self.hippnet_data[ 'hom'] = np.nan 
            
            for col_name in self.non_mandatory_cols:
                if matched_cols[ col_name ] == '*MISSING*':
                    self.hippnet_data[ col_name] = np.nan

            self.colWin.destroy()

            self.ColumnsMatched =True
            self.Text_ColSelect = 'Matched!'
            self.Layout()        

        tk.Button(self.colWin, text='Done', foreground='white', background='darkgreen',
                font='BOLD', command=CMD_colSelect, relief=tk.RAISED).grid(row=len(self.ctfs_names)+1, column = 1 )
        tk.Label( self.colWin, text='Red=Mandatory', foreground='white', background='red').grid(row=len(self.ctfs_names)+1,column=0)

#############
# CENSUS ID #
#############
    def setCensusID( self ):
        censusID_window = tk.Toplevel()
        tk.Label( censusID_window, text='Enter a unique ID integer for this census:', 
                foreground='white', background='darkgreen', font='BOLD').grid(row=0)
        self.censusID_entry = tk.Entry( censusID_window  )
        self.censusID_entry.grid(row=1)
        def CMD_setCensusID():
            self.censusID = int( self.censusID_entry.get() )
            self.CensusNumSet = True
            self.Text_CensusID = '%d'%self.censusID
            self.Layout()
            censusID_window.destroy()

        tk.Button( censusID_window, text='Apply', command=CMD_setCensusID ).grid(row=2)

##########################
# TREE STATUS RESOLUTION #
##########################
    def resolveStatus( self):
        if not self.checkColumnsMatched():
            return
        
        self.statusWin = tk.Toplevel()
        
        self.unique_status = {  stat:tk.StringVar() for stat in  set( self.hippnet_data['RawStatus'])  }
    
        # set default values
        for stat in self.unique_status:
            self.unique_status[stat].set( "alive" )

        dfstat = [ 'alive', 'dead', 'missing', 'gone' ]
        
        tk.Label( self.statusWin, text='Assign a CTFS DFstatus based on the RawStatus', **self.LabelOpts).grid( row=0,columnspan=2 ) 
       
        self.raw_stat_entry =  { stat: tk.Entry( self.statusWin ) for stat in self.unique_status }
       
        tk.Label( self.statusWin, text='Enter corrections if needed', font='BOLD').grid(row=1, column=0)
        tk.Label( self.statusWin, text='Select CTFS status', font='BOLD').grid(row=1, column=1)
        
        for i,stat in enumerate( self.unique_status ):
            stat_entry = self.raw_stat_entry[ stat] 
            stat_entry.grid( row=i+2, column=0 )
            stat_entry.insert(0, stat )
            tk.OptionMenu( self.statusWin, self.unique_status[stat],  *dfstat ).grid( row=i+2 , column=1)
    
        def CMD_resolveStatus():
            self.hippnet_data['DFstatus'] = self.hippnet_data['RawStatus']
            self.DFstatus_map  = {stat:val.get() for stat,val in self.unique_status.items() if stat != val.get() }
            self.RawStatus_map = {stat:val.get() for stat,val in self.raw_stat_entry.items() if stat != val.get() }
            if self.DFstatus_map:
                self.hippnet_data.replace( to_replace={'DFstatus': self.DFstatus_map} , inplace=True )
            if self.RawStatus_map:
                self.hippnet_data.replace( to_replace={'RawStatus': self.RawStatus_map} , inplace=True )
            
            # make the status column as well, which is an abbeviated DFstatus column
            self.hippnet_data['status']   = self.hippnet_data['DFstatus'].map(lambda x:x.upper()[0])
            self.statusWin.destroy() 
            self.Text_ResolveStatus = 'Resolved!'
            self.Layout()
            
        tk.Button( self.statusWin, text='Apply', relief=tk.RAISED , font='BOLD',
                    command=CMD_resolveStatus).grid( row=len(self.unique_status)+2, columnspan=2)

###########################
# TREE SPECIES RESOLUTION #
###########################
    def resolveSpecies( self):
        if not self.checkColumnsMatched():
            return
        self.spWin = tk.Toplevel()
        
        self.unique_sp = { sp:tk.Entry(self.spWin) for sp in set( self.hippnet_data['sp'])  }
    
        tk.Label( self.spWin, text='Correct species mistakes if necessary', **self.LabelOpts).grid( row=0 ) 
        #tk.Label( self.spWin, text='Raw',).grid( row=1,column=0 ) 
        tk.Label( self.spWin, text='Enter Corrections',).grid( row=1 ) 
        
        for i,sp in enumerate( self.unique_sp ):
            #tk.Label( self.spWin, text=sp, relief=tk.RIDGE).grid( row=i+2, column=0)
            sp_entry = self.unique_sp[ sp ] 
            sp_entry.grid( row=i+2)
            sp_entry.insert(0, sp)

        def CMD_resolveSpecies():
            self.sp_map = { sp:val.get() for sp,val in self.unique_sp.items() if sp != val.get() }
            if self.sp_map:
                self.hippnet_data.replace( to_replace={'sp': self.sp_map} , inplace=True )

            self.spWin.destroy() 
            self.Text_ResolveSpecies = 'Resolved!'
            self.Layout()
            
        tk.Button( self.spWin, text='Apply', relief=tk.RAISED , 
                    font='BOLD',command=CMD_resolveSpecies).grid( row=len(self.unique_sp)+2)

#########################
# MULTIPLE STEMS HELPER # 
#########################
    def multiStemBind(self,event):
            self.winCanvas.configure(scrollregion=self.winCanvas.bbox("all"))

    def selectColFromList( self ,window,  column_list, closer, names_list):
        self.winCanvas =tk.Canvas(window)
        self.winCanvasFrame = tk.Frame(self.winCanvas, bd=1, relief=tk.GROOVE)
        self.winCanvasFrame.pack()
         
        self.winVSB=tk.Scrollbar(window,orient="vertical",command=self.winCanvas.yview)
        self.winCanvas.configure(yscrollcommand=self.winVSB.set)
        
        self.winVSB.pack(side="right",fill="y")
        self.winCanvas.pack(side="left")
        self.winCanvas.create_window((0,0),window=self.winCanvasFrame,anchor='nw')
        self.winCanvasFrame.bind("<Configure>",self.multiStemBind)
        
        lab = tk.Label(self.winCanvasFrame, text='Select Columns with Multi-Stem DBH values', **self.LabelOpts  )
        lab.grid(row=0)
        
        self.col_vars = { col:tk.IntVar() for col in column_list }
        #self.selColFromList_cbs = []
        for i,col in enumerate( self.col_vars ):
            cb = tk.Checkbutton(self.winCanvasFrame, text=col, variable=self.col_vars[ col ] ).grid( row = i+1, sticky=tk.W )
            #self.selColFromList_cbs.append(cb)

        def CMD_multiStem():
            for col in self.col_vars:
                if self.col_vars[col].get():
                    names_list.append( col ) 
            self.winCanvas.destroy()
            self.winCanvasFrame.destroy()
            self.winVSB.destroy()
            self.selColFromList_b.destroy()
            #for cb in self.selColFromList_cbs:
            #    cb.destroy()
            
            closer()

        self.selColFromList_b = tk.Button( self.winCanvasFrame, text='SELECT',relief=tk.RAISED, command = CMD_multiStem)
        self.selColFromList_b.grid( row=len( self.col_vars)+2)

###############
# MULTI STEMS #
###############
    def multiStem(self):
        if not self.checkDatabaseLoaded():
            return
        self.multiStemWin = tk.Toplevel()
        self.multi_stem_names = []
        self.selectColFromList( self.multiStemWin, list(self.hippnet_data), self.multiStemCloser, self.multi_stem_names )
        
    def multiStemCloser( self) :
        self.Text_MultiStem = 'Selected!'
        self.Layout()
        print self.multi_stem_names

        
        if self.multi_stem_names:
            self.hippnet_data.replace( to_replace= {name:{0:np.nan} for name in self.multi_stem_names} , inplace=True )
            self.map_multi_names = {name:'dbh_%d'%(index+1) for index,name in enumerate(self.multi_stem_names) }
            self.nom_mstem_cols = len(self.map_multi_names)
            self.hippnet_data.rename(columns=self.map_multi_names, inplace=True)
            self.multiStemWin.destroy()
        else: 
            self.multiStemWin.destroy()

##########################
# ADDITIONAL MULTI STEMS #
##########################
    def moreMultiStem( self):
        if not self.checkColumnsMatched():
            return
        
        self.moreMstemWin = tk.Toplevel(width=400,height=300)
        self.moreMstemWin.grid_propagate(False)
        self.moreMstemWin.title('Additional Multi-Stem Data')

        def CMD_moreInColumn():
            self.moreMstemWin.destroy()

        def CMD_moreInTable():
            self.more_multi_stem_names = []
            self.moreMstemB1.destroy()
            self.moreMstemB2.destroy()
            
            self.lab1 = tk.Label(  self.moreMstemWin,text='MYSQL Database name'  )
            self.lab1.grid(row=0)
            self.lab2 = tk.Label(  self.moreMstemWin,text='Database Table name'  )
            self.lab2.grid(row=1)
            self.database = tk.Entry(self.moreMstemWin)
            self.database.grid(row=0,column=1)
            self.datatable = tk.Entry(self.moreMstemWin)
            self.datatable.grid(row=1,column=1)
            self.database.insert(0,'Palamanui') 
            self.datatable.insert(0,'pn_toomanystems') 
            def CMD_LoadMstemDatabase():
                mysql_database = self.database.get()
                mysql_table    = self.datatable.get()
                self.mstem_datatype, self.mstem_data = helper.mysql_to_dataframe( mysql_database, mysql_table   )
                self.lab1.destroy()
                self.lab2.destroy()
                self.database.destroy()
                self.datatable.destroy()
                self.more_inTable_b.destroy()
                self.selectColFromList( self.moreMstemWin,  list(self.mstem_data), 
                                self.closerInTable, self.more_multi_stem_names)
            self.more_inTable_b = tk.Button(self.moreMstemWin, text="Load MYSQL Database", command= CMD_LoadMstemDatabase)
            self.more_inTable_b.grid(row=2,columnspan=2)
            
#       BUTTONS
        self.moreMstemB1 = tk.Button( self.moreMstemWin, 
                            text='data in separate MYSQL table', 
                            command = CMD_moreInTable)
        self.moreMstemB1.grid(row=0)
        self.moreMstemB2 = tk.Button( self.moreMstemWin, 
                            text='Select data from delimited column (e.g. notes)', 
                            command = CMD_moreInColumn)
        self.moreMstemB2.grid(row=1)
     
    def closerInTable( self):
        
        def merger_closer():
            self.merger_closer_lab = tk.Label( self.moreMstemWin, text='Select corresponding CTFS Column', **self.LabelOpts)
            self.merger_closer_lab.grid(row=0)
            self.ctfs_mstem_merger = tk.StringVar()
            self.merger_closer_opt = tk.OptionMenu( self.moreMstemWin,self.ctfs_mstem_merger, *list(self.ctfs_names) )
            self.merger_closer_opt.grid(row=1)
            self.merger_closer_b = tk.Button( self.moreMstemWin, text='Select', command = self.more_mstem_table_last )
            self.merger_closer_b.grid( row=2)
             
        #def CMD_merger():
        #    self.mstem_merge_lab.destroy()
        #    self.mstem_merge_b.destroy()
            
        def call_merger_closer():
            self.merger_lab.destroy()
            self.merger_opt.destroy()
            self.merger_b.destroy()
            self.mstem_merge_column = self.mstem_merger.get()
            merger_closer()

        self.merger_lab = tk.Label( self.moreMstemWin, text='Select column to merge with HIPPNET database', **self.LabelOpts)
        self.merger_lab.grid(row=0)
        self.mstem_merger = tk.StringVar()
        self.merger_opt = tk.OptionMenu( self.moreMstemWin,self.mstem_merger, *list(self.mstem_data) )
        self.merger_opt.grid(row=1)
        self.merger_b = tk.Button( self.moreMstemWin, text='Select', command = call_merger_closer )
        self.merger_b.grid( row=2)
 
        
    def more_mstem_table_last(self):
        print self.more_multi_stem_names
        ctfs_merger_col = self.ctfs_mstem_merger.get()
        self.mstem_data.rename( columns = {self.mstem_merge_column: ctfs_merger_col }, inplace=True)
        self.Text_MoreMultiStem = 'Selected'
        self.Layout()
        if self.more_multi_stem_names:
            self.mstem_data = self.mstem_data[ [ctfs_merger_col]+self.more_multi_stem_names ] 
#               max nomstem from main database
            max_nomstem = len( filter( lambda x:re.match('dbh_',x), list(self.hippnet_data) )  )
#               rename the columns to a standard name
            self.mstem_data.rename( columns={ name:'dbh_%d'%(i+max_nomstem+1) 
                                        for i,name in enumerate(self.more_multi_stem_names) }, 
                                        inplace=True )
            self.hippnet_data = pandas.merge( self.hippnet_data, self.mstem_data, on=ctfs_merger_col, how='outer')
            print list( self.hippnet_data )
            self.moreMstemWin.destroy()
        else:
            self.multiStemWin.destroy()
       
##########
# FINISH #
##########
    def Finish(self)
        self.master.destroy()
    

root    = tk.Tk()
launch  = App( root  )
root.mainloop()
