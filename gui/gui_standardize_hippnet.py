import os
import sys
import re
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import ttk
import tkFileDialog

import numpy as np
import pandas

sys.path.append('/Users/mender/HIPPNET/hippnet')
import helper
import resolver
ResolveData = resolver.ResolveData


class App:
    def __init__ (self, master):
        self.master = master

#       make main frame
        self.main_frame = tk.Frame(self.master, width=700, height=400)
        self.main_frame.pack_propagate(False)
        self.main_frame.master.title( 'Standardize HIPPNET data')
        self.main_frame.pack() 

#       some standard options for label widgets
        self.LabelOpts = {'font':'BOLD', 'background':'darkgreen', 
                            'foreground':'white','relief':tk.RIDGE }

#       get the databases from mysql  
        self.allDatabases = helper.getDatabaseList()

        self._init_plotCorner_censusID_multiStem()
        self._init_proc_check_vars()
        
        self._make_main_frame_lab_text()
        self._make_widget_container()
        self._layout()
    
    def _make_main_frame_lab_text(self):
        self.Text_DataBase       = 'Not selected.'
        self.Text_PlotCorner     = 'Not defined.'
        self.Text_ColSelect         = 'Not matched.'
        self.Text_CensusID         = 'Not assigned.'
        self.Text_ResolveRawStatus  = 'Unresolved'
        self.Text_ResolveStatus  = 'Unresolved'
        self.Text_ResolveColumns = ''
        self.Text_MultiStem      = 'Unresolved'
        self.Text_MoreMultiStem  = 'Unresolved'

    def _init_plotCorner_censusID_multiStem(self):
        self.censusx0000 = 0
        self.censusy0000 = 0
        self.censusx0000 = 185950
        self.censusy0000 = 2185420

        self.censusID    = 3 #0
        self.multi_stem_names = []
    
    def _init_proc_check_vars(self):
        self.DatabaseLoaded    = {'done':False, 'mssg':'Load a MYSWL database first!'}
        self.ColumnsMatched    = {'done':False, 'mssg':'Match columns First!'}
        self.ResolveRawStatus  = {'done':False, 'mssg':'Resolve Status First!'}
        self.CensusNumSet      = {'done':False, 'mssg':'Set Census ID first!'}
        self.PlotCornerSet     = {'done':False, 'mssg':'Set plot corner first!'}
        self.StatusResolved    = {'done':False, 'mssg':'Resolve status columns first!'}
        self.MultiStemSelected = {'done':False, 'mssg':'Select multiple stem data first!'}

    def _make_widget_container(self):
        self.container_frame = tk.Frame( self.main_frame)
        self.container_frame.pack_propagate(False)
        self.container_frame.pack()
    
    def _layout(self):
        self.container_frame.destroy()
        self._make_widget_container()
        self._button_layout()
        self._label_layout()
        self._text_layout()

    def _button_layout(self):
        tk.Button(self.container_frame, text='Load a HIPPNET MYSQL Database', command = self.LoadDatabase ).grid(row=0, column=2)
        tk.Button(self.container_frame, text='Define Plot Corner',                command=self.plotCorner ).grid(row=1, column=2)
        tk.Button(self.container_frame, text='Column Selector',                    command=self.colSelect ).grid(row=2, column=2)
        tk.Button(self.container_frame, text='Set a CensusID',                  command = self.setCensusID).grid(row=3, column=2)
        tk.Button(self.container_frame, text='Resolve Raw Status',         command = self._resolveRawStatus).grid(row=4, column=2)
        tk.Button(self.container_frame, text='Set CTFS DFstatus',         command = self.resolveStatus).grid(row=5, column=2)
        tk.Button(self.container_frame, text='Resolve Column',       command = self.resolveColVals).grid(row=6, column=2)
        tk.Button(self.container_frame, text='Select Multiple Stems Columns',     command = self.multiStem).grid(row=7, column=2)
        tk.Button(self.container_frame, text='Select More Multiple Stem Data',command = self.moreMultiStem).grid(row=8, column=2)
        tk.Button(self.container_frame, text='Finished',                             command = self.Finish).grid(row=9, column=1)
        tk.Button( self.container_frame, text='Restart',                       command =  self.restartLoop).grid(row=10, column=2)
    
    def _text_layout(self):
        tk.Label(self.container_frame,       text=self.Text_DataBase).grid(row=0, column=1)
        tk.Label(self.container_frame,     text=self.Text_PlotCorner).grid(row=1, column=1)
        tk.Label(self.container_frame,      text=self.Text_ColSelect).grid(row=2, column=1)
        tk.Label(self.container_frame,       text=self.Text_CensusID).grid(row=3, column=1)
        tk.Label(self.container_frame,  text=self.Text_ResolveRawStatus).grid(row=4, column=1)
        tk.Label(self.container_frame,  text=self.Text_ResolveStatus).grid(row=5, column=1)
        tk.Label(self.container_frame, text=self.Text_ResolveColumns).grid(row=6, column=1)
        tk.Label(self.container_frame,      text=self.Text_MultiStem).grid(row=7, column=1)
        tk.Label(self.container_frame, text=self.Text_MoreMultiStem).grid( row=8, column=1)

    def _label_layout(self):
        tk.Label(self.container_frame, text='Database Info:',   **self.LabelOpts).grid(row=0, column=0)
        tk.Label(self.container_frame, text='Plot Corner:',     **self.LabelOpts).grid(row=1, column=0)
        tk.Label(self.container_frame, text='Columns Matched:', **self.LabelOpts).grid(row=2, column=0)
        tk.Label(self.container_frame, text='CensusID:',        **self.LabelOpts).grid(row=3, column=0)
        tk.Label(self.container_frame, text='Resolve Raw Status:',   **self.LabelOpts).grid(row=4, column=0)
        tk.Label(self.container_frame, text='Set DF Status:',   **self.LabelOpts).grid(row=5, column=0)
        tk.Label(self.container_frame, text='Resolve:',  **self.LabelOpts).grid(row=6, column=0)
        tk.Label(self.container_frame, text='Multiple Stems:',  **self.LabelOpts).grid(row=7, column=0)
        tk.Label(self.container_frame, text='More Multiple Stems:',  **self.LabelOpts).grid(row=8,column=0)


    def _check_proc_complete(self, proc):
        proc_done = proc['done']
        proc_mssg = proc['mssg']
        if not proc_done:
            warningWindow = tk.Toplevel()
            tk.Label(warningWindow, text=proc_mssg, background='red', foreground='white', font='BOLD' ).pack()
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
        self.loadWin = tk.Toplevel()
        self.loadWin.title('Select MYSQL database and table')
        
        tk.Label(self.loadWin, text='MYSQL Database name', **self.LabelOpts  ).grid(row=0,column=0)
        self.database_var = tk.StringVar()
        self.database_opt = tk.OptionMenu( self.loadWin, self.database_var, *self.allDatabases )
        self.database_var.set('Laupahoehoe' )##########
        self.database_opt.grid( row=0, column=1)
        
        def CMD_selectDB():
            self.mysql_database = self.database_var.get()
            tk.Label(  self.loadWin,text='Database Table name' , **self.LabelOpts ).grid(row=2, column=0)
            all_tables = helper.getTables(self.mysql_database)
            self.datatable_var = tk.StringVar()
            self.datatable_opt = tk.OptionMenu( self.loadWin, self.datatable_var, *all_tables )
            self.datatable_opt.grid( row=2, column=1)
            self.datatable_var.set( 'LAU_resurvey_2010_v02')#############
            def CMD_LoadTable():
                mysql_table = self.datatable_var.get()
                self.Text_DataBase = '%s; %s'%(self.mysql_database, mysql_table)
