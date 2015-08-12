import os
import itertools
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

import pandas
import numpy as np

cwd = os.getcwd()
os.chdir('/Users/mender/HIPPNET/hippnet' )
import merge_censuses as help_merge
import database_edit
os.chdir(cwd)
find_dupe = help_merge.find_duplicate_inds
Editor = database_edit.EditorApp

pkl_dir = '/Users/mender/Desktop'
plot_name = 'Lau_check'
#plot_name = 'Pal_check'
#plot_name = 'Mam_check'
#plot_name = 'Sanc_check'
yrs = [2009,2010,2011,2012,2013]

pkl_files = [os.path.join( pkl_dir, '%s_%d.pkl'%(plot_name,yr)) for yr in yrs ] 
keys = ['%s_%d'%(plot_name,yr) for yr in yrs ]
loc_col = 'location'
try: 
    writer = pandas.ExcelWriter('%s_report.xlsx'%plot_name)
except ImportError:
    print "No excel support. Error report will be printed to the terminal."

#==============================
# LOAD THE INDIVIDUAL DATA SETS
dfs = [ pandas.read_pickle(pkl_f) for pkl_f in pkl_files ]
max_dbh_col = max([max(help_merge.getDBHcol(df)) for df in dfs ] )
max_stems = max_dbh_col + 1
for df in dfs:
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True,inplace=True)
    help_merge.addDBH_NA( df, max_dbh_col )
    help_merge.assert_not_null(df)
    help_merge.make_locator_col(df,name=loc_col)

dfs_j = pandas.concat( dfs, ignore_index=True) #, keys=keys)

gb = dfs_j.groupby(( loc_col, 'CensusID' ))
gb_sizes = gb.size().reset_index(name='sizes')
gb_dupes = gb_sizes.loc[ gb_sizes.sizes > 1 ]
ulocs = gb_dupes[loc_col].unique()

utags = dfs_j.loc[ dfs_j[loc_col].isin(ulocs) ]['tag'].unique()
dupes_df = dfs_j.loc[ np.logical_or( dfs_j[loc_col].isin(ulocs), dfs_j.tag.isin(utags)) ]

dupes_df.drop_duplicates(inplace=True)
dupes_df = dupes_df.sort( ['tag','CensusID'])

#gb_loc      = dfs_j.groupby( (loc_col, 'CensusID' ))
#group_sizes = gb_loc.size().reset_index(name='sizes')
#dupes       = group_sizes.loc[ group_sizes.sizes > 1 ]

#u_locs      = dupes[loc_col].unique()
#u_tags      = dfs_j.ix[ dfs_j[loc_col].isin(u_locs), 'tag' ].unique()

#dupes_dfs_j = dfs_j.loc[ np.logical_or( dfs_j.tag.isin(u_tags), dfs_j[loc_col].isin(u_locs)) ]

#dfs_j     = pandas.concat( dfs, ignore_index=True)

#gen_dfs   = ((key,dfs_j.loc(axis=0)[key,:]) for key in keys)
#dupes     = { key:find_dupe(df, col=loc_col)[0] for key,df in gen_dfs }

#dupe_locs  = [set( dfs_j.loc(axis=0)[key,inds][loc_col] )
#              for key,inds in dupes.iteritems() ]
#u_locs     = reduce( lambda x,y:x.union(y), dupe_locs)
#u_locs_pos = {key: np.where(dfs_j.loc(axis=0)[key,:].reset_index()[loc_col].isin(u_locs) )[0] 
#              for key in keys}

#dupe_tags  = [set( dfs_j.loc(axis=0)[key,inds]['tag'] )
#              for key,inds in dupes.iteritems() ]
#u_tags     = reduce( lambda x,y:x.union(y), dupe_tags)
#u_tags_pos = {key: np.where(dfs_j.loc(axis=0)[key,:].reset_index()['tag'].isin(u_tags) )[0] 
#              for key in keys}

#gen_loc_dupes  = (dfs_j.loc(axis=0)[key,:].iloc[inds].reset_index()
#                    for key,inds in u_locs_pos.iteritems() if inds.size)
#try:
#    dupes_df_loc   = pandas.concat( gen_loc_dupes )
#except ValueError:
#    dupes_df_loc = None

