import json
import math
import os
import statistics
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from kaleido.scopes.plotly import PlotlyScope
import plotly.express as px
import seaborn as sns
from scipy.stats import stats
from util import findFileinPath

# def plotExp1_1_getListJson(fileDur):
#     dur = []
#     with open(fileDur) as f:
#         durObj = json.load(f)
#     for row in durObj["rows"]:
#         dur.append(row[7])
#     return dur

timeFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
ttpRemote = []
ttpLocal = []


def plotExp1_1_getListFile(fileStr):
    with open(fileStr, "r") as f:
        lines = f.readlines()

    tmp = []
    for line in lines:
        val = float(line.split(",")[2].replace("\n", "")) * 1000
        tmp.append(val)
    return tmp


def processDur(fileDur, expName=None, maxval=1500):
    dfs = []
    if expName is None:
        shouldGetName = True
    else:
        shouldGetName = False

    for i in range(len(fileDur)):
        if shouldGetName:
            expName = plotExp1GetExpName(i)
        # dur = plotExp1_1_getListJson(fileDur[i])

        with open(fileDur[i]) as f:
            durObj = json.load(f)

        tmp = []
        # for val in dur:
        for row in durObj["rows"]:
            # val = row[7]
            val = float(json.loads(row[10])["FunctionExecutionTimeMs"])
            if val < maxval:
                tmp.append({"Invocation Interval": expName,
                            "Metric": "Function Duration",
                            "Value": val,
                            "TimeStamp": row[0]})
        tmpDf = pd.DataFrame(tmp)
        if tmpDf.size > 0:
            print("exp", expName)
            print("dur mean", tmpDf["Value"].mean())
            print("max", tmpDf["Value"].max())
            print("min", tmpDf["Value"].min())
            print("99p", tmpDf["Value"].quantile(0.99))
            print("95p", tmpDf["Value"].quantile(0.95))
            print("\n")
            dfs.append(tmpDf)
    return dfs


def processE2E(fileE2E, expName=None, maxval=700000, factor=1):
    dfs = []
    if expName is None:
        shouldGetName = True
    else:
        shouldGetName = False

    for i in range(len(fileE2E)):
        if shouldGetName:
            expName = plotExp1GetExpName(i)
        print(fileE2E[i])

        with open(fileE2E[i], "r") as f:
            lines = f.readlines()

        tmp = []
        for line in lines:
            val = float(line.split(",")[2].replace("\n", ""))

            if val < maxval:
                tmp.append({"Invocation Interval": expName, "Metric": "End-to-End", "Value": val})

        tmpDf = pd.DataFrame(tmp)
        if factor != 1:
            tmpDf["Value"] *= factor
        print("mean", tmpDf["Value"].mean())
        print("min", tmpDf["Value"].min())
        print("max", tmpDf["Value"].max())
        print("99p", tmpDf["Value"].quantile(0.99))
        print("95p", tmpDf["Value"].quantile(0.95))

        dfs.append(tmpDf)
    return dfs


def plotExp1Sn(fileDur, fileE2E, name, ylim=None):
    dfs = processDur(fileDur)
    dfs.extend(processE2E(fileE2E, factor=1000))

    allDf = pd.concat(dfs)
    print(allDf)
    print(allDf[allDf["Metric"] == "Function Duration"]["Value"].max())

    plt.figure(figsize=(4, 5), dpi=100)
    sns.boxplot(data=allDf, x='Invocation Interval', y='Value', hue='Metric')
    plt.xlabel("Invocation Interval")
    plt.ylabel("Latency (ms)")
    plt.legend(title="Metric", loc="lower center")
    plt.ylim(0)
    plt.tight_layout()
    plt.savefig(name)

    plt.show()


def plotExp1_1():
    # fileDur = ["result/20210621104600.exp1.2.5s/function-PopulateAzure-requests-20210621104600",
    #            "result/20210621112400.exp1.2.1s/function-PopulateAzure-requests-20210621112400",
    #            "result/20210621113700.exp1.2.0.1s/function-PopulateAzure-requests-20210621113700"]
    #
    # fileE2E = ["result/20210621104600.exp1.2.5s/e2e-latency-202106211050",
    #            "result/20210621112400.exp1.2.1s/e2e-latency-202106211124",
    #            "result/20210621113700.exp1.2.0.1s/e2e-latency-202106211137"]

    # fileDur = ["result/20210702213000.exp1.2.terrain/function-PopulateAzure-requests-5s",
    #            "result/20210702213000.exp1.2.terrain/function-PopulateAzure-requests-1s",
    #            "result/20210702213000.exp1.2.terrain/function-PopulateAzure-requests-0.1s"]

    # fileE2E = ["result/20210702213000.exp1.2.terrain/e2e.1.2.5s",
    #            "result/20210702213000.exp1.2.terrain/e2e.1.2.1s",
    #            "result/20210702213000.exp1.2.terrain/e2e.1.2.0.1s"]

    fileDur = ["result/20210702230000.exp1.2.terrain/function-PopulateAzure-5s-requests",
               "result/20210702230000.exp1.2.terrain/function-PopulateAzure-1s-requests",
               "result/20210702230000.exp1.2.terrain/function-PopulateAzure-0.1s-requests"]

    fileE2E = ["result/20210702230000.exp1.2.terrain/e2e.1.2.5s",
               "result/20210702230000.exp1.2.terrain/e2e.1.2.1s",
               "result/20210702230000.exp1.2.terrain/e2e.1.2.0.1s"]

    plotExp1Sn(fileDur, fileE2E, "exp1.1.pdf", ylim=[0, 700])


def plotExp1_2():
    # Old v1 storage account
    # fileDur = [
    # "result/20210621155000.exp1.1.5s/function-PlayerOperation-requests-20210621155000",
    # "result/20210621145000.exp1.1.1s/function-PlayerOperation-requests-20210621145000",
    # "result/20210621160500.exp1.1.0.1s/function-PlayerOperation-requests-20210621160500",
    # "result/20210621222500.exp2.a1/function-PlayerOperation-requests-20210621222500",
    # "result/20210621234000.exp2.a2.v2storage/function-PlayerOperation-requests-20210621234000"
    # ]

    # fileE2E = [
    # "result/20210621155000.exp1.1.5s/e2e-latency-1.1-5s",
    # "result/20210621145000.exp1.1.1s/e2e-latency-1.1-1s",
    # "result/20210621160500.exp1.1.0.1s/e2e-latency-1.1-0.1s",
    # "result/20210621222500.exp2.a1/e2e.exp2.a1",
    # "result/20210621234000.exp2.a2.v2storage/e2e.a2"
    # ]

    # # v2 standard
    # fileDur = [
    #     "result/20210622114000.exp1.1.v2.5s/function-PlayerOperation-requests-20210622114000",
    #     "result/20210622112400.exp1.1.v2.1s/function-PlayerOperation-requests-20210622112400",
    #     "result/20210622123000.exp1.1.v2.0.1s/function-PlayerOperation-requests-20210622123000"
    # ]
    #
    # fileE2E = [
    #     "result/20210622114000.exp1.1.v2.5s/e2e.exp1.5.v2",
    #     "result/20210622112400.exp1.1.v2.1s/e2e.exp1.1.v2",
    #     "result/20210622123000.exp1.1.v2.0.1s/e2e.exp1.0.1.v2"
    # ]

    # v2 Premium
    fileDur = [
        "result/20210626224700.exp1.1.premium.5s/function-PlayerOperation-requests-20210626224700",
        "result/20210626224700.exp1.1.premium.1s/function-PlayerOperation-requests-20210626224700",
        "result/20210626224700.exp1.1.premium.0.1s/function-PlayerOperation-requests-20210626224700"
    ]

    fileE2E = [
        "result/20210626224700.exp1.1.premium.5s/e2e.5s.premium",
        "result/20210626224700.exp1.1.premium.1s/e2e.1s.premium",
        "result/20210626224700.exp1.1.premium.0.1s/e2e.0.1s.premium"
    ]

    plotExp1Sn(fileDur, fileE2E, "exp1.2.pdf")


def plotExp1_3():
    fileDur = [
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-5s",
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-1s",
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-0.1s"
    ]

    fileE2E = [
        "result/20210702190000.exp1.3.sql/e2e.sql.5s",
        "result/20210702190000.exp1.3.sql/e2e.sql.1s",
        "result/20210702190000.exp1.3.sql/e2e.sql.0.1s"
    ]

    plotExp1Sn(fileDur, fileE2E, "exp1.3.pdf")


def plotExp1_2_3_6():
    fileE2E = [
        "result/exp1.5.premiun.sql/e2e.small.5s",
        "result/exp1.5.premiun.sql/e2e.small.1s",
        "result/exp1.5.premiun.sql/e2e.small.0.1s",
        "result/exp1.5.premiun.sql/e2e.small.2h"
    ]

    fileE2ESQL = [
        "result/exp1.5.premiun.sql/sql.e2e.5s",
        "result/exp1.5.premiun.sql/sql.e2e.1s",
        "result/exp1.5.premiun.sql/sql.e2e.0.1s",
        "result/exp1.5.premiun.sql/sql.e2e.2h"
    ]

    dfs = processE2E(fileE2E)
    allDf = pd.concat(dfs)
    allDf = allDf[allDf["Metric"] == "End-to-End"]
    allDf["Service"] = "Premium Storage"

    print("Premiun mean", allDf["Value"].mean())

    dfsSQL = processE2E(fileE2ESQL)
    allDfSQL = pd.concat(dfsSQL)
    allDfSQL = allDfSQL[allDfSQL["Metric"] == "End-to-End"]
    allDfSQL["Service"] = "Serverless SQL"
    all = pd.concat([allDf, allDfSQL])
    print("SQL mean", allDfSQL["Value"].mean())

    fig, (ax, ax2) = plt.subplots(sharex=True, nrows=2, ncols=1, figsize=(5, 4),
                                  gridspec_kw={'height_ratios': [2, 5]})

    allupper = all[all["Value"] >= 5000]
    sns1 = sns.boxplot(data=all, x='Invocation Interval', y='Value',
                       hue='Service', order=["0.1s", "1s", "5s", "2h"], ax=ax)

    sns2 = sns.boxplot(data=all, x="Invocation Interval", y='Value',
                       hue='Service', order=["0.1s", "1s", "5s", "2h"], ax=ax2)
    sns1.get_legend().remove()
    sns2.get_legend().remove()
    ax.set_ylim(140, 90000)
    ax2.set_ylim(0, 140)
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()

    # ax.tick_params(labeltop=False)
    ax.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)
    ax2.xaxis.tick_bottom()
    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    ax2.set_ylabel("End-to-end Latency (ms)", loc="top")
    # ax2.set_ylabel("End-to-end Latency (s)")
    ax.set_xlabel("Invocation Interval", loc="right")
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    ax2.yaxis.label.set_visible(False)
    fig.text(0.0, 0.5, 'End-to-end Latency (ms)', va='center', rotation='vertical')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, 0.78))
    # , bbox_to_anchor = (0.5, 0.70)

    plt.savefig("exp1.2-6.pdf", dpi=fig.dpi)

    plt.show()


