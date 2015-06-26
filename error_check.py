import sys

from pylab import *
import pandas

plot_name = sys.argv[1] # 'Laupahoehoe'
censuses =  [1,5]

types = { 'tag':np.int, 'sp':str, 'gx': str, 'gy':str, 'dbh':str, 'notes':str, 'DFstatus':str  }

data1 = pandas.read_pickle( '%s_%d.pkl'%(plot_name,censuses[0]) ) 
data5 = pandas.read_pickle( '%s_%d.pkl'%(plot_name,censuses[1]) ) 

#######################
# MAKE USEFULE LABELS #
#######################

data1['label_sp_xy'] = data1['sp'].astype(str) + data1['gx'].astype(str) + data1['gy'].astype(str)
data5['label_sp_xy'] = data5['sp'].astype(str) + data5['gx'].astype(str) + data5['gy'].astype(str)

data1['label_tag'] = data1['tag']
data5['label_tag'] = data5['tag']

data1['label_xy'] = data1['gx'].astype(str) + data1['gy'].astype(str)
data5['label_xy'] = data5['gx'].astype(str) + data5['gy'].astype(str)

data1['label_tag_xy'] = data1['tag'].astype(int).astype(str) + data1['gx'].astype(str) + data1['gy'].astype(str)
data5['label_tag_xy'] = data5['tag'].astype(int).astype(str) + data5['gx'].astype(str) + data5['gy'].astype(str)

##################
# ERROR CHECKING #
##################

suffixes    = ('_census%d'%censuses[0], '_census%d'%censuses[1])

dbh_name_map1 = { x:x+suffixes[0] for x in list(data1) if x.startswith('dbh_') }
dbh_name_map5 = { x:x+suffixes[1] for x in list(data5) if x.startswith('dbh_') }

data1.rename( columns=dbh_name_map1, inplace=True)
data5.rename( columns=dbh_name_map5, inplace=True)


output_cols = ['tag', 'sp', 'DFstatus', 'gx', 'gy', 'dbh' , 'notes']
names1_new  = map( lambda x: x+suffixes[0], output_cols)
names5_new  = map( lambda x: x+suffixes[1], output_cols)
output_cols = names1_new + names5_new 
csv_opts    = { 'sep':'\t' , 'float_format':'%.2f' , 'na_rep':'NA' , 'columns':output_cols, 'index':False }
excel_opts  = { 'float_format':'%.2f' , 'na_rep':'NA' , 'columns':output_cols, 'index':False }
try: 
    writer = pandas.ExcelWriter('%s_report.xls'%plot_name)
except ImportError:
    print "Please install module xlwt for excel support."

#####################################"
# MEASUREMENTS WHERE NOSTEMS IS OFF #"
#####################################"


data1.loc[:,['dbh']+dbh_name_map1.values() ] = data1.loc[ :,['dbh']+dbh_name_map1.values()].replace( to_replace=[ 0, -999, -1], value=np.nan).values 
data5.loc[:,['dbh']+dbh_name_map5.values() ] = data5.loc[ :,['dbh']+dbh_name_map5.values()].replace( to_replace=[ 0, -999, -1], value=np.nan).values 

all_dbh_1 = data1.loc[ :,['dbh']+dbh_name_map1.values() ]
all_dbh_5 = data5.loc[ :,['dbh']+dbh_name_map5.values() ] 

nostems_calc_1 = pandas.np.sum( all_dbh_1.notnull().values, axis=1)
nostems_calc_5 = pandas.np.sum( all_dbh_5.notnull().values, axis=1) 

nostems_changed_1 = where( nostems_calc_1 != data1['nostems'] )[0]
nostems_changed_5 = where( nostems_calc_5 != data5['nostems'] )[0]

subdata_1 = data1.iloc[ nostems_changed_1 ]
subdata_5 = data5.iloc[ nostems_changed_5 ]
if writer:
    subdata_1.to_excel( writer, 'nostem_mistakes'+suffixes[0], float_format='%.2f' , na_rep='NA' , index=False) 
    subdata_5.to_excel( writer, 'nostem_mistakes'+suffixes[1], float_format='%.2f' , na_rep='NA' , index=False) 

data1.loc[ nostems_changed_1 , 'nostems'] = nostems_calc_1[ nostems_changed_1 ]
data5.loc[ nostems_changed_5 , 'nostems'] = nostems_calc_5[ nostems_changed_5 ]

# ======================================================

data = pandas.merge(data1, data5, suffixes=suffixes,on='label_tag_xy', how='outer')
print "###################################"
print "# MEASUREMENTS WITH DUPLICATE X,Y #"
print "###################################"
dupe_inds1 = [ g for sublist in data.groupby('label_xy%s'%suffixes[0]).groups.values() if len(sublist) > 1 for g in sublist] 
dupe_inds5 = [ g for sublist in data.groupby('label_xy%s'%suffixes[1]).groups.values() if len(sublist) > 1 for g in sublist] 
dupe_inds_xy = unique( dupe_inds1 + dupe_inds5 )
subdata = data.loc[ dupe_inds_xy]
#subdata.to_csv( 'duplicate_xy.text', **csv_opts)
if writer:
    subdata.to_excel( writer, 'duplicate_xy', **excel_opts)
