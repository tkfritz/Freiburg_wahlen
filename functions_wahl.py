import numpy as np
import pandas as pd
import scipy as sp
import os
from matplotlib import pyplot as plt
import json
#import plotly.express as px
#import plotly.graph_objects as go
import geopandas 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import requests
import io
import time
import warnings
warnings.filterwarnings('ignore')

def process_geo(location='Freiburg',Jahr=2024, return_wahl_bezirke=False):
    if location=='Freiburg':
        Stadtteile = geopandas.read_file('Stadtteile_gliederung.json')
        Stadtbezirke = geopandas.read_file('Stadtbezirke_gliederung.json')
        wahl_bezirke = geopandas.read_file('Stat_bezirke_gliederung.json')
        if Jahr==2024:
            name24=['Brühl-Beurbarung','Kappel','Günterstal','Waltershofen','Opfingen',
                 'Altstadt-Mitte','Herdern-Nord','Mooswald-Ost','Waldsee','Mittelwiehre',
             'Alt-Betzenhausen','Altstadt-Ring','Unterwiehre-Nord','Neuburg','Herdern-Süd',
                     'Zähringen','Brühl-Güterbahnhof/Industriegebiet','Brühl-Güterbahnhof/Industriegebiet',
                 'Mooswald-West','Hochdorf','Betzenhausen-Bischofslinde','Littenweiler','Landwasser',
                        'Ebnet','Haslach-Egerten','Oberau','Oberwiehre','Unterwiehre-Süd',
           'Stühlinger-Eschholz','Alt-Stühlinger','Lehen','Rieselfeld','Haslach-Gartenstadt',
           'Haslach-Gartenstadt','Haslach-Haid','Weingarten','St. Georgen-Nord','St. Georgen-Süd',
            'Tiengen','Munzingen','Rieselfeld','Vauban']
        Stadtbezirke_old=Stadtbezirke.copy()
        Stadtbezirke['name24']=name24
        New_Rieselfeld = Stadtbezirke['geometry'][(Stadtbezirke.name24=='Rieselfeld')].unary_union 
        New_Gartenstadt = Stadtbezirke['geometry'][(Stadtbezirke.name24=='Haslach-Gartenstadt')].unary_union
        New_Gueterbahnhof = Stadtbezirke['geometry'][(Stadtbezirke.name24=='Brühl-Güterbahnhof/Industriegebiet')].unary_union
    Stadtbezirke.drop(labels=[17,31,33],inplace=True)
    Stadtbezirke.loc[40,'geometry']=New_Rieselfeld
    Stadtbezirke.loc[32,'geometry']=New_Gartenstadt
    Stadtbezirke.loc[16,'geometry']=New_Gueterbahnhof
    Stadtbezirke["flaeche"] = Stadtbezirke.area/10**6 # fuer km2
    Stadtbezirke["boundary"] = Stadtbezirke.boundary
    Stadtbezirke["centroid"] = Stadtbezirke.centroid
    Stadtbezirke["umfang"] = Stadtbezirke.length/10**3
    if Jahr==2024:
        Stadtbezirke.set_index('name24',inplace=True)
    Stadtteile = geopandas.read_file('Stadtteile_gliederung.json')

    Stadtteile["Flaeche"] = Stadtteile.area/10**6 # fuer km2
    Stadtteile["boundary"] = Stadtteile.boundary
    Stadtteile["centroid"] = Stadtteile.centroid


    Altstadt = Stadtbezirke["centroid"].iloc[5]
    Stadtbezirke["Entfernung"] = Stadtbezirke["centroid"].distance(Altstadt)/1000 # fuer km
    Stadtteile["Entfernung"] = Stadtteile["centroid"].distance(Altstadt)/1000 # fuer km

    wahl_bezirke["Flaeche"] = wahl_bezirke.area/10**6 # fuer km2
    wahl_bezirke["boundary"] = wahl_bezirke.boundary
    wahl_bezirke["centroid"] = wahl_bezirke.centroid 
    wahl_bezirke["Entfernung"] = wahl_bezirke["centroid"].distance(Altstadt)/1000 # fuer km  
    if return_wahl_bezirke==True:
        return Stadtteile, Stadtbezirke, wahl_bezirke
    else:
        return Stadtteile, Stadtbezirke 
    
    