def plotExp1_2_3_5():
    fileE2E = [
        "result/exp1.5.premiun.sql/e2e.small.5s",
        "result/exp1.5.premiun.sql/e2e.small.1s",
        "result/exp1.5.premiun.sql/e2e.small.0.1s"
    ]

    fileE2ESQL = [
        "result/exp1.5.premiun.sql/sql.e2e.5s",
        "result/exp1.5.premiun.sql/sql.e2e.1s",
        "result/exp1.5.premiun.sql/sql.e2e.0.1s"
    ]

    file2h = ["result/exp1.5.premiun.sql/e2e.small.2h"]
    sql2h = ["result/exp1.5.premium.sql.2h.func/function-PlayerOperationDb-requests"]
    processfile2h = processE2E(file2h, expName='2h', maxval=99999)
    dfFile2h = pd.concat(processfile2h)
    dfFile2h["Service"] = "Premium Storage"
    processsql2h = processDur(sql2h, expName='2h', maxval=99999)
    dfSql2h = pd.concat(processsql2h)
    dfSql2h["Service"] = "Serverless SQL"
    # all2h = pd.concat([dfFile2h, dfSql2h])
    all2h = dfSql2h

    dfs = processE2E(fileE2E)
    # print(dfs)
    dfs.extend(processfile2h)
    allDf = pd.concat(dfs)
    allDf = allDf[allDf["Metric"] == "End-to-End Latency"]
    allDf["Service"] = "Premium Storage"
    print("Premiun mean", allDf["Value"].mean())

    dfsSQL = processE2E(fileE2ESQL)
    allDfSQL = pd.concat(dfsSQL)
    allDfSQL = allDfSQL[allDfSQL["Metric"] == "End-to-End Latency"]
    allDfSQL["Service"] = "Serverless SQL"
    all = pd.concat([allDf, allDfSQL])
    print("SQL mean", allDfSQL["Value"].mean())

    fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
                                  gridspec_kw={'width_ratios': [3, 1]})
    # sns1 = sns.boxplot(data=allDf, x='Invocation Interval', y='Value', hue='Metric', ax=ax[0])

    # sns2 = sns.boxplot(data=allDfSQL, x='Invocation Interval', y='Value', hue='Metric', ax=ax[1])

    # plt.ylabel("End-to-end Latency (ms)")

    sns1 = sns.boxplot(data=all, x='Invocation Interval', y='Value', hue='Service', ax=ax)
    all2h["Value"] /= 1000
    sns2 = sns.boxplot(data=all2h, x="Invocation Interval", y='Value', hue='Service', ax=ax2)
    sns1.get_legend().remove()
    sns2.get_legend().remove()
    ax.set_ylabel("End-to-end Latency (ms)")
    ax2.set_ylabel("End-to-end Latency (s)")
    ax.set_xlabel("Invocation Interval", loc="right")
    ax2.xaxis.label.set_visible(False)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, 0.80))
    # , bbox_to_anchor = (0.5, 0.70)

    plt.savefig("exp1.2-3.pdf")

    plt.show()


def plotExp1_2_3():
    fileDur = [
        "result/20210626224700.exp1.1.premium.5s/function-PlayerOperation-requests-20210626224700",
        "result/20210626224700.exp1.1.premium.1s/function-PlayerOperation-requests-20210626224700",
        "result/20210626224700.exp1.1.premium.0.1s/function-PlayerOperation-requests-20210626224700"
    ]

    # fileE2E = [
    #     "result/20210626224700.exp1.1.premium.5s/e2e.5s.premium",
    #     "result/20210626224700.exp1.1.premium.1s/e2e.1s.premium",
    #     "result/20210626224700.exp1.1.premium.0.1s/e2e.0.1s.premium"
    # ]

    fileDurSQL = [
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-5s",
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-1s",
        "result/20210702190000.exp1.3.sql/function-PlayerOperationDb-requests-0.1s"
    ]

    # fileE2ESQL = [
    #     "result/20210702190000.exp1.3.sql/e2e.sql.5s",
    #     "result/20210702190000.exp1.3.sql/e2e.sql.1s",
    #     "result/20210702190000.exp1.3.sql/e2e.sql.0.1s"
    # ]

    file2h = ["result/exp1.5.premium.sql.2h/function-PlayerOperation-requests"]
    sql2h = ["result/exp1.5.premium.sql.2h/function-PlayerOperationDb-requests"]
    processfile2h = processDur(file2h, expName='2h', maxval=99999)
    dfFile2h = pd.concat(processfile2h)
    dfFile2h["Service"] = "Premium Storage"

    processsql2h = processDur(sql2h, expName='2h', maxval=99999)
    dfSql2h = pd.concat(processsql2h)
    dfSql2h["Service"] = "Serverless SQL"
    all2h = pd.concat([dfFile2h, dfSql2h])

    dfs = []
    dfs.extend(processDur(fileDur))
    # dfs.extend(processE2E(fileE2E))
    allDf = pd.concat(dfs)
    allDf = allDf[allDf["Metric"] == "Function Duration"]
    allDf["Service"] = "Premium Storage"
    print("Premiun mean", allDf[allDf["Metric"] == "Function Duration"]["Value"].mean())

    dfsSQL = []
    dfsSQL.extend(processDur(fileDurSQL))
    # dfsSQL.extend(processE2E(fileE2ESQL))
    allDfSQL = pd.concat(dfsSQL)
    allDfSQL = allDfSQL[allDfSQL["Metric"] == "Function Duration"]
    allDfSQL["Service"] = "Serverless SQL"

    all = pd.concat([allDf, allDfSQL])
    print("SQL mean", allDfSQL[allDfSQL["Metric"] == "Function Duration"]["Value"].mean())

    fig, (ax, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(8, 4),
                                  gridspec_kw={'width_ratios': [3, 1]})
    # sns1 = sns.boxplot(data=allDf, x='Invocation Interval', y='Value', hue='Metric', ax=ax[0])

    # sns2 = sns.boxplot(data=allDfSQL, x='Invocation Interval', y='Value', hue='Metric', ax=ax[1])

    # plt.ylabel("End-to-end Latency (ms)")

    sns1 = sns.boxplot(data=all, x='Invocation Interval', y='Value', hue='Service', ax=ax)
    all2h["Value"] /= 1000
    sns2 = sns.boxplot(data=all2h, x="Invocation Interval", y='Value', hue='Service', ax=ax2)
    sns1.get_legend().remove()
    sns2.get_legend().remove()
    ax.set_ylabel("End-to-end Latency (ms)")
    ax2.set_ylabel("End-to-end Latency (s)")
    ax.set_xlabel("Invocation Interval", loc="right")
    ax2.xaxis.label.set_visible(False)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, 0.70))

    plt.savefig("exp1.2-3.pdf")

    plt.show()


def plotExp1_4():
    files = ["result/20210702230000.exp1.2.terrain/function-PopulateAzure-5s-traces",
             "result/20210702230000.exp1.2.terrain/function-PopulateAzure-1s-traces",
             "result/20210702230000.exp1.2.terrain/function-PopulateAzure-0.1s-traces"]

    tmpList = []

    for exp in range(len(files)):
        with open(files[exp]) as f:
            jObj = json.load(f)
        rows = jObj["rows"]
        rowsLen = len(rows)

        for i in range(rowsLen):
            rowExecuting = rows[i]
            rowInvoked = None
            rowExecuted = None

            opId = rowExecuting[7]
            if rowExecuting[1].startswith("Executing"):

                for j in range(i + 1, rowsLen, 1):
                    print(j)
                    jRow = rows[j]
                    jOpId = jRow[7]
                    print("jopId=", opId)
                    if jOpId == opId and jRow[1].endswith("invoked by Java Worker"):
                        print("invoked")
                        rowInvoked = jRow
                        break

                for k in range(i + 1, rowsLen, 1):
                    kRow = rows[k]
                    kOpId = kRow[7]
                    if kOpId == opId and kRow[1].startswith("Executed"):
                        print("executed")
                        rowExecuted = kRow
                        break

            if rowInvoked is not None and rowExecuted is not None:
                print(rowInvoked[0])
                timeExecuting = pd.to_datetime(rowExecuting[0], format=timeFormat)
                timeInvoked = pd.to_datetime(rowInvoked[0], format=timeFormat)
                timeExecuted = pd.to_datetime(rowExecuted[0], format=timeFormat)

                latencyExecuting = (timeInvoked - timeExecuting).microseconds / 1000
                latencyInvoked = (timeExecuted - timeInvoked).microseconds / 1000

                findStart = rowExecuted[1].find("Duration=")
                findEnd = rowExecuted[1].find("ms")
                duration = int(rowExecuted[1][findStart + 9: findEnd])

                latencyExecuted = duration - latencyInvoked - latencyExecuting
                # print(latencyExecuting, latencyInvoked)
                # print(rowExecuting,rowInvoked,rowExecuted, sep="\n")

                tmpList.append(
                    {"Invocation Interval": plotExp1GetExpName(exp), "Metric": "Function Duration", "Value": duration})

                tmpList.append(
                    {"Invocation Interval": plotExp1GetExpName(exp), "Metric": "Executing Phrase",
                     "Value": latencyExecuting})

                tmpList.append(
                    {"Invocation Interval": plotExp1GetExpName(exp), "Metric": "Invoked Phrase",
                     "Value": latencyInvoked})

                # tmpList.append(
                #     {"Invocation Interval": plotExp1GetExpName(exp), "Metric": "Executed", "Value": latencyExecuted})


            else:
                continue

    allDf = pd.DataFrame(tmpList)
    print(allDf)
    dfExecuting = allDf[allDf["Metric"] == "Executing"]
    dfExecuting5s = dfExecuting[dfExecuting["Invocation Interval"] == "5s"]
    dfExecuting5sMean = dfExecuting5s["Value"].mean()
    print(dfExecuting5sMean)
    dfExecuting1s = dfExecuting[dfExecuting["Invocation Interval"] == "1s"]
    dfExecuting1sMean = dfExecuting1s["Value"].mean()
    print(dfExecuting1sMean)
    dfExecuting01s = dfExecuting[dfExecuting["Invocation Interval"] == "0.1s"]
    dfExecuting01sMean = dfExecuting01s["Value"].mean()
    print(dfExecuting01sMean)

    dfDuration = allDf[allDf["Metric"] == "Duration"]
    dfDuration5s = dfDuration[dfDuration["Invocation Interval"] == "5s"]
    dfDuration1s = dfDuration[dfDuration["Invocation Interval"] == "1s"]
    dfDuration01s = dfDuration[dfDuration["Invocation Interval"] == "0.1s"]

    dfInvoked = allDf[allDf["Metric"] == "Invoked"]

    plt.figure(figsize=(4, 5), dpi=100)

    sns.boxplot(data=allDf, x='Invocation Interval', y='Value', hue='Metric')

    plt.tight_layout()
    plt.ylim(0)
    plt.ylabel("Latency (ms)")
    plt.savefig("exp1.4.pdf")

    plt.show()

    # row[0] time
    # row[1] event msg
    # row[7] operation id


def plotExp1GetExpName(i):
    expName = None
    if i == 0:
        expName = "5s"
    if i == 1:
        expName = "1s"
    if i == 2:
        expName = "0.1s"
    if i == 3:
        expName = "2h"
    return expName


def plotExp2GetExpName(i):
    expName = None
    if i == 0:
        expName = "Standard"
    if i == 1:
        expName = "Premium"
    if i == 2:
        expName = "5s (Premium)"
    if i == 3:
        expName = "10s (Premium)"
    return expName


def plotExp2_getListJson(fileStr):
    li = []
    with open(fileStr) as f:
        obj = json.load(f)
    for row in obj["value"][0]["timeseries"][0]["data"]:
        if row["total"] is not None:
            li.append(row["total"])
    return li


