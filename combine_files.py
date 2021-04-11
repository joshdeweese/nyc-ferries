#%%

from openpyxl import load_workbook
import pandas as pd
from itertools import accumulate
import os

#%%

rootdir = "data/analysis_data/test/"

df_list_summaries = []
for subdir, dirs, files in os.walk(rootdir):
    for dir in dirs:
        for subdir, dirs, files in os.walk(rootdir + dir):
            df_list_files = []
            for file in files:
                if file != 'summary.csv':
                    p = rootdir + dir + '/' + file
                    dfi = pd.read_csv(p)
                    dfi.dropna(how='all', axis=1, inplace=True)
                    dfi = dfi.drop(dfi.filter(regex='Unnamed').columns, axis=1)
                    dfi = dfi.drop(dfi.filter(regex='Total').columns, axis=1)
                    #print(file)
                    if len(dfi) > 1:
                        dfi = pd.melt(dfi, id_vars=['Date', 'Day'], var_name='Ferry', value_name='Rides')
                        dfi.dropna(inplace=True)
                        dfi = dfi[pd.to_numeric(dfi['Rides'], errors='coerce').notnull()]
                        dfi = dfi[dfi['Rides'].astype(int) > 0]
                        dfi['Company'] = dir
                        dfi['Ferry'] = dfi['Ferry'].str.replace('None','Unknown')
                        if len(dfi['Ferry']) > 0:
                            if dfi['Company'].str.contains('Baseball').any() or dfi['Company'].str.contains('NYC Ferry').any():
                                dfi[['Route', 'Landing']] = dfi['Ferry'].str.split(' : ', expand=True)
                            else:
                                dfi[['Landing', 'Route']] = dfi['Ferry'].str.split(' : ', expand=True)
                        dfi.drop(['Ferry'], axis='columns', inplace=True)
                        df_list_files.append(dfi)
            df = pd.concat(df_list_files)
            df_list_summaries.append(df)
            #df.to_csv(rootdir + '/' + f'summary_{dir}.csv')
final_df = pd.concat(df_list_summaries)
final_df = final_df[final_df['Landing'] != 'Unknown']
final_df.to_csv(rootdir + '/' + 'complete_data.csv', index=False)

#%%



#%%


