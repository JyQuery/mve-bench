import json
import os
import threading
import socket
from _thread import *
from datetime import datetime
from time import sleep
from util import SshClient
from insight import *

with open("config.json") as configFile:
    config = json.load(configFile)

try:
    gatewayList = config['gateways']
except:
    gatewayList = []
serverList = config['servers']
clientList = config['clients']
functionList = config['functions']
host = config['benchmarkserver']['host']
port = config['benchmarkserver']['port']
timeout = config['benchmarkserver']['timeout']
iteration = config['benchmark']['iteration']
i = 0
mvepath = config['benchmark']['mvepath']
resultpath = config['benchmark']['resultpath']
clientinterval = config['benchmark']['clientinterval']
# ysconfig = 0, all clients use same yardstick.toml
# ysconfig = 1, clients use yardstick.toml.{clientId}
ysconfig = config['benchmark']['ysconfig']
startTime = datetime.utcnow()
startTimeStr = startTime.strftime("%Y%m%d%H%M%S")
csmap = {}


def startclients():
    # start mve servers
    for host in serverList:
        srv = serverList[host]
        ssh = SshClient(host, srv['port'], srv['username'], srv['password'])
        serverList[host]["ssh"] = ssh
        print("Starting mve server:", host)
        # ssh.command("nohup python3 mves.py > /dev/null 2>&1 &")

        # clean cache for region io
        ssh.command("rm -rf ~/mve/worlds")
        ssh.command("cd {}; screen -S mves -dm python3 mves.py".format(mvepath))
    sleep(config['benchmark']['delay'])

    for host in gatewayList:
        client = gatewayList[host]
        ssh = SshClient(host, client['port'], client['username'], client['password'])
        gatewayList[host]["ssh"] = ssh
        print("Starting mve gateway:", host)
        ssh.command("cd {}; screen -S mvegw -dm python3 mvegw.py".format(mvepath))

    # start mve clients
    i = 0
    for host in clientList:
        client = clientList[host]
        ssh = SshClient(host, client['port'], client['username'], client['password'])
        clientList[host]["ssh"] = ssh

        print("Starting mve client:", host)
        csmap.setdefault(clientList[host]["server"], []).append(host)
        if ysconfig == 1 and i >= 1:
            ssh.putfile("mve/yardstick.toml." + str(i), "mve/yardstick.toml")
            ssh.command('sed -i "s/HOST_HERE/{}/g" ./mve/yardstick.toml'.format(client['server']))
        ssh.command("cd {}; touch event.log; screen -S mvec -dm python3 mvec.py".format(mvepath))
        i += 1
        sleep(clientinterval)


