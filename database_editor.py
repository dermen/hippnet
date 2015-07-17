import Tkinter as tk
import tkFont

import pandas

class EditorApp:
    def __init__( self, master, dataframe, dat_rows ):
        self.root = master
        self.root.minsize(width=600, height=400)
        
        self.root.title('database editor')
        self.main = tk.Frame( self.root )
        self.main.pack(fill=tk.BOTH, expand=True)

#       load the dataframe
        self.df       = dataframe
        self.dat_cols = list( self.df ) 
        self.dat_rows = dat_rows
        self.rowmap   =  { i:row for i,row in enumerate(self.dat_rows ) }

#       subset the data and convert to giant string for viewing        
        self.sub_data      =  self.df.ix[ self.dat_rows, self.dat_cols  ]
        self.sub_datstring = self.sub_data.to_string(index=False).split('\n')
        self.title_string  = self.sub_datstring[0]
#       define the format of the string, so we can update it without recalculating it and preserve the column spacing 
        self.get_line_format(self.title_string)
       
#       fill in the main frame 
        self.fill()

        self.update_history = []

##############
# SCROLL BAR #
##############             
    def onMouseWheel(self, event):
        self.lb_title.xview("scroll", event.delta,"units")
        self.lb.xview("scroll", event.delta,"units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

    def xview(self, *args):
        """connect the yview action together"""
        self.lb.xview(*args)
        self.lb_title.xview(*args)

##################
# ADDING WIDGETS #
##################
    def fill( self): 
        self.canvas = tk.Canvas( self.main )
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.init_scroll()
        self.init_lb()
       
        self.pack_config_scroll()
        self.pack_bind_lb()

        self.fill_listbox()
        
        self.make_editor_frame()

##############
# SCROLLBARS #
##############
    def init_scroll(self):
        self.scrollbar  = tk.Scrollbar(self.canvas, orient="vertical")
        self.xscrollbar = tk.Scrollbar(self.canvas, orient="horizontal")
       
    def pack_config_scroll(self):
        self.scrollbar.config(command=self.lb.yview)
        self.xscrollbar.config(command=self.xview)
        self.scrollbar.pack(side="right", fill="y")
        self.xscrollbar.pack(side="bottom", fill="x")

################
# MAIN LISTBOX #
################
    def init_lb( self):
        self.lb_title = tk.Listbox( self.canvas,height=1, font=tkFont.Font(self.canvas, family="Courier", size=14),
                            yscrollcommand=self.scrollbar.set, xscrollcommand=self.xscrollbar.set, exportselection=False)
        self.lb = tk.Listbox(self.canvas, font=tkFont.Font(self.canvas, family="Courier", size=14),
                        yscrollcommand=self.scrollbar.set, xscrollcommand=self.xscrollbar.set, exportselection=False)

    def pack_bind_lb(self):
        self.lb_title.pack(fill=tk.X) 
        self.lb.pack(fill="both", expand=True)
        self.lb_title.bind("<MouseWheel>", self.onMouseWheel)
        self.lb.bind("<MouseWheel>", self.onMouseWheel)

    def fill_listbox(self):
        """ fill the listbox with rows from the dataframe"""
        self.lb_title.insert( tk.END, self.title_string)
        for line in self.sub_datstring[1:]:
            self.lb.insert(tk.END, line) 
            self.lb.bind('<ButtonRelease-1>',self.listbox_callback)

    def listbox_callback(self, event):
        """ when a listbox item is selected"""
        items = self.lb.curselection()
        try: items = map(int, items)
        except ValueError: pass
        self.idx=items[0]
        self.row = self.rowmap[ self.idx] 
        dataVal = str( self.df.ix[ self.row, self.opt_var.get()] )
        self.entry_box.delete(0,tk.END)
        self.entry_box.insert(0, dataVal)

#####################
# FRAME FOR EDITING #
#####################
    def make_editor_frame(self):
        """ make a frame for editing dataframe rows"""
        self.subframe = tk.Frame( self.main, bd=2, padx=2, pady=2, relief=tk.GROOVE)
        self.subframe.pack(fill=tk.BOTH,side=tk.LEFT) #, expand=tk.YES)

#       column editor
        tk.Label( self.subframe, text='Select a column to edit:', foreground='white', background='darkgreen' ).grid( row=0,sticky=tk.E)
        self.opt_var= tk.StringVar()
        self.opt_var.set('tag')
        self.opt = tk.OptionMenu( self.subframe, self.opt_var, *list(self.df) )
        self.opt.grid(row=0, column=1, sticky=tk.E+tk.W)

#       entry widget
        tk.Label(self.subframe, text='New value:', foreground='white', background='darkgreen').grid(row=1, sticky=tk.E) 
        self.entry_box = tk.Entry( self.subframe, bd=2, relief=tk.GROOVE)
        self.entry_box.grid( row=1, column=1, sticky=tk.E+tk.W)
        
        self.update_b = tk.Button( self.subframe, text='Update single selection', relief=tk.RAISED, command=self.editDF_single )
        self.update_b.grid(row=2, column=1) #, columnspan=2) 
   
        self.sel_mode()
     
        self.make_undo_button()

###################
# SELECTION MODES #
###################
    def sel_mode(self):
        self.sm_frame = tk.Frame( self.main, bd=2, padx=2, pady=2 , relief=tk.GROOVE)
        self.sm_frame.pack(fill=tk.BOTH,side=tk.LEFT) #, expand=tk.YES)
        
        tk.Label( self.sm_frame, text='Selection mode').pack(fill=tk.BOTH,expand=tk.YES)
        
        self.sm_lb = tk.Listbox( self.sm_frame, height=2, width=16, exportselection=False)
        self.sm_lb.pack(fill=tk.BOTH, expand=tk.YES)
        self.sm_lb.insert( tk.END, 'Single selection')
        self.sm_lb.bind('<ButtonRelease-1>', self.sm_lb_callback)
        self.sm_lb.insert( tk.END, 'Multiple selection')
        self.sm_lb.bind('<ButtonRelease-1>', self.sm_lb_callback)
        self.sm_lb.select_set(0)
    
    def sm_lb_callback(self, event):
        items = self.sm_lb.curselection()
        if items[0] == 0:
            self.lb.selection_clear(0,tk.END) 
            self.lb.config( selectmode=tk.BROWSE)
            self.update_b.config( command = self.editDF_single, text='Update single selection')
            self.entry_box.delete( 0, tk.END)
        elif items[0] == 1:
            self.lb.selection_clear(0,tk.END) 
            self.lb.config( selectmode=tk.EXTENDED)
            self.update_b.config( command = self.editDF_single, text='Update single selection')
            self.update_b.config( command = self.editDF_multi, text='Update multi selection' )
            self.entry_box.delete( 0, tk.END)
            self.entry_box.insert( 0, "Enter new value")

#################
# EDIT COMMANDS #
#################
    def editDF_single(self):
        """ button action for updating the dataframe"""
        self.col = self.opt_var.get()
        self.init_hist_tracker()
        self.track()
        self.setval() 
        self.rewrite()
        self.update_hist_tracker() 
       
    def editDF_multi( self ):
        self.col = self.opt_var.get()
        self.init_hist_tracker()
        
        items = self.lb.curselection()
        for i in items:
            self.idx = i
            self.row = self.rowmap[i]
            self.track()
            self.setval()
            self.rewrite()
        self.update_hist_tracker() 
    
    def setval(self):
        try: self.df.set_value( self.row, self.col, self.entry_box.get() )
        except ValueError:
            self.errmsg('Invalid entry `%s` for column `%s`!'%(self.entry_box.get(), self.col ) ) 
    
##############################
# REWRITE MAIN LISTBOX ENTRY #
##############################
    def rewrite(self): 
        """ re-writing the dataframe string in the listbox"""
        new_col_vals = self.df.ix[ self.row , self.dat_cols ].astype(str).tolist() 
        new_line     = self.make_line( new_col_vals ) 
        self.lb.delete(self.idx)
        self.lb.insert(self.idx,new_line)

####################
# HISTORY TRACKING #
####################
    def init_hist_tracker(self):
        self.prev_vals = {}
        self.prev_vals['col'] = self.col
        self.prev_vals['vals'] = {} 
    
    def track(self):
        self.prev_vals['vals'][self.idx] = str( self.df.ix[ self.row, self.col ] ) 

    def update_hist_tracker( self):
        self.update_history.append( self.prev_vals)

    def make_undo_button( self):
        self.undo_b = tk.Button( self.subframe, text='Undo', command = self.undo)
        self.undo_b.grid(row=2, column=0)

    def undo( self):
        if self.update_history:
            updated_vals = self.update_history.pop()
            for idx, val in updated_vals['vals'].items():
                self.row = self.rowmap[idx]
                self.idx = idx
                self.df.set_value(self.row, updated_vals['col'] , val )
                self.rewrite()

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
    def get_line_format(self, line) :
        pos = [1+line.find(' '+n)+len(n) for n in self.dat_cols]
        self.entry_length = [pos[0]] + [ p2-p1 for p1,p2 in zip(  pos[:-1], pos[1:] ) ]

    def make_line( self , col_entries):
        new_line = "".join( [  ('{0: >%d}'%self.entry_length[i]).format(entry)  for  i,entry in enumerate( col_entries ) ] )
        return new_line

def main():
#   read a TSV into dataframe
    tsv_fname = '/Users/mender/CTFS/treelover/tsv2ctfs/data/Laupahoehoe_annual_master.txt'
    df        = pandas.read_table(tsv_fname, sep='\t', na_values='NA')

#   select some rows to edit
    dat_rows   = range( 4000 )

#   start
    root      = tk.Tk()
    editor     = EditorApp(  root, df, dat_rows )
    root.mainloop() # until closes window

#   re-assign dataframe    
    new_df = editor.df

if __name__ == '__main__':
    main()

