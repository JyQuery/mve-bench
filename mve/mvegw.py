# To run on MVE gateway
import json
import select
import socket
import subprocess
from datetime import datetime
from time import sleep
import os

# Connect to benchmark server
with open("benchmarkgw.json") as configFile:
    config = json.load(configFile)

host = config["benchmarkserver"]["host"]
port = config["benchmarkserver"]["port"]
print(host, port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.connect((host, port))
local = s.getsockname()
localStr = "{}-{}".format(local[0], local[1])
message = "hello,mvegw"
s.send(message.encode('ascii'))

cProc = subprocess.Popen(["java", "-Xmx12G", "-jar", "opencraft-gateway.jar"])
gwPid = cProc.pid
# cProc = subprocess.Popen(["sleep", "15"])

# start metric collection for mve client
now = datetime.utcnow()
nowStr = now.strftime("%Y%m%d%H%M%S")
systemFile = "gateway-system-{}-{}".format(localStr, nowStr)
devnull = open(os.devnull, 'w')
pecaProc = subprocess.Popen(["python3", "pecosa.py", systemFile, str(cProc.pid)], stdout=devnull)
pecaPid = pecaProc.pid

# pingFile = "gateway-ping-{}-{}".format(localStr, nowStr)
# pingf = open(pingFile, "w")
# pingProc = subprocess.Popen(["ping", config["mveserver"]], stdout=pingf)

# wait until mve client finishes
i = 0
while True:
    if i == 7:
        message = "keepalive,mvegw"
        s.send(message.encode('ascii'))
        i = 0

    sleep(1)
    i += 1

    ready = select.select([s], [], [], 2)
    if ready[0]:
        data = s.recv(1024)
        # print('Received from the server :', data)
        datasp = data.decode('ascii').split(",")

        # all clients finish task
        if datasp[0] == "bye":
            pecaProc.terminate()
            os.kill(gwPid, 9)
            os.wait()
            message = "result,mvegw,{}".format(systemFile)
            s.send(message.encode('ascii'))
            break
