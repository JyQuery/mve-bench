# https://dev.applicationinsights.io/reference
import json
from datetime import datetime
import requests


def postMetric(functionList, func, metric=None, timespan='PT1H', interval='PT1M'):
    headers = {
        "x-api-key": functionList[func]["apiKey"]
    }
    url = 'https://api.applicationinsights.io/v1/apps/' + functionList[func]["applicationId"] + '/metrics'

    body = [
        {
            "id": "processCpuPercentage",
            "parameters": {
                "metricId": "performanceCounters/processCpuPercentage",
                "aggregation": "avg",
                "timespan": "PT1H",
                "interval": "PT1S"
            }
        },
        {
            "id": "memoryAvailableBytes",
            "parameters": {
                "metricId": "performanceCounters/memoryAvailableBytes",
                "aggregation": "avg",
                "timespan": "PT1H",
                "interval": "PT1S"
            }
        },
        {
            "id": "processIOBytesPerSecond",
            "parameters": {
                "metricId": "performanceCounters/processIOBytesPerSecond",
                "aggregation": "avg",
                "timespan": "PT1H",
                "interval": "PT1S"
            }
        }
    ]
    response = requests.post(url, headers=headers, json=body)
    # print(response.json())
    return response.json()


def insightQuery(functionList, func, timespan, startTime, endTime=None, table='requests'):
    # print(functionList[fun])
    headers = {
        "x-api-key": functionList[func]["apiKey"]
    }

    params = {}

    queryStr = '{} | where timestamp >= datetime("{}")'.format(table, startTime)
    if endTime is not None:
        queryStr += ' and timestamp <= datetime("{}")'.format(endTime)


    if table == "requests":
        queryStr += ' and name == "{}"'.format(func)

    params = {
        ("timespan", timespan),
        ("query", queryStr)  # take n
    }


    # if table == "performanceCounters":
    #     params = {
    #         ("timespan", timespan),
    #         ("query", '{} | where timestamp >= datetime("{}")'.format(table, startTime))  # take n
    #     }
    # if table == "requests":


    url = 'https://api.applicationinsights.io/v1/apps/' + functionList[func]["applicationId"] + '/query'

    print(params)
    response = requests.get(url, headers=headers, params=params)
    # print(response.content)
    return response.json()


if __name__ == "__main__":
    with open("config.json") as configFile:
        config = json.load(configFile)


    # print(datetime("2021-05-26T19:31:26Z"))
    # print(str(datetime.utcnow()))
    # serverList = config['servers']
    functionList = config['functions']

    tables = ["requests", "traces"]
    # for table in tables:
    #     res = insightQuery(functionList, "PopulateAzure", 'PT6H', '2021-07-02 17:31:01', '2021-07-02 17:48:30', table=table)
    #     print(res)
    #     fileName = "result/20210702230000.exp1.2.terrain/function-PopulateAzure-1s-" + table
    #     with open(fileName, "w") as f:
    #         json.dump(res["tables"][0], f)
    #     print(len(res["tables"][0]["rows"]))

    res = insightQuery(functionList, "PopulateAzure", 'P30D', '2021-07-02 17:19:47', endTime='2021-07-02 17:26:08'
                       , table='traces')
    print(res)
    fileName = "result/20210702230000.exp1.2.terrain/function-PopulateAzure-0.1s-traces"
    with open(fileName, "w") as f:
        json.dump(res["tables"][0], f)
    print(len(res["tables"][0]["rows"]))