#               read HIPPNET TSV file into pandas
                self.datatype, self.hippnet_data = helper.mysql_to_dataframe( self.mysql_database, mysql_table   )
                self.hippnet_col_names = list(self.hippnet_data)
                self.loadWin.destroy()
                self._layout() 
                self.DatabaseLoaded['done'] = True
            tk.Button( self.loadWin, text='Load Table', relief = tk.RAISED, command=CMD_LoadTable  ).grid(row=3,columnspan=2)

        tk.Button( self.loadWin, text='Use Database', relief = tk.RAISED, command=CMD_selectDB  ).grid(row=1,columnspan=2)
        
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
                self.PlotCornerSet['done'] = True
                self.Text_PlotCorner= "x= %.2f; y=%.2f"%(self.censusx0000, self.censusy0000)
                self._layout()

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
                self.PlotCornerSet['done'] = True
                self._layout()
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
        if not self._check_proc_complete( self.DatabaseLoaded ):
            return
        if not self._check_proc_complete( self.CensusNumSet ):
            return
        if not self._check_proc_complete( self.PlotCornerSet):
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
            if c== 'tag':
                self.matches[i].set( 'RE_TAG')
            elif c== 'sp':
                self.matches[i].set( 'SPECIES')
            elif c== 'x':
                self.matches[i].set( 'x')
            elif c== 'y':
                self.matches[i].set( 'y')
            elif c== 'dbh':
                self.matches[i].set( 'DBH_2011')
            elif c== 'ExactDate':
                self.matches[i].set( 'RE_DATE')
            elif c== 'RawStatus':
                self.matches[i].set( 'RE_STATUS')
            elif c== 'nostems':
                self.matches[i].set( 'RE_NSTEMS')
            else:
                self.matches[i].set('*MISSING*')
        
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
                    
            nn = self.hippnet_data.notnull()

