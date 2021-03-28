import pandas as pd
import requests
import json
import mpld3
import matplotlib.pyplot as plt, mpld3
import numpy as np
from datetime import date
import csv
import calendar
import os

# General Methods for organizing Files
def genDate():
    today = date.today()
    return today.strftime("%Y%m%d")


def modifyFilename(filename):
    filename = './data/' + genDate() + '_' + filename
    return filename


def writeData(r, filename='data.csv'):
    filename = modifyFilename(filename)
    with open(filename, 'w') as outfile:
        outfile.write(r.text)
    print('Daten in ' + filename + ' geschrieben')


def writeCSV(r, filename='data.csv'):
    filename = modifyFilename(filename)
    r.to_csv(filename, index=False, encoding='utf-8')
    print('CSV ' + filename + ' Geschrieben.')


def importData(filename=modifyFilename('yearlyData.csv')):
    data = pd.read_csv(filename, sep=',', header=0, index_col=0)
    return (data)


def importMonthlyData(filename1='data/monthly_cont.csv', filename2=modifyFilename('monthlyData.csv')):
    monthlyDataNew = pd.read_csv(filename2, sep=',', header=0, index_col=False)
    monthlyDataOld = pd.read_csv(filename1, sep=',', header=0, index_col=0)
    return (monthlyDataNew, monthlyDataOld)


# Methods for requesting Data
def requestdataBFS(url, payload):
    r = requests.post(url, data=json.dumps(payload))
    return r


def requestdataAS():
    url = 'https://www.auto.swiss/fileadmin/3_Statistiken/Autoverkaeufe_nach_Modellen/ModellePW2019.xlsx'
    filename = 'ModellePW2019.xlsx'
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)


# Methods for importing and structuring data
def importDataAS(filename='ModellePW2019.xlsx'):
    df = pd.read_excel(filename, sheet_name=None, header=15, index_col=None, usecols=[0, 1, 2])
    j = 1
    for i in df:
        writeCSV(df[i], 'zulassungenAS_' + str(j) + '.csv')
        j = j + 1
    return (df)

def getMonthlyData(filename='monthlyData.csv'):
    url = 'https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-1103020200_101/px-x-1103020200_101.px'
    payload = {
        "query": [
            {
                "code": "Monat",
                "selection": {
                    "filter": "item",
                    "values": [
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "10",
                        "11",
                        "12"
                    ]
                }
            },
            {
                "code": "Fahrzeuggruppe / -art",
                "selection": {
                    "filter": "item",
                    "values": [
                        "100"
                    ]
                }
            },
            {
                "code": "Treibstoff",
                "selection": {
                    "filter": "item",
                    "values": [
                        "100",
                        "200",
                        "300",
                        "400",
                        "500",
                        "600",
                        "9900",
                        "9999"
                    ]
                }
            }
        ],
        "response": {
            "format": "csv"
        }
    }
    r = requestdataBFS(url, payload)
    writeData(r, filename)
    return r

def getYearlyData(filename='yearlyData.csv'):
    payload = {
        "query": [
            {
                "code": "Treibstoff",
                "selection": {
                    "filter": "item",
                    "values": [
                        "100",
                        "200",
                        "300",
                        "400",
                        "500",
                        "600",
                        "9900"
                    ]
                }
            }
        ],
        "response": {
            "format": "csv"
        }
    }
    url = 'https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-1103020200_200/px-x-1103020200_200.px'
    r = requestdataBFS(url, payload)
    writeData(r, filename)


def processMOFIShistory():
    getMOFISData(filename='mofis2018.xlsx',
                 url='https://files.admin.ch/astra_ffr/mofis/Datenlieferungs-Kunden/opendata/1000-Fahrzeuge_IVZ/1200-Neuzulassungen/1220-Neuzlassungsbericht_woechentlich/1222-Vorjahresdaten/NEUZU_W-2018.xlsx')
    getMOFISData(filename='mofis2019.xlsx',
                 url='https://files.admin.ch/astra_ffr/mofis/Datenlieferungs-Kunden/opendata/1000-Fahrzeuge_IVZ/1200-Neuzulassungen/1220-Neuzlassungsbericht_woechentlich/1222-Vorjahresdaten/NEUZU_W-2019.xlsx')
    importMOFISdata(filename=('data/20210108_mofis2018.xlsb'), destfilename='mofis2018.csv')
    importMOFISdata(filename=modifyFilename('mofis2019.xlsb'), destfilename='mofis2019.csv')
    modifyMOFISData(filename=modifyFilename('mofis2018.csv'), destfilename='mofismonthly_2018.csv')
    modifyMOFISData(filename=modifyFilename('mofis2019.csv'), destfilename='mofismonthly_2019.csv')


