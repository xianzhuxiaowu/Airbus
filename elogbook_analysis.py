import math
import pandas as pd
import matplotlib.pyplot as plt
import os as os
from datetime import datetime
import plotly.express as px
import pandas as pd
import re
import textwrap


"""
eLogbook

single file analysis
Split into Macro- und Microactivities including length calculation 

"""

filepath = r"C:\Users\jsiegber\Capgemini\AHD_Flightline_Transformation - General\40 Steering & internal\05_Data_calculations\H225\00 eLogbook extracts"
filename = "logbook-3137.xls"

folder_name = "{0}".format(filename)

if not os.path.exists(folder_name):
    os.mkdir(folder_name)
    
macro_excel = '{0}_Macroactivites.xlsx'.format(filename)
macro_excel = os.path.join(folder_name, macro_excel)
micro_excel = '{0}_Microactivites.xlsx'.format(filename)
micro_excel = os.path.join(folder_name, micro_excel)

gant_chart = "{0}_Gantt.png".format(filename)
gant_chart = os.path.join(folder_name, gant_chart)


def create_df(filename, sheetname, header):   
    name = filename    
    name = "{0}".format(name)
    path = filepath
    xslx_data = os.path.join(path, name)
    df = pd.read_excel(xslx_data, sheetname,header = header)
    df.columns = df.columns.map(str)
    return df

