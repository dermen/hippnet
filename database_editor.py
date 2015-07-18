import Tkinter as tk
import tkFont
import tkFileDialog

import pandas

class EditorApp:
    def __init__( self, master, dataframe, dat_rows ):
        self.root = master
        self.root.minsize(width=600, height=400)
        self.root.title('database editor')
        
        self.main = tk.Frame( self.root )
        self.main.pack(fill=tk.BOTH, expand=True)

        self.lab_opt = { 'background':'darkgreen', 'foreground':'white'  }

#       the dataframe
        self.df       = dataframe
        self.dat_cols = list( self.df ) 
        self.dat_rows = dat_rows
        self.rowmap   =  { i:row for i,row in enumerate(self.dat_rows ) }

#       subset the data and convert to giant list of strings (rows) for viewing        
        self.sub_data      = self.df.ix[ self.dat_rows, self.dat_cols  ]
        self.sub_datstring = self.sub_data.to_string(index=False).split('\n')
        self.title_string  = self.sub_datstring[0]

#       save the format of the lines, so we can update it without recalculating it and preserve the column spacing 
        self._get_line_format(self.title_string)

#       fill in the main frame 
        self._fill()

#       updater for tracking changes to the database
        self.update_history = []

##################
# ADDING WIDGETS #
##################
    def _fill( self): 
        self.canvas = tk.Canvas( self.main )
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        
        self._init_scroll()
        self._init_lb()
        self._pack_config_scroll()
        self._pack_bind_lb()
        self._fill_listbox()
        self._make_editor_frame()