def getMOFISData(filename='mofisData.xlsb',
                 url='https://files.admin.ch/astra_ffr/mofis/Datenlieferungs-Kunden/opendata/1000-Fahrzeuge_IVZ/1200-Neuzulassungen/1220-Neuzlassungsbericht_woechentlich/NEUZU_W.xlsb'):
    if os.path.isfile(modifyFilename(filename)):
        print('MOFIS Datei schon vorhanden')
    else:
        print('MOFIS Datei wird heruntergeladen')
        r = requests.get(url, allow_redirects=True)
        open(modifyFilename(filename), 'wb').write(r.content)
        print('Neuste MOFIS Datei heruntergeladen')


def importMOFISdata(filename=modifyFilename('mofisData.xlsb'), destfilename='mofis_raw_clean.csv'):
    if filename[-4:] == 'xlsb':
        data = pd.read_excel(filename, engine='pyxlsb', sheet_name='Rohdaten')
    if filename[-3:] == 'xls':
        data = pd.read_excel(filename, sheet_name='Rohdaten')
    data = data.drop(data.columns[0], axis=1)
    data.iloc[4] = data.iloc[4].str.replace('\n', '').str.replace('-', '')
    data.columns = data.iloc[4]
    data = data.iloc[5:]
    data.to_csv(modifyFilename(destfilename))
    print('rohdaten excel file importiert, csv abgespeichert')
    explainations = pd.read_excel(filename, engine='pyxlsb', sheet_name='Erläuterungen')
    if filename == modifyFilename('mofisData.xlsb'):
        global mofis_latestupdate
        mofis_latestupdate = explainations.iat[13, 4]
        print('MOFIS Stand: ' + mofis_latestupdate)
        with open('latestupdateMOFIS.txt', 'w') as text_file:
            text_file.write(mofis_latestupdate)


def modifyMOFISData(filename=modifyFilename('mofis_raw_clean.csv'), destfilename='mofis_monthly_thisyear.csv'):
    data = pd.read_csv(filename)
    print('Mofis Daten für auswertung geladen')
    data = data[data['Fahrzeugart'] == '01 Personenwagen']
    count = data.groupby(['Erstinverkehrsetzung_Monat', 'Treibstoff', 'Erstinverkehrsetzung_Jahr']).sum()
    countPivot = count['AnzahlFahrzeuge'].unstack(level=['Treibstoff'])
    countPivot.reset_index(inplace=True)
    countPivot['Erstinverkehrsetzung_Jahr'] = countPivot.Erstinverkehrsetzung_Jahr.astype(int).astype(str)
    countPivot['Erstinverkehrsetzung_Monat'] = countPivot.Erstinverkehrsetzung_Monat.astype(int).astype(str)
    countPivot['Erstinverkehrsetzung_Monat'] = countPivot['Erstinverkehrsetzung_Monat'].apply(lambda x: x.zfill(2))
    countPivot['date'] = countPivot[['Erstinverkehrsetzung_Jahr', 'Erstinverkehrsetzung_Monat']].agg('-'.join, axis=1)
    countPivot = countPivot.drop(columns=['Erstinverkehrsetzung_Jahr', 'Erstinverkehrsetzung_Monat'])
    # countPivot = countPivot.set_index('date')
    writeCSV(countPivot, destfilename)
    print('Personenwagen nach Monaten gezählt - MOFIS Tabelle gespeichert')


