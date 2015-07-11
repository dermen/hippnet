import os
from collections import Counter
from decimal import Decimal

import pandas

os.chdir('/Users/mender/HIPPNET/hippnet')
import tk_editor


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

def resolve_duplicates(dataframe):
    counted    = Counter( dataframe.locator)
    duplicates = [ k for k,val in counted.items() if val > 1 ]

    output_cols = ['tag','sp', 'RawStatus', 'notes', 'CensusID', 'locator', 'ExactDate']
    
    while duplicates:
        dupe_inds = [ pandas.np.where( dataframe.locator == dupe)[0] for dupe in duplicates ] 
        dupe_inds = [ i for sublist in dupe_inds for i in sublist] 
        dataframe = tk_editor.editDataframe( dataframe, edit_rows = dupe_inds, edit_cols = output_cols)
        counted    = Counter( dataframe.locator)
        duplicates = [ k for k,val in counted.items() if val > 1 ]
    
    return dataframe

def resolve_na(dataframe, column ):
    inds = pandas.np.where( dataframe[column].isnull() )[0]
    output_cols = ['tag','sp', 'RawStatus', 'notes', 'CensusID', 'ExactDate']
    if inds.size:
        #print dataframe.ix[ inds, column ]
        dataframe = tk_editor.editDataframe( dataframe, edit_rows=inds, edit_cols = output_cols )
        #print dataframe.ix[ inds, column ]
    return dataframe

pkl_dir = '/Users/mender/Desktop'
pkl_files = [ os.path.join( pkl_dir, 'Palamanui_%d.pkl'%x) for x in xrange(2009, 2014) ] 

dfs = [ pandas.read_pickle( pkl_f) for pkl_f in pkl_files ]

# find the census with most stems, and add NA columns to the other censuses, so num columns is equal across censuses
maxStems = max( [  max( getDBHcol(df)  ) for df in dfs ] )
for df in dfs:
    addDBH_NA( df, maxStems )

# find unique census IDs and use them to make suffixes
uID = [ df.CensusID[0] for df in dfs ]  # censusID should be same for each row in each census
suffixes = [ '_census%d'%x for x in uID]

# make a locator column so we can merge the censuses
for i,df in enumerate( dfs):
    assert( all( df.gx.notnull() ) )
    assert( all( df.gy.notnull() ) )
    df = resolve_na( dataframe = df, column='tag' ) 
    convert_tag_int(df)

#   this is a unique locator within the plot for each point at centimeter resolution
    df['locator'] = df.tag.astype(str) + (df.gx*100 + df.gy*100*20000).astype(int).astype(str)
    assert( all( df.locator.notnull() ) )
    df = resolve_duplicates( df)

#   rename census columns
    sfx = suffixes[i]
    df.rename( columns={ n:n+sfx for n in list( df ) if n not in ['locator']} , inplace=True )
    dfs[i] = df.copy()

df_merged = reduce( lambda x,y: pandas.merge( x,y, on='locator', how='outer'), dfs )
df_merged.to_pickle('/Users/mender/Desktop/merged.pkl')

