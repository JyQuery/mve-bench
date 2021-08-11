# To run on MVE server
import json
import socket
import subprocess
from datetime import datetime
from time import sleep
import os
import select

# Connect to benchmark server
with open("benchmarks.json") as configFile:
    config = json.load(configFile)

host = config["benchmarkserver"]["host"]
port = config["benchmarkserver"]["port"]

# start mve server in background
devnull = open(os.devnull, 'w')
mveProc = subprocess.Popen(['java', '-Xmx6G', '-jar', 'opencraft.jar'])
mvePid = mveProc.pid
sleep(15)

# start socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.setblocking(0)
local = s.getsockname()
localStr = "{}-{}".format(local[0], local[1])
message = "hello,mveserver"
s.send(message.encode('ascii'))

# start metric collection
now = datetime.utcnow()
nowStr = now.strftime("%Y%m%d%H%M%S")
systemFile = "server-system-{}-{}".format(localStr, nowStr)
pecaProc = subprocess.Popen(["python3", "pecosa.py", systemFile, str(mvePid)], stdout=devnull)
pecaPid = pecaProc.pid

# start pinging target
pingFile = "server-ping-{}-{}".format(localStr, nowStr)
pingf = open(pingFile, "w")
pingProc = subprocess.Popen(["ping", config["pingtarget"]], stdout=pingf)

# Listening for instructions from benchmark server
i = 0
while True:
    if i == 5:
        message = "keepalive,mveserver"
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
            os.kill(mvePid, 9)
            os.wait()
            pingProc.kill()
            pingf.close()
            message = 'result,mveserver,{},{}'.format(systemFile, pingFile)
            s.send(message.encode('ascii'))
            break
s.close()