def aggregate2020Data():
    mofisBASEa = pd.read_csv('data/20210108_mofismonthly_2018.csv', index_col=False)
    mofisBASEb = pd.read_csv('data/20210108_mofismonthly_2019.csv', index_col=False)
    monthlyDataToAdd = pd.read_csv(modifyFilename('mofis_monthly_thisyear.csv'), index_col=False)
    aggregated = mofisBASEa.append(mofisBASEb, ignore_index=True)
    aggregated = aggregated.append(monthlyDataToAdd, ignore_index=True)
    aggregated.fillna(0, inplace=True)
    aggregated.encode('utf-8')
    aggregated.to_csv(modifyFilename('mofisMonthlyComplete.csv'), index=False)
    print('Tabelle 2018-2020 geschrieben')

def aggregateNewData():
    mofisBase = pd.read_csv('data/mofis_BASE2020.csv', index_col=False)
    monthlyDataToAdd = pd.read_csv(modifyFilename('mofis_monthly_thisyear.csv'), index_col=False)
    aggregated = mofisBase.append(monthlyDataToAdd, ignore_index=True)
    aggregated.fillna(0, inplace=True)
    aggregated.to_csv(modifyFilename('mofisMonthlyComplete.csv'), encoding='utf-8', index=False)
    return aggregated

def modifyMonthlyData2021(data):
    # Additional Outputs
    # - Nur Elektrisch
    monthlyElectric = data.filter(['date', 'Elektrisch'])
    writeCSV(monthlyElectric, 'monthlyElectric.csv')

    # - Nur Nicht-elektrisch
    monthlyNonElectric = data.drop(
        ['Elektrisch'], axis=1)
    monthlyNonElectric['Nicht-Elektrisch'] = monthlyNonElectric.sum(axis=1)
    monthlyNonElectric = monthlyNonElectric.filter(['date', 'Nicht-Elektrisch'])
    writeCSV(monthlyNonElectric, 'monthlyNonElectric.csv')

    # - Elektrisch und Nicht-Elektrisch
    monthlyElNonEl = pd.concat([monthlyElectric, monthlyNonElectric['Nicht-Elektrisch']], axis=1)
    print(monthlyElNonEl)
    writeCSV(monthlyElNonEl, 'monthlyElNonEl.csv')
    print('Monatsdaten Abgeschlossen')

def modifyYearlyData2021(dataNew):
    yearly= pd.DataFrame()
    years = [2018,2019,2020,2021]
    for i in years:
        yearly[i] = dataNew[dataNew['date'].str.startswith(str(i))].sum()
    yearly.drop(['date'], inplace=True)
    yearly.to_csv(modifyFilename('mofisYearlyComplete.csv'), encoding='utf-8')
    yearlyBase = pd.read_csv('data/yearlyBASE.csv', index_col=0)
    yearlyElectric = yearlyBase.loc['Elektrisch']
    yearlyElectric.loc[2021] = yearly.loc['Elektrisch'][2021]
    yearlyElectric.drop(labels=['2005','2006','2007','2008', '2009', '2010'], inplace=True)
    yearlyElectric.index.name='date'
    yearlyElectric.to_csv(modifyFilename('yearlyElectric.csv'), encoding='utf-8')
    yearlyNonElBase = yearlyAddNonElectric(yearlyBase)
    yearlyEl = yearly.loc['Elektrisch']
    yearlyNonEl = yearlyAddNonElectric(yearly)
    yearlyNonElBase= yearlyNonElBase.update(yearlyNonEl)
    yearlyElNonEl = pd.concat([yearlyEl, yearlyNonEl], axis=1)
    yearlyElNonEl.to_csv(modifyFilename('mofisYearlyElNonEl.csv'), encoding='utf-8')
    return yearly



