import os

import paramiko


def findFileinPath(path, keyword):
    it = os.listdir(path)
    for fname in it:
        if keyword in fname:
            if path.endswith("/"):
                return path + fname
            else:
                return path + "/" + fname


class SshClient:
    ssh = paramiko.SSHClient()
    sftp = None

    def __init__(self, host, port, username, password):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, port, username, password)
        self.sftp = self.ssh.open_sftp()

    def command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.readlines()

    def putfile(self, local, remote=None):
        if remote is None:
            remote = local
        self.sftp.put(local, remote)

    def getfile(self, remote, local):
        self.sftp.get(remote, local)

    def close(self):
        self.ssh.close()
        self.sftp.close()