def time_difference(timestamp1, timestamp2):
    # Convert the timestamps to datetime objects
    date1 = datetime.strptime(timestamp1, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.strptime(timestamp2, '%Y-%m-%d %H:%M:%S') 
    
    # # Calculate the difference between the two dates
    diff = date2 - date1
    
    return (diff.total_seconds() / 3600,str(diff))

filename = os.path.join(filepath, filename)
xx = pd.read_excel(filename)
if xx.columns[0] == "Filtre":

    elogbook = create_df(filename,"Observations - Anomalies",1)
    
    elogbook = elogbook.applymap(lambda x: re.sub(r'(\s)\n', r'\1', x) if isinstance(x, str) else x)
    elogbook = elogbook.applymap(lambda x: re.sub(r'\n(\s)', r' \1', x) if isinstance(x, str) else x)
    elogbook = elogbook.replace(r'\r\n|\r|\n', ' ', regex=True)
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].str.rstrip()
    
    "match the keyactivities"       
    
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 02 POINT FIXE AVANT 1ER VOL PFA', 'POSTE 02 PFA (Point Fixe Avant 1er vol)')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 02 TRAVAUX SYSTEMATIQUES après 1er point fixe', 'POSTE 02 TRAVAUX SYSTEMATIQUES APRES 1er POINT FIXE')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 02 VAV (VISITE AVANT VOL)', 'POSTE 02 VAV (Visite avant vol)')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 03 VOL T1','POSTE 03 VOL T1 (K1)')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 06 MAINTENACE VAL', 'POSTE 06 MAINTENANCE VAL')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 06 VAH', 'POSTE 06 VAH (Visite Avant Habillage)')
    elogbook["Travail à faire - Décision"] = elogbook["Travail à faire - Décision"].replace('POSTE 09 Présentation machine services officiels / TRANSFERT LH', 'POSTE 09 PRESENTATION MACHINE SERVICES OFFICIELS / TRANSFERT LH')
            
    ""
    
    elogbook['Date'] = pd.to_datetime(elogbook['Date'])
    elogbook['Date'] = elogbook['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    elogbook['Fait (Date)'] = pd.to_datetime(elogbook['Fait (Date)'])
    elogbook['Fait (Date)'] = elogbook['Fait (Date)'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    elogbook['Unnamed: 15'] = pd.to_datetime(elogbook['Unnamed: 15'])
    elogbook['Unnamed: 15'] = elogbook['Unnamed: 15'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    
    is_nan = elogbook[['Date', 'Auteur','N° de tampon','Réponse','Date.1','Auteur.1','N° de tampon.1']].isna().all(axis=1)
    
    df_filtered = elogbook[is_nan]
    
    macros = df_filtered["Travail à faire - Décision"].tolist()
    index_list = df_filtered.index.tolist()
    
    columnnames = ["Macroactivity","Minoractivity", "length_calc_hours", "length_calc_days", "Start", "End"]
    length_df_minor = pd.DataFrame(columns = columnnames)
    
            
    dic = {}
    o = 0
    m = 0
    for j in index_list:
        if o+1 < len(index_list):
            i = "{0}".format(macros[o])
            dic[i] = {}
            dic[i][j] = elogbook.iloc[index_list[o]+1:index_list[o+1]]
            o += 1
            
        else:
            i = "{0}".format(macros[o])
            dic[i] = {}
            dic[i][j] = elogbook.iloc[index_list[o]+1:]        
    
    
    for outer_key, inner_dict in dic.items():
        for inner_key, dic[outer_key][inner_key] in inner_dict.items():
            for index, row in dic[outer_key][inner_key].iterrows():
    
                start = str(row['Date'])
                end = str(row['Unnamed: 15'])
                name = str(row["Travail à faire - Décision"])
                response = str(row["Réponse"])
                if start == "nan" or end == "nan":
                    pass
                else:
                    length_calc = time_difference(start,end)
                    length_df_small = pd.DataFrame({
                        "Macroactivity": [outer_key],
                        "Minoractivity": [name],
                        "Answer": [response],
                        "length_calc_hours": [length_calc[0]],
                        "length_calc_days": [length_calc[1]],
                        "Start": [start],
                        "End": [end]
                        })
                    
                    length_df_minor = pd.concat([length_df_minor, length_df_small])         
            
    
    
    
    columnnames = ["Macroactivity", "length_calc_hours", "length_calc_days","Start", "End"]
    length_df = pd.DataFrame(columns = columnnames)
    
    
    for index, row in df_filtered.iterrows():
    
        start = str(row['Fait (Date)'])
        end = str(row['Unnamed: 15'])
        name = str(row["Travail à faire - Décision"])
        if start == "nan" or end == "nan":
            pass
        else:
            length_calc = time_difference(start,end)
            length_df_small = pd.DataFrame({
                "Macroactivity": [name],
                "length_calc_hours": [length_calc[0]],
                "length_calc_days": [length_calc[1]],
                "Start": [start],
                "End": [end]
                })
        
            length_df = pd.concat([length_df, length_df_small])  
        
        
    length_df.to_excel(macro_excel, index=False)
    length_df_minor.to_excel(micro_excel, index=False)    

elif xx.columns[0] == "Filter":
    elogbook = create_df(filename,"Discrepancies",1)
    
    elogbook = elogbook.applymap(lambda x: re.sub(r'(\s)\n', r'\1', x) if isinstance(x, str) else x)
    elogbook = elogbook.applymap(lambda x: re.sub(r'\n(\s)', r' \1', x) if isinstance(x, str) else x)
    elogbook = elogbook.replace(r'\r\n|\r|\n', ' ', regex=True)
    elogbook["To be done"] = elogbook["To be done"].str.rstrip()
    
    "match the keyactivities"       
    
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 02 POINT FIXE AVANT 1ER VOL PFA', 'POSTE 02 PFA (Point Fixe Avant 1er vol)')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 02 TRAVAUX SYSTEMATIQUES après 1er point fixe', 'POSTE 02 TRAVAUX SYSTEMATIQUES APRES 1er POINT FIXE')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 02 VAV (VISITE AVANT VOL)', 'POSTE 02 VAV (Visite avant vol)')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 03 VOL T1','POSTE 03 VOL T1 (K1)')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 06 MAINTENACE VAL', 'POSTE 06 MAINTENANCE VAL')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 06 VAH', 'POSTE 06 VAH (Visite Avant Habillage)')
    elogbook["To be done"] = elogbook["To be done"].replace('POSTE 09 Présentation machine services officiels / TRANSFERT LH', 'POSTE 09 PRESENTATION MACHINE SERVICES OFFICIELS / TRANSFERT LH')
            
    ""
    
    elogbook['Date'] = pd.to_datetime(elogbook['Date'])
    elogbook['Date'] = elogbook['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    elogbook['Done (Date)'] = pd.to_datetime(elogbook['Done (Date)'])
    elogbook['Done (Date)'] = elogbook['Done (Date)'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    elogbook['Unnamed: 15'] = pd.to_datetime(elogbook['Unnamed: 15'])
    elogbook['Unnamed: 15'] = elogbook['Unnamed: 15'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    
    is_nan = elogbook[['Date', 'Author','Stamp-ID','Answer','Date.1','Author.1','Stamp-ID.1']].isna().all(axis=1)
    df_filtered = elogbook[is_nan]
    
    macros = df_filtered["To be done"].tolist()
    index_list = df_filtered.index.tolist()
    
    columnnames = ["Macroactivity","Minoractivity", "length_calc_hours", "length_calc_days", "Start", "End"]
    length_df_minor = pd.DataFrame(columns = columnnames)
    
            
    dic = {}
    o = 0
    m = 0
    for j in index_list:
        if o+1 < len(index_list):
            i = "{0}".format(macros[o])
            dic[i] = {}
            dic[i][j] = elogbook.iloc[index_list[o]+1:index_list[o+1]]
            o += 1
            
        else:
            i = "{0}".format(macros[o])
            dic[i] = {}
            dic[i][j] = elogbook.iloc[index_list[o]+1:]        
    
    
    for outer_key, inner_dict in dic.items():
        for inner_key, dic[outer_key][inner_key] in inner_dict.items():
            for index, row in dic[outer_key][inner_key].iterrows():
    
                start = str(row['Date'])
                end = str(row['Unnamed: 15'])
                name = str(row["To be done"])
                response = str(row["Answer"])
                if start == "nan" or end == "nan":
                    pass
                else:
                    length_calc = time_difference(start,end)
                    length_df_small = pd.DataFrame({
                        "Macroactivity": [outer_key],
                        "Minoractivity": [name],
                        "Answer": [response],
                        "length_calc_hours": [length_calc[0]],
                        "length_calc_days": [length_calc[1]],
                        "Start": [start],
                        "End": [end]
                        })
                    
                    length_df_minor = pd.concat([length_df_minor, length_df_small])         
            
    
    
    
    columnnames = ["Macroactivity", "length_calc_hours", "length_calc_days","Start", "End"]
    length_df = pd.DataFrame(columns = columnnames)
    
    
    for index, row in df_filtered.iterrows():
    
        start = str(row['Done (Date)'])
        end = str(row['Unnamed: 15'])
        name = str(row["To be done"])
        if start == "nan" or end == "nan":
            pass
        else:
            length_calc = time_difference(start,end)
            length_df_small = pd.DataFrame({
                "Macroactivity": [name],
                "length_calc_hours": [length_calc[0]],
                "length_calc_days": [length_calc[1]],
                "Start": [start],
                "End": [end]
                })
        
            length_df = pd.concat([length_df, length_df_small])  
        
        
    length_df.to_excel(macro_excel, index=False)
    length_df_minor.to_excel(micro_excel, index=False)   





POSTE_df = length_df[length_df['Macroactivity'].str.startswith('POSTE')]
POSTE_df = POSTE_df.reset_index(drop=True)

poste_activs = POSTE_df['Macroactivity'].tolist()

POSTE_df['Start'] = pd.to_datetime(POSTE_df['Start'])
POSTE_df['End'] = pd.to_datetime(POSTE_df['End'])

POSTE_df['Duration'] = (POSTE_df['End'] - POSTE_df['Start']).dt.days / 7


'GANTT charts'
fig = px.timeline(POSTE_df, x_start='Start', x_end='End', y='Macroactivity')
fig.update_layout(
    width=1800,  # set the width to 1800 pixels
    height=600,  # set the height to 600 pixels
    margin=dict(l=50, r=50, t=50, b=50),  # set the margins
    annotations=[
        dict(
            x=row['End'], 
            y=row['Macroactivity'], 
            xref='x', 
            yref='y', 
            text='{:.1f} weeks ({:d} days)'.format(row['Duration'], int(row['Duration']*7)), 
            showarrow=False, 
            font=dict(size=14)
        ) for _, row in POSTE_df.iterrows()
    ],
    title={
       'text': "{0}".format(filename),  # set the title text
       'y': 0.98,  # set the y position of the title
       'x': 0.5,  # set the x position of the title
       'xanchor': 'center',  # set the x anchor of the title
       'yanchor': 'top'  # set the y anchor of the title
   }
)

fig.update_xaxes(
    type='date',
    tickformat='Start of %CW%V'
)

fig.write_image(gant_chart, scale=2)


POSTE_df_minor = length_df_minor[length_df_minor['Macroactivity'].str.startswith('POSTE')]
POSTE_df_minor = POSTE_df_minor.reset_index(drop=True)

POSTE_df_minor['Start'] = pd.to_datetime(POSTE_df_minor['Start'])
POSTE_df_minor['End'] = pd.to_datetime(POSTE_df_minor['End'])

POSTE_df_minor['Duration'] = (POSTE_df_minor['End'] - POSTE_df_minor['Start']).dt.days / 7

for i in poste_activs:
    small_gantt_df = POSTE_df_minor[POSTE_df_minor['Macroactivity'] == i]
    small_gantt_df.loc[:, 'Minoractivity'] = small_gantt_df['Minoractivity'].str.slice(stop=100).copy()
    

    'GANTT charts'
    fig = px.timeline(small_gantt_df, x_start='Start', x_end='End', y='Minoractivity')
    fig.update_layout(
        width=1800,  # set the width to 1800 pixels
        height=600,  # set the height to 600 pixels
        margin=dict(l=50, r=50, t=50, b=50),  # set the margins
        annotations=[
            dict(
                x=row['End'], 
                y=row['Minoractivity'], 
                xref='x', 
                yref='y', 
                text= row['length_calc_days'],
                showarrow=False, 
                font=dict(size=14)
            ) for _, row in small_gantt_df.iterrows()
        ],
    title={
           'text': "{0}".format(i),  # set the title text
           'y': 0.98,  # set the y position of the title
           'x': 0.5,  # set the x position of the title
           'xanchor': 'center',  # set the x anchor of the title
           'yanchor': 'top'  # set the y anchor of the title
       }
    )
    
    fig.update_xaxes(
        type='date',
        tickformat='Start of %CW%V'
    )
    a = i.split("/")
    a = a[0]  # concatenate the first two elements
    micro_gantt = "{0}_Gantt_minor.png".format(a)
    micro_gantt = os.path.join(folder_name, micro_gantt)
    fig.write_image(micro_gantt, scale=2)





    
    
    
