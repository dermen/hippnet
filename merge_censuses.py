import os
from collections import Counter
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import itertools


import pandas

cwd = os.getcwd()
os.chdir('/Users/mender/HIPPNET/hippnet')
import database_edit
EditorApp = database_edit.EditorApp
os.chdir(cwd)

def convert_tag_int(dataframe):
    dataframe[ 'tag'] = dataframe[  'tag'].astype(int)

def getDBHcol(dataframe):
    dbhCols = [ n for n in list(dataframe) if n.startswith('dbh_') ]
    dbhCols = [ int( n.split('dbh_')[-1] ) for n in dbhCols ] 
    return dbhCols

def addDBH_NA( dataframe, maxDBH):
    thisMaxDBH = max( getDBHcol(dataframe) )
    while thisMaxDBH < maxDBH:
        thisMaxDBH += 1
        new_col = 'dbh_%d'%(thisMaxDBH)
        dataframe[ new_col] = pandas.np.nan
    return 

def launch_editor( df, inds, message = None):
    root      = tk.Tk()
    editor     = EditorApp(  root, df, inds )
    editor.pack()
    tk.Button( root, text='Finish', command=root.destroy ).pack()
    if message:
        root.title(message)
        win = tk.Toplevel(root)
        tk.Label(win,text=message, background='red', foreground='white').pack()
        tk.Button(win, text='ok', command=win.destroy).pack() 
    root.mainloop()
    return editor.get_df()

def find_duplicate_inds( df, col, flatten=True):
    """ find the rows of duplicates in dataframe df, column col"""
    counter    = Counter(df[col])
    duplicates = [ k for k,val in counter.items() if val > 1 ]
    if duplicates:
        dupe_inds  = [ pandas.np.where(df[col] == dupe)[0] for dupe in duplicates ] 
        dupe_inds  = [ i for sublist in dupe_inds for i in sublist] #flatten
    else:
        dupe_inds  = []
        duplicates = []
    return dupe_inds,duplicates

def resolve_duplicates(df, col,  message=None):
    dupe_inds,_ = find_duplicate_inds(df=df, col=col)
    while dupe_inds:
        df         = launch_editor( df, dupe_inds, message=message)
        dupe_inds,_  = find_duplicate_inds(df=df, col=col)
    return df

def resolve_na(dataframe, column ,message = None):
    inds = pandas.np.where( dataframe[column].isnull() )[0]
    if inds.size:
        dataframe = launch_editor( dataframe, inds, message=message)
    return dataframe

def make_locator_col(df,name='locator'):
    df[name] = (df.gx*100 + df.gy*100*20000).astype(int).astype(str)

def assert_not_null(df, cols=['gx','gy','tag','RawStatus', 'status','DFstatus']):
    for col in cols:
        df = resolve_na( df, col, 'resolve na in col %s'%col)
        assert( all(df[col].notnull() ) ) #'col %s has na values'%col

def main():
    pkl_dir   = '/Users/mender/Desktop'
    plotName  = 'Lau_check'
    pkl_files = [os.path.join( pkl_dir, '%s_%d.pkl'%(plotName,x)) for x in xrange(2009, 2014) ] 
    dfs       = [ pandas.read_pickle( pkl_f) for pkl_f in pkl_files ]

#####################
# RESOLVE MAX STEMS #
#####################
    maxStems = max( [  max( getDBHcol(df)  ) for df in dfs ] )
    for df in dfs:
        addDBH_NA( df, maxStems )

########################
# MAKE COLUMN SUFFIXES #
########################
    uID      = [ df.CensusID[0] for df in dfs ]  # censusID should be same for each row in each census
    suffixes = [ '_census%d'%x for x in uID]

##################################
# FIND TAGS WHERE XY IS DUPICATE #
##################################
    all_tag_info = {}
    for i,df in enumerate(dfs):
        assert_not_null(df) 
        make_locator_col(df) # gives attribute df.locator

        counter    = Counter(df.locator)
        dupe_dict  = {k : pandas.np.where(df.locator==k)[0].tolist() 
                      for k,v in counter.iteritems() 
                      if v>1}

        all_dupe_inds = [ i for sublist in dupe_dict.values() for i in sublist ]
        
#       resolve tag duplicates if x,y is also a duplicate
        resolve_duplicates( df.ix[df.index[all_dupe_inds],] , 'tag')  
        
        tags  = df.ix[df.index[all_dupe_inds], 'tag']
        locs = df.ix[df.index[all_dupe_inds], 'locator']
        for tag,loc in itertools.izip(tags, locs):
            new_loc = str(tag)+loc
            if tag not in all_tag_info:
                all_tag_info[tag] =new_loc 

    for i,df in enumerate(dfs):
        where_tags = pandas.np.where( df.tag.isin(all_tag_info) )[0]
        if where_tags.size:
            df.ix[ where_tags,'locator'] = [ all_tag_info[tag] for tag in df.ix[where_tags,'tag'] ]

        inds,loc_dupes = find_duplicate_inds( df, 'locator')

        resolve_duplicates(df, 'locator', message='resolve location duplicates census %s'%suffixes[i])
        df.rename( columns={ n:n+suffixes[i] for n in list(df) if n not in ['locator']} , inplace=True )
        dfs[i] = df.copy()

    df_merged = reduce( lambda x,y: pandas.merge( x,y, on='locator', how='outer'), dfs )
    df_merged.to_pickle('merged.pkl')

    exit()