#gen_tag_dupes  = (dfs_j.loc(axis=0)[key,:].iloc[inds].reset_index()
#                    for key,inds in u_tags_pos.iteritems() if inds.size)
#try:
#    dupes_df_tag   = pandas.concat( gen_tag_dupes )
#except ValueError:
#    dupes_df_tag = None

#if dupes_df_tag is not None and dupes_df_loc is None:
#    dupes_df = dupes_df_tag
#elif dupes_df_loc is not None and dupes_df_tag is None:
#    dupes_df = dupes_df_loc
#elif dupes_df_loc is not None and dupes_df_tag is not None:
#    dupes_df = pandas.concat( (dupes_df_tag,dupes_df_loc),ignore_index=True ).drop_duplicates()
#else:
#    dupes_df = None
#==============================

#==============================

if dupes_df is not None:
#===========================================
#   GROUP BY TAG/LOCATION AND MAKE CORRECTIONS
    gb_dupes  = dupes_df.groupby([loc_col])

#--------------------------------------
#   A correct grouping will only have
#   one record in gb_dupe.groups
#   (one tag at one x,y for wach census)
    #group_sizes = gb_dupes.size().reset_index(name='group_size') # makes loc_col and tag into columns so we can re-index later
    
    #correctly_grouped      = group_sizes.loc[ group_sizes.group_size == 1]
    #correctly_grouped_inds = correctly_grouped[[loc_col, 'tag']].values
    #correctly_grouped_inds = map( tuple, correctly_grouped_inds )
    #for group_index in correctly_grouped_inds:
    #    group   = gb_dupes.get_group( group_index )
    #    new_loc = group.tag.astype(int).astype(str) + group[loc_col]
    #    index   = map(tuple, group[['level_0','level_1']].values )
    #    dfs_j.ix[index,loc_col] = new_loc.values
#--------------------------------------

#-----------------------------------
#   Otherwise, there is ambiguity
#   which can only be solved by user
#   investigation of the data
    #wrongly_grouped      = group_sizes.loc[ group_sizes.group_size > 1]
    #wrongly_grouped_inds = wrongly_grouped[[loc_col, 'tag']].values
    #wrongly_grouped_inds = map( tuple, wrongly_grouped_inds )
    
    #inds_wrong = []
    #for group_index in wrongly_grouped_inds:
    #    dupe_df_inds = gb_dupes.groups[ group_index ]
    #    inds_wrong += dupe_df_inds
    #inds_wrong = list(set(inds_wrong))

    #dupes_df = dupes_df.ix[inds_wrong, [l for l in list(dupes_df) if not l.startswith('dbh_')] ]
    #dupes_df.reset_index(drop=True,inplace=True)
#   ...END...
#-----------------------------------

#===============================================================
#   The GUI part #
#-----------
#   Initialize
    root         = tk.Tk()
    root.title('Select rows that corrspond to the same tree')
    editor_frame = Editor(root, dupes_df,edit_cols=['tag','sp','gx','gy','CensusID',loc_col,'dbh', 'RawStatus'] )
    data_lb      = editor_frame.lb
    row_map      = editor_frame.rowmap
    errmsg       = editor_frame.errmsg
    group_colors = itertools.cycle( 'gray%d'%x for x in xrange( 60,70) )
#-----------

#----------------------
#   Some global variables
    grouped_items   = []
    group_names     = dfs_j[loc_col].tolist()
    new_loc_counter = 0
#----------------------

#----------------------
#   BUTTON: Seclect group
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
            index     = group.index.values #map(tuple, group[['level_0','level_1']].values )
            dfs_j.ix[index,loc_col] = new_loc 
            for i in items:
                data_lb.itemconfig(i, {'bg':'black','fg':'white'} ) #group_colors.next()})
                data_lb.selection_clear(i)
            grouped_items += items
        
        elif items_already_grouped:
            errmsg('please only select un-grouped items')

    group_button = tk.Button(root,text='Group selection', command=group_sel )
#----------------------