print subdata.to_string( columns=output_cols+ ['label_tag_xy'] )


# ======================================================

print "####################################"
print "# MEASUREMENTS WITH DUPLICATE TAGS #"
print "####################################"
data_onXY = pandas.merge( data1, data5, suffixes=suffixes,on='label_xy',how='outer')
dupe_tags = [key for key,val in data5.groupby('tag').groups.items() if len(val)>1]
dupe_inds = [where( data_onXY['tag_census5'] == tag)[0] for tag in dupe_tags]
dupe_inds = [ i for sublist in dupe_inds for i in sublist ]
subdata = data_onXY.iloc[dupe_inds]
#subdata.to_csv( 'duplicate_tags.text', **csv_opts)
if writer:
    subdata.to_excel( writer, 'duplicate_tags', **excel_opts)
print subdata.to_string( columns=output_cols )

# ======================================================

print "#######################################"
print "# MEASUREMENTS WITH TAGS THAT CHANGED #"
print "#######################################"
subdata = data_onXY.dropna(subset=['tag_census5','tag_census1'] ).query( 'tag_census1 != tag_census5' )
if writer:
    subdata.to_excel( writer, 'changed_tags', **excel_opts)
#subdata.to_csv( 'changed_tags.text', **csv_opts)
print subdata.to_string( columns=output_cols )

# ~~~~~~~ update tags ~~~~~~~ 
changed_tags = { new:(new,old) for new,old in zip( subdata['tag_census5'], subdata['tag_census1'] ) }

data_onXY.loc[ subdata.index, 'tag_census1' ] = data_onXY.loc[ subdata.index, 'tag_census5' ]

# ======================================================

print "##########################################"
print "# MEASUREMENTS WHERE SPECIES HAS CHANGED #"
print "##########################################"
subdata = data_onXY.dropna(subset=('tag_census1','tag_census5') ).query( 'sp_census1 != sp_census5' ) 
if writer:
    subdata.to_excel( writer, 'changed_species', **excel_opts)
#subdata.to_csv( 'species_update.text', **csv_opts)
print subdata.to_string( columns=output_cols )

# ~~~~~~~ update species ~~~~~~~ 
data_onXY.loc[ subdata.index, 'sp_census1' ] = data_onXY.loc[ subdata.index, 'sp_census5' ]

# ======================================================

####################
# COMBINE CENSUSES #
####################

# ~~~~~~ trees missing from the recensus ~~~~~~~~~~
missing = data_onXY.query( 'tag_census5 != tag_census5' ).index
# ~~~~~~ new trees recorded in the recensus ~~~~~~~~~~
prior   = data_onXY.query( 'tag_census1 != tag_census1' ).index

data_onXY.ix[ missing, 'DFstatus_census5' ] = 'missing'
data_onXY.ix[ missing, 'status_census5'   ] = 'M'
data_onXY.ix[ missing, 'RawStatus_census5'] = 'missing'
data_onXY.ix[ prior,   'DFstatus_census1' ] = 'prior'
data_onXY.ix[ prior,   'status_census1'   ] = 'P'
data_onXY.ix[ prior,   'RawStatus_census1'] = 'prior'

# ~~~ columns that will be used to make the treeID ~~~~~
cols1 = [ x+suffixes[0] for x in ['tag', 'gx', 'gy', 'x', 'y', 'nostems', 'sp','CensusID'] ]
cols5 = [ x+suffixes[1] for x in ['tag', 'gx', 'gy', 'x', 'y', 'nostems', 'sp', 'CensusID'] ]
data_onXY.loc[ missing,cols5 ] = data_onXY.loc[ missing, cols1 ].values 
data_onXY.loc[ prior, cols1 ]  = data_onXY.loc[ prior, cols5 ].values 

# ~~~~~~ unmerge the censuses and create unique tree IDs ~~~~~~~~~~~~~

data1 = data_onXY[ [n for n in list(data_onXY) if n.endswith(suffixes[0])] ].query( 'tag_census1 == tag_census1' )
data5 = data_onXY[ [n for n in list(data_onXY) if n.endswith(suffixes[1])] ].query( 'tag_census5 == tag_census5' )

data1['label_tag_xy'] = data1['tag_census1'].astype(str) + data1['gx_census1'].astype(str) + data1['gy_census1'].astype(str)
data5['label_tag_xy'] = data5['tag_census5'].astype(str) + data5['gx_census5'].astype(str) + data5['gy_census5'].astype(str)

# ~~~~~~ the index of this dataframe will be the treeID ~~~~~~~~~~~~~~~~~
data = pandas.merge(data1, data5, suffixes=suffixes,on='label_tag_xy', how='outer')
data['treeID'] = data.index.values

data['associated_tags' ] = data['tag%s'%suffixes[1] ].map( lambda x :'%.0f'%x )
for key,tags in changed_tags.iteritems():
    ind = where( data[ 'tag%s'%suffixes[1] ] == key)[0]
    data.ix[ ind, 'associated_tags' ] = ' '.join( map(lambda x:'%.0f'%x, tags ) ) 

data.to_pickle( '%s_report.pkl'%plot_name )

########
# SAVE #
########
if writer:
    data.to_excel( excel_writer=writer,sheet_name='census_data',float_format='%.2f', na_rep='NA', index=False )
    writer.save()


