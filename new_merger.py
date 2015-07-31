import os
import collections

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

#=============================================================

#####################################
# GROUP BY TAG AND MAKE CORRECTIONS #
#####################################
gb_tag  = dupes_df_tag.groupby(['location','tag'])

########################################
# A correct grouping will only have    #
# one record in gb_tag.groups          #
# (one tag at one x,y for wach census) #
########################################
correct = [tag for tag,count in collections.Counter( tag for loc,tag in gb_tag.groups ).iteritems() if count ==1]
correct = set(correct)
for tag in correct:
    group   = gb_tag.get_group( [g for g in gb_tag.groups if g[1] == tag][0] )
    new_loc = group.tag.astype(int).astype(str) + group[loc_col]
    index   = map(tuple, group[['level_0','level_1']].values )
    dfs_j.ix[index,loc_col] = new_loc.values

####################################
# Otherwise, there is ambiguity    #
# which can only be solved by user #
# investigation of the data        #
####################################
wrong   = [tag for tag,count in collections.Counter( tag for loc,tag in gb_tag.groups ).iteritems() if count > 1]
wrong  += [tag for (loc,tag),inds in gb_tag.groups.iteritems() if len(inds) == 1]
wrong   = set(wrong)
inds_wrong = []
for group, inds in gb_tag.groups.iteritems():
    if group[1] in wrong:
        inds_wrong += inds
dupes_df = dupes_df_tag.ix[inds_wrong, [l for l in list(dupes_df_tag) if not l.startswith('dbh_')] ]
dupes_df.reset_index(drop=True,inplace=True)

################
# the GUI part #
################
root         = tk.Tk()
root.title('Select rows that corrspond to the same tree')
editor_frame = Editor(root, dupes_df)
data_lb      = editor_frame.lb
row_map      = editor_frame.rowmap
errmsg       = editor_frame.errmsg


grouped_items   = []
group_names     = dfs_j[loc_col].tolist()
new_loc_counter = 0

def group_sel():
    global grouped_items,group_names, new_loc_counter

    items = data_lb.curselection()
    items_already_grouped = [i for i in items if i in grouped_items ]
    
    if items and not items_already_grouped:
        rows  = [ row_map[i] for i in items ] 
        group = dupes_df.ix[ rows, ]

        new_loc = str(new_loc_counter)
        while new_loc in group_names:
            new_loc_counter += 1
            new_loc = str(new_loc_counter)
        group_names.append( new_loc)
        index     = map(tuple, group[['level_0','level_1']].values )
        dfs_j.ix[index,loc_col] = new_loc 
        for i in items:
            data_lb.itemconfig(i, {'bg':'black'})
            data_lb.selection_clear(i)
        grouped_items += items
    
    elif items_already_grouped:
        errmsg('please only select un-grouped items')

def group_done():
    global grouped_items, group_names, new_loc_counter
    
    remaining_items = [ i for i in xrange( data_lb.size()) if int(i) not in grouped_items ]
    remaining_rows = [ row_map[i] for i in remaining_items]
    for row in remaining_rows:
        new_loc = str(new_loc_counter) # give it a unique group
        while new_loc in group_names: # if group exists, iterate
            new_loc_counter += 1
            new_loc = str(new_loc_counter)
        group_names.append( new_loc)
        group   = dupes_df.ix[ row, ]
        index   = map(tuple, group[['level_0','level_1']].values )
        dfs_j.ix[index, loc_col ] = new_loc
    
    root.destroy()

group_button = tk.Button(root,text='Group selection', command=group_sel )
done_button  = tk.Button(root,text='Done grouping', command=group_done)

group_button.pack()
done_button.pack()
editor_frame.pack()
root.mainloop()

# CONTINUE HERE


