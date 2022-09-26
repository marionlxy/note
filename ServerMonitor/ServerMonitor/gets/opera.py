import paramiko


def gets(ip, user, path, private, port=22):
    pkey = paramiko.RSAKey.from_private_key_file(private)
    transport = paramiko.Transport((ip, port))
    transport.connect(username=user, pkey=pkey)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remotepath='/var/log/monitor/monitor.log', localpath=path)
    finally:
        transport.close()


def puts(ip, user, path, private, port=22):
    pkey = paramiko.RSAKey.from_private_key_file(private)
    transport = paramiko.Transport((ip, port))
    transport.connect(username=user, pkey=pkey)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(remotepath='/tasks/monitor.sh', localpath=path)
        sftp.put(remotepath='/tasks/deploy.sh', localpath=path)
    finally:
        transport.close()


def execute(ip, user, private, port=22):
    pkey = paramiko.RSAKey.from_private_key_file(private)
    transport = paramiko.Transport((ip, port))
    transport.connect(username=user, pkey=pkey)
    try:
        client = paramiko.SSHClient()
        client._transport = transport
        client.exec_command(command='bash /tasks/deploy.sh')
    finally:
        transport.close()

