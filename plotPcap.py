import pyshark
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


# print(cap[1].ip.src)
# print(cap[1].frame.time)
# cap[1].
# pkt.sniff_timestamp
# for pkt in cap:
#     print(pkt.sniff_timestamp)

# print(str(cap[1].tcp))

def processCapture(cap, srcIp="10.0.0.4", dstIp="20.150.54.36"):
    startTimestamp = 0
    pktList = []
    dfs = []
    i = 0
    for pkt in cap:

        if float(pkt.sniff_timestamp) - startTimestamp > 3:
            startTimestamp = float(pkt.sniff_timestamp)

            if len(pktList) > 0:
                tmpDf = pd.DataFrame(pktList)
                tmpDf["seconds"] = tmpDf["timestamp"] - tmpDf["timestamp"].shift(1)
                # dfs.append(tmpDf)
                tmpDfSent = tmpDf[tmpDf["srcip"] == srcIp].head(8)
                # print(tmpDfSent)
                dfs.append({"totalSent": tmpDfSent[tmpDfSent["isAck"] == False]["seconds"].sum(),
                            "totalRecv": tmpDf[tmpDf["srcip"] == dstIp]["seconds"].sum(),
                            "totalTime": tmpDf["seconds"].sum()
                            })

                pktList.clear()
        isAck = False
        if "This is an ACK to the segment" in str(pkt.tcp):
            isAck = True

        pktList.append({'timestamp': float(pkt.sniff_timestamp),
                        'srcip': pkt.ip.src,
                        'dstip': pkt.ip.dst,
                        'isAck': isAck
                        })
        i += 1

    allDf = pd.DataFrame(dfs)
    print(allDf)
    return allDf


def generate_csv():
    # cap = pyshark.FileCapture('result/tcpdump/premium.e2e.small.pcap')
    # df1 = processCapture(cap)
    # df1.to_csv('result/tcpdump/premium.small.processed.csv')

    # cap2 = pyshark.FileCapture('result/tcpdump/premium.e2e.large.pcap')
    # df2 = processCapture(cap2)
    # df2.to_csv('result/tcpdump/premium.large.processed.csv')

    # cap = pyshark.FileCapture('result/tcpdump/standard.e2e.small.pcap')
    # df1 = processCapture(cap, srcIp="10.0.0.5", dstIp="20.38.118.132")
    # df1.to_csv('result/tcpdump/standard.small.processed.csv')

    cap = pyshark.FileCapture('result/tcpdump/standard.e2e.large.pcap')
    df1 = processCapture(cap, srcIp="10.0.0.5", dstIp="20.38.118.132")
    df1.to_csv('result/tcpdump/standard.large.processed.csv')


def processDf(df1):
    df1["sendPer"] = df1["totalSent"] / df1["totalTime"] * 100
    df1["recvPer"] = df1["totalRecv"] / df1["totalTime"] * 100
    df1["otherTime"] = df1["totalTime"] - df1["totalSent"] - df1["totalRecv"]
    df1["otherPer"] = df1["otherTime"] / df1["totalTime"] * 100
    return df1


def process_csv():
    df1 = pd.read_csv('result/tcpdump/premium.small.processed.csv', index_col=0)
    df1 = processDf(df1)
    df1["exp"] = "Small File\nPremium"
    df2 = pd.read_csv('result/tcpdump/premium.large.processed.csv', index_col=0)
    df2 = processDf(df2)
    df2["exp"] = "Large File\nPremium"
    df3 = pd.read_csv('result/tcpdump/standard.small.processed.csv', index_col=0)
    df3 = processDf(df3)
    df3["exp"] = "Small File\nStandard"
    df4 = pd.read_csv('result/tcpdump/standard.large.processed.csv', index_col=0)
    df4 = processDf(df4)
    df4["exp"] = "Large File\nStandard"

    dfs = [df1, df3, df2, df4]

    # print(df1)
    # print(df2)
    labels = ["Small File\nPremium",
              "Small File\nStandard", "Large File\nPremium", "Large File\nStandard"]
    width = 0.2
    sendPermeans = [df["sendPer"].mean() for df in dfs]
    recvPermeans = [df["recvPer"].mean() for df in dfs]
    otherMeans = [(100 - df["sendPer"].mean() - df["recvPer"].mean()) for df in dfs]

    print(sendPermeans, recvPermeans, otherMeans, sep="\n")

    sendMeans = [df["totalSent"].mean() * 100 for df in dfs]
    valDf1 = pd.DataFrame(list(zip(sendMeans, labels)), columns=['value', 'exp'])
    valDf1["valueType"] = "Sent"

    recvMeans = [df["totalRecv"].mean() * 100 for df in dfs]
    valDf2 = pd.DataFrame(list(zip(recvMeans, labels)), columns=['value', 'exp'])
    valDf2["valueType"] = "Receive"

    oMeans = [df["otherTime"].mean() * 100 for df in dfs]
    valDf3 = pd.DataFrame(list(zip(oMeans, labels)), columns=['value', 'exp'])
    valDf3["valueType"] = "Others"

    valDfs = [valDf1, valDf2, valDf3]

    valAllDf = pd.concat(valDfs)
    # print(sendMeans, recvMeans, oMeans, sep="\n" )
    #
    #
    # df = pd.DataFrame(list(zip(sendMeans, recvMeans, oMeans, labels)),
    #            columns =['value', 'recvMeans', 'oMeans', 'exp'])
    print(valAllDf)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(labels, sendPermeans, width, label='Send requests to retrieve a file')
    ax.bar(labels, recvPermeans, width, bottom=sendPermeans, label='Receive a file from blob storage')
    ax.bar(labels, otherMeans, width, bottom=[(df["sendPer"].mean() + df["recvPer"].mean()) for df in dfs],
           label='Process other network packets')
    # sns.barplot(data=valAllDf, x="exp", y="value", hue="valueType")

    plt.legend(loc="center", title="Events", fontsize=11)
    plt.xticks(fontsize=11)
    plt.xlabel("File Sizes / Storage Solutions", fontsize=11)
    plt.ylabel("% of Time Spent on Events", fontsize=11)
    plt.tight_layout()
    plt.savefig("exp1.5.pdf")
    plt.show()


# generate_csv()
process_csv()
