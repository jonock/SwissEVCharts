
import pandas as pd
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
    global chartIndex
    chartIndex = ca.chartAdmin()
    global mofis_latestupdate
    mofis_latestupdate = open('latestupdateMOFIS.txt', 'r').read()
    dk.dataWrapperConnect()
    for i, row in chartIndex.iterrows():
        print(str(i) + ' und ' + str(row));
        try:
            dk.updatedwchart(row['id'], filename=dh.modifyFilename(row['filename']), timeframe=mofis_latestupdate)
            print('Chart ' + row['title'] + ' mit Daten beschickt')
        except:
            print('Chart ' + row['title'] + ' hat nicht funktioniert')

def processMOFISData():
    dh.getMOFISData()
    dh.importMOFISdata()
    dh.modifyMOFISData()
    monthlydata = dh.aggregateNewData()
    dh.modifyMonthlyData2021(monthlydata)
    dh.modifyYearlyData2021(monthlydata)


# gatherData()
# gatherAutoSchweiz()
# processDataBFS()
# processDataAS()
# drawBFS()
# drawAS()
processMOFISData()
kickdatawrapper()
#ca.chartIndexHousekeeping(chartIndex)
# csvcorrections()
# fu.ftpupload('data/dwcharts/')
# print('Erfolg.')

# nonelectric = addNonElectric(data)
# drawSinglePlot(data)
# drawMultiplePlot(data,nonelectric

print('das Skript ist bis zum Schluss gelaufen. Wer hätte das gedacht...')