def plotExp2Sn(fileSS, fileSE2E, fileE2E, name, maxVal=900, ylim=None):
    dfs = []
    for i in range(len(fileSS)):
        expName = plotExp2GetExpName(i)
        li = plotExp2_getListJson(fileSS[i])
        print(li)
        tmp = []
        outlierSS = []
        for val in li:
            if val < maxVal:
                tmp.append({"Request Interval": expName, "Metric": "Azure Server", "Value": val})
            else:
                outlierSS.append(val)
        tmpDf = pd.DataFrame(tmp)
        dfs.append(tmpDf)
        # print("Outlier SS,", len(outlierSS), outlierSS)
        print("99p SS", np.quantile(li, q=0.99))
        print("95p SS", np.quantile(li, q=0.95))
        print("max SS,", max(li))
        print("mean SS,", sum(li) / len(li))

    for i in range(len(fileSE2E)):
        expName = plotExp2GetExpName(i)
        li = plotExp2_getListJson(fileSE2E[i])
        print(li)
        tmp = []
        outlierSE2E = []
        for val in li:
            if val < maxVal:
                tmp.append({"Request Interval": expName, "Metric": "Azure End-to-End", "Value": val})
            else:
                outlierSE2E.append(val)
        tmpDf = pd.DataFrame(tmp)
        dfs.append(tmpDf)
        # print("Outlier SE2E,",len(outlierSE2E), outlierSE2E)
        print("99p SE2E", np.quantile(li, q=0.99))
        print("95p SE2E", np.quantile(li, q=0.95))
        print("max SE2E", max(li))
        print("mean SE2E,", sum(li) / len(li))

    for i in range(len(fileE2E)):
        expName = plotExp2GetExpName(i)

        with open(fileE2E[i], "r") as f:
            lines = f.readlines()

        tmp = []
        vals = []
        outlierE2E = []
        for line in lines:
            val = float(line.split(",")[2].replace("\n", ""))
            vals.append(val)
            if val < maxVal:
                tmp.append({"Request Interval": expName, "Metric": "Java End-to-End", "Value": val})
            else:
                outlierE2E.append(val)
        tmpDf = pd.DataFrame(tmp)
        dfs.append(tmpDf)
        # print("Outlier E2E,",len(outlierE2E), outlierE2E)
        print("99p E2E", np.quantile(vals, q=0.99))
        print("95p E2E", np.quantile(vals, q=0.95))
        print("max E2E,", max(vals))
        print("mean E2E,", sum(vals) / len(vals))

    allDf = pd.concat(dfs)
    print(allDf)

    plt.figure(figsize=(3.8, 5), dpi=100)
    sns.boxplot(data=allDf, y='Value', x='Request Interval', hue='Metric')
    plt.xlabel("Storage Plan")
    plt.ylabel("Latency (ms)")
    if ylim:
        plt.ylim(ylim)

    plt.tight_layout()
    plt.savefig(name)

    plt.show()


def plotExp2_1():
    # fileSS = [
    #     "result/20210622233000.exp2.standard.small.5s/az.SuccessServerLatency.small.5s",
    #     "result/20210622234500.exp2.standard.small.10s/az.SuccessServerLatency.small.10s"
    # ]
    # fileSE2E = [
    #     "result/20210622233000.exp2.standard.small.5s/az.SuccessE2ELatency.small.5s",
    #     "result/20210622234500.exp2.standard.small.10s/az.SuccessE2ELatency.small.10s"
    # ]
    # fileE2E = [
    #     "result/20210622233000.exp2.standard.small.5s/e2e.small.5s",
    #     "result/20210622234500.exp2.standard.small.10s/e2e.small.10s"
    # ]

    # was written to file
    #         "result/20210623131000.exp2.standard.small.1m/az.SuccessServerLatency.small.1m",
    #         "result/20210623131000.exp2.standard.small.1m/az.SuccessE2ELatency.small.1m",
    #         "result/20210623131000.exp2.standard.small.1m/e2e.small.1m",

    fileSS = [
        "result/20210623150000.exp2.standard.small.1m/az.SuccessServerLatency.small.1m",
        "result/20210623154100.exp2.premium.small.1m/az.SuccessServerLatency.small.1m"
    ]
    fileSE2E = [
        "result/20210623150000.exp2.standard.small.1m/az.SuccessE2ELatency.small.1m",
        "result/20210623154100.exp2.premium.small.1m/az.SuccessE2ELatency.small.1m"
    ]
    fileE2E = [
        "result/20210623150000.exp2.standard.small.1m/e2e.small.1m",
        "result/20210623154100.exp2.premium.small.1m/e2e.small.1m"
    ]

    plotExp2Sn(fileSS, fileSE2E, fileE2E, "exp2.1.pdf", maxVal=100, ylim=[0, 100])


def plotExp2_2():
    fileSS = [
        "result/20210623180000.exp2.standard.large.1m/az.SuccessServerLatency.large.1m",
        "result/20210623183000.exp2.premium.large.1m/az.SuccessServerLatency.large.1m"
    ]
    fileSE2E = [
        "result/20210623180000.exp2.standard.large.1m/az.SuccessE2ELatency.large.1m",
        "result/20210623183000.exp2.premium.large.1m/az.SuccessE2ELatency.large.1m"
    ]
    fileE2E = [
        "result/20210623180000.exp2.standard.large.1m/e2e.large.1m",
        "result/20210623183000.exp2.premium.large.1m/e2e.large.1m"
    ]

    plotExp2Sn(fileSS, fileSE2E, fileE2E, "exp2.2.pdf", ylim=[0, 900])


def plotRegionFileCache5(path, name):
    dfs = []
    for i in range(4):
        dir = path + str(i)
        it = os.listdir(dir)
        for fname in it:
            if (fname.startswith("server-events-")):
                df2 = pd.read_csv(dir + "/" + fname, delimiter="\t", index_col="timestamp")

                filter_read_cache_getRegionFile = df2["key"] == "read_cache_getRegionFile"
                df2 = df2[filter_read_cache_getRegionFile]
                df2["value"] = pd.to_numeric(df2["value"])

                # remove server initilization
                df2 = df2[df2.index > df2.index[0] + 90 * 1000]
                dfs.append(df2)

    allDf = pd.concat(dfs)
    return allDf


def plotRegionFileGetCDF(data):
    count, bins_count = np.histogram(data, bins=10000)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    return cdf, bins_count


def plotRegionFileData(data, name):
    print("\n\n" + name)
    print("mean: ", data["value"].mean())
    print("95p: ", data["value"].quantile(0.95))
    print("99p: ", data["value"].quantile(0.99))
    print("99.6p: ", data["value"].quantile(0.996))
    print("99.67p: ", data["value"].quantile(0.9967))
    print("max: ", data["value"].max())
    print("min: ", data["value"].min())
    # print("count (>=50)", len(data[data["value"] >= 50]))
    # print("% (>=50)", len(data[data["value"] >= 50]) / len(data))
    # print("count (>=100)", len(data[data["value"] >= 100]))
    # print("% (>=100)", len(data[data["value"] >= 100]) / len(data))


def plotRegionFileCache():
    pathLocal = 'result/20210626173211.local.none/'
    pathNone = 'result/20210626162529.remote.none/'
    pathDis = 'result/20210626161132.remote.distance/'

    # pathLocal = 'result/20210726152736.local.none/'
    # pathNone = 'result/20210726144052.remote.none/'
    # pathDis = 'result/20210726135400.remote.distance/'

    dfLocal = plotRegionFileCache5(pathLocal, 'local')
    dfNone = plotRegionFileCache5(pathNone, 'none')
    dfSimple = plotRegionFileCache5(pathDis, 'simple')

    plotRegionFileData(dfLocal, 'local')
    plotRegionFileData(dfNone, 'none')
    plotRegionFileData(dfSimple, 'simple')

    cdfLocal, bins_countLocal = plotRegionFileGetCDF(dfLocal["value"])
    cdfNone, bins_countNone = plotRegionFileGetCDF(dfNone["value"])
    cdfSimple, bins_countSimple = plotRegionFileGetCDF(dfSimple["value"])

    # plt.figure(0, figsize=(8,3))
    # plt.plot(bins_countLocal[1:], cdfLocal, label="Local", color="green")
    # plt.plot(bins_countNone[1:], cdfNone, label="Remote, No Policy", color="blue")
    # plt.plot(bins_countSimple[1:], cdfSimple, label="Remote, Simple Distance", color="red")

    f, (ax, ax2) = plt.subplots(1, 2, sharey=True, figsize=(8, 3),
                                gridspec_kw={'width_ratios': [6, 3]})
    ax.plot(bins_countLocal[1:], cdfLocal, label="Local", color="green")
    ax.plot(bins_countNone[1:], cdfNone, label="Remote, No Preloading", color="blue")
    ax.plot(bins_countSimple[1:], cdfSimple, label="Remote, Simple Distance", color="red")
    ax2.plot(bins_countLocal[1:], cdfLocal, label="Local", color="green")
    ax2.plot(bins_countNone[1:], cdfNone, label="Remote, No Preloading", color="blue")
    ax2.plot(bins_countSimple[1:], cdfSimple, label="Remote, Simple Distance", color="red")

    # ax2.yaxis.set_visible(False)
    # ax2.set_yticks([])

    ax.set_xlim(-1, 50)
    ax2.set_xlim(100, 500)
    # ax.margins(x=50)
    ax.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax.yaxis.tick_left()
    # ax.tick_params(labelright='off')

    ax2.yaxis.tick_right()

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)

    # plt.ylim(0.5,1)
    # plt.xlim(0,50)
    # plt.margins(1)
    ax.set_xlabel("Latency (ms)", loc="right")
    ax.set_ylabel("Fraction of Data")
    # ax.legend()
    ax.legend()
    f.tight_layout()
    plt.savefig("exp3.1.pdf")
    plt.show()

    # plt.figure(1)
    # plt.plot(bins_countNone[1:], cdfNone, label="Remote, No Preload Policy", color="blue")
    # plt.legend()
    # plt.savefig("exp3.2.pdf")
    # plt.show()


def processCPU(f1, normalized=None, startMs=100 * 1000):
    df = pd.read_csv(f1, delimiter='\t', index_col="timestamp")
    df = df[df.index > df.index[0] + startMs]
    # df = df[(np.abs(stats.zscore(df["proc.cpu_percent"])) < 3)]
    df["second"] = np.arange(len(df))
    if normalized is not None:
        df["relative_cpu"] = df["proc.cpu_percent"] / normalized
    else:
        df["relative_cpu"] = df["proc.cpu_percent"]
    return df


def plotExp4CPU(f1, f2, name, normalized=None, rolling=None):
    df = processCPU(f1, normalized)
    print("remote cpu mean", df["proc.cpu_percent"].mean())
    print("relative remote cpu mean", df["relative_cpu"].mean())
    df2 = processCPU(f2, normalized)
    print("local cpu mean", df2["proc.cpu_percent"].mean())
    print("relative local cpu mean", df2["relative_cpu"].mean())

    if rolling:
        df["sample"] = df["relative_cpu"].rolling(rolling).mean()
        df = df[df['sample'].notna()]
        df = df.reset_index()
        df2["sample"] = df2["relative_cpu"].rolling(rolling).mean()
        df2 = df2[df2['sample'].notna()]
        df2 = df2.reset_index()

    x1 = np.arange(len(df))
    x2 = np.arange(len(df2))

    plt.figure(figsize=(5, 4), dpi=100)
    if rolling:
        plt.plot(x2, df2["sample"], label="Monolithic", linestyle="--")
        plt.plot(x1, df["sample"], label="Serverless", color="green")
    else:
        plt.plot(x2, df2["relative_cpu"], label="Monolithic", linestyle=":")
        plt.plot(x1, df["relative_cpu"], label="Serverless", color="green")
    if normalized:
        plt.ylim(0, 100)

    plt.xlim(0, 500)
    ax = plt.gca()
    matplotlib.rcParams.update({'font.size': 11})
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("CPU Usage %", fontsize=11)
    plt.legend()
    plt.savefig(name)
    plt.show()


