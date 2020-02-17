import os.path
import pandas as pd


def chartAdmin():
    if os.path.exists('chartindex.csv'):
        ci = loadChartIndex()
        print('chartIndex gefunden und geladen')
        return ci
    else:
        ci = createChartIndex()
        print('neuer chartIndex angelegt')
        return ci


def chartIndexHousekeeping(data):
    writeChartIndex(data)
    print('ChartIndex aktualisiert gespeichert')


def createChartIndex():
    global chartIndex
    chartIndex = pd.DataFrame(data={'id': [0, 0, 0, 0], 'title': ['Jährliche Zulassungen von Elektroautos',
                                                                  'Jährliche Zulassungen aller Antriebsarten',
                                                                  'Monatliche Zulassungen von Elektroautos seit 2018',
                                                                  'Monatliche Zulassungen aller Antriebsarten seit 2018'],
                                    'filename': ['yearlyElectric.csv', 'yearlyData.csv', 'monthlyElectric.csv',
                                                 'completeDataPivot.csv']})
    return chartIndex


def writeChartIndex(data):
    data.to_csv('chartindex.csv', sep=';')
    print('Chartindex gespeichert')


def loadChartIndex():
    data = pd.read_csv('chartindex.csv', sep=';', header=0, index_col=0)
    return (data)
