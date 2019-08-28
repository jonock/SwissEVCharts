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
    teslaNumbers = dh.getTeslaNumbers(asData)
    #  dh.drawTeslaStats(teslaNumbers)
    global model3Numbers
    model3Numbers = dh.drawTeslaComp(
        teslaNumbers[teslaNumbers['Modell'] == 'Model 3'].sort_values('MonatID', axis=0, ascending=True).loc[:,
        'Differenz'], monthlydata.get('data_2019').loc['Elektrisch',], filename='Model_3_vs_total')


gatherData()
processDataBFS()
gatherAutoSchweiz()
processDataAS()

print('Erfolg.')


#nonelectric = addNonElectric(data)
#drawSinglePlot(data)
#drawMultiplePlot(data,nonelectric