def karte_stadtbezirke(df,column,cmap='Greys',legend='Anteil [%]',wahl='Gemeinderat'):
     dic_label={ 'CDU':'Anteil CDU [%]',
       'GRÜNE':'Anteil GRÜNE [%]', 'SPD':'Anteil SPD [%]', 'AfD':'Anteil AfD [%]', 'FDP':'Anteil FDP [%]', 
               'LiSSt.':'Anteil LiSSt. [%]','max-schnellmeldungen':'Moegliche Schnellmeldungen',
               'wahlbezirke_prozent':'Anteil ausgezaehlt [%]',
              'anz-schnellmeldungen':'Anzahl Schnellmeldungen','FW':'Anteil Freie Waehler [%]',
               'GAF':'Anteil GAF [%]','FL':'Anteil FL [%]',
              'Junges_F':'Anteil Junges F [%]','Urbanes_F':'Anteil Urbanes F [%]',
              'Kultur':'Anteil Kultur [%]',
              'UFF':'Anteil UFF [%]','Bürger_F':'Anteil Bürger F [%]','LTI':'Anteil LTI [%]',
               'APPD':'APPD_ [%]','FFPCV':'Anteil FFPCV [%]','Meinrad_Spitz':'Anteil Meinrad Spitz [%]', 'LINKE':'Anteil LINKE [%]',
               'BSW':'Anteil BSW [%]','Volt':'Anteil Volt [%]','Klimaliste':'Anteil Klimaliste [%]',
              'Letzte_Generation':'Anteil Letzte Generation [%]','ÖDP':'Anteil ÖDP [%]',
              'Tierschutz':'Anteil Tierschutz [%]','DIE_PARTEI':'Anteil Die Partei [%]',
              'dieBasis':'Anteil die Basis [%]','Piraten':'Anteil Piraten [%]','Familien':'Anteil Familien [%]',
               'MERA25':'Anteil MERA25 [%]','DAVA':'Anteil DAVA [%]','Gewinne_CDU':'Gewinne CDU [%]',
       'Gewinne_GRÜNE':'Gewinne GRÜNE [%]', 'Gewinne_SPD':'Gewinne SPD [%]', 'Gewinne_AfD':'Gewinne AfD [%]', 
               'Gewinne_FDP':'Gewinne FDP [%]', 
               'Gewinne_LINKE':'Gewinne LINKE [%]','Gewinne_sonstige':'Gewinne sonstige [%]'}
     col_label={ 'CDU':'Greys',
       'GRÜNE':'Greens', 'SPD':'Reds', 'AfD':'Blues', 'FDP':'plasma', 
               'LiSSt.':'RdPu','max-schnellmeldungen':'Greens',
              'anz-schnellmeldungen':'Greys','FW':'plasma',
               'LTI':'BuPu','Volt':'YlGn','GAF':'YlGn',
              'Letzte_Generation':'YlGn','ÖDP':'YlGn',
              'UFF':'Purples',
              'Urbanes_F':'PuBu','Kultur':'Purples','Bürger_F':'OrRd', 'LINKE':'RdPu',
              'anz-schnellmeldungen':'Greys','FW':'plasma',
               'BSW':'BuPu','Volt':'YlGn','Klimaliste':'YlGn',
              'Letzte_Generation':'YlGn','ÖDP':'YlGn',
              'Tierschutz':'Purples','DIE_PARTEI':'Purples',
              'dieBasis':'PuBu','Piraten':'Purples','Familien':'Greys','MERA25':'Purples','DAVA':'OrRd',
              'Gewinne_CDU':'RdYlGn',
       'Gewinne_GRÜNE':'RdYlGn', 'Gewinne_SPD':'RdYlGn', 'Gewinne_AfD':'RdYlGn', 'Gewinne_FDP':'RdYlGn', 
               'Gewinne_LINKE':'RdYlGn','Gewinne_sonstige':'RdYlGn'
              }  
     if wahl=='Gemeinderat':
         partei_liste=[ 'CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LiSSt.', 'DIE_PARTEI', 'GAF',
       'FL', 'Volt', 'Junges_F', 'Urbanes_F', 'Kultur', 'Bürger_F',
       'UFF', 'LTI', 'APPD', 'FFPCV', 'Meinrad_Spitz']
     elif wahl=='Europa':    
             partei_liste=[ 'CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LINKE', 'DIE_PARTEI', 'Tierschutz',
       'ÖDP', 'Volt', 'Piraten', 'Familien', 'MERA25', 'Bündnis_C',
       'Aktion_Tierschutz', 'BIG', 'HEIMAT', 'PdH', 'PfSV', 'MW', 'MLPD',
       'DKP', 'SGP', 'ABG', 'dieBasis', 'B_Deutschland', 'BSW', 'DAVA',
       'Klimaliste', 'Letzte_Generation', 'PDV', 'PdF', 'PVVV']
     if column in dic_label.keys():
         legend=dic_label[column]
     if column in col_label.keys():
         cmap=col_label[column]    
     if column in partei_liste:
         df['Anteil']=df[column]/df['Gueltige_Stimmen']*100
         column='Anteil'
        
     fig, ax = plt.subplots(1, 1,figsize=(10,10))
     divider = make_axes_locatable(ax)
     cax = divider.append_axes("bottom", size="5%", pad=0.1)
 
     df.plot(ax=ax, color='white', edgecolor='black')
     plot=df.plot(column=column,
                     ax=ax,
                     legend=True,cax=cax,
                     cmap=cmap,
                
                     legend_kwds={"label": legend, "orientation": "horizontal"},)
     plot.set_axis_off()   
    
    
