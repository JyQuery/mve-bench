# To run on MVE client
import json
import socket
import subprocess
from datetime import datetime
from time import sleep
import os

# Connect to benchmark server
with open("benchmarkc.json") as configFile:
    config = json.load(configFile)

host = config["benchmarkserver"]["host"]
port = config["benchmarkserver"]["port"]
print(host, port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.connect((host, port))
local = s.getsockname()
localStr = "{}-{}".format(local[0], local[1])
message = "hello,mveclient"
s.send(message.encode('ascii'))

cProc = subprocess.Popen(["java", "-Xmx6G", "-jar", "yardstick.jar"])
# cProc = subprocess.Popen(["sleep", "15"])

# start metric collection for mve client
now = datetime.utcnow()
nowStr = now.strftime("%Y%m%d%H%M%S")
systemFile = "client-system-{}-{}".format(localStr, nowStr)
devnull = open(os.devnull, 'w')
pecaProc = subprocess.Popen(["python3", "pecosa.py", systemFile, str(cProc.pid)], stdout=devnull)
pecaPid = pecaProc.pid

pingFile = "client-ping-{}-{}".format(localStr, nowStr)
pingf = open(pingFile, "w")
pingProc = subprocess.Popen(["ping", config["mveserver"]], stdout=pingf)

# wait until mve client finishes
i = 0
while True:
    if cProc.poll() is not None:
        break

    if i == 7:
        message = "keepalive,mveclient"
        s.send(message.encode('ascii'))
        i = 0

    sleep(1)
    i += 1

pecaProc.kill()
pingProc.kill()
pingf.close()
sleep(5)
message = "result,mveclient,{},{}".format(systemFile, pingFile)
s.send(message.encode('ascii'))
s.close()
