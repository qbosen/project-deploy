from os import system
import paramiko


class Project:
    def __init__(self, config):
        self.local_project_path = config["project_path"]
        self.local_jar_path = config["project_path"] + '/build/libs/' + config["jar_name"]
        self.remote_project_path = config["remote_project_path"]
        self.remote_jar_path = f'{config["remote_project_path"]}/lib/{config["jar_name"]}'
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(config["remote_host"], username=config["remote_user"], password=config["remote_passwd"])
        transport = paramiko.Transport((config["remote_host"], 22))
        transport.connect(username=config["remote_user"], password=config["remote_passwd"])
        self.sftp = paramiko.SFTPClient.from_transport(transport)
        self.java_opts = f'-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address={config["vm_port"]}'
        self.api_path = f'{config["remote_project_path"]}/bin/{config["project_name"]}'

    @staticmethod
    def run_local(command):
        print(">> ", command)
        system(command)

    def run_remote(self, command):
        print(">> ", command)
        std_in, std_out, std_err = self.ssh.exec_command(command)
        for line in std_out.readlines():
            print(line)

    def build_project(self):
        self.run_local(f'cd {self.local_project_path}; ./gradlew clean build')
        print(">>" * 10, "build finish")

    def upload_jar(self):
        self.sftp.put(self.local_jar_path, self.remote_jar_path)
        print(">> upload file from %s to %s" % (self.local_jar_path, self.remote_jar_path))

    def restart_project(self):
        self.run_remote(f'JAVA_OPTS={self.java_opts} {self.api_path} restart')

    def close(self):
        self.sftp.close()
        self.ssh.close()
