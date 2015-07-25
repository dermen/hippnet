try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import pandas

import database_edit
EditorApp  = database_edit.EditorApp


class ResolveData(tk.Frame):
    def __init__(self, master, dataframe, edit_this_col=None):
        """ This class resilves errors in a dataframe column
            by allowing the user to inspect the data in that column.
            master: parent widget
            dataframe: a pandas.Data.Frame object
            edit_this_col: str, name a a column to edit by default"""
        tk.Frame.__init__(self, master, bd=3, relief=tk.RIDGE)
        self.master  = master

#       the dataframe
        self.df_orig = dataframe.copy()
        self.df      = dataframe
        
        self.b_opt = {'bd':4,'relief':tk.RAISED}

        self.topwin = tk.Frame( self.master, width=300, height=200)
        self.topwin.pack()

        self.win      = tk.Frame( self.topwin, width=300, height=200)
        self.win.pack()

#       option menu for selection of dataframe column to resolve
        self.init_lab = tk.Label(self.win,text='Select a column to edit', foreground='white', background='darkgreen')
        self.opt_var  = tk.StringVar(self.win)
        self.opt      = tk.OptionMenu( self.win, self.opt_var, *list(self.df) )
        self.opt_var.set(list(self.df)[0])

        if edit_this_col:
            if edit_this_col in self.df:
                self.opt_var.set(edit_this_col)
                self._col_select()
            else:
                raise ValueError
        else:
#           make button for selecting column and spawning the next set of widgets
            self.sel_b    = tk.Button(self.win, text='Select', command = self._col_select )
            self._grid_init()
    def _grid_init(self):
        self.init_lab.grid(row=0,column=0)
        self.opt.grid(row=0, column=1)
        self.sel_b.grid(row=1, columnspan=2)
        
    def _start(self, reset_df=False):
        self.win.destroy()

        self.win      = tk.Frame( self.topwin, width=300, height=200)
        self.win.pack()

#       set the dataframe
        if reset_df:
            self.df       = self.df_orig.copy() 

        self._fill_resolve_frame()

    def _col_select( self):
        self.col = self.opt_var.get() 
        if self.col not in list(self.df):
            return
        else:
            self._start()
    
    def _fill_resolve_frame(self):
        self._where_unique_and_null_vals()
        self._make_title_labels()
        self._fill_in_vals()
        self._make_reset_button()
    
    def _where_unique_and_null_vals(self):
        self.unique_vals = {}
        
        where_    = pandas.np.where
        df_col    = self.df[self.col]
        u_vals    = pandas.unique( df_col[ df_col.notnull() ] )
        
        for val in u_vals:
            self.unique_vals[val] = {}
            self.unique_vals[val]['entry']  = tk.Entry(self.win)
            self.unique_vals[val]['indices'] = where_( df_col==val)[0]
   
        null_inds = where_(self.df.isnull()[self.col]) [0]
        if null_inds.size:
            self.unique_vals['NULL__'] = {}
            self.unique_vals['NULL__']['entry']   = tk.Entry(self.win)
            self.unique_vals['NULL__']['indices'] = null_inds

    def _make_title_labels(self):
        tk.Label( self.win, text='Old value', background='darkgreen', foreground='white', bd=2, relief=tk.RIDGE).grid(row=0, column=0) 
        tk.Label( self.win, text='New value', background='darkgreen', foreground='white', bd=2, relief=tk.RIDGE).grid(row=0, column=1)

    def _fill_in_vals(self): 
        """ iterate over unique values and enter them in the frame
            also, enter buttons for altering the values"""
        for i, col_val in enumerate( self.unique_vals ):
            tk.Label(self.win, text=str( col_val), bd=2, relief=tk.RIDGE ).grid(row=i+1, column=0)
            entry = self.unique_vals[col_val]['entry'] 
            entry.grid( row=i+1, column=1)
            entry.insert(0, col_val)
            tk.Button(self.win, text='replace all',  command=lambda x=col_val : self._replace_data(x), **self.b_opt ).grid(row=i+1, column=2)
            tk.Button(self.win, text='resolve data', command=lambda x=col_val : self._resolve_data(x) , **self.b_opt  ).grid(row=i+1, column=3)
            tk.Button(self.win, text='remove all',   command=lambda x=col_val : self._remove_data(x) , **self.b_opt  ).grid(row=i+1, column=4)
    
    def _make_reset_button(self):
        self.reset_b = tk.Button( self.win, text='Reset', command=lambda :self._restart(reset_df=True), **self.b_opt)
        self.reset_b.grid(row=len(self.unique_vals)+1, column=2, columnspan=1)
   
    def _replace_data( self, col_val):
        new_val = self.unique_vals[col_val]['entry'].get()
        if new_val != col_val:
            inds     = self.unique_vals[col_val]['indices']
            col_type = self.df.dtypes[self.col]
            self.df.ix[ inds, self.col ] = pandas.np.array( [new_val], dtype=col_type)[0]
        self._restart()

    def _resolve_data(self, col_val):
        rows = self.unique_vals[col_val]['indices']
        #rows = pandas.np.where(self.df[self.col] == col_val)[0]
        #if rows.size:
        self.resolve_win  = tk.Toplevel()
        self.editor_frame = EditorApp( self.resolve_win , self.df, rows )
        self.editor_frame.pack()
        b = tk.Button(self.resolve_win, text='Done', command=self._resolve_data_done)
        b.pack(side=tk.LEFT,fill=tk.BOTH)
             
    def _resolve_data_done(self):    
        self.resolve_win.destroy()
        self.df = self.editor_frame.get_df()
        self._restart()

    def _remove_data( self, col_val):
        rows = pandas.np.where(self.df[self.col] == col_val)[0] 
        if rows.size:
            self.df.drop( self.df.index[rows] , inplace=True)
            self.df.reset_index(drop=True, inplace=True)
        self._restart()

    def _restart(self, reset_df=False):
        self._start(reset_df)


if __name__ == '__main__':
    df     = pandas.DataFrame( {'model': pandas.np.random.randint( 0,3,30), 'param1': pandas.np.random.random(30).round(3), 'param2': pandas.np.random.random(30).round(3)} )
    root   = tk.Tk()
    editor =  ResolveData(root, df)
    editor.pack()
    tk.Button( root, text='Exit', command=root.destroy).pack()
    root.mainloop()