#           ~~~~ SPECIES ~~~
            self.hippnet_data.ix[ nn['sp'], 'sp'] = self.hippnet_data.ix[ nn['sp'],'sp'].map( lambda x:x.upper() )
#           ~~~~ DATE ~~~
            datetime_stamp = pandas.DatetimeIndex( self.hippnet_data ['ExactDate'] )
            self.hippnet_data ['ExactDate'] = datetime_stamp
            self.hippnet_data ['date']      = datetime_stamp.to_julian_date()
#           ~~~ GPS ~~~~
            self.hippnet_data.ix[nn['x'], 'gx']       = np.round(self.hippnet_data.ix[nn['x'],'x'] - self.censusx0000, decimals=3)
            self.hippnet_data.ix[nn['y'], 'gy']       = np.round(self.hippnet_data.ix[nn['y'],'y'] - self.censusy0000, decimals=3)
#           ~~~ NULL columns which are required for CTFS formatting but dont apply to HIPPNET data 
            self.hippnet_data ['StemTag']  = np.nan
            self.hippnet_data ['stemID']   = np.nan
            self.hippnet_data ['codes']    = np.nan
            self.hippnet_data ['agb']      = np.nan
#           ~~~ CENSUS ID label ~~~
            self.hippnet_data ['CensusID'] = self.censusID 
#           ~~~~ POINT OF MEASUREMENT related ~~~~~
            if matched_cols['pom'] != '*MISSING*':
                self.hippnet_data.ix[nn['pom'], 'hom'] = self.hippnet_data.ix[nn['pom'], 'pom'].map(lambda x:'%.2f'%x)
            else:
                self.hippnet_data[ 'pom'] = np.nan 
                self.hippnet_data[ 'hom'] = np.nan 
            
            for col_name in self.non_mandatory_cols:
                if matched_cols[ col_name ] == '*MISSING*':
                    self.hippnet_data[ col_name] = np.nan

            self.colWin.destroy()

            self.ColumnsMatched['done'] =True
            self.Text_ColSelect = 'Matched!'
            self._layout()        

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
            self.CensusNumSet['done'] = True
            self.Text_CensusID = '%d'%self.censusID
            self._layout()
            censusID_window.destroy()

        tk.Button( censusID_window, text='Apply', command=CMD_setCensusID ).grid(row=2)

##########################
# TREE STATUS RESOLUTION #
##########################
    def resolveStatus( self):
        if not self._check_proc_complete( self.ColumnsMatched):
            return
        if not self._check_proc_complete( self.ResolveRawStatus):
            return
        
        self.statusWin = tk.Toplevel()
        self.unique_status = {  stat:tk.StringVar() for stat 
                in  set( self.hippnet_data.ix[self.hippnet_data.notnull()['RawStatus'],'RawStatus'])  }
    
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
            self.hippnet_data.ix[self.hippnet_data.notnull()['RawStatus'], 'status'] =  self.hippnet_data.ix[self.hippnet_data.notnull()['RawStatus'], 'DFstatus'].map(lambda x:x.upper()[0])
            self.statusWin.destroy() 
            
            self.StatusResolved['done'] = True
            self.Text_ResolveStatus = 'Resolved!'
            self._layout()
            
        tk.Button( self.statusWin, text='Apply', relief=tk.RAISED , font='BOLD',
                    command=CMD_resolveStatus).grid( row=len(self.unique_status)+2, columnspan=2)

    def _resolveRawStatus(self):
        if not self._check_proc_complete( self.ColumnsMatched):
            return
        self.resolveColVals(edit_this_col='RawStatus')
        self.ResolveRawStatus['done'] = True
        self.Text_ResolveRawStatus  = 'Resolved!'