def sainte_l(array_all,sitze=48,test=True,parteien=['CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LiSSt.', 'DIE_PARTEI', 'GAF',
       'FL', 'Volt', 'Junges_F', 'Urbanes_F', 'Kultur', 'Bürger_F',
       'UFF', 'LTI', 'APPD', 'FFPCV', 'Meinrad_Spitz']):
    array=np.array(array_all.loc[parteien])
    summe=np.sum(array)
    start_div=int(np.round(summe/sitze))
    start_sitze=np.round((array/start_div).astype(float))

    if sum(start_sitze)==sitze:
        if test==True:
            print(f" {int(np.sum(start_sitze))} wurden zugeteilt wie es sein sollte")
        return start_sitze
    elif sum(start_sitze)>sitze:
        res_sitze=start_sitze
        div=start_div
        while sum(res_sitze)>sitze:
            div+=1
            res_sitze=np.round((array/div).astype(float))
        if test==True:
            if int(np.sum(res_sitze))==sitze:
               print(f" {int(np.sum(res_sitze))} wurden zugeteilt wie es sein sollte")   
            else:
               print(f" {int(np.sum(res_sitze))} wurden zugeteilt, {sitze} sollten es sein")                 
        return res_sitze    
    else:
        res_sitze=start_sitze
        div=start_div
        while sum(res_sitze)<sitze:
            div-=1
            res_sitze=np.round((array/div).astype(float))
        if test==True:    
            if int(np.sum(res_sitze))==sitze:
               print(f" {int(np.sum(res_sitze))} wurden zugeteilt wie es sein sollte")   
            else:
               print(f" {int(np.sum(res_sitze))} wurden zugeteilt, {sitze} sollten es sein")              
        return res_sitze         
    
    
