import numpy
import pandas as pd
import requests
import json
import mpld3
import matplotlib.pyplot as plt, mpld3
import numpy as np
import csv
import plotly
import calendar
import datahandler as dh
import datakicker as dk
import chartadmin as ca
import ftpupload as fu


def gatherData():
    dh.getMonthlyData()
    dh.getYearlyData()


def processDataBFS():
    global yearly
    yearly = dh.importData()
    global monthly
    monthlyNEW, monthlyOLD = dh.importMonthlyData()
    global monthlydata
    monthlydata = dh.modifyMonthlyData2020(monthlyNEW, monthlyOLD)
    global yearlyComplete
    yearlyComplete = dh.completeYearly(monthlydata, yearly)


def processData2021():
    global yearly
    yearly = dh.importData()
    global monthly


def drawBFS():
    dh.drawSinglePlot(yearlyComplete, recolor=True)
    dh.drawMultiplePlot(yearlyComplete, dh.yearlyAddNonElectric(yearlyComplete), filename='multipleComplete',
                        recolor=True)
    dh.drawSinglePlot(monthlydata.get('data_2019'), 'monthlySingle', 'Monat')
    dh.drawSingleLinePlot(monthlydata.get('data_2019'))
    dh.drawMultiplePlot(monthlydata.get('data_2019'), monthlydata.get('data_NE_2019'), 'Monat', 'monthlyStacked')
    dh.drawRelativePlot((monthlydata.get('data_2019')).loc['Elektrisch',] / (monthlydata.get('data_2019').sum()),
                        monthlydata.get('data_NE_2019') / (monthlydata.get('data_2019').sum()), 'Monat',
                        filename='relativeValuesMonthly')
    dh.drawRelativePlot(yearlyComplete.loc['Elektrisch',] / yearlyComplete.sum(),
                        dh.yearlyAddNonElectric(yearlyComplete) / yearlyComplete.sum(), xlab='Jahr',
                        filename='relativeYearly', recolor=True)
    relative = yearlyComplete.loc['Elektrisch',]/yearlyComplete.sum(), dh.yearlyAddNonElectric(yearlyComplete)/yearlyComplete.sum()
    print(relative)
    print('success')


def gatherAutoSchweiz():
    dh.requestdataAS()


def processDataAS():
    asData = dh.importDataAS()
    global teslaNumbers
    teslaNumbers = dh.getTeslaNumbers(asData, monthlydata.get('data_2019'))


def drawAS():
    dh.drawTeslaStats(teslaNumbers)
    # global model3Numbers
    # model3Numbers = dh.drawTeslaComp(
    #    teslaNumbers['Monat'], teslaNumbers[('Differenz', 'Model 3')], teslaNumbers[('Elektrisch')],filename='Model_3_vs_total')


def kickdatawrapper():
    dk.dataWrapperConnect()
    for i, row in chartIndex.iterrows():
        print(str(i) + ' und ' + str(row));
        dk.updatedwchart(row['id'], dh.modifyFilename(row['filename']))
        print('Chart ' + row['title'] + 'mit Daten beschickt')


global chartIndex
chartIndex = ca.chartAdmin()



def csvcorrections():
    # hardcoded stuff for nasty mistakes due to improper coding...
    data = pd.read_csv('data/dwcharts/t--N8_data.csv', header=0,
                       names=['MonatID', 'Monat', 'Model 3', 'Model S', 'Model X'])
    data = data.drop('MonatID', axis=1)
    data.to_csv('data/dwcharts/t--N8_data.csv', index=False)


def processMOFISData():
    dh.getMOFISData()
    dh.importMOFISdata()
    dh.modifyMOFISData()
    dh.aggregateNewData()


# gatherData()
# gatherAutoSchweiz()
# processDataBFS()
# processDataAS()
# drawBFS()
# drawAS()
processMOFISData()
kickdatawrapper()
ca.chartIndexHousekeeping(chartIndex)
# csvcorrections()
# fu.ftpupload('data/dwcharts/')
# print('Erfolg.')

# nonelectric = addNonElectric(data)
# drawSinglePlot(data)
# drawMultiplePlot(data,nonelectric

print('das Skript ist bis zum Schluss gelaufen. Wer hätte das gedacht...')