###########################
# COLUMN VALUE RESOLUTION #
###########################
    def resolveColVals(self, edit_this_col=None):
        if not self._check_proc_complete( self.ColumnsMatched):
            return
        self.res_win  = tk.Toplevel()
        if edit_this_col:
            self.resolver = ResolveData(self.res_win, self.hippnet_data, edit_this_col)
        else:
            self.resolver = ResolveData(self.res_win, self.hippnet_data)
        self.resolver.pack(side=tk.LEFT, fill=tk.BOTH)
        bframe = tk.Frame(self.res_win, bd=3, relief=tk.RIDGE)
        bframe.pack(side=tk.LEFT,fill=tk.BOTH)
        b = tk.Button(bframe, text='Exit', command=self._exit_resolve, bd=4, relief=tk.RAISED)
        b.pack( side=tk.LEFT, fill=tk.BOTH)
    
    def _exit_resolve(self):
        self.res_win.destroy()
        self.hippnet_data = self.resolver.df

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
        for i,col in enumerate( self.col_vars ):
            cb = tk.Checkbutton(self.winCanvasFrame, text=col, variable=self.col_vars[ col ] ).grid( row = i+1, sticky=tk.W )

        def CMD_multiStem():
            for col in self.col_vars:
                if self.col_vars[col].get():
                    names_list.append( col ) 
            self.winCanvas.destroy()
            self.winCanvasFrame.destroy()
            self.winVSB.destroy()
            self.selColFromList_b.destroy()
            closer()
        
        self.selColFromList_b = tk.Button( self.winCanvasFrame, text='SELECT',relief=tk.RAISED, command = CMD_multiStem)
        self.selColFromList_b.grid( row=len( self.col_vars)+2)

###############
# MULTI STEMS #
###############
    def multiStem(self):
        if not self._check_proc_complete( self.DatabaseLoaded ):
            return
        self.multiStemWin = tk.Toplevel()
        self.multi_stem_names = []
        self.selectColFromList( self.multiStemWin, list(self.hippnet_data), self.multiStemCloser, self.multi_stem_names )
        
    def multiStemCloser( self) :
        self.MultiStemSelected['done'] = True
        self.Text_MultiStem = 'Selected!'
        self._layout()
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
        if not self._check_proc_complete( self.ColumnsMatched):
            return

        self.moreMstemWin = tk.Toplevel(width=400,height=300)
        self.moreMstemWin.grid_propagate(False)
        self.moreMstemWin.title('Additional Multi-Stem Data')

        def CMD_moreInColumn():
            self.moreMstemB1.destroy()
            self.moreMstemB2.destroy()
            
            self.moreInColumn_lab1 = tk.Label( self.moreMstemWin, text='select a column', **self.LabelOpts )
            self.moreInColumn_lab1.grid(row=0)
            self.moreInColumn_var1 = tk.StringVar()
            self.moreInColumn_opt1 = tk.OptionMenu( self.moreMstemWin , self.moreInColumn_var1, *list(self.hippnet_data) )
            self.moreInColumn_opt1.grid(row=1)
            
            def CMD_grabFromColumn():

                more_mstem_col = self.moreInColumn_var1.get()

                null_inds = self.hippnet_data[ more_mstem_col].isnull()
                self.hippnet_data.loc[ self.hippnet_data[more_mstem_col].isnull(), more_mstem_col]  = ''
                mstem_from_notes = self.hippnet_data[more_mstem_col].map( lambda x: re.findall('[0-9]{1,2}\.[0-9]*' , x) ) 

#               make all notes lower case for easier logical comparison
                self.hippnet_data[more_mstem_col]= self.hippnet_data[more_mstem_col].map( lambda x:x.lower() )

#               filter out mstam matches from notes, where mstem is actually a single dbh measurement of the main stem
                not_mstem_condition = [ 'stem' not in note 
                                        and 'previous' in note 
                                        and len(matches)==1 
                                        and 'maybe' in note 
                                        or 'past' in note 
                                        for note,matches in zip(self.hippnet_data[more_mstem_col], mstem_from_notes) ]
                mstem_from_notes[ not_mstem_condition ] = None