def make_bar_plot(df,title='',index=0,ylabel="Anteil [%]",sitze=0,parteien=['CDU','GRÜNE', 'SPD', 'AfD', 'FDP', 'FW'],Wahl='Gemeinderat'):
    if Wahl=='Gemeinderat':
        parteien=['CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LiSSt.', 'DIE_PARTEI', 'GAF',
       'FL', 'Volt', 'Junges_F', 'Urbanes_F', 'Kultur', 'Bürger_F',
       'UFF', 'LTI', 'APPD', 'FFPCV', 'Meinrad_Spitz']
    elif Wahl=='Europa':
        parteien=[ 'CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LINKE', 'DIE_PARTEI', 'Tierschutz',
       'ÖDP', 'Volt', 'Piraten', 'Familien', 'MERA25', 'Bündnis_C',
       'Aktion_Tierschutz', 'BIG', 'HEIMAT', 'PdH', 'PfSV', 'MW', 'MLPD',
       'DKP', 'SGP', 'ABG', 'dieBasis', 'B_Deutschland', 'BSW', 'DAVA',
       'Klimaliste', 'Letzte_Generation', 'PDV', 'PdF', 'PVVV']
    if sitze==0:
        array=np.array(df.loc[index,parteien])[:]/np.array(df.loc[index,'Gueltige_Stimmen'])*100
    else:
        array=sainte_l(df.loc[index,parteien][:],test=False,sitze=sitze,parteien=parteien)
        ylabel='Gemeinderatssitze'
        if Wahl=='Europa':
            ylabel='Europaparliamentssitze'
    d = {'namen': parteien, 'Prozent_24':array}

    df_new=pd.DataFrame(data=d)
    bar_colors=[]
    for i in range(len(parteien)):
        if parteien[i]=='CDU':
            bar_colors.append('black')
        elif parteien[i]=='SPD':
            bar_colors.append('red')    
        elif parteien[i]=='FDP':
            bar_colors.append('yellow')    
        elif parteien[i]=='AfD':
            bar_colors.append('blue')
        elif parteien[i]=='LiSSt.':
            bar_colors.append('magenta')    
        elif parteien[i]=='GRÜNE':
            bar_colors.append('green')
        elif parteien[i]=='FW':
            bar_colors.append('darkgray')   
        elif parteien[i]=='FL':
            bar_colors.append('cornflowerblue')    
        elif parteien[i]=='GAF':
            bar_colors.append('mediumseagreen')   
        elif parteien[i]=='DIE_PARTEI':
            bar_colors.append('darkred')       
        elif parteien[i]=='Volt':
            bar_colors.append('purple')     
        elif parteien[i]=='LTI':
            bar_colors.append('orange')   
        elif parteien[i]=='UFF':
            bar_colors.append('violet')       
        elif parteien[i]=='Urbanes_F':
            bar_colors.append('cyan')    
        elif parteien[i]=='Junges_F':
            bar_colors.append('navy')   
        elif parteien[i]=='FFPCV':
            bar_colors.append('gold')       
        elif parteien[i]=='Kultur':
            bar_colors.append('brown')   
        elif parteien[i]=='Bürger_F':
            bar_colors.append('olive')   
        elif parteien[i]=='BSW':
            bar_colors.append('darkred')
        elif parteien[i]=='LINKE':
            bar_colors.append('magenta')            
        elif parteien[i]=='APPD':
            bar_colors.append('pink')      
        elif parteien[i]=='ÖDP':
            bar_colors.append('orange')     
        elif parteien[i]=='Tierschutz':
            bar_colors.append('darkseagreen')     
        elif parteien[i]=='MERA25':
            bar_colors.append('orangered')           
        elif parteien[i]=='Letzte_Generation':
            bar_colors.append('lime')    
        elif parteien[i]=='PdF':
            bar_colors.append('gold')              
        else:    
            bar_colors.append('lightgray')   
       
    df_new.loc[:,'namen']=np.where(df_new.loc[:,'namen']=='DIE_PARTEI','DIE PARTEI',df_new.loc[:,'namen'])  
    df_new.loc[:,'namen']=np.where(df_new.loc[:,'namen']=='Junges_F','Junges',df_new.loc[:,'namen']) 
    df_new.loc[:,'namen']=np.where(df_new.loc[:,'namen']=='Urbanes_F','Urbanes',df_new.loc[:,'namen']) 
    df_new.loc[:,'namen']=np.where(df_new.loc[:,'namen']=='Bürger_F','Bürger',df_new.loc[:,'namen'])      
    df_new.loc[:,'namen']=np.where(df_new.loc[:,'namen']=='Meinrad_Spitz','Meinrad Spitz',df_new.loc[:,'namen'])       
    plt.figure(figsize=(10, 8))
    plt.bar(df_new.namen,df_new.Prozent_24,color=bar_colors)
    plt.xticks(rotation=80)
    plt.ylabel(ylabel)    
    plt.title(title)