# exp 4 (old)
# def processTick(f1, name, zscore=3, continous=1, rollingtick=100, quantile=0.995,
#                 joinInterval=15, maxBot=40, startms=90 * 1000):
# exp4
# def processTick(f1, name, zscore=3, continous=1, rollingtick=100, quantile=0.995,
#                 joinInterval=10, maxBot=50, startms=90 * 1000):

# exp5
def processTick(f1, name, zscore=3, continous=1, rollingtick=100, quantile=0.995,
                joinInterval=5, maxBot=100, startms=90 * 1000):
    # def processTick(f1, name, zscore=3, continous=1, rollingtick=50, quantile=1,
    #                 joinInterval=1, maxBot=400, startms=90 * 1000):
    # def processTick(f1, name, zscore=3, continous=1, rollingtick=50, quantile=0.995,
    #                     joinInterval=7, maxBot=90):
    # exp5 local
    # def processTick(f1, name, zscore=3, continous=1, rollingtick=100, quantile=0.995,
    #                 joinInterval=10, maxBot=60, startms=90 * 1000):

    print("f = ", f1)
    df = pd.read_csv(f1, delimiter='\t', low_memory=False)
    df = df[df["key"] == "tick"]
    df = df[df["timestamp"] >= df.iloc[0]["timestamp"] + startms]
    df["value"] = pd.to_numeric(df["value"])
    df["dfname"] = name

    print("Count before removal", df.size)
    # remove outlier: quantile looks better than zscore
    df = df[df["value"] <= df["value"].quantile(quantile)]
    # df = df[(np.abs(stats.zscore(df["value"])) < zscore)]
    print("Count after removal", df.size)

    df["sample"] = df["value"].rolling(rollingtick).mean()
    df = df[df['sample'].notna()]
    df = df.reset_index()
    df["second"] = (df["timestamp"] - df.iloc[0]["timestamp"]) / 1000
    # print(df.head(100))

    tmpDf = df[df["sample"] > 50]
    print(tmpDf)
    if tmpDf.size != 0:
        # first three consective tick

        # first overload tick as overloaded
        overloadTick = tmpDf.index.format()[0]
        overloadTime = tmpDf.iloc[0]["second"]
    else:
        overloadTick = df["value"].count()
        overloadTime = df.iloc[-1]["second"]
    tick2Player2 = overloadTime / joinInterval

    if tick2Player2 > maxBot:
        tick2Player2 = maxBot

    print("tick to player count method 2, tick=", overloadTick, ",t2p=", tick2Player2,
          ",time=", overloadTime)
    # ",timestamp=", tmpDf.iloc[0]["timestamp"]
    if name == "remote":
        ttpRemote.append(math.floor(tick2Player2))

    if name == "local":
        ttpLocal.append(math.floor(tick2Player2))

    print("count", df["sample"].count())
    print("95p", df["sample"].quantile(0.95))
    print("99p", df["sample"].quantile(0.99))
    print("mean", df["sample"].mean())
    print("max", df["sample"].max())
    print("value max", df["value"].max())
    print("min", df["sample"].min())

    print("\n")
    return df


def plotExp4Tick(f1, f2, name):
    df = processTick(f1, "remote")
    df2 = processTick(f2, "local")

    fig = plt.figure(figsize=(5, 4), dpi=100)

    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()

    ax1.plot(df2["second"], df2["sample"], label="Monolithic", linestyle="--")
    ax1.plot(df["second"], df["sample"], label="Serverless", color="green")
    ax1.axhline(y=50, color='red', linestyle='dashed')
    ax1.axhspan(50, 70, alpha=0.5, color='red')

    ax2.plot(range(50), np.zeros(50), color="white")
    ax2.set_xlim(0, 50)

    ax1.set_ylim(0, 60)
    ax1.set_xlim(0, 500)

    matplotlib.rcParams.update({'font.size': 11})

    ax1.set_xlabel("Time (s)", fontsize=11)
    ax1.set_ylabel("Tick Duration (ms)", fontsize=11)
    ax1.legend()
    ax2.set_xlabel("No. of Players", fontsize=11)
    # ax2.cla()

    plt.savefig(name)

    plt.show()


def plotExp4_1CPU():
    # f1 = "result/20210704140304.8bots.remote.new/0/server-system-10.0.0.5-56700-20210704140320"
    # f1 = "result/20210704140304.8bots.remote.new/1/server-system-10.0.0.5-57822-20210704141532"
    # f1 = "result/20210704140304.8bots.remote.new/4/server-system-10.0.0.5-45824-20210704170928"
    f1 = "result/20210704140304.8bots.remote.new/5/server-system-10.0.0.5-47056-20210704172141"
    # f2 = "result/20210704142928.8bots.local.new/0/server-system-10.0.0.5-59232-20210704142944"
    f2 = "result/20210704142928.8bots.local.new/1/server-system-10.0.0.5-60364-20210704144157"

    plotExp4CPU(f1, f2, 'exp4.1.cpu.pdf')


def plotExp4_1Tick():
    # f1 = "result/20210704140304.8bots.remote.new/0/server-events-20.52.233.235-56700"
    # f1 = "result/20210704140304.8bots.remote.new/1/server-events-20.52.233.235-57822"
    # f1 = "result/20210704140304.8bots.remote.new/4/server-events-20.52.233.235-45824"
    f1 = "result/20210704140304.8bots.remote.new/5/server-events-20.52.233.235-47056"

    # f2 = "result/20210704142928.8bots.local.new/0/server-events-20.52.233.235-59232"
    f2 = "result/20210704142928.8bots.local.new/1/server-events-20.52.233.235-60364"

    plotExp4Tick(f1, f2, 'exp4.1.tick.pdf')


def plotExp4Memory(f1, f2, name, key="proc.memory_full_info.uss"):
    df = pd.read_csv(f1, delimiter='\t', index_col="timestamp")
    df = df[df.index > df.index[0] + 90 * 1000]
    print(list(df))

    df["relative_memory"] = df[key] / (16397796 * 1024) * 100

    df2 = pd.read_csv(f2, delimiter='\t', index_col="timestamp")
    df2 = df2[df2.index > df2.index[0] + 90 * 1000]

    df2["relative_memory"] = df2[key] / (16397796 * 1024) * 100

    print(df2)

    x1 = np.arange(len(df))
    x2 = np.arange(len(df2))

    plt.figure(figsize=(5, 4), dpi=100)
    plt.plot(x2, df2["relative_memory"], label="Monolithic", linestyle="--")
    plt.plot(x1, df["relative_memory"], label="Serverless", color="green")
    plt.xlim(0, 500)
    plt.ylim(0)
    ax = plt.gca()
    matplotlib.rcParams.update({'font.size': 11})
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Memory Usage %", fontsize=11)
    plt.legend()
    plt.savefig(name)
    plt.show()


def processPkt(f1):
    df = pd.read_csv(f1, delimiter='\t', index_col="timestamp")
    df = df[df.index > df.index[0] + 90 * 1000]
    df["net.packets_sent.eth0.relative"] = df["net.packets_sent.eth0"] - df.iloc[0]["net.packets_sent.eth0"]
    df["net.packets_recv.eth0.relative"] = df["net.packets_recv.eth0"] - df.iloc[0]["net.packets_recv.eth0"]
    df['send_per_second'] = df['net.packets_sent.eth0.relative'] - df['net.packets_sent.eth0.relative'].shift(1)
    df['recv_per_second'] = df['net.packets_recv.eth0.relative'] - df['net.packets_recv.eth0.relative'].shift(1)

    # apply rolling average
    df['send_per_second_sample'] = df['send_per_second'].rolling(5).mean()
    df['recv_per_second_sample'] = df['recv_per_second'].rolling(5).mean()

    df["net.bytes_sent.eth0.relative"] = df["net.bytes_sent.eth0"] - df.iloc[0]["net.bytes_sent.eth0"]
    df["net.bytes_recv.eth0.relative"] = df["net.bytes_recv.eth0"] - df.iloc[0]["net.bytes_recv.eth0"]
    df['sent_bytes_per_second'] = df['net.bytes_sent.eth0.relative'] - df['net.bytes_sent.eth0.relative'].shift(1)
    df['recv_bytes_per_second'] = df['net.bytes_recv.eth0.relative'] - df['net.bytes_recv.eth0.relative'].shift(1)
    df['sent_bytes_per_second'] = df['sent_bytes_per_second'] / 1024 / 1024
    df['recv_bytes_per_second'] = df['recv_bytes_per_second'] / 1024 / 1024
    print(df["recv_bytes_per_second"])
    return df


def plotExp4Pkt(f1, f2, name):
    df = processPkt(f1)
    df2 = processPkt(f2)
    x1 = np.arange(len(df))
    x2 = np.arange(len(df2))

    plt.figure(0, figsize=(5, 4), dpi=100)

    # # pkt count
    # plt.plot(x1, df["net.packets_recv.eth0.relative"], label="Serverless Recv", color='b')
    # plt.plot(x1, df["net.packets_sent.eth0.relative"], label="Serverless Sent", color='r')
    # print("serverless recv", df.iloc[-1]["net.packets_recv.eth0.relative"])
    # print("serverless sent", df.iloc[-1]["net.packets_sent.eth0.relative"])
    #
    # plt.plot(x2, df2["net.packets_sent.eth0.relative"], label="Monolithic Sent", color='m')
    # plt.plot(x2, df2["net.packets_recv.eth0.relative"], label="Monolithic Recv", color='c')
    #
    # print("mono recv", df2.iloc[-1]["net.packets_recv.eth0.relative"])
    # print("mono sent", df2.iloc[-1]["net.packets_sent.eth0.relative"])

    # pkt count per second
    plt.plot(x1, df["send_per_second_sample"], label="Serverless Recv", color='b')
    plt.plot(x1, df["recv_per_second_sample"], label="Serverless Sent", color='r')
    plt.plot(x2, df2["send_per_second_sample"], label="Monolithic Sent", color='m')
    plt.plot(x2, df2["recv_per_second_sample"], label="Monolithic Recv", color='c')

    print("serverless recv / mono recv",
          df.iloc[-1]["net.packets_recv.eth0.relative"] / df2.iloc[-1]["net.packets_recv.eth0.relative"])
    print("serverless sent / mono sent",
          df.iloc[-1]["net.packets_sent.eth0.relative"] / df2.iloc[-1]["net.packets_sent.eth0.relative"])

    plt.xlim(0, 500)
    ax = plt.gca()
    matplotlib.rcParams.update({'font.size': 11})
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Packets per Second (PPS)", fontsize=11)
    plt.tight_layout()
    plt.legend()
    plt.savefig("exp4.2.pps.pdf")
    plt.show()

    # plt.figure(1, figsize=(5, 4), dpi=100)
    # #throughput per second
    # plt.plot(x1, df["sent_bytes_per_second"], label="Serverless Recv", color='b')
    # plt.plot(x1, df["recv_bytes_per_second"], label="Serverless Sent", color='r')
    # plt.plot(x2, df2["sent_bytes_per_second"], label="Monolithic Sent", color='m')
    # plt.plot(x2, df2["recv_bytes_per_second"], label="Monolithic Recv", color='c')
    # plt.xlim(0,550)
    # plt.xlabel("Time (s)")
    # plt.ylabel("Throughput (MB/s)")
    # plt.legend()
    # plt.savefig("exp4.2.throughput.pdf")
    # plt.show()


