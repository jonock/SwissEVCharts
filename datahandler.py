import pandas as pd
import requests
import json
import mpld3
import matplotlib.pyplot as plt, mpld3
import numpy as np
from datetime import date
import csv
import calendar
import plotly.plotly as py
import plotly.tools as tls
import plotly.offline as plo


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
    r.to_csv(filename)
    print('CSV ' + filename + ' Geschrieben.')


def importData(filename=modifyFilename('yearlyData.csv')):
    data = pd.read_csv(filename, sep=',', header=0, index_col=0)
    return (data)


def importMonthlyData(filename=modifyFilename('monthlyData.csv')):
    monthlyData = pd.read_csv(filename, sep=',', header=0, index_col=0)
    return (monthlyData)


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
                        "7"
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


def modifyMonthlyData(data):
    data.set_index(['Treibstoff'])
    data = data.drop(columns=['Fahrzeuggruppe / -art'])
    data = data.reset_index()
    data2018 = data.drop(columns=['2019'])
    data2019 = data.drop(columns=['2018'])
    data2019 = data2019.pivot(index='Treibstoff', columns='Monat', values='2019')
    data2018 = data2018.pivot(index='Treibstoff', columns='Monat', values='2018')
    data2019 = data2019[['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli']]
    sum2019 = data2019.sum(axis=1)
    sum2018 = data2018.sum(axis=1)
    data2018 = data2018[['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli']]
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


def completeYearly(monthlydata, yearly):
    sum2019 = monthlydata.get('sum_2019')
    sum2019 = sum2019.rename('2019')
    yearly = yearly.merge(sum2019, left_index=True, right_index=True)
    return (yearly)


def yearlyAddNonElectric(data):
    dataTemp = data
    dataTemp = dataTemp.drop(['Elektrisch'])
    dataTemp = dataTemp.sum()
    return (dataTemp)


def getTeslaNumbers(data):
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
    return teslaNumbers


def drawTeslaStats(data):
    drawTeslaData(data[data['Modell'] == 'Model 3'], filename='Model_3', xlab='Monate',
                  title='Insgesamt zugelassene Tesla Model 3')
    drawTeslaData(data[data['Modell'] == 'Model 3'], query='Differenz', filename='Model_3_Diff', xlab='Monate',
                  title='Neu zugelassene Tesla Model 3')
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
    plotly_fig = tls.mpl_to_plotly(fig2)
    plo.plot(plotly_fig, filename='outputs/plotly/' + genDate() + '_' + filename + '_code.html')


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


def drawTeslaComp(teslaData, totalData, xlab='Monat', filename='figboth', recolor=False):
    print(teslaData)
    teslaData = teslaData.reset_index()
    totalData = totalData.reset_index()
    objects = pd.concat([totalData, teslaData], axis=1).reset_index().drop(['index', 'level_0'], axis=1)
    objects.columns = ['Monat', 'Total Elektrisch', 'Model3']
    objects['NonModel3'] = objects['Total Elektrisch'] - objects['Model3']
    objects['relative'] = (objects['Model3'] / objects['Total Elektrisch']) * 100
    # drawing the figure itself
    y_pos = np.arange(len(objects))
    fig = plt.figure(figsize=[16, 9], dpi=250)
    p1 = plt.bar(y_pos, height=objects['Model3'])
    p2 = plt.bar(y_pos, height=objects['NonModel3'], bottom=objects['Model3'])
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    plt.xticks(y_pos, objects['Monat'])
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.legend(['Tesla Model 3', 'Übrige Elektroautos'])
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
    plt.close(fig)
    if recolor:
        p1[(len(p1) - 1)].set_color('C3')
        p2[(len(p2) - 1)].set_color('#FFC080')
    fig2 = plt.figure(figsize=[16, 9], dpi=250)
    plt.ylim(0, 100)
    p1 = plt.bar(y_pos, height=objects['relative'])
    # p2 = plt.bar(y_pos, height=(100 - objects['relative']), bottom=objects['relative'])
    plt.xticks(y_pos, objects['Monat'])
    plt.ylabel('Zulassungen')
    plt.xlabel(xlab)
    plt.savefig('outputs/png/' + genDate() + '_' + filename + '_relative.png')
    mpld3.save_html(fig, 'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')
    return objects