def get_process_wahl(wahl='Gemeinderat',final=True):
    if wahl=='Gemeinderat':
        if final==True:
            gem24_all=pd.read_csv('gem24_summe.csv',sep=';')
            gem24_stadtbezirke=pd.read_csv('gem24_stadtbezirke.csv',sep=';')
            gem24_stadtbezirke['wahlbezirke_prozent']=gem24_stadtbezirke['anz-schnellmeldungen']/gem24_stadtbezirke['max-schnellmeldungen']*100
            gem24_wahlbezirke=pd.read_csv('gem24_wahlbezirke.csv',sep=';')
        else:
            gem24_all=pd.read_csv('gem24_summe10.csv',sep=';')
            gem24_stadtbezirke=pd.read_csv('gem24_stadtbezirke_10.csv',sep=';')
            gem24_stadtbezirke['wahlbezirke_prozent']=gem24_stadtbezirke['anz-schnellmeldungen']/gem24_stadtbezirke['max-schnellmeldungen']*100
            gem24_wahlbezirke=pd.read_csv('gem24_wahlbezirke_10.csv',sep=';')            
        print(f"Wahlbezirke {gem24_wahlbezirke['max-schnellmeldungen'].sum()}")
        print(f"ausgezaehlte Wahlbezirke {gem24_wahlbezirke['anz-schnellmeldungen'].sum()}")
        gem24_stadtbezirke.set_index('gebiet-name',inplace=True)
    elif wahl=='Europa':
        gem24_all=pd.read_csv('eu24_summe.csv',sep=';')
        gem24_stadtbezirke=pd.read_csv('eu24_stadtbezirke.csv',sep=';')
        gem24_stadtbezirke['wahlbezirke_prozent']=gem24_stadtbezirke['anz-schnellmeldungen']/gem24_stadtbezirke['max-schnellmeldungen']*100
        gem24_wahlbezirke=pd.read_csv('eu24_wahlbezirke.csv',sep=';')
        print(f"Wahlbezirke {gem24_wahlbezirke['max-schnellmeldungen'].sum()}")
        print(f"ausgezaehlte Wahlbezirke {gem24_wahlbezirke['anz-schnellmeldungen'].sum()}")
        gem24_stadtbezirke.set_index('gebiet-name',inplace=True)        
    bev=pd.read_csv("de-bw-freiburg-grunddaten_fuer_indikatoren_stadtbezirke_-_bevoelkerungsbestand.csv",dtype=str)
    for i in range(bev.shape[1]):
        if i==2 or i==3:
            bev.iloc[:,i]=bev.iloc[:,i].str.replace(",",".").astype(float)
        elif i!=1:    
            bev.iloc[:,i]=bev.iloc[:,i].astype(int,errors='ignore')

    soz=pd.read_csv("de-bw-freiburg-grunddaten_fuer_indikatoren_stadtbezirke_-_soziales.csv",dtype=str)
    soz.Jahr=soz.Jahr.astype(int)
    for i in range(2,soz.shape[1]):

        soz.iloc[:,i]=soz.iloc[:,i].fillna(0).astype(int)
        bevdic={'Jahr':'Jahr', 'Stadtbezirk':'Stadtbezirk',
       'Summe Altersjahre (für Durchschnittsberechnung)':'summe_alter',
       'Summe Wohndauer in Tagen (für Durchschnittsberechnung)':'summe_tage',
       'Anzahl Einwohner_innen':"einwohner", 'Anzahl Einwohner_innen Vorjahr':"einwohner_vorjahr",
       'Anzahl Einwohner_innen unter 3 Jahre':"einwohner_u3",
       'Anzahl Einwohner_innen unter 6 Jahre':"einwohner_u6",
       'Anzahl Einwohner_innen unter 15 Jahre':"einwohner_u15",
       'Anzahl Einwohner_innen unter 18 Jahre':"einwohner_u18",
       'Anzahl Einwohner_innen unter 25 Jahre':"einwohner_u25",
       'Anzahl Einwohner_innen 0 bis unter 65 Jahre':"einwohner_u65",
       'Anzahl Einwohner_innen 3 bis unter 6 Jahre':"einwohner_3_6",
       'Anzahl Einwohner_innen 6 bis unter 10 Jahre':"einwohner_6_10",
       'Anzahl Einwohner_innen 10 bis unter 15 Jahre':"einwohner_10_15",
       'Anzahl Einwohner_innen 15 bis unter 50 Jahre':"einwohner_10_50",
       'Anzahl Einwohner_innen 15 bis unter 65 Jahre':"einwohner_15_65",
       'Anzahl Einwohner_innen 15 bis unter 65 Jahre, weiblich':"einwohner_15_65_w",
       'Anzahl Einwohner_innen 15 bis unter 65 Jahre, männlich':"einwohner_15_65_m",
       'Anzahl Einwohner_innen 15 bis unter 65 Jahre, deutsch':"einwohner_15_65_d",
       'Anzahl Einwohner_innen 15 bis unter 65 Jahre, nicht-deutsch':"einwohner_15_65_d",
       'Anzahl Einwohner_innen 60 bis unter 80 Jahre':"einwohner_60_80",
       'Anzahl Einwohner_innen 50 Jahre und älter':"einwohner_50p",
       'Anzahl Einwohner_innen 65 Jahre und älter':"einwohner_65p",
       'Anzahl Einwohner_innen 80 Jahre und älter':"einwohner_80p",
       'Anzahl Frauen 15 bis unter 45 Jahren':"einwohner_15_45_w",
       'Anzahl Einwohner_innen männlich':"einwohner_m", 'Anzahl Einwohner_innen weiblich':"einwohner_w",
       'Anzahl Einwohner_innen deutsch':"einwohner_d",
       'Anzahl Einwohner_innen nicht-deutsch':"einwohner_nd",
       'Anzahl Einwohner_innen EU-Ausland':"einwohner_eu",
       'Anzahl Einwohner_innen Nicht-EU-Ausland':"einwohner_neu",
       'Anzahl Einwohner_innen inkl. Nebenwohnsitzen':"einwohner_pneben"}
    bev.rename(columns=bevdic,inplace=True)
    sozdic={'Anzahl Personen Eingliederungshilfe (SGB IX)':'Behinderte',
       'Anzahl Personen Grundsicherung (SGB XII)':'Sozialhilfe_personen',
       'Anzahl Personen Grundsicherung im Alter (SGB XII)':'Sozialhilfe_alter',
       'Anzahl Personen Hilfen zum Lebensunterhalt (SGB XII)':'Sozialhilfe_lebensunterhalt',
       'Anzahl Personen Hilfen zur Pflege (SGB XII)':'Sozialhilfe_pflege',
       'Anzahl Personen SGB XII (inkl. KOF)':'Sozialhilfe_personen_kof',
       'Anzahl Personen SGB XII (inkl. KOF) im Alter 65+':'Sozialhilfe_alter_kof',
       'Anzahl Haushalte SGB XII (inkl. KOF)':'Sozialhilfe_haushalte', 'Anzahl Personen AsylblG':'Asylbewerber',
       'Anzahl Haushalte AsylblG':'Asylbewerber_Haushalte', 'Anzahl Personen SGBVIII':'Sozial_kinder'}
    soz.rename(columns=sozdic,inplace=True)


    soz['Stadtbezirk'] = np.where(soz['Stadtbezirk'] =='Brühl-Industriegebiet', 'Brühl-Güterbahnhof/Industriegebiet', soz['Stadtbezirk'])
    bev['Stadtbezirk'] = np.where(bev['Stadtbezirk'] =='Brühl-Industriegebiet', 'Brühl-Güterbahnhof/Industriegebiet', bev['Stadtbezirk'])

    soz_21=soz[(soz.Jahr==2021)]
    bev_21=bev[(bev.Jahr==2021)]
    comb=pd.merge(gem24_stadtbezirke,bev_21,how='inner',left_on=gem24_stadtbezirke.index,right_on=["Stadtbezirk"])
    comb2=pd.merge(comb,soz_21,how='inner',left_on="Stadtbezirk",right_on=["Stadtbezirk"])
    comb2.set_index('Stadtbezirk',inplace=True)
    if wahl=='Europa':
        wahl2=pd.read_csv("de-bw-freiburg-wahlergebnisse_bundestags_landtags-_und_europawahl_stadtbezirke_zeitreihe.csv",dtype=str,sep=';')

        wahl2.Jahr=wahl2.Jahr.astype(int)
        wahl2['Erst-/Zweitstimmen']=wahl2['Erst-/Zweitstimmen'].astype(int)
        wahl2.Wahlart=wahl2.Wahlart.astype(int)
        for i in range(3,wahl2.shape[1]-1):
            wahl2.iloc[:,i]=wahl2.iloc[:,i].str.replace(",",".").astype(float)
        euro19=wahl2[(wahl2.Jahr==2019)]
        euro19['Stadtbezirk'] = np.where(euro19['Stadtbezirk'] =='Brühl-Güterbahnhof', 'Brühl-Güterbahnhof/Industriegebiet', euro19['Stadtbezirk'])
        euro19['Anteil_sonstige']=100-euro19['Anteil CDU']-euro19['Anteil SPD']-euro19['Anteil FDP']-euro19['Anteil LINKE']-euro19['Anteil AfD']-euro19['Anteil GRÜNE']
        comb3=pd.merge(comb2,euro19,how='inner',left_on="Stadtbezirk",right_on=["Stadtbezirk"])
        comb3.set_index('Stadtbezirk',inplace=True)
        comb3['Gewinne_GRÜNE']=comb3['GRÜNE']/comb3['Gueltige_Stimmen']*100-comb3['Anteil GRÜNE']
        comb3['Gewinne_CDU']=comb3['CDU']/comb3['Gueltige_Stimmen']*100-comb3['Anteil CDU']
        comb3['Gewinne_SPD']=comb3['SPD']/comb3['Gueltige_Stimmen']*100-comb3['Anteil SPD']
        comb3['Gewinne_FDP']=comb3['FDP']/comb3['Gueltige_Stimmen']*100-comb3['Anteil FDP']
        comb3['Gewinne_LINKE']=comb3['LINKE']/comb3['Gueltige_Stimmen']*100-comb3['Anteil LINKE']
        comb3['Gewinne_AfD']=comb3['AfD']/comb3['Gueltige_Stimmen']*100-comb3['Anteil AfD']
        comb3['Gewinne_sonstige']=-(comb3['Gewinne_GRÜNE']+comb3['Gewinne_CDU']+comb3['Gewinne_SPD']+comb3['Gewinne_LINKE']+comb3['Gewinne_FDP']+comb3['Gewinne_AfD'])
        comb3['Asylbewerber_anteil']=comb3['Asylbewerber']/comb3['einwohner']*100
        comb3['Auslaender_anteil']=comb3['einwohner_nd']/comb3['einwohner']*100
        comb3['Sozialhilfe_anteil']=comb3['Sozialhilfe_personen_kof']/comb3['einwohner']*100
        return gem24_all, comb3, gem24_wahlbezirke   
    elif wahl=='Gemeinderat':
        comb2['Asylbewerber_anteil']=comb2['Asylbewerber']/comb2['einwohner']*100
        comb2['Auslaender_anteil']=comb2['einwohner_nd']/comb2['einwohner']*100
        comb2['Sozialhilfe_anteil']=comb2['Sozialhilfe_personen_kof']/comb2['einwohner']*100
        return gem24_all, comb2, gem24_wahlbezirke 
    
    