def modifyMonthlyData2020(monthlyNEW, monthlyOLD):
    monthlyNEW2020 = monthlyNEW.drop(columns=['2019'])
    monthlyNEW2020['Jahr'] = '2020'
    unique = pd.DataFrame(monthlyNEW2020.Monat.unique(), columns=['Monat'])
    unique.index += 1
    unique['monthnumber'] = list(unique.index)
    unique.monthnumber = unique.monthnumber.astype(str)
    unique['monthnumber'] = unique['monthnumber'].apply(lambda x: x.zfill(2))
    monthlyNEW2020 = monthlyNEW2020.merge(unique, on='Monat', how='left')
    monthlyNEW2020['datestring'] = 0
    monthlyNEW2020['datestring'] = monthlyNEW2020['datestring'].apply(
        lambda x: monthlyNEW2020['Monat'] + ' ' + monthlyNEW2020['Jahr'])
    # monthlyNEW2020['Jahr'] = monthlyNEW2020['Jahr'].apply(lambda x: str(x) + '-' + str(x))
    monthlyNEW2020['Jahr'] = monthlyNEW2020[['Jahr', 'monthnumber']].agg('-'.join, axis=1)
    monthlyNEW2020 = monthlyNEW2020.drop(['Fahrzeuggruppe / -art'], axis=1).rename(columns={'2020': 'n'})
    cols = ['Jahr', 'Monat', 'Treibstoff', 'n', 'monthnumber', 'datestring']
    monthlyNEW2020 = monthlyNEW2020[cols]
    monthlyComplete = pd.concat([monthlyOLD, monthlyNEW2020], axis=0, sort=False)
    writeCSV(monthlyComplete, 'CompleteData.csv')

    # Pivot der Daten
    monthlyPivot = monthlyComplete.pivot(index='Jahr', columns='Treibstoff', values='n')
    writeCSV(monthlyPivot, 'completeDataPivot.csv')

    # Additional Outputs
    # - Nur Elektrisch
    monthlyElectric = monthlyPivot.drop(
        ['Andere', 'Benzin', 'Benzin-elektrisch', 'Diesel', 'Diesel-elektrisch', 'Gas (mono- und bivalent)',
         'Ohne Motor'], axis=1)
    writeCSV(monthlyElectric, 'monthlyElectric.csv')

    # - Nur Nicht-elektrisch
    monthlyNonElectric = monthlyPivot.drop(
        ['Elektrisch'], axis=1)
    monthlyNonElectric['Nicht-Elektrisch'] = monthlyNonElectric.sum(axis=1)
    monthlyNonElectric = monthlyNonElectric.drop(
        ['Andere', 'Benzin', 'Benzin-elektrisch', 'Diesel', 'Diesel-elektrisch', 'Gas (mono- und bivalent)',
         'Ohne Motor'], axis=1
    )
    writeCSV(monthlyNonElectric, 'monthlyNonElectric.csv')

    # - Elektrisch und Nicht-Elektrisch
    monthlyElNonEl = pd.concat([monthlyElectric, monthlyNonElectric], axis=1)
    print(monthlyElNonEl)
    writeCSV(monthlyElNonEl, 'monthlyElNonEl.csv')
    return monthlyPivot
    print('Monatsdaten Abgeschlossen')

def modifyMonthlyData(data):
    data.set_index(['Treibstoff'])
    data = data.drop(columns=['Fahrzeuggruppe / -art'])
    data = data.reset_index()
    data2018 = data.drop(columns=['2019'])
    data2019 = data.drop(columns=['2018'])
    data2019 = data2019.pivot(index='Treibstoff', columns='Monat', values='2019')
    data2018 = data2018.pivot(index='Treibstoff', columns='Monat', values='2018')
    # Sortieren der Spalten - keine Benennung
    data2018 = data2018[
        ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November',
         'Dezember']]
    data2019 = data2019[
        ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November',
         'Dezember']]
    #    data2019 = data2019.columns = ['Januar 2019', 'Februar 2019', 'März 2019', 'April 2019', 'Mai 2019', 'Juni 2019', 'Juli 2019', 'August 2019', 'September 2019', 'Oktober 2019', 'November 2019', 'Dezember 2019']
    #    data2018 = data2018.columns = ['Januar 2018', 'Februar 2018', 'März 2018', 'April 2018', 'Mai 2018', 'Juni 2018', 'Juli 2018', 'August 2018', 'September 2018', 'Oktober 2018', 'November 2018', 'Dezember 2018']
    sum2019 = data2019.sum(axis=1)
    sum2018 = data2018.sum(axis=1)
    writeCSV(sum2018, 'monthlySum2018.csv')
    writeCSV(sum2019, 'monthlySum2019.csv')
    writeCSV(data2019, 'monthly2019.csv')
    writeCSV(data2018, 'monthly2018.csv')
    dataNE2019 = yearlyAddNonElectric(data2019)
    electric2019 = sum2019.loc['Elektrisch']
    ret = {
        'data_2019': data2019,
        'data_NE_2019': dataNE2019,
        'sum_2019': sum2019,
        'sum_2018': sum2018,
        'electric2019': electric2019
    }
    return ret


