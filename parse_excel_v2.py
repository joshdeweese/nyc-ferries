#%%

import openpyxl
import pandas as pd
from itertools import accumulate
import os
import datetime



#%%

path = 'data/Ridership Data Files'

main_df_list = []
for file in [file for file in os.listdir(path) if 'xlsx' in file]:
    f = path + '/' + file
    print(f)
    wb = openpyxl.load_workbook(f, data_only=True)
    sheet_list = []
    for sheet in wb.worksheets:
        l = []
        if sheet.sheet_state == 'visible' and 'Totals' not in sheet.title:
            for row, dim in sheet.row_dimensions.items():
                if dim.hidden != True:
                    r = [cell.value for cell in sheet[row]]
                    l.append(r)
        if len(l) > 0:
            df = pd.DataFrame(l)
            df.dropna(how='all', axis=1, inplace=True)
            df = df[df.columns[:-1]]
            df.dropna(how='all', inplace=True)
            df = df[~df.iloc[:, 0].str.contains('Week', na=False)]
            first_row = df.loc[[0]]
            first_row = first_row.ffill(axis=1)

            df = df.iloc[1:]
            df = pd.concat([first_row, df])
            df.reset_index(inplace=True)

            tuple_list = zip(df.values.tolist()[0], df.values.tolist()[1])

            l = []
            for t in tuple_list:
                pair = str(t[0]) + ' : ' + str(t[1])
                l.append(pair)

            df.columns = l
            df = df.reset_index(drop=True)

            df = df.iloc[2:, 1:]

            df = df[df.iloc[:,1].notna()]
            df = df[df.columns[~df.columns.str.contains('Total')]]
            print(file)
            print(df)
            df = df.rename(columns={df.columns[0]: 'Day',
                                          df.columns[1]: 'Date'})

            df.fillna(0, inplace=True)
            df['Company'] = sheet.title

            df = df[
               df['Day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]

            df = pd.melt(df, id_vars=['Day', 'Date', 'Company'],
                           var_name='Route', value_name='Rides')

            sheet_list.append(df)

    d = pd.concat(sheet_list)
    d['Filename'] = file

    main_df_list.append(d)

final_df = pd.concat(main_df_list)
final_df.to_csv('data/final_v2.csv')

#%%
final_df.to_clipboard()




#%%


#path = 'data/Ridership Data Files'
path = 'data/test_data_files'


dl = []
for file in os.listdir(path):
    print(file)
    flist = []
    f = path + '/' + file
    sheet_list = pd.read_excel(f, sheet_name=None, header=None)
    for name, sheet in sheet_list.items():
        if 'Totals' not in name and 'Sheet' not in name and file[-4:] == 'xlsx':
            print(file, name)
            #print(sheet.iloc[:,0])
            #sheet = sheet[~sheet.iloc[:,1].isnull()]
            sheet.dropna(how='all', inplace=True)
            sheet = sheet[~sheet.iloc[:,1].str.contains('Week', na=False)]
            first_row = sheet.loc[[0]]
            first_row = first_row.ffill(axis=1)
            sheet = sheet.iloc[1:]
            sheet = pd.concat([first_row, sheet])
            sheet.reset_index(inplace=True)

            tuple_list = zip(sheet.values.tolist()[0], sheet.values.tolist()[1])

            l = []
            for t in tuple_list:
                pair = str(t[0]) + ' : ' + str(t[1])
                l.append(pair)

            sheet.columns = l
            sheet = sheet.reset_index(drop=True)

            sheet = sheet.iloc[2:, 1:]

            sheet = sheet[sheet.iloc[:,1].notna()]
            sheet = sheet[sheet.columns[~sheet.columns.str.contains('Total')]]

            sheet = sheet.rename(columns={sheet.columns[0]: 'Day',
                                          sheet.columns[1]: 'Date'})

            sheet.fillna(0, inplace=True)
            sheet['Company'] = name
            testdf = sheet
            sheet = pd.melt(sheet, id_vars=['Day', 'Date', 'Company'],
                            var_name='Route', value_name='Rides')

            sheet = sheet[sheet['Day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]

            sheet['Filename'] = file
            sheet['Rides'] = pd.to_numeric(sheet['Rides'], errors='coerce')
            sheet['Rides'].fillna(0, inplace=True)
            sheet = sheet[sheet['Rides'].astype(int) > 0]
            flist.append(sheet)

            #sheet[['Landing', 'Route']] = sheet['Route'].str.split(' : ', expand=True)
    df = pd.concat(flist)
    dl.append(df)

f = pd.concat(dl)

# = f[f['Date'].astype(str).str.len() > 6]
#f['Date'] = pd.to_datetime(f['Date'])
#f = f[f['Date'] > datetime.datetime(2010,1,1,0,0)]

f.to_csv('data/' + 'final.csv')





