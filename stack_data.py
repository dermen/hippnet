import sys

import pandas
from pylab import *

plot_name = sys.argv[1]

census  = pandas.read_pickle( '%s_report.pkl'%plot_name)
num_trees = len( census )

treeFile = 'treeFile'
census[treeFile] = 1
col_names = list(census)
census_nums=[1,5]

nostems1 =  census[ 'nostems_census%d'%census_nums[0] ]
nostems2 =  census[ 'nostems_census%d'%census_nums[1] ]

stems_lost = where( nostems1 > nostems2 )[0]
stems_grew = where( nostems1 < nostems2 )[0]
stems_same = where( nostems1 == nostems2)[0]

#for census_num in census_nums:
suffix1   = '_census%d'%census_nums[0] 
suffix2   = '_census%d'%census_nums[1] 
dbh_names1 = [ n 
              for n in col_names 
              if n.startswith('dbh_') 
              and n.endswith(suffix1) 
              and  n != 'dbh%s'%suffix1  ]
dbh_names2 = [ n 
              for n in col_names 
              if n.startswith('dbh_') 
              and n.endswith(suffix2) 
              and  n != 'dbh%s'%suffix2  ]

# some useful names
dbh1       = 'dbh%s'%suffix1
dbh2       = 'dbh%s'%suffix2
RawStatus1 = 'RawStatus%s'%suffix1
RawStatus2 = 'RawStatus%s'%suffix2
DFstatus1  = 'DFstatus%s'%suffix1
DFstatus2  = 'DFstatus%s'%suffix2
status1    = 'status%s'%suffix1
status2    = 'status%s'%suffix2

multi_stems = []
##############
# stems lost #
##############
for n1 in dbh_names1:
    frame = census.iloc[stems_lost].query('%s==%s'%(n1,n1))
    if frame.empty:
        break
    
    frame[dbh1] = frame[n1]
    n2 = n1.replace(suffix1,suffix2)
    if n2 in col_names:
        frame[dbh2] = frame[n2]
    else:
        frame[dbh2] = np.nan 
    frame.ix[frame[ dbh2 ].isnull(), DFstatus2] = 'missing'
    frame.ix[frame[ dbh2 ].isnull(), status2] = 'M'
    frame.ix[frame[ dbh2 ].isnull(), RawStatus2] = 'missing'
    frame[treeFile] = 0
    multi_stems.append(frame)
##############
# stems grew #
##############
for n2 in dbh_names2:
    frame = census.iloc[stems_grew].query('%s==%s'%(n2,n2))
    if frame.empty:
        break
    frame[dbh2] = frame[n2]
    n1 = n2.replace(suffix2,suffix1)
    if n1 in col_names:
        frame[dbh1] = frame[n1]
    else:
        frame[dbh1] = np.nan 
    frame.ix[ frame[dbh1].isnull(), DFstatus1] = 'prior'
    frame.ix[ frame[dbh1].isnull(), status1] = 'P'
    frame.ix[ frame[dbh1].isnull(), RawStatus1] = 'prior'
    frame[treeFile] = 0
    
    multi_stems.append(frame)

##############
# stems same #
##############
for n1 in dbh_names1:
    frame = census.iloc[stems_same].query('%s==%s'%(n1,n1))
    if frame.empty:
        break
    frame['dbh%s'%suffix1] = frame[n1]
    n2 = n1.replace(suffix1,suffix2)
    frame['dbh%s'%suffix2] = frame[n2]
    frame[treeFile] = 0
    multi_stems.append(frame)

multi_stems = pandas.concat( multi_stems, ignore_index=True)

census = census.append( multi_stems, ignore_index=True)

label_columns = [ x for x in list( census) if x.startswith('label') ]
census.drop( labels= dbh_names1+dbh_names2 + label_columns,
            axis=1, inplace=True )

names1 = [ n for n in list( census) if n.endswith(suffix1) ]
names2 = [ n for n in list( census) if n.endswith(suffix2) ]

names  = [ n for n in list(census) 
             if not n.endswith(suffix1) 
            and not n.endswith(suffix2) ]

new_col_order = names + [n for sublist in zip(names1, names2) for n in sublist]

census = census[ new_col_order]

census.to_pickle('%s_master.pkl'%plot_name)
census.to_excel( '%s_master.xls'%(plot_name), index=False,na_rep='NA', float_format='%.2f' )

