import os

import pymysql
import pandas
from pylab import *

cur_dir = os.getcwd()
os.chdir('/Users/mender/HIPPNET/') 
import helper 
os.chdir( cur_dir )


def standardizeHIPPNET( plot_name, census_num, more_mstems_in, dump_file_dir = '/Users/mender/HIPPNET' ):

#########################
# HIPPNET DATABASE INFO #
#########################
# ~~~ plot/census specific parameters
    #datfile              = os.path.join(datdir, '%s_%d.txt'%(plot_name, census_num) )
    
    mysql_data  = {  'Palamanui':
                                { 1: {'table':'pn_tree_data',           'db':'Palamanui'},
                                  5: {'table':'pn_5_year_resurvey_v02', 'db':'Palamanui'}},
                    'Laupahoehoe':
                                {1:{'table': 'lau_tree_data',          'db': 'Laupahoehoe'}, 
                                 5:{'table': 'lau_5_year_resurvey_v02', 'db': 'Laupahoehoe'}}   }
    
    mysql_database       = mysql_data[plot_name][census_num]['db']
    mysql_table          = mysql_data[plot_name][census_num]['table']
    #outfile_xls          = os.path.join(datdir, '%s_intermediate_%d.xls'%(plot_name, census_num) )
    #outfile_txt          = os.path.join(datdir, '%s_intermediate_%d.txt'%(plot_name, census_num) )
    census_x0000         = { 'Palamanui': 185950.006 , 'Laupahoehoe': 260420.001  }  [ plot_name ]
    census_y0000         = { 'Palamanui': 2185419.984 ,'Laupahoehoe': 2205378.002  } [ plot_name ]
    more_mstems_table    = { 'Palamanui':'pn_toomanystems', 'Laupahoehoe': 'lau_toomanystems'}[  plot_name ]
    if census_num ==1 :
        recensus = False
    else:
        recensus = True
# ~~~~~~~ CTFS standardized column names ~~~~~~~~~~~
    tree_ctfs_table = loadtxt( 
                        '/Users/mender/CTFS/CTFS_tree_column_info.txt', 
                        dtype=str,delimiter='\t',
                        comments='supercalifragilisticexpialidocious' )
    tree_col_names  = tree_ctfs_table[:,0]
    tree_col_descr  = tree_ctfs_table[:,1]

# ~~~~~~~ potential HIPPNET column names ~~~~~~~~~~~
    if recensus:
        potential_names = {'tag'  : ['re_tag'],
                        'sp'      :    ['re_species'],
                        'quadrat' : ['quad'] ,
                        'subquad' : ['subquad'] ,
                        'x'       : ['x'] ,
                        'y'       : ['y'] ,
                        'nostems' : ['re_num_of_', 're_nstems'],
                        'notes'   : ['re_notes', 're_note'],
                        'slp'     : ['re_slp', 're_s_l_p', 'r_e_s_l_p'],
                        'ExactDate': ['re_exactdate_', 're_exactdate', 're_date', 're_date_'] , 
                        'RawStatus': [ 're_status'], 
                        'dbh'     :  ['re_dbh'] , 
                        'dist_to_nail'  :['re_dtn'] , 
                        'substrate' :  ['re_subs','re_substra','re_substrate'] , 
                        'pig_damage':  ['re_pigdmg','re_pig','re_pig_damage'] , 
                        'pom'     : ['re_pom' ] }

        multi_stem_names =  ['rs_ms_%d'%x for x in xrange( 1,16)] + ['re_ms_%d'%x for x in xrange( 1,16)]
    else:
        potential_names = { 'tag'     :[ 'tag']  ,
                        'sp'      :['species'] ,
                        'quadrat' : ['quad'] ,
                        'subquad' : ['subquad'] ,
                        'x'       : ['x'] ,
                        'y'       : ['y'] ,
                        'nostems' :  ['num_of_stems' ], 
                        'notes'   : ['meas_notes', 'notes', 'notes'],
                        'slp'     : [ 'slp', 's_l_p'],
                        'ExactDate': ['exactdate_', 'exactdate', 'date', 'date_'] ,
                        'dbh'      : ['dbh'] , 
                        'dist_to_nail'      :['dtn'] , 
                        'substrate' :  ['substrate'] , 
                        'pom'      : ['pom'] }
        multi_stem_names =  ['mstem_%d'%x for x in xrange( 1,16)  ]


# ~~~~ read HIPPNET TSV file into pandas ~~~~~~~
    #hippnet_data       = pandas.read_table( datfile, na_values=( 'NaN', 'NA', 'None', None, 'NULL' ) )
    datatype, hippnet_data        = helper.mysql_to_dataframe( mysql_database, mysql_table   )
    hippnet_data.rename(columns = lambda x:x.lower(), inplace=True )
    hippnet_col_names  = list(hippnet_data)
    hippnet_num_rows   = len( hippnet_data )