#-------------
#   BUTTON: Done
    def group_done():
        global grouped_items, group_names, new_loc_counter
        
        remaining_items = [ i for i in xrange(data_lb.size()) if int(i) not in grouped_items ]
        remaining_rows = [ row_map[i] for i in remaining_items]
        for row in remaining_rows:
        #   OPTION TO GROUP REMAINING
            #new_loc = str(new_loc_counter) # give it a unique group
            #while new_loc in group_names: # if group exists, iterate
            #    new_loc_counter += 1
            #    new_loc = str(new_loc_counter)
            #group_names.append( new_loc)
            #group   = dupes_df.ix[ row, ]
            #index   = map(tuple, group[['level_0','level_1']].values )
            #dfs_j.ix[index, loc_col ] = new_loc
            
            group   = dupes_df.ix[ [row], ]
            index   = group.index.values #map(tuple, group[['level_0','level_1']].values )
            dfs_j.drop(index, inplace=True)
             
        root.destroy()

    done_button  = tk.Button(root,text='Done grouping', command=group_done)
#-------------

#-----
#   Pack
    editor_frame.pack()
    group_button.pack()
    done_button.pack()
#-----

    root.mainloop()
#   ...END...

#=====================
# BEGIN ERROR CHECKING
#--------------------
# Assigin the tree ID
treeID_map = { loc:i for i,loc in enumerate(pandas.unique(dfs_j[loc_col])) }
treeID     = [ treeID_map[l] for l in dfs_j[loc_col] ]
dfs_j.ix[:,'treeID'] = treeID
#--------------------

# rename dbh main stem col
dfs_j.rename( columns={'dbh':'dbh_0'}, inplace=True)


#--------------------
# NOSTEMS corrections
dbh_cols = ['dbh_%d'%x for x in xrange(max_stems)] # colums corresponding to the dbh values
dfs_j    = dfs_j.ix[:, [c for c in list(dfs_j) if c not in dbh_cols] + dbh_cols] # rearrange the column order for cleanliness

# map certain dbh flag-values to nan
dbh_na_map = {0:np.nan, -1:np.nan, -999:np.nan}
dfs_j.replace(to_replace={c:dbh_na_map for c in dbh_cols}, inplace=True)

# sort the dbh vals so no vals are at the end 
dfs_j.ix[:,['dbh_%d'%x for x in xrange(1,max_stems)]] = np.sort( dfs_j.ix[:,['dbh_%d'%x for x in xrange(1,max_stems)]].values, axis=1)

# number of recorded stems dbh values VS the number recorded in the 'nostems' columns
nostems_actual   = dfs_j.ix[:,dbh_cols].notnull().sum(axis=1)
nostems_err_inds = np.where( nostems_actual != dfs_j.nostems )[0]
if nostems_err_inds.size:
    subdata = dfs_j.iloc[nostems_err_inds].sortlevel(0)
    if writer:
        subdata.to_excel( writer, 'nostem_mistakes', float_format='%.2f' , na_rep='NA') 
    dfs_j.update(nostems_actual.iloc[nostems_err_inds].to_frame('nostems') )
#--------------------

#---------------
# X,Y duplicates
dfs_j_flat     = dfs_j.reset_index() # flatten so we can groupby levels easier
xy_groups      = dfs_j_flat.groupby(['level_0','gx','gy'])
xy_dupe_inds   = [inds for group,inds in xy_groups.groups.iteritems() if len(inds) > 1 ]
if xy_dupe_inds:
    xy_dupe_inds   = [i for sublist in xy_dupe_inds for i in sublist] # 2d to 1d
#   re-index multi_index
    index          = map(tuple, dfs_j_flat.ix[xy_dupe_inds,['level_0','level_1']].values )
    subdata     = dfs_j.ix[index,].sortlevel(0)
    if writer:
        subdata.to_excel( writer, 'xy_duplicates', float_format='%.2f' , na_rep='NA') 
#---------------

#---------------
# TAG duplicates
tag_groups      = dfs_j_flat.groupby(['level_0','tag'])
tag_dupe_inds   = [inds for group,inds in tag_groups.groups.iteritems() if len(inds) > 1 ]
if tag_dupe_inds:
    tag_dupe_inds   = [i for sublist in tag_dupe_inds for i in sublist] # 2d to 1d
#   re-index multi_index
    index          = map(tuple, dfs_j_flat.ix[tag_dupe_inds,['level_0','level_1']].values )
    subdata     = dfs_j.ix[index,].sortlevel(0)
    if writer:
        subdata.to_excel( writer, 'tag_duplicates', float_format='%.2f' , na_rep='NA') 
#---------------

# GROUP BY TREE_ID TO CHECK FOR CHANGES
id_groups       = dfs_j.groupby( ['treeID'] )

