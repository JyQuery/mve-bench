import configparser
import hashlib
import json
import os
from datetime import datetime
import tempfile

import paramiko
from util import SshClient

with open("config.json") as configFile:
    config = json.load(configFile)

try:
    gatewayList = config['gateways']
    functionList = config['functions']
except:
    gatewayList = []
    functionList = []
serverList = config['servers']
clientList = config['clients']
mvepath = config['benchmark']['mvepath']


def executebash(ssh, username, password):
    ssh.command("chmod +x ./mve/install.sh")
    ssh.command("/bin/bash ./mve/install.sh")
    # check if root user
    # if username == "root":
    #     ssh.command("/bin/bash ./mve/install.sh")
    # else:
    #     ssh.command('echo "{}" | sudo -S -k /bin/bash ./mve/install.sh'.format(password))


def isremote(ssh, file):
    path = "{}/{}".format(mvepath, file)
    remoteMd5stout = ssh.command("md5sum " + path)

    # no such file in remote
    if len(remoteMd5stout) != 1:
        return True

    # file exists in remote, check remote and local md5
    remoteMd5 = remoteMd5stout[0].split()[0]
    localMd5 = hashlib.md5(open('./mve/opencraft.jar', 'rb').read()).hexdigest()

    if remoteMd5 != localMd5:
        return True
    return False


def uploadtmpjson(ssh, data, remotename):
    fd, path = tempfile.mkstemp()

    try:
        with os.fdopen(fd, 'w') as tmp:
            json.dump(data, tmp)
        ssh.putfile(path, "./mve/" + remotename)
    finally:
        os.remove(path)


def installserver(host, port, username, password):
    ssh = SshClient(host, port, username, password)
    ssh.command("mkdir -p mve/config")

    # avoid sending large files that already exist in remote
    for file in ["opencraft.jar"]:
        if isremote(ssh, file):
            ssh.putfile('{}/{}'.format(mvepath, file))

    for file in ["config/opencraft.yml", "pecosa.py", "mves.py", "install.sh"]:
        ssh.putfile('{}/{}'.format(mvepath, file))

    # generate benchmark json for mve server
    data = {"benchmarkserver": config["benchmarkserver"],
            "pingtarget": config["benchmark"]["pingtarget"]}
    uploadtmpjson(ssh, data, "benchmarks.json")

    executebash(ssh, username, password)


def installclient(host):
    client = clientList[host]
    ssh = SshClient(host, client['port'], client['username'], client['password'])
    ssh.command("mkdir mve")

    # avoid sending large files that already exist in remote
    for file in ["yardstick.jar"]:
        if isremote(ssh, file):
            ssh.putfile('{}/{}'.format(mvepath, file))

    # send and overwrite files
    for file in ["yardstick.toml", "mvec.py", "pecosa.py", "install.sh"]:
        ssh.putfile('./mve/' + file, './mve/' + file)

    # generate benchmark json for mve client
    data = {"benchmarkserver": config["benchmarkserver"],
            "mveserver": client['server']}

    uploadtmpjson(ssh, data, "benchmarkc.json")
    ssh.command('sed -i "s/HOST_HERE/{}/g" ./mve/yardstick.toml'.format(client['server']))

    executebash(ssh, client['username'], client['password'])


def installgw(gateway):
    client = gatewayList[gateway]
    ssh = SshClient(gateway, client['port'], client['username'], client['password'])
    ssh.command("mkdir mve")

    # avoid sending large files that already exist in remote
    for file in ["opencraft-gateway.jar"]:
        if isremote(ssh, file):
            ssh.putfile('{}/{}'.format(mvepath, file))

    # generate gateway-config.json for gateway

    # send and overwrite files
    for file in ["gateway-config.json", "mvegw.py", "pecosa.py", "install.sh"]:
        ssh.putfile('./mve/' + file, './mve/' + file)

    # generate benchmark json for mve client
    data = {"benchmarkserver": config["benchmarkserver"]}
    uploadtmpjson(ssh, data, "benchmarkgw.json")

    executebash(ssh, client['username'], client['password'])


if __name__ == "__main__":
    print("Deploying {} MVE gateways ...".format(len(gatewayList)))
    for gateway in gatewayList:
        print("Deploying Gateway: " + gateway)
        installgw(gateway)

    print("Deploying {} MVE servers ...".format(len(serverList)))
    startTime = datetime.utcnow()
    for host in serverList:
        print("Deploying MVE Server: " + host)
        srv = serverList[host]
        installserver(host, srv['port'], srv['username'], srv['password'])

    print("Deploying {} MVE clients ...".format(len(clientList)))
    for host in clientList:
        print("Deploying MVE Client: " + host)
        installclient(host)

    print("Deployment complete. Elapsed time: {} \nYou can now start benchmark"
          .format((datetime.utcnow() - startTime).total_seconds()))
