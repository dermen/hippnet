import Tkinter as tk

import pandas

class EditorApp:
    def __init__( self , master, dataframe, edit_rows, edit_cols, test):
        
        self.dataframe = dataframe.copy()
        
        self.test= test
        self.master = master
        self.rows = edit_rows
        self.cols = edit_cols
        
        self.num_cols = len(self.cols)
        self.num_rows = len(self.rows)
        
        # define the main frame
        self.mainFrame = tk.Frame(self.master, width=700, height=400)
        #self.mainFrame.grid_propagate(True)
        #self.mainFrame.pack_propagate(False)
        self.mainFrame.pack() 
        self.mainFrame.master.title( 'Standardize HIPPNET data')

        self.makeMainWidgetContainer()
     
        self.dropped_rows = []

        self.fillMainFrame()
    
    def makeMainWidgetContainer(self):
        self.containerFrame = tk.Frame( self.mainFrame)
        #self.containerFrame.pack_propagate(False)
        self.containerFrame.grid_propagate(True)
        self.containerFrame.pack()

    def fillMainFrame(self):
        self.containerFrame.destroy()
        self.makeMainWidgetContainer()
        
        rows = [ r for r in self.rows if r not in self.dropped_rows ] 
        
        self.entries     = { row:{col: tk.StringVar() for col in self.cols} for row in rows }
        self.entry_boxes = { row:{col: tk.Entry(self.containerFrame) for col in self.cols  } for row in rows }
        
        for i,col in enumerate( self.cols ):
            tk.Label( self.containerFrame, text=col, background='darkgreen', foreground='white').grid( row=0, column=i)
       
#       initialize entry boxes
        for i, row in enumerate( rows ):
            for j,col in enumerate( self.cols ):
                dataVal = str( self.dataframe.ix[ row,col] )
                
                entryBox = self.entry_boxes[row][col]
                entryBox.grid(row=i+1, column=j )
                entryBox.insert(0, dataVal)

        for i,row in enumerate( rows ):
            b = tk.Button( self.containerFrame, text='delete', relief=tk.RAISED, command=lambda x=row: self.delete_row(x) )
            b.grid( row=i+1, column=self.num_cols +1)

        tk.Button( self.containerFrame, text='Done', relief=tk.RAISED, command=self.done ).grid( row=self.num_rows+2, columnspan=self.num_cols)

    def done(self):
        rows = [ r for r in self.rows if r not in self.dropped_rows ] 
        
        for i, row in enumerate( rows):
            for j,col in enumerate( self.cols ):
                entryBox   = self.entry_boxes[row][col]
                dataValNew = entryBox.get()
                self.dataframe.set_value(row,col,dataValNew )

        
        self.dataframe.drop( self.dataframe.index[ self.dropped_rows], inplace=True)
        self.master.destroy()
    
    def delete_row( self, row):
        self.dropped_rows.append( row )
        self.fillMainFrame()

def editDataframe( dataframe, edit_rows,edit_cols ):
    root = tk.Tk()
    launch = EditorApp( root, dataframe, edit_rows, edit_cols,0 )
    root.mainloop()
    return launch.dataframe