#----------------------------------------------------
# TAGs that change (will not alter these in the data)
tags_per_treeID = id_groups['tag'].unique()
tags_changed    = [ treeID for treeID,tags in tags_per_treeID.iteritems() if len(tags) > 1 ]
if tags_changed:
    subdata = pandas.concat([ id_groups.get_group(treeID) for treeID in tags_changed], keys=tags_changed )
    if writer:
        subdata.to_excel( writer, 'tags_changed', float_format='%.2f' , na_rep='NA') 
#-------------------------------------------------------

#--------------------------------------------------
# SPECIES that change (will alter these in the data
sp_per_treeID = id_groups['sp'].unique()
sp_changed    = [ treeID for treeID,sp_vals in sp_per_treeID.iteritems() if len(sp_vals) > 1 ]
if sp_changed:
    subdata = pandas.concat([ id_groups.get_group(treeID) for treeID in sp_changed], keys=sp_changed )
    if writer:
        subdata.to_excel( writer, 'sp_changed', float_format='%.2f' , na_rep='NA') 
#   adjust the species in the earlier censuses
    for treeID in sp_changed:
        group      = id_groups.get_group(treeID)
        recent_sp  = group.ix[ np.argmax(group.CensusID), 'sp']
        dfs_j.ix[group.index.tolist(),'sp' ] = recent_sp

previous  = [i for i in group.index if i != np.argmax(group.CensusID) ]


#--------------------------------------------------
#=====================

#==========================
# BEGIN STACKING THE LEVELS 
# sigh

# all census IDs
allcensuses       = np.unique( dfs_j.CensusID)
nostem_per_treeID = id_groups['nostems'].unique()
census_per_treeID = id_groups['CensusID'].unique()

myvals          = ['gx','gy','x','y','subquad','quadrat','sp','treeID', 'tag']
id_groups_myvals = dfs_j[myvals].reset_index(drop=True).groupby( ['treeID'] )

records = [] # prior and missing etc
for tree in np.unique(dfs_j.treeID):
    group     = id_groups_myvals.get_group(tree) # slow part, but I cannot speed it up
    vals      = group.iloc[0].to_dict() # another slow part...
    
    censuses  = census_per_treeID[tree]
    where_new = censuses.min() 
    new_items = [ (key,vals[key]) for key in myvals ]

    new_censuses = np.setdiff1d( allcensuses, censuses) 
    prior        = new_censuses[ new_censuses < where_new] 
    missing      = new_censuses[ new_censuses > where_new] 

    for c in prior:
        records.append(dict(new_items+[('CensusID',c),('RawStatus', 'prior')]) )
    for c in missing:
        records.append(dict(new_items+[('CensusID',c),('RawStatus', 'missing')]) )

new_data    = pandas.DataFrame.from_records(records)
data        = pandas.concat((dfs_j, new_data),ignore_index=True)
data.loc[ data.RawStatus=='missing',['DFstatus','status'] ] = 'missing','M'
data.loc[ data.RawStatus=='prior',  ['DFstatus','status'] ] = 'prior','P'
nostems_max = data.groupby('treeID')['nostems'].max()

# ~ MELT ~
melted_data = []
id_vars     = [c for c in list(subdata) if c not in dbh_cols] 
for n in np.unique(nostems_max).astype(int):
    trees   = nostems_max.loc[ nostems_max==n].index.values
    subdata = data[ data['treeID'].isin(trees) ]
    melted  = pandas.melt( subdata, value_vars=dbh_cols[:n] , 
                            var_name='mstem', value_name='dbh', id_vars=id_vars)
    melted_data.append(melted)

tidy_data               = pandas.concat( melted_data, ignore_index=True)
tidy_data.ix[:,'mstem'] = tidy_data.ix[:,'mstem'].map( lambda x:x.split('_')[-1] )
tidy_data               = tidy_data.sort_index(by=['treeID','CensusID'])

#tidy_data.to_pickle('%s_stacked.pkl'%plot_name)
#tidy_data.to_csv('%s_stacked.txt'%plot_name, sep='\t', na_rep='NA', float_format='%.2f')

if writer:
    writer.save()

# MAKE SUPER BEAUTIFUL XLSX DATA VIEWER
beautiful_data = tidy_data.groupby(('treeID','CensusID','mstem')).first()
#beautiful_data.to_excel( '%s_beauty.xlsx'%plot_name, na_rep='NA', float_format='%.2f')

