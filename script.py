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


def processData():
    yearly = dh.importData()
    monthly = dh.importMonthlyData()
    monthlydata = dh.modifyMonthlyData(monthly)
    yearlyComplete = dh.completeYearly(monthlydata, yearly)
    dh.drawSinglePlot(yearlyComplete, recolor=True)
    dh.drawMultiplePlot(yearlyComplete, dh.yearlyAddNonElectric(yearlyComplete),filename='multipleComplete', recolor=True)
    dh.drawSinglePlot(monthlydata.get('data_2019'), 'monthlySingle', 'Monat')
    dh.drawSingleLinePlot(monthlydata.get('data_2019'))
    dh.drawMultiplePlot(monthlydata.get('data_2019'),monthlydata.get('data_NE_2019'),'Monat','monthlyStacked')
    print('success')


processData()


#nonelectric = addNonElectric(data)
#drawSinglePlot(data)
#drawMultiplePlot(data,nonelectric