def get_and_save_komm():
    gem_total='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Gemeinderatswahl-Stadt-Freiburg-insgesamt.csv?ts=1717981762932'
    gem_stadtbezirke='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Gemeinderatswahl-Stadtbezirke.csv?ts=1717981762932'
    gem_wahlbezirke='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Gemeinderatswahl-Wahlbezirk.csv?ts=1717981762932'

    name_output=['gem24_summe.csv','gem24_stadtbezirke.csv','gem24_wahlbezirke.csv']
    url_list=[gem_total,gem_stadtbezirke,gem_wahlbezirke]

    dic_gem={'A1':'Wahlberechtigte_lokal', 'A2':'Wahlberechtigte_nicht_lokal', 'A3':'Wahlberechtigte_zusaetzliche', 'A':'Wahlberechtigte_summe',
       'B':'Waehler', 'B1':'Waehler_Wahlschein','B2':'Briefwaehler_Wahlschein', 'C':'Ungueltige_Stimmen', 'D':'Gueltige_Stimmzettel',  'E':'Gueltige_Stimmen',  'D3':'CDU',
       'D1':'GRÜNE', 'D2':'SPD', 'D10':'AfD', 'D9':'FDP', 'D6':'FW', 'D4':'LiSSt.', 'D12':'DIE_PARTEI',
       'D5':'GAF', 'D7':'FL', 'D8':'Junges_F', 'D11':'Urbanes_F', 'D13':'Kultur', 'D14':'UFF', 'D15':'Bürger_F',
          'D16':'LTI', 'D17':'APPD', 'D18':'FFPCV',
       'D19':'Volt', 'D20':'Meinrad_Spitz'}

    for i in range(48):
        dic_gem.update({'D1_'+str(i+1): 'GRÜNE_'+str(i+1)})
        dic_gem.update({'D3_'+str(i+1): 'CDU_'+str(i+1)})
        dic_gem.update({'D2_'+str(i+1): 'SPD_'+str(i+1)})
        dic_gem.update({'D10_'+str(i+1): 'AfD_'+str(i+1)})
        dic_gem.update({'D9_'+str(i+1): 'FDP_'+str(i+1)})
        dic_gem.update({'D6_'+str(i+1): 'FW_'+str(i+1)})    
        dic_gem.update({'D4_'+str(i+1): 'LiSSt._'+str(i+1)})
        dic_gem.update({'D12_'+str(i+1): 'DIE_PARTEI_'+str(i+1)})
        dic_gem.update({'D5_'+str(i+1): 'GAF_'+str(i+1)})
        dic_gem.update({'D7_'+str(i+1): 'FL_'+str(i+1)})
        dic_gem.update({'D8_'+str(i+1): 'Junges_F_'+str(i+1)})
        dic_gem.update({'D11_'+str(i+1): 'Urbanes_F_'+str(i+1)})    
        dic_gem.update({'D13_'+str(i+1): 'Kultur_'+str(i+1)})
        dic_gem.update({'D14_'+str(i+1): 'UFF_'+str(i+1)})
        dic_gem.update({'D15_'+str(i+1): 'Bürger_F_'+str(i+1)})
        dic_gem.update({'D16_'+str(i+1): 'LTI_'+str(i+1)})
        dic_gem.update({'D17_'+str(i+1): 'APPD_'+str(i+1)})
        dic_gem.update({'D18_'+str(i+1): 'FFPV_'+str(i+1)})
        dic_gem.update({'D19_'+str(i+1): 'Volt_'+str(i+1)})
        dic_gem.update({'D20_'+str(i+1): 'Meinrad_Spitz_'+str(i+1)})

    start_time=time.time()
    for i in range(len(url_list)):
        print(f"getting table {i}")
        data = requests.get(url_list[i])
        val=data.content
        csv_data = val.decode('utf-8')
        csv_file = io.StringIO(csv_data)
        df = pd.read_csv(csv_file,sep=';')
        df = df.rename(columns=dic_gem)
        df.to_csv(name_output[i],sep=';')
    stop_time=time.time()    

    #print(f"needed {round(stop_time-start_time,4)} seconds")
    
