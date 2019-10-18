import pandas as pd
import webbrowser
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
import time
import csv
from credentials import dwToken


# DataWrapper API Connection
def dataWrapperConnect():
    print(dwToken + ' ist der Token. Erfolgreich geladen')
    headers = {
        'Authorization': f'Bearer {dwToken}',
    }

    response = requests.get('https://api.datawrapper.de/account', headers=headers)
    print(response.text)
    return response


def createDWChart(title="Test"):
    headers = {
        'Authorization': f'Bearer {dwToken}',
    }

    data = {
        "title": title,
        "type": "d3-lines"
    }

    response = requests.post('https://api.datawrapper.de/v3/charts', headers=headers, data=data)
    resp = response.json()
    print('New Chart created with id :' + resp['id'])
    id = resp['id']
    return id


def addDWData(id, dataimp):
    headers = {
        'authorization': f'Bearer {dwToken}',
        'content-type': 'text/csv'
    }
    print(id)
    print(dataimp)
    data = dataimp.to_csv(f'data/dwcharts/{id}_data.csv', index=True, encoding='utf-8')
    print(repr(data))
    url = f'https://api.datawrapper.de/charts/{id}/data'

    #    respo = requests.put(url, headers=headers, data=data)
    #    webbrowser.open(f'https://datawrapper.de/chart/{id}/upload')
    headers = {
        'authorization': f'Bearer {dwToken}'
    }
    print((requests.get(url=f'https://api.datawrapper.de/v3/charts/{id}/data', headers=headers).json()))

    metadata = {
        'title': 'newTitleSet',
        'type': 'd3-bars',
    }
    # response = requests.put(url = f'https://api.datawrapper.de/charts/{id}', headers=headers, data=json.dumps(metadata))

    # print(response.json())


def getChartMetadata(id):
    headers = {
        'authorization': f'Bearer {dwToken}'
    }
    metadataJson = requests.get(url=f'https://api.datawrapper.de/v3/charts/{id}', headers=headers)
    metadataDict = metadataJson.json()
    print('Metadaten erhalten')
    return metadataDict, metadataJson


def metaDatatemp():
    metadata, metadataJson = getChartMetadata('f8YHe')
    pd.DataFrame.from_dict(metadata['metadata']['visualize']).to_csv('meta.csv')