def plotExp6Pkt(f1):
    df = processPkt(f1)
    x1 = np.arange(len(df))

    plt.figure(0, figsize=(5, 4), dpi=100)

    # pkt count
    # plt.plot(x1, df["net.packets_recv.eth0.relative"], label="Serverless Recv", color='b')
    # plt.plot(x1, df["net.packets_sent.eth0.relative"], label="Serverless Sent", color='r')
    print("serverless recv", df.iloc[-1]["net.packets_recv.eth0.relative"])
    print("serverless sent", df.iloc[-1]["net.packets_sent.eth0.relative"])

    # pkt count per second
    plt.plot(x1, df["send_per_second"], label="Serverless Recv", color='b')
    plt.plot(x1, df["recv_per_second"], label="Serverless Sent", color='r')

    plt.xlim(0, 550)
    ax = plt.gca()
    matplotlib.rcParams.update({'font.size': 11})
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Packets per Second (PPS)", fontsize=11)
    plt.legend()
    # plt.savefig(name)
    plt.show()

    plt.figure(1, figsize=(5, 4), dpi=100)
    # throughput per second
    plt.plot(x1, df["sent_bytes_per_second"], label="Serverless Recv", color='b')
    plt.plot(x1, df["recv_bytes_per_second"], label="Serverless Sent", color='r')
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (MB/s)")
    plt.legend()
    plt.show()


def plotExp4_2CPU():
    # f1 = "result/20210704201755.20b.remote/0/server-system-10.0.0.5-35898-20210704201811"
    # f2 = "result/20210704194930.20b.local/0/server-system-10.0.0.5-33260-20210704194946"

    f1 = findFileinPath("result/20210725204005.exp4.remote/1/", "server-system")
    f2 = findFileinPath("result/20210725211819.exp4.local/3/", "server-system")

    plotExp4CPU(f1, f2, "exp4.2.cpu.pdf", normalized=4, rolling=3)

    plotExp4Memory(f1, f2, "exp4.2.memory.pdf")
    # plotExp4Memory(f1, f2, "exp4.2.io.pdf", key="net.packets_sent.eth0")
    # plotExp4IO(f1, f2, "exp4.2.io.pdf")
    # plotExp4Pkt(f1, f2, "exp4.2.pkt.pdf")


def plotExp4_2Tick():
    # f1 = "result/20210704201755.20b.remote/0/server-events-20.52.233.235-35898"
    # f2 = "result/20210704194930.20b.local/0/server-events-20.52.233.235-33260"

    # run
    # f1 = findFileinPath("result/20210711190742.40bots.15s.remote/1/", "server-events")
    # f2 = findFileinPath("result/20210711193232.40bots.15s.local/2/", "server-events")
    # plotExp4Tick(f1, f2, "exp4.2.tick.run.pdf")

    # walk
    f1 = findFileinPath("result/20210725204005.exp4.remote/2/", "server-events")
    f2 = findFileinPath("result/20210725211819.exp4.local/3/", "server-events")
    plotExp4Tick(f1, f2, "exp4.2.tick.pdf")

    f1 = findFileinPath("result/20210726014243.exp4.0.4.remote/3/", "server-events")
    f2 = findFileinPath("result/20210726030905.exp4.0.4.local/1/", "server-events")
    plotExp4Tick(f1, f2, "exp4.2.tick.run.pdf")


def plot4_2TickDas5():
    file = []
    # VU
    file.append(findFileinPath("result/20210714183806.das5.exp10.def.local.100bots/1/", "server-event"))
    file.append(findFileinPath("result/20210721210406.das5.exp5.flat.local.400bots/0/", "server-event"))
    file.append(findFileinPath("result/20210721220834.das5.exp11.flat.local.400bots/1/", "server-event"))
    file.append(findFileinPath("result/20210721223449.das5.exp10.flat.local.200bots/0/", "server-event"))
    file.append(findFileinPath("result/20210722210045.das5.exp10.def.local/0/", "server-event"))
    file.append(findFileinPath("result/20210722204717.das5.exp11.def.local/0/", "server-event"))

    dfs = []

    dfs.append(processTick(file[1], "exp5, flat", joinInterval=1, maxBot=400))
    dfs.append(processTick(file[2], "exp11, flat", joinInterval=1, maxBot=400))
    dfs.append(processTick(file[0], "exp10, def", joinInterval=4, maxBot=100, quantile=0.995))
    dfs.append(processTick(file[3], "exp10, flat", joinInterval=1, maxBot=200))
    dfs.append(processTick(file[4], "exp10, def2", joinInterval=1, maxBot=312))

    # plt.figure(0)
    # allDf = pd.concat(dfs)
    # sns.lineplot(data=allDf, x="second", y="sample", hue="dfname")
    # plt.axhline(y=50, color='green', linestyle='dashed')
    # plt.ylim(0, 100)
    # plt.xlabel("Time (s)")
    # plt.ylabel("Tick Duration (ms)")
    # plt.legend()
    # plt.show()

    plt.figure(1)
    fileRemote = []
    fileRemote.append(findFileinPath("result/20210722223017/0/", "server-event"))
    fileRemote.append(findFileinPath("result/20210722223017/6/", "server-event"))
    dfsRemote = []
    dfsRemote.append(processTick(fileRemote[0], "exp10, def, srvless", joinInterval=3, maxBot=312, rollingtick=200))
    dfsRemote.append(processTick(fileRemote[1], "exp10, def2, srvless", joinInterval=3, maxBot=312, rollingtick=200))

    allRemote = pd.concat(dfsRemote)
    sns.lineplot(data=allRemote, x="second", y="sample", hue="dfname")
    plt.axhline(y=50, color='green', linestyle='dashed')
    plt.ylim(0, 100)
    plt.xlabel("Time (s)")
    plt.ylabel("Tick Duration (ms)")
    plt.legend()
    plt.show()


def plotExp4_2Dur():
    f1 = ["result/20210704201755.20b.remote/0/function-PopulateAzure-requests-20210704201755"]
    # f2 = ["result/20210704194930.20b.local/0/function-PopulateAzure-requests-20210704194930"]
    dur1 = processDur(f1, expName="Serverless", maxval=sys.maxsize)

    # dur1.extend(processDur(f2, expName="Monolithic"))
    allDf = pd.concat(dur1)
    # startTime = pd.to_datetime(allDf.iloc[0]["TimeStamp"], format=timeFormat)

    # allDf["RelativeTime"] = allDf['TimeStamp'].dt.total_seconds()
    allDf["TimeStamp"] = pd.to_datetime(allDf["TimeStamp"], format=timeFormat)
    allDf["Seconds"] = allDf['TimeStamp'] - allDf.iloc[0]["TimeStamp"]
    print(allDf)

    cdfNone, bins_countNone = plotRegionFileGetCDF(allDf["Value"])

    # plt.figure(0)
    # plt.plot(bins_countNone[1:], cdfNone, label="Remote, No Policy", color="blue")

    sns.boxplot(data=allDf, x='Invocation Interval', y='Value', hue='Metric')
    # plt.xlabel("Invocation Interval")
    # plt.ylabel("Value (ms)")

    plt.figure(1)
    # plt.plot(range(len(allDf)), allDf["Value"])
    plt.show()


def plotExp5_Tick_Path(f1Path, f2Path, iter):
    for i in range(iter):
        f1 = None
        f2 = None
        dir1 = f1Path + str(i)
        it1 = os.listdir(dir1)
        for fname in it1:
            if (fname.startswith("server-events-")):
                f1 = dir1 + "/" + fname
                print(f1)

        if f2Path is not None:
            dir2 = f2Path + str(i)
            it2 = os.listdir(dir2)
            for fname in it2:
                if (fname.startswith("server-events-")):
                    f2 = dir2 + "/" + fname
                    print(f2)

        plotExp4Tick(f1, f2, "exp5.tick.pdf")


f1CPUMean = []
f2CPUMean = []


def plotExp5_CPU_Path(f1Path, f2Path, iter):
    f1Dfs = []
    f2Dfs = []
    for i in range(iter):
        dir1 = f1Path + str(i)
        it1 = os.listdir(dir1)
        for fname in it1:
            if (fname.startswith("server-system-10.0")):
                df1 = pd.read_csv(dir1 + "/" + fname, delimiter="\t", index_col="timestamp")
                df1 = df1.head(680)
                df1["iter"] = i
                df1["System"] = "Serverless"
                f1Dfs.append(df1)
                # f1CPUMean.append(df1["proc.cpu_percent"].mean())
                f1CPUMean.append(df1["proc.cpu_percent"].quantile(0.99) / 4.03)

        dir2 = f2Path + str(i)
        it2 = os.listdir(dir2)
        for fname in it2:
            if (fname.startswith("server-system-10.0")):
                df2 = pd.read_csv(dir2 + "/" + fname, delimiter="\t", index_col="timestamp")
                df2 = df2.head(680)
                df2["iter"] = i
                df2["System"] = "Monolithic"
                f2Dfs.append(df2)
                # f2CPUMean.append(df2["proc.cpu_percent"].mean())
                f2CPUMean.append(df2["proc.cpu_percent"].quantile(0.99) / 4.03)

    return pd.concat(f1Dfs), pd.concat(f2Dfs)


def plotExp5_CPU():
    f1Path = "result/20210711223109.exp5.random.remote/"
    f2Path = "result/20210712040218.exp5.random.local/"
    f1Dfs, f2Dfs = plotExp5_CPU_Path(f1Path, f2Path, 20)
    #
    # allDf = pd.concat([f2Dfs, f1Dfs])
    # sns.boxplot(data=allDf, y='proc.cpu_percent', x='iter', hue='System')
    #
    # plt.ylabel("CPU Usage %")
    # plt.xlabel("Iteration")

    print("Remote CPUMean", f1CPUMean)
    print("Local CPUMean", f2CPUMean)

    fLocal = pd.DataFrame(f2CPUMean, columns=['99-th Percentile CPU Usage %'])
    fLocal["System"] = "Monolithic"
    fRemote = pd.DataFrame(f1CPUMean, columns=['99-th Percentile CPU Usage %'])
    fRemote["System"] = "Serverless"

    print("\nRemote max", fRemote["99-th Percentile CPU Usage %"].max())
    print("min", fRemote["99-th Percentile CPU Usage %"].min())
    print("mean", fRemote["99-th Percentile CPU Usage %"].mean())
    print("stdev", fRemote["99-th Percentile CPU Usage %"].std())

    print("\nLocal max", fLocal["99-th Percentile CPU Usage %"].max())
    print("min", fLocal["99-th Percentile CPU Usage %"].min())
    print("mean", fLocal["99-th Percentile CPU Usage %"].mean())
    print("stdev", fLocal["99-th Percentile CPU Usage %"].std())

    allDf = pd.concat([fLocal, fRemote])
    fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(5, 4),
                                  gridspec_kw={'height_ratios': [10, 0.15]})
    sns.boxplot(data=allDf, y='99-th Percentile CPU Usage %', x='System', ax=ax)

    ax.set_ylim(90, 100)
    # ax.axes.get_yaxis().set_visible(False)
    ax2.set_ylim(0, 0.5)  # ignored value
    # fig.set_tight_layout(False)
    # bax = brokenaxes(ylims=((0, 1), (90, 100)), hspace=.05)
    ax.xaxis.set_visible(False)
    ax.spines['bottom'].set_visible(False)

    ax2.spines['top'].set_visible(False)
    ax2.yaxis.set_ticks([0])

    ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()
    ax.tick_params(labeltop=False)
    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs = dict(transform=ax2.transAxes, color='k', clip_on=False)
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    plt.xlabel("System Under Test")
    # plt.ylabel("99-th Percentile CPU Usage %")
    print(allDf)
    plt.savefig("exp5.cpu.99p.pdf")
    plt.show()

    # f1Path = "result/20210707151040.random.40bots.remote/"
    # f2Path = "result/20210707163558.random.40bots.local/"
    # plotExp5_CPU_Path(f1Path, f2Path, 5)