def get_and_save_eur():
    eu_total='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Europawahl-2024-Stadt-Freiburg-insgesamt.csv?ts=1717683184474html'
    eu_stadtbezirke='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Europawahl-2024-Stadtbezirke.csv?ts=1717763903131'
    eu_wahlbezirke='https://wahlergebnisse.komm.one/lb/produktion/wahltermin-20240609/08311000/daten/opendata/Open-Data-08311000-Europawahl-2024-Wahlbezirk.csv?ts=1717763903131'

    name_output=['eu24_summe.csv','eu24_stadtbezirke.csv','eu24_wahlbezirke.csv']
    url_list=[eu_total,eu_stadtbezirke,eu_wahlbezirke]

    dic_euro={'A1':'Wahlberechtigte_lokal', 'A2':'Wahlberechtigte_nicht_lokal', 'A3':'Wahlberechtigte_zusaetzliche', 'A':'Wahlberechtigte_summe',
       'B':'Waehler', 'B1':'Waehler_Wahlschein', 'C':'Ungueltige_Stimmen', 'D':'Gueltige_Stimmen', 'D1':'CDU', 'D2':'GRÜNE', 'D3':'SPD', 'D4':'AfD', 'D5':'FDP', 'D6':'FW', 'D7':'LINKE', 'D8':'DIE_PARTEI',
       'D9':'Tierschutz', 'D10':'ÖDP', 'D11':'Volt', 'D12':'Piraten', 'D13':'Familien', 'D14':'MERA25', 'D15':'Bündnis_C',
          'D16':'Aktion_Tierschutz', 'D17':'BIG', 'D18':'HEIMAT',
       'D19':'PdH', 'D20':'PfSV', 'D21':'MW','D22':'MLPD', 'D23':'DKP', 'D24':'SGP', 'D25':'ABG', 
          'D26':'dieBasis', 'D27':'B_Deutschland', 'D28':'BSW',
       'D29':'DAVA', 'D30':'Klimaliste', 'D31':'Letzte_Generation', 'D32':'PDV', 'D33':'PdF', 'D34':'PVVV'}
    start_time=time.time()
    for i in range(len(url_list)):
        print(f"getting table {i}")
        data = requests.get(url_list[i])
        val=data.content
        csv_data = val.decode('utf-8')
        csv_file = io.StringIO(csv_data)
        df = pd.read_csv(csv_file,sep=';')
        df = df.rename(columns=dic_euro)
        df.to_csv(name_output[i],sep=';')
    stop_time=time.time()    

    #print(f"needed {round(stop_time-start_time,4)} seconds")

