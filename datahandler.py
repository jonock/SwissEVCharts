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



def genDate():
    today = date.today()
    return today.strftime("%Y%m%d")


def modifyFilename(filename):
    filename = './data/' + genDate() + '_' + filename
    return filename


def requestdata(url, payload):
    r = requests.post(url, data=json.dumps(payload))
    return r


def writeData(r, filename='data.csv'):
    with open(filename, 'w') as outfile:
        outfile.write(r.text)
    print('Daten in ' + filename + ' geschrieben')


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
              "5"
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
    r = requestdata(url, payload)
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
    r = requestdata(url, payload)
    writeData(r, filename)


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

def modifyMonthlyData(data):
  data.set_index(['Treibstoff'])
  data = data.drop(columns=['Fahrzeuggruppe / -art'])
  data = data.reset_index()
  data2018 = data.drop(columns=['2019'])
  data2019 = data.drop(columns=['2018'])
  data2019 = data2019.pivot(index='Treibstoff', columns='Monat', values='2019')
  data2018 = data2018.pivot(index='Treibstoff', columns='Monat', values='2018')
  data2019 = data2019[['Januar', 'Februar', 'März', 'April']]
  sum2019 = data2019.sum(axis=1)
  sum2018 = data2018.sum(axis=1)
  data2018 = data2018[['Januar', 'Februar', 'März', 'April']]
  writeCSV(sum2018, 'monthlySum2018.csv')
  writeCSV(sum2019, 'monthlySum2019.csv')
  writeCSV(data2019,'monthly2019.csv')
  writeCSV(data2018,'monthly2018.csv')
  dataNE2019 = yearlyAddNonElectric(data2019)
  electric2019 = sum2019.loc['Elektrisch']
  ret = {
      'data_2019':data2019,
      'data_NE_2019':dataNE2019,
      'sum_2019':sum2019,
      'sum_2018':sum2018,
      'electric2019': electric2019
  }
  return ret

def completeYearly(monthlydata, yearly):
    sum2019 = monthlydata.get('sum_2019')
    sum2019 = sum2019.rename('2019')
    yearly = yearly.merge(sum2019, left_index=True, right_index=True)
    return(yearly)

def yearlyAddNonElectric(data):
  dataTemp = data
  dataTemp = dataTemp.drop(['Elektrisch'])
  dataTemp = dataTemp.sum()
  return(dataTemp)

def drawSinglePlot(data,filename='figsingle', xlab = 'Jahr',recolor=False):
  objects = data.loc['Elektrisch',]
  y_pos = np.arange(len(objects))
  fig = plt.figure(figsize= [16,9], dpi=250)
  barlist = plt.bar(y_pos, height = objects)
  if recolor:
    barlist[(len(barlist)-1)].set_color('r')
  plt.xticks(y_pos, data)
  plt.ylabel('Zulassungen')
  plt.xlabel(xlab)
  plt.show()
  plt.savefig('outputs/png/' + genDate() + '_' + filename + '_image.png')
  #mpld3.show()
  mpld3.save_html(fig,'outputs/mpld3/' + genDate() + '_' + filename+'_code.html')

def drawSingleLinePlot(data,filename='lineplot'):
  objects = data.loc['Elektrisch',]
  y_pos = np.arange(len(objects))
  fig = plt.figure(figsize= [13,6], dpi=250)
  plt.plot(objects,'o-', linewidth=4, markersize=12 )
#  plt.plot(objects, 'o')
  plt.axis(ymin = 0)
#  plt.xticks(y_pos, data)
  plt.ylabel('Zulassungen')
  plt.show()
  plt.savefig('outputs/png/' + genDate() + '_' + filename + '_image.png')
  #mpld3.show()
  mpld3.save_html(fig,'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')

def drawRelativePlot(data,dataSumNE,xlab='Jahr',filename='figboth', recolor=False):
  objects = data
  y_pos = np.arange(len(objects))
  fig = plt.figure(figsize= [16,9], dpi=72)
  p1 = plt.bar(y_pos, height = objects)
  p2 = plt.bar(y_pos, height = dataSumNE, bottom=objects)
  if recolor:
    p1[(len(p1)-1)].set_color('C3')
    p2[(len(p2)-1)].set_color('#FFC080')
  plt.xticks(ticks=y_pos,labels=dataSumNE.index)
  plt.ylabel('Anteile Gesamte Inverkehrssetzungen')
  plt.show()
  plt.xlabel(xlab)
  plt.legend(['Elektroautos','Andere Antriebe'])
  plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
  #mpld3.show()
  mpld3.save_html(fig,'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')
  plotly_fig = tls.mpl_to_plotly(fig)
  plo.plot(plotly_fig, filename='outputs/plotly/' + genDate() + '_' + filename + '_code.html')

def drawMultiplePlot(data,dataSumNE,xlab='Jahr',filename='figboth', recolor=False):
  objects = data.loc['Elektrisch',]
  y_pos = np.arange(len(objects))
  fig = plt.figure(figsize= [16,9], dpi=250)
  p1 = plt.bar(y_pos, height = objects)
  p2 = plt.bar(y_pos, height = dataSumNE, bottom=objects)
  if recolor:
    p1[(len(p1)-1)].set_color('C3')
    p2[(len(p2)-1)].set_color('#FFC080')
  plt.xticks(y_pos, data)
  plt.ylabel('Zulassungen')
  plt.show()
  plt.xlabel(xlab)
  plt.legend(['Elektroautos','Andere Antriebe'])
  plt.savefig('outputs/png/' + genDate() + '_' + filename + '_legend.png')
  #mpld3.show()
  mpld3.save_html(fig,'outputs/mpld3/' + genDate() + '_' + filename + '_code.html')