def plotExp5_Players():
    # f1Path = "result/20210711223109.exp5.random.remote/"
    f1Path = "result/20210726170816.exp5.random.remote.100b/"
    # f2Path = "result/20210712040218.exp5.random.local/"
    f2Path = "result/20210727090126.exp5.random.local.100b/"
    plotExp5_Tick_Path(f1Path, f2Path, 20)

    print("ttpRemote", ttpRemote)
    print("ttpRemote max", max(ttpRemote))
    print("ttpRemote min", min(ttpRemote))
    print("ttpRemote mean", sum(ttpRemote) / len(ttpRemote))
    print("ttpRemote stdev", statistics.stdev(ttpRemote))

    print("ttpLocal", ttpLocal)
    print("ttpLocal max", max(ttpLocal))
    print("ttpLocal min", min(ttpLocal))
    print("ttpLocal mean", sum(ttpLocal) / len(ttpLocal))
    print("ttpLocal stdev", statistics.stdev(ttpLocal))

    dfttpLocal = pd.DataFrame(ttpLocal, columns=['No. of Players'])
    dfttpLocal["System"] = "Monolithic"

    dfttpRemote = pd.DataFrame(ttpRemote, columns=['No. of Players'])
    dfttpRemote["System"] = "Serverless"

    dfttp = pd.concat([dfttpLocal, dfttpRemote])

    print(dfttp)
    plt.figure(figsize=(5, 4), dpi=100)
    plt.ylim(0, 73)
    sns.boxplot(data=dfttp, x='System', y='No. of Players')
    plt.ylabel("No. of Players", fontsize=11)
    plt.xlabel("System Under Test", fontsize=11)
    plt.savefig("exp5.players.pdf")
    plt.show()


def plotExp6_Tick(f1):
    df = processTick(f1, "remote", joinInterval=5, maxBot=10, rollingtick=100, quantile=0.998)

    plt.figure(figsize=(5, 4), dpi=100)

    df = df[df["second"] >= 90]
    df = df[df["second"] <= 480]

    plt.plot(df["second"], df["sample"], label="Serverless")

    maxval = 70
    plt.yticks(np.arange(0, maxval, 10))
    # plt.ylim(0, 65)
    # plt.xlim(0, 530)

    ax = plt.gca()
    matplotlib.rcParams.update({'font.size': 11})

    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Tick Duration (ms)", fontsize=11)
    plt.legend()
    # plt.savefig(name)
    plt.show()

    # plt.figure(1)
    # sns.boxplot(data=df, y='value')
    #
    # plt.show()


def processTick6_1(f1Path, behavior, keyword="server-event", iterations=None):
    dfs = []
    # showInter = [3, 21, 49]
    for i in iterations:
        # for i in range(50):
        f1 = None
        dir1 = f1Path + str(i)
        f1 = findFileinPath(dir1, keyword)
        print(f1)
        df = processTick(f1, "remote", joinInterval=5, maxBot=10, rollingtick=50, quantile=1)
        # df = df[df["second"] >= 80]
        df = df[df["second"] <= 500]
        print("stdev", df["sample"].std())
        print("mean", df["sample"].mean())
        print("max", df["sample"].max())
        print("min", df["sample"].min())
        print("max - min", df["sample"].max() - df["sample"].min())

        df["iteration"] = i
        df["behavior"] = behavior
        dfs.append(df)
        # plt.plot(df["second"], df["sample"], label="StraightWalk " + str(i))
    return dfs


def plotExp6_1Tick(f1Path, f2Path=None):
    plt.figure(0, figsize=(5, 4))
    matplotlib.rcParams.update({'font.size': 11})
    dfs = processTick6_1(f1Path, "Straight Walk", iterations=[1, 23, 43])
    if f2Path is not None:
        dfs.extend(processTick6_1(f2Path, "Random", iterations=[1, 23, 43]))

    allDf = pd.concat(dfs)

    f, (ax, ax2) = plt.subplots(2, 1, figsize=(5, 4), sharex=True,
                                gridspec_kw={'height_ratios': [1, 1]})
    for i in range(3):
        ax.plot(dfs[i]["second"], dfs[i]["sample"], label=dfs[i].iloc[0]["iteration"])

    for i in range(3, 6):
        ax2.plot(dfs[i]["second"], dfs[i]["sample"], label=dfs[i].iloc[0]["iteration"])

    ax.set_ylim(0, 90)
    ax.set_xlim(0, 500)
    ax2.set_ylim(0, 50)
    handles, labels = ax.get_legend_handles_labels()

    lg = f.legend(handles, labels, loc='center', title="Iteration", bbox_to_anchor=(0.5, -0.08), fancybox=False,
                  shadow=False, ncol=3)

    ax2.set_xlabel("Time (s)", fontsize=11)

    ax.set_ylabel("Straight Walk", rotation=270, labelpad=13)
    ax.yaxis.set_label_position("right")
    ax.axhline(y=50, color='red', linestyle='dashed')
    # ax2.axhline(y=50, color='red', linestyle='dashed')

    # ax.yaxis.tick_right()
    ax2.set_ylabel("Random", rotation=270, labelpad=13)
    ax2.yaxis.set_label_position("right")
    # ax2.yaxis.tick_right()

    ft = f.text(0.03, 0.5, 'Tick Duration (ms)', va='center', rotation='vertical')
    # f.tight_layout()
    plt.savefig("exp6.1.pdf", dpi=f.dpi, bbox_extra_artists=(lg, ft,), bbox_inches='tight')
    plt.show()

    # plt.figure(1, figsize=(10, 4))
    # print(allDf)
    # sns.boxplot(data=allDf, x='behavior', y='value', hue="iteration")
    # plt.show()


def processExp6_2(f1Path, behavior):
    dfs = []
    # for i in range(50):
    showInter = [1, 23, 43]
    for i in showInter:
        f1 = None
        dir1 = f1Path + str(i)
        f1 = findFileinPath(dir1, "server-system")
        df = processCPU(f1, 4)
        df = df[df["second"] >= 20]
        df = df[df["second"] <= 530]
        df["label"] = behavior
        df["iteration"] = i
        df["sample"] = df["relative_cpu"].rolling(3).mean()
        dfs.append(df)

    return dfs


def plotExp6_2CPU(f1Path, f2Path=None):
    plt.figure(0, figsize=(5, 4))
    matplotlib.rcParams.update({'font.size': 11})
    dfs = processExp6_2(f1Path, "Straight Walk")
    if f2Path is not None:
        dfs.extend(processExp6_2(f2Path, "Random"))

    allDf = pd.concat(dfs)

    f, (ax, ax2) = plt.subplots(2, 1, figsize=(5, 4), sharex=True,
                                gridspec_kw={'height_ratios': [1, 1]})
    for i in range(3):
        ax.plot(dfs[i]["second"], dfs[i]["sample"], label=dfs[i].iloc[0]["iteration"])

    for i in range(3, 6):
        ax2.plot(dfs[i]["second"], dfs[i]["sample"], label=dfs[i].iloc[0]["iteration"])

    ax.set_ylim(0, 90)
    ax2.set_ylim(0, 90)
    # ax2.set_xlim(0, 490)
    # ax.set_xlim(0, 490)
    handles, labels = ax.get_legend_handles_labels()
    lg = f.legend(handles, labels, loc='center', title="Iteration", ncol=3, bbox_to_anchor=(0.5, -0.08), fancybox=False,
                  shadow=False, )
    ax2.set_xlabel("Time (s)", fontsize=11)
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Straight Walk", rotation=270, labelpad=13)

    ax2.yaxis.set_label_position("right")
    ax2.set_ylabel("Random", rotation=270, labelpad=13)

    ft = f.text(0.03, 0.5, 'CPU Usage %', va='center', rotation='vertical')

    plt.savefig("exp6.2.pdf", dpi=f.dpi, bbox_extra_artists=(lg, ft,), bbox_inches='tight')
    plt.show()


def plotExp6_3Box_2(f1Path, f2Path, f3Path=None, f4Path=None):
    file = "result/exp6.3-2.csv"

    # save the df result to file for faster access
    if not os.path.isfile(file):
        dfs = processTick6_1(f1Path, "Straight Walk", iterations=range(50))
        dfs.extend(processTick6_1(f2Path, "Random", iterations=range(50)))
        allDf = pd.concat(dfs)
        # allDf["iteration"] = "all"
        allDf["System"] = "Serverless"

        dfs = processTick6_1(f3Path, "Straight Walk", iterations=range(50))
        dfs.extend(processTick6_1(f4Path, "Random", iterations=range(50)))

        allDf2 = pd.concat(dfs)
        allDf2["System"] = "Monolithic"

        allDf = pd.concat([allDf, allDf2])
        allDf.to_csv(file)

    else:
        allDf = pd.read_csv(file, index_col=0, low_memory=False)
        # allDf = allDf[allDf["second"] < 300]
        allDfMono = allDf[allDf["System"] == "Monolithic"]
        allDfSrc = allDf[allDf["System"] == "Serverless"]

        print("allDf upper count", allDf[allDf["value"] >= 300].count())
        print("allDfMono upper count", allDfMono[allDfMono["value"] >= 300].count())
        print("allDfSrv upper count", allDfSrc[allDfSrc["value"] >= 300].count())
        print(allDf)

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(5, 4), gridspec_kw={'height_ratios': [3, 5]})

    matplotlib.rcParams.update({'font.size': 11})
    sns1 = sns.boxplot(data=allDf, x="behavior", y="value", hue="System", hue_order=["Monolithic", "Serverless"], ax=ax)
    sns2 = sns.boxplot(data=allDf, x="behavior", y="value", hue="System", hue_order=["Monolithic", "Serverless"],
                       ax=ax2)
    sns1.get_legend().remove()
    sns2.get_legend().remove()
    ax.set_ylim(301, 3100)
    ax2.set_ylim(0, 300)

    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # ax.xaxis.tick_top()
    ax.tick_params(labeltop=False, labelbottom=False)
    ax.xaxis.set_ticks([])
    ax2.xaxis.tick_bottom()
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    # ax.xaxis.tick_bottom()

    ax2.yaxis.label.set_visible(False)
    fig.text(0.01, 0.5, 'Tick Duration (ms)', va='center', rotation='vertical')
    ax2.set_xlabel("Behavior Model")

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center left', title="System", bbox_to_anchor=(0.32, 0.62))

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    plt.savefig('exp6.3.box.pdf', dpi=fig.dpi)
    plt.show()


