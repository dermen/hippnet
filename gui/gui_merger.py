import os
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import tkFileDialog

import pandas

class Merger(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self,master,*args,**kwargs)
        
        self.main_frame = tk.Frame(self)
        
        self.btn_frame = tk.Frame( self.main_frame, bd=2, relief=tk.RIDGE)
        self.sel_btn = tk.Button(self.btn_frame,
                                text='select files to merge', 
                                command=self._sel_files,
                                relief=tk.RAISED, bd=3)
        self.clear_btn = tk.Button(self.btn_frame, 
                                   text='clear selected files', 
                                   command=self._clear_selection,
                                   relief=tk.RAISED, bd=3)
        self.open_files_btn = tk.Button(self.btn_frame,
                                            text='Merge files',
                                            command=self._open_and_merge,
                                            relief=tk.RAISED, bd=3)
        self.filenames = []
        self.file_list = tk.Listbox(self.main_frame, bd='3',relief=tk.SUNKEN)
        self._add_listbox_title()
        self._pack_widgets()


    def _sel_files(self):
        file_opt = {'filetypes': [],
                    'initialdir': os.path.expanduser('~')}
        filenames = tkFileDialog.askopenfilenames(**file_opt)
        self.filenames = list(set( filenames).union(self.filenames))
        self._list_files()

    def _clear_selection(self):
        self.filenames = []
        self.file_list.delete(0,tk.END)
        self._add_listbox_title()

    def _add_listbox_title(self):
        self.file_list.insert(tk.END,"Currently Selected Files:")
        self.file_list.itemconfig(0,{'background':'darkgreen','foreground':'white'} )

    def _list_files(self):
        self.file_list.delete(0,tk.END)
        self._add_listbox_title()
        for fname in self.filenames:
            self.file_list.insert(tk.END,fname)
        self.file_list.selection_clear(0,tk.END)
    
    def _pack_widgets(self):
        self.main_frame.pack(fill=tk.BOTH,expand=tk.YES)
        
        self.btn_frame.pack( side=tk.TOP) 
        self.file_list.pack(side=tk.TOP,fill=tk.BOTH,
                            expand=tk.YES, padx=5, pady=5)
        
        self.sel_btn.pack(side=tk.LEFT, expand=tk.YES)
        self.clear_btn.pack(side=tk.LEFT, expand=tk.YES)
        self.open_files_btn.pack(side=tk.LEFT,expand=tk.YES)
        
    def _open_and_merge(self):
        self.dfs  = []
        for fname in self.filenames:
            if fname.endswith('.pkl'):
                try:
                    df = pandas.read_pickle(fname)
                except Exception as err:
                    self._errmsg(message=err)
                    self.clear_selection()
                    self.dfs = []
                    return
            elif fname.endswith('.xlsx'):
                try:
                    df = pandas.read_excel(fname)
                except Exception as err:
                    self._errmsg(message=err)
                    self.clear_selection()
                    self.dfs = []
                    return
            else:
                self._errmsg(message='Please only select ".xlsx" or ".pkl" files.')
                self.clear_selection()
                self.dfs = []
                return
            self.dfs.append(df)
       
        print self.dfs

    def _errmsg(self, message):
        """ opens a simple error message"""
        errWin = tk.Toplevel()
        tk.Label(errWin, text=message, foreground='white', background='red' ).pack()
        tk.Button( errWin,text='Ok', command=errWin.destroy ).pack()






if __name__ =='__main__':
    root = tk.Tk()
    merger_frame = Merger(root)
    merger_frame.pack(fill=tk.BOTH, expand=tk.YES)
    root.mainloop()
        