def completeYearly(monthlydata):
    sumNew = monthlydata.loc['2020-01': '2020-12']
    sumNew = sumNew.sum(axis=0)
    yearly['2020'] = sum2020
    writeCSV(yearly, 'YearlyData_app.csv')
    yearlyelectric = yearly.loc['Elektrisch']
    yearlyelectricexport = yearlyelectric.iloc[4:]
    writeCSV(yearlyelectricexport, 'yearlyElectric.csv')

    yearlynonev = yearlyAddNonElectric(yearly)
    yearlycomplete = pd.DataFrame(dict(Elektrisch=yearlyelectric, Andere=yearlynonev))
    yearlycompleteexport = yearlycomplete.iloc[4:]
    # yearlycomplete = yearlycomplete.rename(columns={'index':'Jahr'})
    writeCSV(yearlycompleteexport, 'yearlyComp.csv')

    return (yearly)


def yearlyAddNonElectric(data):
    dataTemp = data
    dataTemp = dataTemp.drop(['Elektrisch'])
    dataTemp = dataTemp.sum()
    return (dataTemp)


def getTeslaNumbers(data, totalData):
    j = 1
    teslaNumbers = pd.DataFrame(columns=['Monat', 'MonatID', 'Marke', 'Modell', 'Anzahl', 'Differenz'])
    for i in data:
        appendd = data[i][data[i]['Marke'] == 'Tesla']
        appendd.insert(0, 'Monat', i)
        appendd.insert(1, 'MonatID', j)
        appendd.insert(5, 'Differenz', 0)
        if (j > 1):
            for p in appendd['Modell']:
                dx = (appendd[appendd['Modell'] == str(p)]['Anzahl'])
                if (teslaNumbers[teslaNumbers['MonatID'] == (j - 1)][teslaNumbers['Modell'] == str(p)]['Anzahl'].empty):
                    dp = pd.Series(data=[0])
                else:
                    dp = (
                        teslaNumbers[teslaNumbers['MonatID'] == (j - 1)][teslaNumbers['Modell'] == str(p)]['Anzahl'])
                diff = dx.iloc[0] - dp.iloc[0]
                appendd.loc[appendd['Modell'] == str(p), ['Differenz']] = int(diff)
        teslaNumbers = teslaNumbers.append(appendd, ignore_index=True)
        j = j + 1
    teslaNumbers = teslaNumbers.append(
        {'Monat': 'Jan', 'MonatID': 1, 'Marke': 'Tesla', 'Modell': 'Model 3', 'Anzahl': 0, 'Differenz': 0},
        ignore_index=True)
    teslaNumbers = teslaNumbers.sort_values('MonatID', axis=0, ascending=True)
    teslaData = teslaNumbers.reset_index()
    #    totalData = totalData.transpose().reset_index()
    #    totalData.insert(0, 'MonatID', range(1, len(totalData) + 1))
    #    totalData = totalData.set_index('MonatID')
    teslaData = teslaData.pivot(index='MonatID', columns='Modell', values=['Anzahl', 'Differenz'])
    #    totalData = totalData.join(teslaData)
    #    return totalData
    teslaDataDiff = teslaData.drop(columns='Anzahl')

    writeCSV(teslaDataDiff, 'TeslaData.csv')
    return teslaData


def drawTeslaStats(data):
    drawTeslaData(data, query=('Anzahl', 'Model 3'), filename='Model_3', xlab='Monate',
                  title='Insgesamt zugelassene Tesla Model 3')
    drawTeslaData(data, query=('Differenz', 'Model 3'), filename='Model_3_Diff', xlab='Monate',
                  title='Neu zugelassene Tesla Model 3')
    drawTeslaData(data, query=('Differenz', 'Model S'), filename='Model_S_Diff', xlab='Monate',
                  title='Neu zugelassene Tesla Model S')
    print('Teslaplots erfolgreich')


