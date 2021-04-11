#%%

import pandas as pd
import os
import numpy as np


#%%
path = 'data/Ridership Data Files'

dl = []
for file in os.listdir(path):
    if file[-4:] == 'xlsx':
        flist = []
        f = path + '/' + file
        sheet_list = pd.read_excel(f, sheet_name=None, header=None)
        for name, sheet in sheet_list.items():
            # Exclude Totals sheets and empty sheets
            if 'Totals' not in name and 'Sheet' not in name:
                print(file, name)

                # Remove empty rows and summary rows
                sheet.dropna(how='all', inplace=True)
                sheet = sheet[~sheet.iloc[:,1].str.contains('Week', na=False)]

                # First row has grouped titles, so fill right empty cells
                first_row = sheet.loc[[0]]
                first_row = first_row.ffill(axis=1)
                sheet = sheet.iloc[1:]
                sheet = pd.concat([first_row, sheet])
                sheet.reset_index(inplace=True)

                # Combine first and second rows for column titles
                tuple_list = zip(sheet.values.tolist()[0], sheet.values.tolist()[1])

                l = []
                for t in tuple_list:
                    pair = str(t[0]) + ' : ' + str(t[1])
                    l.append(pair)

                sheet.columns = l
                sheet = sheet.reset_index(drop=True)

                # Clean up unnecessary columns and rows
                sheet = sheet.iloc[2:, 1:]
                sheet = sheet[sheet.iloc[:,1].notna()]
                sheet = sheet[sheet.columns[~sheet.columns.str.contains('Total')]]

                sheet = sheet.rename(columns={sheet.columns[0]: 'Day',
                                              sheet.columns[1]: 'Date'})

                sheet.fillna(0, inplace=True)
                sheet['Company'] = name

                # Unpivot columns
                sheet = pd.melt(sheet, id_vars=['Day', 'Date', 'Company'],
                                var_name='Route', value_name='Rides')

                # Clean up
                sheet = sheet[sheet['Day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]
                sheet['Filename'] = file
                sheet['Rides'] = pd.to_numeric(sheet['Rides'], errors='coerce')
                sheet['Rides'].fillna(0, inplace=True)
                sheet = sheet[sheet['Rides'].astype(int) > 0]
                flist.append(sheet)

        df = pd.concat(flist)
        dl.append(df)

f = pd.concat(dl)

# Remove totals columns that didn't have "Total" in the name
f = f[~f['Route'].str.endswith('nan')]

# Split Route into Route and Landing columns
f[['S1', 'S2']] = f['Route'].str.split(' : ', expand=True)

# Some of them are backwards
f['Landing'] = np.where(f['Company'].isin(['Baseball', 'NYC Ferry']), f['S2'], f['S1'])
f['Route'] = np.where(f['Company'].isin(['Baseball', 'NYC Ferry']), f['S1'], f['S2'])

f.drop(['S1', 'S2'], axis=1, inplace=True)

f.to_csv('data/' + 'final.csv')

#%%



