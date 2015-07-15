import Tkinter as tk

import pandas

class App:
    def __init__( self, master, dataframe, dat_cols, dat_rows, edit_col ):
       
        self.root = master

        self.df = dataframe
        self.edit_col = edit_col
        self.dat_cols = dat_cols
        self.dat_rows = dat_rows
       
        self.fill()

    def fill( self): 
        self.scrollbar  = tk.Scrollbar(self.root, orient="vertical")
        self.xscrollbar = tk.Scrollbar(self.root, orient="horizontal")
        self.lb = tk.Listbox(self.root, width=50, height=20,
                        yscrollcommand=self.scrollbar.set, xscrollcommand=self.xscrollbar.set)
        self.scrollbar.config(command=self.lb.yview)
        self.xscrollbar.config(command=self.lb.xview)
        self.scrollbar.pack(side="right", fill="y")
        self.xscrollbar.pack(side="bottom", fill="x")
        self.lb.pack(side="left",fill="both", expand=True)

        self.rowmap =  { i:row for i,row in enumerate(self.dat_rows ) }

        self.sub_data =  self.df.ix[ self.dat_rows, self.dat_cols  ]
        self.sub_datstring = self.sub_data.to_string(index=False ).split('\n')
        
        for line in self.sub_datstring:
            self.lb.insert("end", line)
            self.lb.bind('<ButtonRelease-1>',self.callback)

    def unfill(self):
        self.xscrollbar.destroy()
        self.scrollbar.destroy()
        self.lb.destroy()

    def callback(self, event):
        self.lb=event.widget
        items = self.lb.curselection()
        try: items = map(int, items)
        except ValueError: pass
        idx=items[0]
        df_idx = self.rowmap[ idx - 1]
        if idx > 0:
            self.row = df_idx
            self.editDF() 

    def editDF(self):
        self.new = tk.Toplevel(self.root)
        tk.Label( self.new, text=self.edit_col, background='darkgreen', foreground='white').grid( row=0)
        
        self.entry = tk.StringVar()
        self.entry_box = tk.Entry( self.new )
        self.entry_box.grid( row=1)


        dataVal = str( self.df.ix[ self.row,self.edit_col] )
        self.entry_box.insert(0, dataVal)
   
        tk.Button( self.new, text='Done', relief=tk.RAISED, command=self.editDF_done ).grid(row=2 ) 

    def editDF_done(self):
        dataValNew = self.entry_box.get()
        self.df.set_value(self.row,self.edit_col,dataValNew )
        self.new.destroy()
        self.unfill()
        self.fill()


def main():
    df = pandas.read_table( '/Users/mender/CTFS/treelover/tsv2ctfs/data/Laupahoehoe_annual_master.txt', sep='\t', na_values='NA')

    dat_cols = ['tag', 'sp', 'CensusID', 'date', 'ExactDate', 'dbh', 'nostems', 'status', 'DFstatus', 'RawStatus','treeID'] 
    dat_rows = [ 10,23,100, 200, 400 ]
    edit_col = 'RawStatus'
    root = tk.Tk()

    app = App(  root, df,  dat_cols, dat_rows,edit_col  )
    root.mainloop()

if __name__ == '__main__':
    main()
 


