from os import system
import paramiko


class Project:
    def __init__(self, config):
        local_relative_jar_path = config["local_relative_jar_path"]
        remote_relative_jar_path = config["remote_relative_jar_path"]
        gradle_run_script = config["gradle_run_script"]
        remote_project_path = config["remote_project_path"]
        local_project_path = config["project_path"]
        jar_name = config["jar_name"]
        remote_host = config["remote_host"]
        project_name = config["project_name"]
        username = config["remote_user"]
        passwd = config["remote_passwd"]
        vm_port = config["vm_port"]
        run_params = config["run_params"]
        env_opts = config["env_opts"]
        self.remote_host = remote_host
        self.local_jar_path = local_project_path + local_relative_jar_path + jar_name
        self.remote_jar_path = f'{remote_project_path}{remote_relative_jar_path}{jar_name}'
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(remote_host, username=username, password=passwd)
        transport = paramiko.Transport((remote_host, 22))
        transport.connect(username=username, password=passwd)
        self.sftp = paramiko.SFTPClient.from_transport(transport)
        self.java_opts = f'-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address={vm_port}'
        self.api_path = f'{remote_project_path}/bin/{project_name}'
        self.compile_command = f'cd {local_project_path}; {gradle_run_script}'
        self.run_params = run_params
        self.env_opts = env_opts

    @staticmethod
    def run_local(command):
        print(">> ", command)
        system(command)

    def run_remote(self, command):
        print(self.remote_host, ">> ", command)
        std_in, std_out, std_err = self.ssh.exec_command(command)
        for line in std_out.readlines():
            print(line)

    def build_project(self):
        print(">>" * 10, "build finish")
        self.run_local(self.compile_command)

    def upload_jar(self):
        print(">> upload file from %s to %s" % (self.local_jar_path, self.remote_jar_path))
        self.sftp.put(self.local_jar_path, self.remote_jar_path)

    def restart_project(self):
        self.run_remote(f'JAVA_OPTS={self.java_opts} {self.env_opts} {self.api_path} restart {self.run_params}')

    def stop_project(self):
        self.run_remote(f'JAVA_OPTS={self.java_opts} {self.env_opts} {self.api_path} stop')

    def start_project(self):
        self.run_remote(f'JAVA_OPTS={self.java_opts} {self.env_opts} {self.api_path} start {self.run_params}')

    def close(self):
        self.sftp.close()
        self.ssh.close()