def plotExp6_3Box(f1Path, f2Path):
    file = "result/exp6.3.csv"

    # save the df result to file for faster access
    if not os.path.isfile(file):
        dfsSome = processTick6_1(f1Path, "Straight Walk", iterations=[1, 23, 43])
        dfsSome.extend(processTick6_1(f2Path, "Random", iterations=[1, 23, 43]))
        allDfSome = pd.concat(dfsSome)

        dfs = processTick6_1(f1Path, "Straight Walk", iterations=range(50))
        dfs.extend(processTick6_1(f2Path, "Random", iterations=range(50)))
        allDf = pd.concat(dfs)
        allDf["iteration"] = "all"

        allDf = pd.concat([allDf, allDfSome])
        allDf.to_csv(file)

    else:
        allDf = pd.read_csv(file, index_col=0, low_memory=False)
        allDf = allDf[allDf["iteration"] == "all"]
        allIteration = allDf[allDf["iteration"] == "all"]
        print("allDf upper count", allIteration[allIteration["value"] >= 301].count())
        print(allDf)

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(4, 4), gridspec_kw={'height_ratios': [2, 9]})

    # matplotlib.rcParams.update({'font.size': 11})
    sns1 = sns.boxplot(data=allDf, x="behavior", y="value", ax=ax)
    sns2 = sns.boxplot(data=allDf, x="behavior", y="value", ax=ax2)
    # ax.boxplot(allDf["behavior"], allDf["value"])
    # ax2.boxplot(allDf["behavior"], allDf["value"])

    # sns1.get_legend().remove()
    # sns2.get_legend().remove()
    ax.set_ylim(251, 3100)
    ax2.set_ylim(0, 250)

    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # ax.xaxis.tick_top()
    ax.tick_params(labeltop=False, labelbottom=False)
    ax.xaxis.set_ticks([])
    ax2.xaxis.tick_bottom()
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    # ax.xaxis.tick_bottom()

    ax2.yaxis.label.set_visible(False)
    fig.text(0.011, 0.5, 'Tick Duration (ms)', va='center', rotation='vertical')
    ax2.set_xlabel("Behavior Model")

    handles, labels = ax.get_legend_handles_labels()
    # fig.legend(handles, labels, loc='center left', title="Iteration", bbox_to_anchor=(0.18, 0.62))

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    fig.tight_layout()
    print(fig.dpi)
    plt.savefig('exp6.3.box.png', dpi=300)
    plt.show()


def processExp6FunDur(f1Path, behavior, keyword="function-PopulateAzure-requests", iterations=None, funName=None):
    dfs = []
    # showInter = [3, 21, 49]
    for i in iterations:
        # for i in range(50):
        dir1 = f1Path + str(i)
        f1 = findFileinPath(dir1, keyword)
        print(f1)
        dfRes = processDur([f1], expName=behavior, maxval=99999)

        if len(dfRes) > 0:
            df = dfRes[0]
            print(df)
            # printDf(df, "Value")

            df["iteration"] = i
            df["behavior"] = behavior
            if funName is not None:
                df["funName"] = funName
            dfs.append(df)
            # plt.plot(df["second"], df["sample"], label="StraightWalk " + str(i))
    return dfs


def printDf(df, key="Value"):
    print("stdev", df[key].std())
    print("mean", df[key].mean())
    print("max", df[key].max())
    print("min", df[key].min())
    print("max - min", df[key].max() - df[key].min())
    print("999p", df[key].quantile(0.999))
    print("99p", df[key].quantile(0.99))
    print("95p", df[key].quantile(0.95))
    print("\n")


def plotExp6FunDur(f1Path, f2Path):
    file = "result/exp6.4.csv"

    if not os.path.isfile(file):
        # straight walk, 2 functions
        dfs = processExp6FunDur(f1Path, behavior="Straight Walk", keyword="function-PopulateAzure-requests",
                                iterations=range(50), funName="TerrainGeneration")
        # dfs.extend(processExp6FunDur(f2Path, behavior="Random", iterations=range(50)))
        dfs.extend(processExp6FunDur(f1Path, behavior="Straight Walk", keyword="function-PlayerOperation-requests",
                                     iterations=range(50), funName="PlayerOperation"))

        allDf = pd.concat(dfs)

        # random, 2 functions
        dfsRandom = processExp6FunDur(f2Path, behavior="Random", keyword="function-PopulateAzure-requests",
                                      iterations=range(50), funName="TerrainGeneration")
        dfsRandom.extend(processExp6FunDur(f2Path, behavior="Random", keyword="function-PlayerOperation-requests",
                                           iterations=range(50), funName="PlayerOperation"))

        allDfRandom = pd.concat(dfsRandom)

        allDf = pd.concat([allDf, allDfRandom])
        allDf.to_csv(file)
    else:
        allDf = pd.read_csv(file, index_col=0, low_memory=False)
        allDfTerrain = allDf[allDf["funName"] == "TerrainGeneration"]
        allDfPlayer = allDf[allDf["funName"] == "PlayerOperation"]

        print("max terrain", allDfTerrain["Value"].max())
        print("max player", allDfPlayer["Value"].max())

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(4, 4), gridspec_kw={'height_ratios': [3, 9]})

    # matplotlib.rcParams.update({'font.size': 11})
    sns1 = sns.boxplot(data=allDf, x="behavior", y="Value", hue="funName", ax=ax)
    sns2 = sns.boxplot(data=allDf, x="behavior", y="Value", hue="funName", ax=ax2)
    sns1.get_legend().remove()
    sns2.get_legend().remove()
    ax.set_ylim(800, 14000)
    ax2.set_ylim(0, 800)

    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # ax.xaxis.tick_top()
    ax.tick_params(labeltop=False, labelbottom=False)
    ax.xaxis.set_ticks([])

    ax2.xaxis.tick_bottom()
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    # ax.xaxis.tick_bottom()

    ax2.yaxis.label.set_visible(False)
    fig.text(0.023, 0.5, 'Function Duration (ms)', va='center', rotation='vertical')
    ax2.set_xlabel("Behavior Model")

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', title="Function")

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    fig.tight_layout()
    plt.savefig('exp6.4.box.pdf', dpi=300)
    plt.show()


def plotExp6():
    # f1Path = "result/20210713161019.20bots.fixed.remote/"
    # f1Path = "result/20210718204848.20bots.fixed.random.local/"
    # f2Path = "result/20210714152611.20bots.fixed.random.remote/"

    f1Path = "result/20210719215455.fixed.straight.remote.20bots/"
    f2Path = "result/20210720130223.fixed.random.remote.20bots/"
    f3Path = "result/20210718204848.fixed.straight.local.20bots/"
    f4Path = "result/20210721194930.fixed.random.local.20bots/"
    # tick plots for three iterations
    # plotExp6_1Tick(f1Path, f2Path)

    # CPU plots for three iterations
    # plotExp6_2CPU(f1Path, f2Path)

    # tick plots (some iterations)
    plotExp6_3Box(f1Path, f2Path)

    # tick plots (all iterations)
    # plotExp6_3Box_2(f1Path, f2Path, f3Path, f4Path)

    # function duration plots
    plotExp6FunDur(f1Path, f2Path)

    # plotExp5_Tick_Path(f1Path, None, 10)

    # for i in range(40):
    #     f1 = None
    #     dir1 = f1Path + str(i)
    #     it1 = os.listdir(dir1)
    #     for fname in it1:
    #         if (fname.startswith("server-system-")):
    #             f1 = dir1 + "/" + fname
    #             print(f1)
    #     plotExp6Pkt(f1)

    # for i in range(0,10,1):
    #     f1 = None
    #     dir1 = f4Path + str(i)
    #     it1 = os.listdir(dir1)
    #     for fname in it1:
    #         if (fname.startswith("server-events-")):
    #             f1 = dir1 + "/" + fname
    #             print(f1)
    #     plotExp6_Tick(f1)


def plotExp7():
    f1Path = './result/20210718165653.overhead.remote/'
    f2Path = './result/20210718191646.overhead.local/'

    dfs = []
    for i in range(5):
        dir1 = f1Path + str(i)
        f1 = findFileinPath(dir1, "client-events")
        df = pd.read_csv(f1, delimiter='\t', low_memory=False, names=['timestamp', 'key', 'value'])
        df["System"] = "Serverless"
        dfs.append(df)

        dir2 = f2Path + str(i)
        f2 = findFileinPath(dir2, "client-events")
        df = pd.read_csv(f2, delimiter='\t', low_memory=False, names=['timestamp', 'key', 'value'])
        df["System"] = "Monolithic"
        dfs.append(df)
        # print(df)

    allDf = pd.concat(dfs)
    print("Serverless")
    srvless = allDf[allDf["System"] == "Serverless"]
    print("login mean", srvless[srvless["key"] == "login"]["value"].mean())
    print("banlist mean", srvless[srvless["key"] == "banlist"]["value"].mean())
    print("ban mean", srvless[srvless["key"] == "ban"]["value"].mean())
    print("unban mean", srvless[srvless["key"] == "unban"]["value"].mean())
    print("clear mean", srvless[srvless["key"] == "clear"]["value"].mean())
    print("thunder mean", srvless[srvless["key"] == "thunder"]["value"].mean())

    print("Monolithic")
    mono = allDf[allDf["System"] == "Monolithic"]
    print("login mean", mono[mono["key"] == "login"]["value"].mean())
    print("banlist mean", mono[mono["key"] == "banlist"]["value"].mean())
    print("banlist max", mono[mono["key"] == "banlist"]["value"].max())
    print("ban mean", mono[mono["key"] == "ban"]["value"].mean())
    print("ban max", mono[mono["key"] == "ban"]["value"].max())
    print("unban mean", mono[mono["key"] == "unban"]["value"].mean())
    print("clear mean", mono[mono["key"] == "clear"]["value"].mean())
    print("thunder mean", mono[mono["key"] == "thunder"]["value"].mean())

    fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(7, 4.5), gridspec_kw={'height_ratios': [1.5, 9]},
                                  sharex=True)

    allDf.key[allDf.key == 'login'] = "Player\nLogin"
    allDf.key[allDf.key == 'banlist'] = "Show\nBan List"
    allDf.key[allDf.key == 'ban'] = "Ban\nA Player"
    allDf.key[allDf.key == 'unban'] = "Unban\nA Player"

    allDf.key[allDf.key == 'clear'] = "Weather\nClear"
    allDf.key[allDf.key == 'thunder'] = "Weather\nThunder"

    # matplotlib.rcParams.update({'font.size': 11})
    dfUpper = allDf[allDf["value"] > 900]
    print(dfUpper)
    dfUpper = allDf[allDf["System"] == "Serverless"]
    # #
    # for key in ["login", "banlist", "ban", "unban"]:
    #     dfUpper = dfUpper.append({
    #     "timestamp": "9999",
    #     "key": key,
    #     "value": 99999999999,
    #     "System": "Monolithic"
    # }, ignore_index=True)

    print(dfUpper[dfUpper["key"] == "login"])
    # sns.scatterplot(data=dfUpper, x="key", y="value", hue="System",
    #         hue_order=['Monolithic', 'Serverless'], ax=ax, color=".25")
    # ax.plot(x="login",y=dfUpper[dfUpper["key"] == "login"]["value"], kind="scatter")
    sns.boxplot(data=dfUpper, x="key", y="value", hue="System",
                hue_order=['Monolithic', 'Serverless'], ax=ax, dodge=True)
    sns.boxplot(data=allDf, x="key", y="value", hue="System",
                hue_order=['Monolithic', 'Serverless'], ax=ax2, dodge=True)
    ax.get_legend().remove()
    ax2.get_legend().remove()
    ax.set_ylim(901, 9000)
    ax2.set_ylim(0, 900)

    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # ax.xaxis.tick_top()
    ax.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)
    # ax.xaxis.set_ticks([])

    ax2.xaxis.tick_bottom()
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    # ax.xaxis.tick_bottom()

    ax2.yaxis.label.set_visible(False)
    fig.text(0.0, 0.5, 'End-to-end Latency (ms)', va='center', rotation='vertical')
    ax2.set_xlabel("Event")

    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center', title="System", bbox_to_anchor=(0.5, 0.7))

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    fig.tight_layout()

    plt.savefig("exp7.pdf", dpi=fig.dpi)
    plt.show()


def plotLocal():
    f1 = "E:/opencraft-dev/opencraft-events.log"
    df = processTick(f1, "remote", joinInterval=5, maxBot=10, rollingtick=50, quantile=1, startms=0)
    print("stdev", df["sample"].std())
    print("mean", df["sample"].mean())
    print("max", df["sample"].max())
    print("min", df["sample"].min())
    print("max - min", df["sample"].max() - df["sample"].min())