# ~~~~~~~ now we will match HIPPNET columns w CTFS standard names ~~~~~~~~~
    matched_cols = {}
    for ctfs_name, names in potential_names.items():
        matched_name = [n for n in names if n in hippnet_col_names ]
        
        if not matched_name:
            print '%s ctfs columns not matched in [%s]'%(ctfs_name,','.join( names ) ) 
            matched_cols[ ctfs_name ] = "*missing*"
            continue
        
        matched_name = matched_name[0]
        if matched_name == ctfs_name:
            continue
        
        elif matched_name != ctfs_name and ctfs_name not in hippnet_col_names:
            matched_cols[ matched_name ] = ctfs_name
        
        elif matched_name != ctfs_name and ctfs_name in hippnet_col_names:
            matched_cols[ matched_name ] = ctfs_name
            hippnet_data.drop( ctfs_name, axis=1, inplace=True)

    hippnet_col_names  = list(hippnet_data)
    hippnet_data.rename(columns=matched_cols, inplace=True) 

###########################
# PROCESS AND ADD COLUMNS #
###########################

# ~~~~ SPECIES ~~~
    hippnet_data['sp'] = hippnet_data['sp'].map( lambda x:x.upper() )
    hippnet_data.loc[ hippnet_data['sp'] == 'COPSP', 'sp'] = 'COPRHY'

# ~~~~ DATE ~~~
    datetime_stamp =  pandas.DatetimeIndex( hippnet_data ['ExactDate'] )
    hippnet_data ['ExactDate'] = datetime_stamp
    hippnet_data ['date']      = datetime_stamp.to_julian_date()

# ~~~ GPS ~~~~
    hippnet_data ['gx']       = np.round(hippnet_data['x'] - census_x0000, decimals=3)
    hippnet_data ['gy']       = np.round(hippnet_data['y'] - census_y0000, decimals=3)

# ~~~ NULL columns which are required for CTFS formatting but dont apply to HIPPNET data 
    hippnet_data ['StemTag']  = np.nan
    hippnet_data ['stemID']   = np.nan
    hippnet_data ['codes']    = np.nan
    hippnet_data ['agb']      = np.nan

# ~~~ CENSUS ID label ~~~
    hippnet_data ['CensusID'] = census_num 

# ~~~~~~ tree STATUS
    if not recensus:
        hippnet_data['RawStatus'] = 'alive'    
    
    hippnet_data['RawStatus'] = hippnet_data['RawStatus'].map( lambda x:str(x.strip().lower()) )
    
    RawStatus_map = {  'yes' : 'alive'} 

    hippnet_data.replace( to_replace={'RawStatus': RawStatus_map} , inplace=True )

    hippnet_data['DFstatus'] = hippnet_data['RawStatus']
    DFstatus_map = {  'new main stem'    : 'alive', 
                      'new'              : 'alive', 
                      'not found'        : 'missing', 
                      'broken not found' : 'gone' }
    hippnet_data.replace( to_replace={'DFstatus': DFstatus_map} , inplace=True )
    hippnet_data['status']   = hippnet_data['DFstatus'].map(lambda x:x.upper()[0])

# ~~~~ POINT OF MEASUREMENT related ~~~~~
    hippnet_data[ 'hom'] = hippnet_data[ 'pom'].map(lambda x:'%.2f'%x)


##################
# MULTIPLE STEMS #
##################
    matched_names  = [name for name in multi_stem_names if name in list(hippnet_data)] 
    map_nan        = { 0:np.nan }
    hippnet_data.replace( to_replace= {name:map_nan for name in matched_names} , inplace=True )
    map_names      = {name:'dbh_%d'%(index+1) for index,name in enumerate(matched_names) }
    nom_mstem_cols = len(map_names)
    hippnet_data.rename(columns=map_names, inplace=True)

# ~~~ check for additional multi stems in oher data bases or in the notes
    if more_mstems_in == 'table':
        hippnet_data = helper.addStemsFromTable( hippnet_data, 
                                              db_name=plot_name, 
                                              table_name=more_mstems_table , 
                                              multi_stem_col_expression='mstem')

    elif more_mstems_in == 'notes':
        hippnet_data = helper.addStemsFromNotes(hippnet_data)

# ~ sort the mstems columns
    mstem_cols = [ col_name for col_name in list(hippnet_data) if col_name.startswith('dbh_') ]
    hippnet_data[ mstem_cols] = pandas.np.sort( hippnet_data[ mstem_cols ].values.astype(float) ,axis=1)


######################
# SPECIFY SOME TYPES #
######################
    newtypes = { 'sp':str,
                'tag':int,
                'notes':str,
                'slp':str,
                'dbh':float,
                'gx': float,
                'gy': float,
                'hom': float,
                'pom':str}
    for col,t in newtypes.iteritems():
        to_convert = hippnet_data[col].notnull()
        hippnet_data.ix[ to_convert, col] = hippnet_data.ix[to_convert,col ].astype(t) 

    output_cols = [ col for col in tree_col_names if col in list(hippnet_data) ] + mstem_cols + [ 'subquad','RawStatus', 'slp', 'x', 'y', 'notes', 'pig_damage', 'substrate', 'dist_to_nail' ]
    print [ x for x in output_cols if x not in list(hippnet_data ) ] 
    return hippnet_data.loc[:, output_cols]


data_info = [[ 'Palamanui',   1, 'table'], 
             [ 'Palamanui',   5, 'notes'],
             [ 'Laupahoehoe', 1, 'table'],
             [ 'Laupahoehoe', 5, 'notes'] ]

data_dump  = { '%s_%d'%(plot_name, census_num):standardizeHIPPNET(plot_name, census_num, xtra_mstems ) for plot_name,census_num, xtra_mstems in data_info }

for name,data in data_dump.iteritems():
    data.to_pickle(name+'.pkl')