###############################
# CHECK FOR TAGS THAT CHANGED #
###############################
    #tag_cols    = [n for n in list(df_merged) if n.startswith('tag')]
    #df_tag      = df_merged[:,tag_cols].transpose()  
    #tags_vstime = [(i, df_tags[i].tolist() ) for i in list(df_tags) ]
    #tags_evol   = [(i, tags) for i,tags in tags_vstime if len(set(filter( lambda x: not np.isnan(x), tags)))>1 ]


if __name__ == '__main__':
    main()

"""

tags_changed = { i:d for i,d in 
                 enumerate( [ [ x for x in t if x==x]  for t in 
                     df_merged[tag_cols].values ])  
                 if len(set(d)) > 1 }

df_notnull = df_merged.notnull()

###############
# TAG CHANGED #
###############
for k,val in tags_changed.items():
    utags = ' '.join( map( lambda x : str(int(x)), set (val) ) )
    df_merged.set_value( k, 'associated_tags', utags )
    
    main_tag = val[-1]
    
    tag_notnull_cols = [ col for col in tag_cols if df_notnull.ix[k,col] ]
    df_merged.ix[ k, tag_notnull_cols] = main_tag
    

##############
# SP CHANGED #
##############
sp_cols     = [ n for n in list(df_merged) if n.startswith( 'sp') ]
sp_changed = { i:d for i,d in 
                 enumerate( [ [ x for x in t if x==x]  for t in 
                     df_merged[sp_cols].values ])  
                 if len(set(d)) > 1 }
for k,val in sp_changed.items():
    main_sp = val[-1]
   
    sp_notnull_cols = [ col for col in sp_cols if df_notnull.ix[k,col] ]
    df_merged.ix[ k, sp_notnull_cols] = main_sp

################
# STATUS NULLS #
################
stat_cols     = [ n for n in list(df_merged) if n.startswith( 'status') ]
DFstat_cols     = [ n for n in list(df_merged) if n.startswith( 'DFstatus') ]
Rawstat_cols     = [ n for n in list(df_merged) if n.startswith( 'RawStatus') ]
stats_ = map( lambda  x: x[0] , zip( [ d for d in  df_notnull[stat_cols].values.tolist() ]  ) )

where_new = [ min( where( x)[0] ) for x in stats_ ] # everything before will be

df_isnull = df_merged.isnull()
for row in xrange( len(df_merged)):
    for i in xrange( len( stat_cols)):
        col     = stat_cols[i]
        raw_col = Rawstat_cols[i]
        df_col  = DFstat_cols[i]
        if i < where_new[row]:
            df_merged.set_value( row, col, 'P')
            df_merged.set_value( row, raw_col, 'prior')
            df_merged.set_value( row, df_col, 'prior')
        elif df_isnull.ix[ row, col ] and i > where_new[row]:
            df_merged.set_value( row, col, 'M')
            df_merged.set_value( row, raw_col, 'missing')
            df_merged.set_value( row, df_col, 'missing')


df_merged['treeID'] = df_merged.index.values

for i in xrange( len(dfs )):
    df         = df_merged[ [ n for n in list( df_merged) if n.endswith( suffixes[i]) ] + ['treeID','associated_tags']].copy()
    
    df.rename(columns= { n:n.split(suffixes[i])[0] for n in list( df) if n != 'treeID' } ,inplace=True)
    
    df['main_stem'] = 1 
    df.nostems = 1 
    #df.to_csv( 'Lau_file%d.txt'%i, sep='\t', float_format='%.2f', na_rep='NA' )

    censusID = df.CensusID[ where( df.CensusID.notnull() )[0][0] ]
    null_censusID = where( df.CensusID.isnull() )[0]
    df.ix[ null_censusID, 'CensusID'] = censusID
    df.CensusID = df.CensusID.astype(int)
    
    mstem_cols = [ c for c in list( df) if c.startswith( 'dbh_') ]
    df.drop( axis=1, labels=mstem_cols, inplace=True )
    
    df.ix[ where( df.dbh <= 0)[0], 'dbh' ] = pandas.np.nan

#   remove later
    datetime_stamp = pandas.DatetimeIndex( df.ExactDate )
    df['date'] = datetime_stamp.to_julian_date()
    df['hom'] = df.pom.astype(float)

    dfs[i] = df

df_master = pandas.concat( dfs, ignore_index=True)

df_master.to_csv( '%s_annual_master.txt'%plotName, sep='\t', float_format='%.2f', na_rep='NA', index=False )
"""
