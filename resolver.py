try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import pandas

import database_edit
EditorApp  = database_edit.EditorApp


class ResolveWin:
    def __init__(self, tk_root, dataframe):
        """ This class resilves errors in a dataframe column
            by allowing the user to inspect the data in that column.
            tk_root: parent widget
            dataframe: a pandas.Data.Frame object"""
        self.tk_root  = tk_root
        self.win      = tk.Frame( self.tk_root, width=300, height=200)
        self.win.pack()

        print "how"
#       copy the dataframe
        self.df       = dataframe

#       option menu for selection of dataframe column to resolve
        self.init_lab = tk.Label(self.win,text='Select a column to edit', foreground='white', background='darkgreen')
        self.init_lab.grid(row=0,column=0)
        self.opt_var  = tk.StringVar(self.win)
        self.opt      = tk.OptionMenu( self.win, self.opt_var, *list(self.df) )
        self.opt.grid(row=0, column=1)
        self.opt_var.set('sp')

#       make button for selecting column and spawning the next set of widgets
        self.sel_b    = tk.Button(self.win, text='Select', command = self._resolve )
        self.sel_b.grid(row=1)
    
        self.replacement_map  = []

        self.not_done     = True
    
    def _resolve(self):
        if not self._col_selected():
            return
        self._clear_frame()
        self._set_unique_vals()
        self._make_title_labels()
        self._fill_in_vals()
        self._make_done_button()
    
    def _col_selected( self):
        self.col = self.opt_var.get()
        if self.col not in list(self.df):
            return False
        else:
            return True
    
    def _clear_frame( self):
        self.init_lab.destroy()
        self.opt.destroy()
        self.sel_b.destroy()
    
    def _set_unique_vals(self):     
        self.val_entry = {col_val:tk.Entry(self.win) for col_val in pandas.unique(self.df[self.col])}
    
    def _make_title_labels(self):
        tk.Label( self.win, text='Old value', background='darkgreen', foreground='white', bd=2, relief=tk.RIDGE).grid(row=0, column=0) 
        tk.Label( self.win, text='New value', background='darkgreen', foreground='white', bd=2, relief=tk.RIDGE).grid(row=0, column=1)

    def _fill_in_vals(self): 
        """ iterate over unique values and enter them in the frame
            also, enter buttons for altering the values"""
        for i, col_val in enumerate( self.val_entry ):
            tk.Label(self.win, text=str( col_val), bd=2, relief=tk.RIDGE ).grid(row=i+1, column=0)
            entry = self.val_entry[col_val] 
            entry.grid( row=i+1, column=1)
            entry.insert(0, col_val)
            tk.Button(self.win, text='replace all',  command=lambda x=col_val : self._update_replacement_map(x) ).grid(row=i+1, column=2)
            tk.Button(self.win, text='resolve data', command=lambda x=col_val : self._resolve_data(x)   ).grid(row=i+1, column=3)
    
    def _make_done_button(self): 
        self.done_b = tk.Button( self.win, text='Done', 
                                relief=tk.RAISED , bd=2, command=self._finish_resolve)
        self.done_b.grid(row=len(self.val_entry)+1, column=1, columnspan=2)
   
    def _resolve_data(self, col_val):
        rows = pandas.np.where(self.df[ self.col] == col_val)[0] 
        if rows.size:
            new_root = tk.Tk()
            editor   = EditorApp( new_root, self.df, rows )
            new_root.mainloop()
            self.df  = editor.df

    def _update_replacement_map(self, col_val):
        entry   = self.val_entry[col_val]
        new_val = entry.get()
        if new_val != col_val:
            self.replacement_map[col_val] = new_val
        
    def _finish_resolve(self):
        if self.replacement_map:
            self.df.replace( to_replace={self.col: self.replacement_map} , inplace=True )
        self.win.destroy()
        self.not_done = False
