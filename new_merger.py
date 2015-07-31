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

dfs       = [ pandas.read_pickle(pkl_f) for pkl_f in pkl_files ]
for df in dfs:
    help_merge.assert_not_null(df)
    help_merge.make_locator_col(df,name=loc_col)

dfs_j     = pandas.concat( dfs, keys=keys)

gen_dfs   = ((key,dfs_j.loc(axis=0)[key,:]) for key in keys)
dupes     = { key:find_dupe(df, col=loc_col)[0] for key,df in gen_dfs }

dupe_locs  = [set( dfs_j.loc(axis=0)[key,inds]['location'] )
              for key,inds in dupes.iteritems() ]
u_locs     = reduce( lambda x,y:x.union(y), dupe_locs)
u_locs_pos = {key: np.where(dfs_j.loc(axis=0)[key,:].reset_index()['location'].isin(u_locs) )[0] 
              for key in keys}

dupe_tags  = [set( dfs_j.loc(axis=0)[key,inds]['tag'] )
              for key,inds in dupes.iteritems() ]
u_tags     = reduce( lambda x,y:x.union(y), dupe_tags)
u_tags_pos = {key: np.where(dfs_j.loc(axis=0)[key,:].reset_index()['tag'].isin(u_tags) )[0] 
              for key in keys}

colors = ['snow','NavajoWhite','SpringGreen','DarkOliveGreen']
colors = [ c+'2' for c in colors] + [ c+'3' for c in colors] + [c+'4' for c in colors]

cols = [ 'CensusID','tag', 'gx', 'gy', 'location','sp','quadrat','subquad','dbh','ExactDate','notes','RawStatus' ]
gen_loc_dupes  = (dfs_j.loc(axis=0)[key,:].iloc[inds].reset_index()[ ['level_0','level_1']+cols ] 
                    for key,inds in u_locs_pos.iteritems() if inds.size)
dupes_df_loc   = pandas.concat( gen_loc_dupes,ignore_index=True )

gen_tag_dupes  = (dfs_j.loc(axis=0)[key,:].iloc[inds].reset_index()[ ['level_0','level_1']+cols ] 
                    for key,inds in u_tags_pos.iteritems() if inds.size)
dupes_df_tag   = pandas.concat( gen_tag_dupes,ignore_index=True )

gb_tag  = dupes_df_tag.groupby(['location','tag'])
correct = [tag for tag,count in Counter( tag for loc,tag in gb_tag.groups ).iteritems() if count ==1]
correct = set(correct)
wrong   = [tag for tag,count in Counter( tag for loc,tag in gb_tag.groups ).iteritems() if count > 1]
wrong  += [tag for (loc,tag),inds in gb_tag.groups.iteritems() if len(inds) == 1]
wrong = set(wrong)

for tag in correct:
    group   = gb_tag.get_group( [g for g in gb_tag.groups if g[1] == tag][0] )
    new_loc = group.tag.astype(int).astype(str) + group[loc_col]
    index   = map(tuple, group[['level_0','level_1']].values )
    dfs_j.ix[index,loc_col] = new_loc.values


#gb = dupes_df_tag.groupby(['tag','location'])

dupes_df       = pandas.merge( left=dupes_df_tag,right=dupes_df_loc, on=['tag','location'], how='outer')

############################################################################################ 
# if there is a dupicate then it will show up as a row of NaN vals for one of the censuses #
############################################################################################

#where_nan_row = [i for i in xrange(len(dupes_df)) if np.isnan(dupes_df.iloc[i]['gx_x']) or np.isnan(dupes_df.iloc[i]['gx_y']) ]

#print where_nan_row

#dupes_df.append( pandas.concat(gen_tag_dupes,ignore_index=True),ignore_index=True)

cols = [ 'CensusID', 'gx', 'gy','sp','quadrat','subquad','dbh','ExactDate','notes','RawStatus' ]
dupes_df = dupes_df[ ['tag', 'location']+ map(lambda x:x+'_x',cols) + map(lambda x:x+'_y', cols) ]

root         = tk.Tk()
editor_frame = Editor(root, dupes_df)
data_lb      = editor_frame.lb

editor_frame.pack()
root.mainloop()