# Methods for drawing plots
def drawTeslaData(data, query='Anzahl', filename='figsingle', xlab='Jahr', recolor=False, title=''):
    objects = data[query]
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=250)
    barlist = plt.bar(y_pos, height=objects)
    if recolor:
        barlist[(len(barlist) - 1)].set_color('r')
    plt.xticks(y_pos, data['Monat'])
    plt.title(title)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_image.png')
    plt.close(fig)
    fig2 = plt.figure()
    barlist = plt.bar(y_pos, height=objects)
    if recolor:
        barlist[(len(barlist) - 1)].set_color('r')
    plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    mpld3.save_html(fig2, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')


def drawSinglePlot(data, filename='figsingle', xlab='Jahr', recolor=False):
    objects = data.loc['Elektrisch',]
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=250)
    barlist = plt.bar(y_pos, height=objects)
    if recolor:
        barlist[(len(barlist) - 1)].set_color('r')
    plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_image.png')
    plt.close(fig)
    fig2 = plt.figure()
    barlist = plt.bar(y_pos, height=objects)
    if recolor:
        barlist[(len(barlist) - 1)].set_color('r')
    plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    mpld3.save_html(fig2, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')


def drawSingleLinePlot(data, filename='lineplot'):
    objects = data.loc['Elektrisch',]
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[13, 6], dpi=250)
    plt.plot(objects, 'o-', linewidth=4, markersize=12)
    #  plt.plot(objects, 'o')
    plt.axis(ymin=0)
    #  plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_image.png')
    # mpld3.show()
    mpld3.save_html(fig, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')


def drawRelativePlot(data, dataSumNE, xlab='Jahr', filename='figboth', recolor=False):
    objects = data
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=72)
    p1 = plt.bar(y_pos, height=objects)
    p2 = plt.bar(y_pos, height=dataSumNE, bottom=objects)
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(ticks=y_pos, labels=dataSumNE.index)
    plt.ylabel('Anteile Gesamte Inverkehrssetzungen')
    plt.xlabel(xlab)
    plt.legend(['Elektroautos', 'Andere Antriebe'])
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
    plt.close(fig)
    fig2 = plt.figure()
    p1 = plt.bar(y_pos, height=objects)
    p2 = plt.bar(y_pos, height=dataSumNE, bottom=objects)
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(ticks=y_pos, labels=dataSumNE.index)
    plt.ylabel('Anteile Gesamte Inverkehrssetzungen')
    plt.xlabel(xlab)
    plt.legend(['Elektroautos', 'Andere Antriebe'])
    mpld3.save_html(fig2, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')
    # lplotly_fig = tls.mpl_to_plotly(fig2)
    # plo.plot(plotly_fig, filename='outputs/plotly/' + genDate() + '_' + filename + '_code.html')


def drawMultiplePlot(data, dataSumNE, xlab='Jahr', filename='figboth', recolor=False):
    objects = data.loc['Elektrisch',]
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=250)
    p1 = plt.bar(y_pos, height=objects)
    p2 = plt.bar(y_pos, height=dataSumNE, bottom=objects)
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.legend(['Elektroautos', 'Andere Antriebe'])
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
    plt.close(fig)
    fig2 = plt.figure()
    p1 = plt.bar(y_pos, height=objects)
    p2 = plt.bar(y_pos, height=dataSumNE, bottom=objects)
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(y_pos, data)
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.legend(['Elektroautos', 'Andere Antriebe'])
    mpld3.save_html(fig, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')


def drawTeslaComp(months, teslaData, totalData, xlab='Monat', filename='figboth', recolor=False):
    print(teslaData)
    objects = pd.concat([months, totalData, teslaData], axis=1)
    objects.columns = ['Monat', 'Total Elektrisch', 'Model 3']
    objects['NonModel3'] = objects['Total Elektrisch'] - objects['Model 3']
    objects['relative'] = (objects['Model 3'] / objects['Total Elektrisch']) * 100
    # drawing the figure itself
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=250)
    p1 = plt.bar(y_pos, height=objects['Model 3'])
    p2 = plt.bar(y_pos, height=objects['NonModel3'], bottom=objects['Model 3'])
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(y_pos, objects['Monat'])
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.legend(['Tesla Model 3', 'Übrige Elektroautos'])
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
    plt.close(fig)
    return objects