#               max nomstem from main database
                max_nomstem = len( filter( lambda x:re.match('dbh_',x), list(self.hippnet_data) )  )

#               create a mapping from mstem_from_notes series to a new dataframe, where the columns are the mstem dbh measurements
                mstems_map = [ {'dbh_%d'%(i+max_nomstem+1):float(val) 
                                for i,val in enumerate(vals) }  
                                if vals 
                                else {} 
                                for vals in mstem_from_notes.values ]
                more_mstems_df = pandas.DataFrame( mstems_map, index=mstem_from_notes.index )

                self.hippnet_data = pandas.concat( (self.hippnet_data, more_mstems_df) ,axis=1 )
                
                self.Text_MoreMultiStem = 'Selected'
                self._layout()
                self.moreMstemWin.destroy()
            
            self.moreInColumn_b1 = tk.Button( self.moreMstemWin, text='Select', command=CMD_grabFromColumn )
            self.moreInColumn_b1.grid(row=2)


        def CMD_moreInTable():
            self.more_multi_stem_names = []
            self.moreMstemB1.destroy()
            self.moreMstemB2.destroy()
            
            self.db_lab = tk.Label(self.moreMstemWin, text='MYSQL Database name', **self.LabelOpts  )
            self.db_lab.grid(row=0,column=0)
            
            self.database_var = tk.StringVar()
            self.database_opt = tk.OptionMenu( self.moreMstemWin, self.database_var, *self.allDatabases )
            self.database_opt.grid( row=0, column=1)
        
            def CMD_selectDB():
                self.mysql_database = self.database_var.get()
                self.tbl_lab = tk.Label(  self.moreMstemWin,text='Database Table name' , **self.LabelOpts )
                self.tbl_lab.grid(row=2, column=0)
                
                all_tables = helper.getTables(self.mysql_database)
                self.datatable_var = tk.StringVar()
                self.datatable_opt = tk.OptionMenu( self.moreMstemWin, self.datatable_var, *all_tables )
                self.datatable_opt.grid( row=2, column=1)
                def CMD_LoadTable():
                    mysql_table = self.datatable_var.get()
#                   read HIPPNET TSV file into pandas
                    self.mstem_datatype, self.mstem_data = helper.mysql_to_dataframe( self.mysql_database, mysql_table   )
                    self.db_lab.destroy()
                    self.database_opt.destroy()
                    self.tbl_lab.destroy()
                    self.datatable_opt.destroy()
                    self.db_b.destroy()
                    self.tbl_b.destroy()
                    
                    self.selectColFromList( self.moreMstemWin,  list(self.mstem_data), 
                                            self.closerInTable, self.more_multi_stem_names)
                
                self.tbl_b = tk.Button( self.moreMstemWin, text='Load Table', relief = tk.RAISED, command=CMD_LoadTable)
                self.tbl_b.grid(row=3,columnspan=2)
            self.db_b = tk.Button( self.moreMstemWin, text='Use Database', relief = tk.RAISED, command=CMD_selectDB )
            self.db_b.grid(row=1,columnspan=2)
            
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
        ctfs_merger_col = self.ctfs_mstem_merger.get()
        self.mstem_data.rename( columns = {self.mstem_merge_column: ctfs_merger_col }, inplace=True)
        self.Text_MoreMultiStem = 'Selected'
        self._layout()
        if self.more_multi_stem_names:
            self.mstem_data = self.mstem_data[ [ctfs_merger_col]+self.more_multi_stem_names ] 
#           max nomstem from main database
            max_nomstem = len( filter( lambda x:re.match('dbh_',x), list(self.hippnet_data) )  )
#           rename the columns to a standard name
            self.mstem_data.rename( columns={ name:'dbh_%d'%(i+max_nomstem+1) 
                                        for i,name in enumerate(self.more_multi_stem_names) }, 
                                        inplace=True )
            self.hippnet_data = pandas.merge( self.hippnet_data, self.mstem_data, on=ctfs_merger_col, how='outer')
            self.moreMstemWin.destroy()
        else:
            self.multiStemWin.destroy()
       