def get_percent(df,columns=['SPD','CDU'],endung='_gem24',wahl='Gemeinderat'):
    if wahl=='Gemeinderat':
        columns=['CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LiSSt.', 'DIE_PARTEI', 'GAF',
       'FL', 'Volt', 'Junges_F', 'Urbanes_F', 'Kultur', 'Bürger_F',
       'UFF', 'LTI', 'APPD', 'FFPCV', 'Meinrad_Spitz']
    elif wahl=='Europa':
        endung='_eu24'
        columns=['CDU',
       'GRÜNE', 'SPD', 'AfD', 'FDP', 'FW', 'LINKE', 'DIE_PARTEI', 'Tierschutz',
       'ÖDP', 'Volt', 'Piraten', 'Familien', 'MERA25', 'Bündnis_C',
       'Aktion_Tierschutz', 'BIG', 'HEIMAT', 'PdH', 'PfSV', 'MW', 'MLPD',
       'DKP', 'SGP', 'ABG', 'dieBasis', 'B_Deutschland', 'BSW', 'DAVA',
       'Klimaliste', 'Letzte_Generation', 'PDV', 'PdF', 'PVVV']
    for i in range(len(columns)):
        new_col=columns[i]+'_prozent'+endung
        df[new_col]=df[columns[i]]/df['Gueltige_Stimmen']*100
    if wahl=='Europa':
        #rename to avoid name collisions
        party_dic={'CDU':'CDU_eu24',
       'GRÜNE':'GRÜNE_eu24', 'SPD':'SPD_eu24', 'AfD':'AfD_eu24', 'FDP':'FDP_eu24', 'FW':'FW_eu24',
                   'DIE_PARTEI':'DIE_PARTEI_eu24', 'Volt':'Volt_eu24'}
        df.rename(columns=party_dic,inplace=True)
    return df


def linf(x,a,b):
    return a+x*b
