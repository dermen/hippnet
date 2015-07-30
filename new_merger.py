import os

import pandas
np = pandas.np

import merge_censuses as help_merge
import database_edit
find_dupe = help_merge.find_duplicate_inds
Editor    = database_edit.EditorApp
tk        = database_edit.tk

pkl_dir   = '/Users/mender/Desktop'
plot_name = 'Lau_check'
pkl_files = [os.path.join( pkl_dir, '%s_%d.pkl'%(plot_name,x)) for x in xrange(2009, 2014) ] 
keys      = ['%s_%d'%(plot_name,x) for x in xrange(2009, 2014) ]
loc_col   = 'location'

dfs       = [ pandas.read_pickle( pkl_f) for pkl_f in pkl_files ]
for df in dfs:
    help_merge.assert_not_null(df)
    help_merge.make_locator_col(df,name=loc_col)

dfs_j     = pandas.concat( dfs, keys=keys)

gen_dfs   = ((key,dfs_j.loc(axis=0)[key,:]) for key in keys)
dupes     = { key:find_dupe(df, col=loc_col)[0] for key,df in gen_dfs }