###################
# SAVE AND FINISH #
###################
    def Finish(self):
        if not self._check_proc_complete(self.ColumnsMatched):
            return

        if not self._check_proc_complete(self.StatusResolved):
            return 

        # sort the mstems columns
        mstem_cols = [ col_name for col_name in list(self.hippnet_data) if col_name.startswith('dbh_') ]
        self.hippnet_data[ mstem_cols] = np.sort( self.hippnet_data[ mstem_cols ].values.astype(float) ,axis=1)
        ######################
        # SPECIFY SOME TYPES #
        ######################
        newtypes = { 'sp':str,
                    'tag':int,
                    'notes':str,
                    'slp':str,
                    'dbh':float,
                    'gx': float,
                    'gy': float,
                    'hom': float,
                    'pom':str}
        for col,t in newtypes.iteritems():
            to_convert = self.hippnet_data[col].notnull()
            self.hippnet_data.ix[ to_convert, col] = self.hippnet_data.ix[to_convert,col ].astype(t) 

        output_cols  = [ col for col in self.ctfs_names if col in list(self.hippnet_data) ] 
        output_cols += mstem_cols 
        output_cols += ['DFstatus', 'status', 'gx', 'gy', 'StemTag', 'stemID', 'agb', 'CensusID', 'codes', 'hom', 'date' ]
       
        self.hippnet_data = self.hippnet_data.loc[:, output_cols]

        self.saveWin = tk.Toplevel()
        self.saveWin.title('Save')
        tk.Label(self.saveWin,text='Enter an output filename:', **self.LabelOpts).grid(row=0,column=0)
        self.saveEntry = tk.Entry(self.saveWin)
        self.saveEntry.grid(row=0,column=2)
        
        tk.Label( self.saveWin, text='Select Format' , **self.LabelOpts ).grid(row=1,column=0 )
        self.xlsx_var = tk.IntVar()
        self.pkl_var = tk.IntVar()
        self.xlsx_cb = tk.Checkbutton(self.saveWin, text='xlsx', variable = self.xlsx_var )
        self.xlsx_cb.grid(row=1,column=1)
        self.pkl_cb = tk.Checkbutton(self.saveWin, text='pkl', variable = self.pkl_var )
        self.pkl_cb.grid(row=1,column=2)

        def CMD_save():
            saveName = self.saveEntry.get()
            outfile_xlsx = os.path.join( self.saveDir , '%s.xlsx'%saveName )
            outfile_pkl = os.path.join( self.saveDir , '%s.pkl'%saveName )
            
            
            if self.xlsx_var.get():
                try:
                    self.hippnet_data.to_excel(outfile_xlsx , float_format='%.2f' , na_rep='NA' , index=False)

                except ImportError:
                    errorWin = tk.Toplevel()
                    tk.Label(self.errorWin, text='XLSX not supported', background='red', foreground='white').grid(row=0)
                    tk.Button(errorWin, text='Ok', command=errorWin.destroy ).grid(row=1)
            if self.pkl_var.get():
                self.hippnet_data.to_pickle(outfile_pkl)
            
            self.container_frame.destroy()
            self.saveWin.destroy()
            
            tk.Label(self.main_frame, text='Mahalo HIPPNET!').grid(row=0,columnspan=2)
            tk.Button( self.main_frame, text='Aloha', command = self.master.destroy ).grid(row=1,column=0)
            tk.Button( self.main_frame, text='Restart', command = self.restartLoop ).grid(row=1,column=1)
        
        self.saveDir = os.getcwd()
        tk.Label( self.saveWin, text='Current Output Directory:', **self.LabelOpts).grid( row=2, column=0)
        
        self.dir_label = tk.Label( self.saveWin , text=self.saveDir)
        self.dir_label.grid( row=2, column=2 )
        
        tk.Button( self.saveWin, text='Change Directory', command = self.changeSaveDir ).grid(row=3,columnspan=3)
        tk.Button( self.saveWin, text='Save', command=CMD_save ).grid(row=4, columnspan=3)

    def changeSaveDir(self):
        askdir_opt = {}
        askdir_opt['mustexist'] = False
        askdir_opt['parent'] = self.saveWin
        self.saveDir = tkFileDialog.askdirectory(**askdir_opt)
        self.dir_label.config(text=self.saveDir)

    def restartLoop(self):
        self.master.destroy()
        root    = tk.Tk()
        launch  = App( root  )
        root.mainloop()

if __name__ == '__main__':
    root    = tk.Tk()
    launch  = App( root  )
    root.mainloop()
