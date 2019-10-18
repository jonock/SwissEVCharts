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



def gatherData():
    dh.getMonthlyData()
    dh.getYearlyData()


def processDataBFS():
    global yearly
    yearly = dh.importData()
    global monthly
    monthly = dh.importMonthlyData()
    global monthlydata
    monthlydata = dh.modifyMonthlyData(monthly)
    global yearlyComplete
    yearlyComplete = dh.completeYearly(monthlydata, yearly)


def drawBFS():
    dh.drawSinglePlot(yearlyComplete, recolor=True)
    dh.drawMultiplePlot(yearlyComplete, dh.yearlyAddNonElectric(yearlyComplete),filename='multipleComplete', recolor=True)
    dh.drawSinglePlot(monthlydata.get('data_2019'), 'monthlySingle', 'Monat')
    dh.drawSingleLinePlot(monthlydata.get('data_2019'))
    dh.drawMultiplePlot(monthlydata.get('data_2019'),monthlydata.get('data_NE_2019'),'Monat','monthlyStacked')
    dh.drawRelativePlot((monthlydata.get('data_2019')).loc['Elektrisch',]/(monthlydata.get('data_2019').sum()),monthlydata.get('data_NE_2019')/(monthlydata.get('data_2019').sum()), 'Monat', filename='relativeValuesMonthly')
    dh.drawRelativePlot(yearlyComplete.loc['Elektrisch',]/yearlyComplete.sum(), dh.yearlyAddNonElectric(yearlyComplete)/yearlyComplete.sum(), xlab='Jahr', filename='relativeYearly', recolor=True)
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
        if len(row['id']) < 3:
            index = dk.createDWChart(row['title'])
            print(index)
            row['id'] = index
            chartIndex.loc[i, 'id'] = index
            print(chartIndex.loc[i])
        dk.addDWData(row['id'], eval(row['query']))
        print('Chart ' + row['title'] + 'mit Daten beschickt')


global chartIndex
chartIndex = ca.chartAdmin()

# gatherData()
#gatherAutoSchweiz()
processDataBFS()
processDataAS()
drawBFS()
drawAS()
kickdatawrapper()
ca.chartIndexHousekeeping(chartIndex)

print('Erfolg.')



#nonelectric = addNonElectric(data)
#drawSinglePlot(data)
#drawMultiplePlot(data,nonelectric