def plotExp9():
    overloadCPUs = []
    for i in range(3):
        # folder = "result/20210729142442.2srv.1gw.5s/" + str(i) + "/"
        folder = "result/20210730091126.2srv.1gw.5s/" + str(i) + "/"

        f1 = findFileinPath(folder, "server-system-10.0.8.5")
        f2 = findFileinPath(folder, "server-system-10.0.8.6")
        f3 = findFileinPath(folder, "gateway-system-")

        df = processCPU(f1, 4)
        df2 = processCPU(f2, 4)
        df3 = processCPU(f3, 4, startMs=0)

        df["sample"] = df["relative_cpu"].rolling(4).mean()
        df = df[df['sample'].notna()]
        df = df.reset_index()

        df2["sample"] = df2["relative_cpu"].rolling(4).mean()
        df2 = df2[df2['sample'].notna()]
        df2 = df2.reset_index()

        df3["sample"] = df3["relative_cpu"].rolling(4).mean()
        df3 = df3[df3['sample'].notna()]
        df3 = df3.reset_index()

        overloadCPUs.append(df3[df3["sample"] > 97].index[0])

        x1 = np.arange(len(df))
        x2 = np.arange(len(df2))
        x3 = np.arange(len(df3))

        plt.figure(0, figsize=(5, 4), dpi=100)
        plt.plot(x1, df["sample"], label="Instance 0")
        plt.plot(x2, df2["sample"], label="Instance 1")
        plt.plot(x3, df3["sample"], label="Gateway")

        plt.ylim(0, 100)

        # plt.xlim(0, 500)
        ax = plt.gca()
        matplotlib.rcParams.update({'font.size': 11})
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("CPU Usage %", fontsize=11)
        plt.legend()

        plt.show()

    print(overloadCPUs)
    avgCPU = sum(overloadCPUs) / len(overloadCPUs)
    print("2srv, 1gw", avgCPU)
    print("player", avgCPU / 5)
    return avgCPU / 5


def plotExp9_2():
    overloadCPUs = []
    for i in range(5):
        # folder = "result/20210729154313.4srv.1gw.5s/" + str(i) + "/"
        folder = "result/20210729221014.4srv.1gw.5s/" + str(i) + "/"
        f1 = findFileinPath(folder, "server-system-10.0.0.6")
        f2 = findFileinPath(folder, "server-system-10.0.0.7")
        f3 = findFileinPath(folder, "server-system-10.0.8.5-")
        f4 = findFileinPath(folder, "server-system-10.0.8.6")
        f5 = findFileinPath(folder, "gateway-system-")

        df = processCPU(f1, 4)
        df2 = processCPU(f2, 4)
        df3 = processCPU(f3, 4)
        df4 = processCPU(f4, 4)
        df5 = processCPU(f5, 4, startMs=0)

        rolling = 5
        df["sample"] = df["relative_cpu"].rolling(rolling).mean()
        df = df[df['sample'].notna()]
        df = df.reset_index()

        df2["sample"] = df2["relative_cpu"].rolling(rolling).mean()
        df2 = df2[df2['sample'].notna()]
        df2 = df2.reset_index()

        df3["sample"] = df3["relative_cpu"].rolling(rolling).mean()
        df3 = df3[df3['sample'].notna()]
        df3 = df3.reset_index()

        df4["sample"] = df4["relative_cpu"].rolling(rolling).mean()
        df4 = df4[df4['sample'].notna()]
        df4 = df4.reset_index()

        df5["sample"] = df5["relative_cpu"].rolling(rolling).mean()
        df5 = df5[df5['sample'].notna()]
        df5 = df5.reset_index()

        overloadCPUs.append(df5[df5["sample"] > 97].index[0])

        x1 = np.arange(len(df))
        x2 = np.arange(len(df2))
        x3 = np.arange(len(df3))
        x4 = np.arange(len(df4))
        x5 = np.arange(len(df5))

        fig = plt.figure(0, figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax2 = ax.twiny()
        ax.plot(x5, df5["sample"], label="Gateway 0")
        ax.plot(x1, df["sample"], label="Instance 0")
        ax.plot(x2, df2["sample"], label="Instance 1")
        ax.plot(x3, df3["sample"], label="Instance 2")
        ax.plot(x4, df4["sample"], label="Instance 3")
        ax.legend()
        matplotlib.rcParams.update({'font.size': 11})
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("CPU Usage %", fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 500)

        ax2.plot(range(100), np.zeros(100), color="white")
        ax2.set_xlim(0, 100)
        ax2.set_xlabel("No. of Players")
        if i == 1:
            plt.savefig("exp9.4-1.cpu.pdf")
        plt.show()

    print(overloadCPUs)
    avgCPU = sum(overloadCPUs) / len(overloadCPUs)
    print("4srv, 1gw", avgCPU)
    print("player", avgCPU / 5)
    return avgCPU / 5


def plotExp9_3():
    overloadCPUs = []
    for i in range(5):
        folder = "result/20210729235240.4srv.2gw.5s/" + str(i) + "/"
        f1 = findFileinPath(folder, "server-system-10.0.0.6")
        f2 = findFileinPath(folder, "server-system-10.0.0.7")
        f3 = findFileinPath(folder, "server-system-10.0.8.5-")
        f4 = findFileinPath(folder, "server-system-10.0.8.6")
        f5 = findFileinPath(folder, "gateway-system-10.2.0.4")
        f6 = findFileinPath(folder, "gateway-system-10.2.0.5")

        df = processCPU(f1, 4)
        df2 = processCPU(f2, 4)
        df3 = processCPU(f3, 4)
        df4 = processCPU(f4, 4)
        df5 = processCPU(f5, 4, startMs=0)
        df6 = processCPU(f6, 4, startMs=0)

        rolling = 10
        df["sample"] = df["relative_cpu"].rolling(rolling).mean()
        df = df[df['sample'].notna()]
        df = df.reset_index()

        df2["sample"] = df2["relative_cpu"].rolling(rolling).mean()
        df2 = df2[df2['sample'].notna()]
        df2 = df2.reset_index()

        df3["sample"] = df3["relative_cpu"].rolling(rolling).mean()
        df3 = df3[df3['sample'].notna()]
        df3 = df3.reset_index()

        df4["sample"] = df4["relative_cpu"].rolling(rolling).mean()
        df4 = df4[df4['sample'].notna()]
        df4 = df4.reset_index()

        df5["sample"] = df5["relative_cpu"].rolling(rolling).mean()
        df5 = df5[df5['sample'].notna()]
        df5 = df5.reset_index()

        df6["sample"] = df6["relative_cpu"].rolling(rolling).mean()
        df6 = df6[df6['sample'].notna()]
        df6 = df6.reset_index()

        overloadCPUs.append(df2[df2["sample"] > 97].index[0])

        x1 = np.arange(len(df))
        x2 = np.arange(len(df2))
        x3 = np.arange(len(df3))
        x4 = np.arange(len(df4))
        x5 = np.arange(len(df5))
        x6 = np.arange(len(df6))

        fig = plt.figure(0, figsize=(5, 4), dpi=100)
        matplotlib.rcParams.update({'font.size': 11})

        ax = fig.add_subplot(111)
        ax2 = ax.twiny()
        ax.plot(x5, df5["sample"], label="Gateway 0")
        ax.plot(x6, df6["sample"], label="Gateway 1")
        ax.plot(x1, df["sample"], label="Instance 0")
        ax.plot(x2, df2["sample"], label="Instance 1")
        ax.plot(x3, df3["sample"], label="Instance 2")
        ax.plot(x4, df4["sample"], label="Instance 3")
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("CPU Usage %", fontsize=11)
        ax.legend()

        ax.set_ylim(0, 100)
        ax.set_xlim(0, 750)
        ax2.plot(range(200), np.zeros(200), color="white")
        ax2.set_xlim(0, 150)
        ax2.set_xlabel("No. of Players")

        # plt.xlim(0, 500)

        if i == 2:
            plt.savefig("exp9.4-2.cpu.pdf")
        plt.show()

    print(overloadCPUs)
    avgCPU = sum(overloadCPUs) / len(overloadCPUs)
    print("4srv, 2gw", avgCPU)
    print("player", avgCPU / 5)
    return avgCPU / 5


def plotExp9_1():
    overloadCPUs = []
    for i in range(5):
        # folder = "result/20210729142442.2srv.1gw.5s/" + str(i) + "/"
        folder = "result/20210730104451/" + str(i) + "/"

        f1 = findFileinPath(folder, "server-system-10.0.8.6")
        f3 = findFileinPath(folder, "gateway-system-")

        df = processCPU(f1, 4)
        df3 = processCPU(f3, 4, startMs=0)

        df["sample"] = df["relative_cpu"].rolling(4).mean()
        df = df[df['sample'].notna()]
        df = df.reset_index()

        df3["sample"] = df3["relative_cpu"].rolling(4).mean()
        df3 = df3[df3['sample'].notna()]
        df3 = df3.reset_index()

        overloadCPUs.append(min(df3[df3["sample"] > 97].index[0], df[df["sample"] > 90].index[0]))

        x1 = np.arange(len(df))
        x3 = np.arange(len(df3))

        plt.figure(0, figsize=(5, 4), dpi=100)
        plt.plot(x1, df["sample"], label="Instance 0")
        plt.plot(x3, df3["sample"], label="Gateway")

        plt.ylim(0, 100)

        # plt.xlim(0, 500)
        ax = plt.gca()
        matplotlib.rcParams.update({'font.size': 11})
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("CPU Usage %", fontsize=11)
        plt.legend()

        plt.show()

    print(overloadCPUs)
    avgCPU = sum(overloadCPUs) / len(overloadCPUs)
    print("4srv, 1gw", avgCPU)
    print("player", avgCPU / 5)
    return avgCPU / 5


def plotExp9Strong():
    p0 = 33
    # p05 = plotExp9_1()
    # p1 = plotExp9()
    p2 = plotExp9_2()
    # p3 = plotExp9_3()
    y = [p0, p05, p1, p2, p3]
    x = ["1 Server \n 0 Gateway", "1 Server\n1 Gateway", "2 Servers \n1 Gateway", "4 Servers\n1 Gateway",
         "4 Servers\n2 Gateways"]

    plt.figure(2, figsize=(6, 4))
    plt.plot(x, y)
    plt.xlabel("No. of Workers / Roles")
    plt.ylabel("No. of Players")
    plt.ylim(0, 110)
    plt.tight_layout()
    plt.savefig("exp9.strong.pdf")
    plt.show()


if __name__ == '__main__':
    ## Azure Function: Terrain Population
    # plotExp1_1()
    ## Azure Function: Player Operation
    # plotExp1_2()
    # plotExp1_3()

    # merge above two plots
    # plotExp1_2_3()
    # plotExp1_2_3_6()
    # Azure Function Traces: Terrain Population
    # plotExp1_4()

    ## Azure Storage: Player Ban File
    # plotExp2_1()
    ## Azure Storage: Region File
    # plotExp2_2()

    ## Experiment: region file cache policy
    # plotRegionFileCache()

    ## Increasing workload (Straight Walk)
    # plotExp4_2CPU()
    # plotExp4_2Tick()
    # plotExp4_2Dur()

    ## Increasing workload (Random Behavior)
    # plotExp5_CPU()
    # plotExp5_Tick()
    # plotExp5_Players()

    ## Fixed workload
    plotExp6()
    # plotLocal()

    ## Overhead of using serverless tech
    # plotExp7()

    ## Multiple MVE instances
    # plotExp9Strong()

    ## Das5
    # plot4_2TickDas5()

    ## removed exp
    # plotExp4_1CPU()
    # plotExp4_1Tick()