def clientthread(c):
    while True:
        data = c.recv(1024)

        if not data:
            continue
        datasp = data.decode('ascii').split(",")

        if datasp[0] != "keepalive":
            print("Message:", c.getpeername(), data)

        # log mve client/server sockets
        if datasp[0] == "hello":
            if datasp[1] == "mveserver":
                serverList[addr[0]]['conn'] = c
            if datasp[1] == "mveclient":
                clientList[addr[0]]['conn'] = c
            if datasp[1] == "mvegw":
                gatewayList[addr[0]]['conn'] = c

        # if mve client/server finishes tasks and sends results
        if datasp[0] == "result":
            if datasp[1] == "mveserver":
                mveserver = c.getpeername()[0]
                mveserverport = c.getpeername()[1]
                print("Collecting results from mveserver", mveserver, mveserverport)
                ssh = serverList[mveserver]["ssh"]

                endFileIndex = len(datasp)
                for j in range(2, endFileIndex):
                    ssh.getfile('./mve/' + datasp[j],
                                'result/{}/{}/{}'.format(startTimeStr, i, datasp[j]))

                # ssh.getfile('./mve/dyconits.log',
                #             '{}/server-dyconits-{}-{}'.format(currResultpath, mveserver, mveserverport))
                ssh.getfile('./mve/opencraft-events.log',
                            '{}/server-events-{}-{}'.format(currResultpath, mveserver, mveserverport))
                # clean server
                # ssh.command('rm -f ./mve/{dyconits.log,opencraft-events.log}')
                serverList[mveserver]["conn"].close()
                break

            if datasp[1] == "mvegw":
                mvegw = c.getpeername()[0]
                mvegwport = c.getpeername()[1]
                print("Collecting results from mvegateway", mvegw, mvegwport)
                ssh = gatewayList[mvegw]["ssh"]

                endFileIndex = len(datasp)
                for j in range(2, endFileIndex):
                    ssh.getfile('./mve/' + datasp[j],
                                'result/{}/{}/{}'.format(startTimeStr, i, datasp[j]))

                gatewayList[mvegw]["conn"].close()
                break

            # mveclient finishes tasks
            if datasp[1] == "mveclient":
                mveclient = c.getpeername()[0]
                mveclientport = c.getpeername()[1]
                print("Collecting results from mveclient", mveclient, mveclientport)

                endFileIndex = len(datasp)
                for j in range(2, endFileIndex):
                    clientList[mveclient]["ssh"].getfile('./mve/' + datasp[j],
                                                         '{}/{}'.format(currResultpath, datasp[j]))

                clientList[mveclient]["ssh"].getfile('./mve/event.log',
                                                     '{}/client-events-{}-{}'.format(currResultpath, mveclient,
                                                                                     mveclientport))
                # remove current cs pair
                mveserver = clientList[mveclient]["server"]
                csmap[mveserver].remove(mveclient)

                if len(gatewayList) == 0:
                    # check if all clients for one server finish
                    if len(csmap[mveserver]) == 0:
                        # shutdown mve server if there is no active client
                        print("Shuting down server: ", serverList[mveserver]["conn"].getpeername())
                        serverList[mveserver]["conn"].send(b"bye,bmserver")
                        break
                else:
                    for mveserver in serverList:
                        print("Shuting down server: ", serverList[mveserver]["conn"].getpeername())
                        serverList[mveserver]["conn"].send(b"bye,bmserver")
                    for gateway in gatewayList:
                        print("Shuting down gateway: ", gatewayList[gateway]["conn"].getpeername())
                        gatewayList[gateway]["conn"].send(b"bye,bmserver")

    c.close()


if __name__ == "__main__":
    os.mkdir("{}/{}".format(resultpath, startTimeStr))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.bind((host, port))
    s.bind(("0.0.0.0", port))
    s.listen(100)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    s.settimeout(timeout)
    print("Benchmark server listen on {}:{}".format(host, port))

    # iteration parameters
    nextI = True
    currResultpath = None
    iTime = None
    while True:
        # if there is iteration
        if i < iteration:
            # if this iteration is not started
            if nextI:
                print("Starting iteration", i)
                nextI = False
                currResultpath = "{}/{}/{}".format(resultpath, startTimeStr, i)
                os.mkdir(currResultpath)
                iTime = datetime.utcnow()
                threading.Thread(target=startclients).start()

        # end benchmark server if there is no pending iteration
        else:
            # collect aggregated Function metrics after benchmark ends
            for func in functionList:
                responseData = postMetric(functionList, func)
                with open('{}/function-{}-metrics'.format(currResultpath, func), 'w') as f:
                    json.dump(responseData, f)
            print("Benchmark Complete. Elapsed Time:", (datetime.utcnow() - startTime).total_seconds())
            break

        try:
            c, addr = s.accept()
            # print('Connected to', addr)
            start_new_thread(clientthread, (c,))
        except socket.timeout:
            # Remove active mve server without clients
            for cs in list(csmap):
                if len(csmap[cs]) == 0:
                    csmap.pop(cs, None)

            # if no active mve c/s
            if len(csmap) == 0:
                for func in functionList:
                    print("Collecting results from function", func)
                    # retrieve Function query
                    for table in ["requests", "performanceCounters"]:
                        responseData = insightQuery(functionList, func, 'PT1H', iTime.strftime("%Y-%m-%d %H:%M:%S"),
                                                    table=table)
                        with open('{}/function-{}-{}-{}'.format(currResultpath, func, table,
                                                                iTime.strftime("%Y%m%d%H%M%S")), 'w') as f:
                            json.dump(responseData["tables"][0], f)
                print("Iteration {} Complete, results are stored in: {}".format(i, currResultpath))
                # start next iteration
                i += 1
                nextI = True
    s.close()