##############
# SCROLLBARS #
##############
    def _init_scroll(self):
        self.scrollbar  = tk.Scrollbar(self.canvas, orient="vertical")
        self.xscrollbar = tk.Scrollbar(self.canvas, orient="horizontal")
       
    def _pack_config_scroll(self):
        self.scrollbar.config(command=self.lb.yview)
        self.xscrollbar.config(command=self._xview)
        self.scrollbar.pack(side="right", fill="y")
        self.xscrollbar.pack(side="bottom", fill="x")

    def _onMouseWheel(self, event):
        self.lb_title.yview("scroll", event.delta,"units")
        self.lb.yview("scroll", event.delta,"units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

    def _xview(self, *args):
        """connect the yview action together"""
        self.lb.xview(*args)
        self.lb_title.xview(*args)

################
# MAIN LISTBOX #
################
    def _init_lb( self):
        self.lb_title = tk.Listbox( self.canvas,height=1, 
                                    font=tkFont.Font(self.canvas, 
                                                     family="Courier",
                                                     size=14),
                                    yscrollcommand=self.scrollbar.set, 
                                    xscrollcommand=self.xscrollbar.set,
                                    exportselection=False)
        
        self.lb = tk.Listbox(self.canvas, 
                            font=tkFont.Font(self.canvas, 
                                             family="Courier",
                                             size=14),
                            yscrollcommand=self.scrollbar.set, 
                            xscrollcommand=self.xscrollbar.set, 
                            exportselection=False)

    def _pack_bind_lb(self):
        self.lb_title.pack(fill=tk.X) 
        self.lb.pack(fill="both", expand=True)
        self.lb_title.bind("<MouseWheel>", self._onMouseWheel)
        self.lb.bind("<MouseWheel>", self._onMouseWheel)

    def _fill_listbox(self):
        """ fill the listbox with rows from the dataframe"""
        self.lb_title.insert( tk.END, self.title_string)
        for line in self.sub_datstring[1:]:
            self.lb.insert(tk.END, line) 
            self.lb.bind('<ButtonRelease-1>',self._listbox_callback)
        self.lb.select_set(0)

    def _listbox_callback(self, event):
        """ when a listbox item is selected"""
        items = self.lb.curselection()
        if items:
            self.idx=items[0]
            self.row = self.rowmap[ self.idx] 
            dataVal = str( self.df.ix[ self.row, self.opt_var.get()] )
            self.entry_box_old.config( state=tk.NORMAL)
            self.entry_box_old.delete(0,tk.END)
            self.entry_box_old.insert(0, dataVal)
            self.entry_box_old.config( state=tk.DISABLED)

#####################
# FRAME FOR EDITING #
#####################
    def _make_editor_frame(self):
        """ make a frame for editing dataframe rows"""
        self.subframe = tk.Frame( self.main, bd=2, padx=2, pady=2, relief=tk.GROOVE)
        self.subframe.pack(fill=tk.BOTH,side=tk.LEFT) #, expand=tk.YES)

#       column editor
        self.col_sel_lab = tk.Label( self.subframe, text='Select a column to edit:',**self.lab_opt )
        self.col_sel_lab.grid( row=0, columnspan=2,sticky=tk.W+tk.E)
        
        self.opt_var= tk.StringVar()
        self.opt_var.set(self.dat_cols[0])
        self.opt = tk.OptionMenu( self.subframe, self.opt_var, *list(self.df) )
        self.opt.grid(row=0, columnspan=2,column=2, sticky=tk.E+tk.W)

        self.old_val_lab = tk.Label(self.subframe, text='Old value:',**self.lab_opt)
        self.old_val_lab.grid(row=1, sticky=tk.W, column=0) 
        self.entry_box_old = tk.Entry(self.subframe, state=tk.DISABLED, bd=2, relief=tk.GROOVE)
        self.entry_box_old.grid( row=1, column=1, sticky=tk.E)

#       entry widget
        self.new_val_lab = tk.Label(self.subframe, text='New value:',**self.lab_opt)
        self.new_val_lab.grid(row=1, sticky=tk.E, column=2) 
        self.entry_box_new = tk.Entry( self.subframe, bd=2, relief=tk.GROOVE)
        self.entry_box_new.grid( row=1, column=3, sticky=tk.E+tk.W)
        
        self.update_b = tk.Button( self.subframe, text='Update single selection', relief=tk.RAISED, command=self._editDF_single )
        self.update_b.grid(row=2, columnspan=1, column=3, sticky=tk.W+tk.E) 
   
        self._sel_mode()
     
        self._make_undo_button()

###################
# SELECTION MODES #
###################
    def _sel_mode(self):
        self.sm_frame = tk.Frame( self.main, bd=2, padx=2, pady=2 , relief=tk.GROOVE)
        self.sm_frame.pack(fill=tk.BOTH,side=tk.LEFT) #, expand=tk.YES)
        
        tk.Label( self.sm_frame, text='Selection mode', **self.lab_opt).pack(fill=tk.BOTH,expand=tk.YES)
        
        self.sm_lb = tk.Listbox( self.sm_frame, height=2, width=16, exportselection=False)
        self.sm_lb.pack(fill=tk.BOTH, expand=tk.YES)
        self.sm_lb.insert( tk.END, 'Single selection')
        self.sm_lb.bind('<ButtonRelease-1>', self._sm_lb_callback)
        self.sm_lb.insert( tk.END, 'Multiple selection')
        self.sm_lb.bind('<ButtonRelease-1>', self._sm_lb_callback)
        self.sm_lb.insert( tk.END, 'Find and replace')
        self.sm_lb.bind('<ButtonRelease-1>', self._sm_lb_callback)
        self.sm_lb.select_set(0)
    
    def _sm_lb_callback(self, event):
        items = self.sm_lb.curselection()
        if items[0] == 0:
            self._swap_mode( 'single')
        elif items[0] == 1:
            self._swap_mode( 'multi')
        elif items[0] == 2:
            self._swap_mode('findrep')

    def _swap_mode(self,mode='single'): 
        self.lb.selection_clear(0,tk.END)
        self._swap_lab( mode)
        if mode=='single':
            self.lb.configure(state=tk.NORMAL)
            self.entry_box_old.configure( state=tk.DISABLED )
            self.lb.config( selectmode=tk.BROWSE)
            self.update_b.config( command = self._editDF_single, text='Update single selection')
        elif mode=='multi':
            self.lb.configure(state=tk.NORMAL)
            self.entry_box_old.configure( state=tk.DISABLED )
            self.lb.config( selectmode=tk.EXTENDED)
            self.update_b.config( command = self._editDF_multi, text='Update multi selection' )
        elif mode=='findrep':
            self.lb.config(selectmode=tk.EXTENDED)
            self.lb.configure(state=tk.DISABLED)
            self.entry_box_old.configure( state=tk.NORMAL )
            self.update_b.config( command = self._editDF_findrep, text='Find and replace' )
        self.entry_box_old.delete( 0, tk.END) 
        self.entry_box_new.delete( 0, tk.END)
        self.entry_box_new.insert( 0, "Enter new value")

    def _swap_lab( self,mode='single' ):
        if mode=='single' or mode=='multi':
            self.old_val_lab.config(text='Old value:')
            self.new_val_lab.config(text='New value:')
        elif mode=='findrep':
            self.old_val_lab.config(text='Find:')
            self.new_val_lab.config(text='Replace:')

#################
# EDIT COMMANDS #
#################
    def _editDF_single(self):
        """ button action for updating the dataframe"""
        self.col = self.opt_var.get()
        self._init_hist_tracker()
       
        self._track_items( [ self.idx ]  )
        self._track()
        self._setval() 
        self._rewrite()
        self._update_hist_tracker() 
       
    def _editDF_multi(self):
        self.col = self.opt_var.get()
        self._init_hist_tracker()
        items = self.lb.curselection()
        self._track_items( items)

    def _editDF_findrep(self):
        self.col = self.opt_var.get()
        self._init_hist_tracker()
        old_val = self.entry_box_old.get()
        try:
            items = pandas.np.where( self.sub_data[self.col].astype(str) == old_val )[0]
        except TypeError as err:
            self.errmsg('%s: `%s` for column `%s`!'%(err,str(old_val), self.col ) )  
            return
        if not items.size:
            self.errmsg('Value`%s` not found in column `%s`!'%(str(old_val), self.col ) )  
            return
        else:
            self.lb.config(state=tk.NORMAL)
            self._track_items(items)
            self.lb.config(state=tk.DISABLED)

####################
# HISTORY TRACKING #
####################
    def _track_items(self,items):
        for i in items:
            self.idx = i
            self.row = self.rowmap[i]
            self._track()
            self._setval()
            self._rewrite()
        self._update_hist_tracker()  
    
    def _setval(self):
        try: 
            self.df.set_value( self.row, self.col, self.entry_box_new.get() )
        except ValueError:
            self.errmsg('Invalid entry `%s` for column `%s`!'%(self.entry_box_new.get(), self.col ) ) 
    
    def _init_hist_tracker(self):
        self.prev_vals = {}
        self.prev_vals['col'] = self.col
        self.prev_vals['vals'] = {} 
    
    def _track(self):
        self.prev_vals['vals'][self.idx] = str( self.df.ix[ self.row, self.col ] ) 

    def _update_hist_tracker( self):
        self.update_history.append( self.prev_vals)

    def _make_undo_button( self):
        self.undo_b = tk.Button( self.subframe, text='Undo', command = self._undo)
        self.undo_b.grid(row=2, columnspan=1, column=1, sticky=tk.W+tk.E)

    def _undo( self):
        if self.update_history:
            updated_vals = self.update_history.pop()
            for idx, val in updated_vals['vals'].items():
                self.row = self.rowmap[idx]
                self.idx = idx
                self.df.set_value(self.row, updated_vals['col'] , val )
                self._rewrite()

#################
# ERROR MESSAGE #
#################
    def errmsg(self, message):
        errWin = tk.Toplevel()
        tk.Label(errWin, text=message, foreground='white', background='red' ).pack()
        tk.Button( errWin,text='Ok', command=errWin.destroy ).pack()

##################
# UPDATING LINES #
##################
    def _rewrite(self): 
        """ re-writing the dataframe string in the listbox"""
        new_col_vals = self.df.ix[ self.row , self.dat_cols ].astype(str).tolist() 
        new_line     = self._make_line( new_col_vals ) 
        self.lb.delete(self.idx)
        self.lb.insert(self.idx,new_line)
    
    def _get_line_format(self, line) :
        pos = [1+line.find(' '+n)+len(n) for n in self.dat_cols]
        self.entry_length = [pos[0]] + [ p2-p1 for p1,p2 in zip(  pos[:-1], pos[1:] ) ]

    def _make_line( self , col_entries):
        new_line = "".join( [  ('{0: >%d}'%self.entry_length[i]).format(entry)  for  i,entry in enumerate( col_entries ) ] )
        return new_line


def main():
#   load a TSV as dataframe
    #tsv_fname = '/Users/mender/CTFS/treelover/tsv2ctfs/data/Laupahoehoe_annual_master.txt'
    #df        = pandas.read_table(tsv_fname, sep='\t', na_values='NA')

    df = pandas.DataFrame(pandas.np.random.randint(0,100, (1000, 20)), columns=['col_%d'%x for x in xrange( 20 ) ] ) 

#   start
    root      = tk.Tk()
    editor     = EditorApp(  root, df, range(len(df)) )
    root.mainloop() # until closes window

#   re-assign dataframe    
    new_df = editor.df

    print "THIS IS THE NEW DATABASE:"
    print new_df.to_string(index=False) 

if __name__ == '__main__':
    main()

