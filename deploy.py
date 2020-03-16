import sys
import configparser
import os
from project import Project


# pip install --index-url http://mirrors.aliyun.com/pypi/simple/ paramiko --trusted-host mirrors.aliyun.com


def load_configs(config_file="config.ini"):
    # 执行脚本位置 deploy.py的位置
    project_root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config = configparser.ConfigParser()
    config.read(os.path.join(project_root_dir, config_file))
    return config


def run(configs):
    build_path = set()
    for conf in configs:
        pj = Project(conf)
        # 同项目只编译一次
        if pj.local_project_path not in build_path:
            build_path.add(pj.local_project_path)
            pj.build_project()
        pj.upload_jar()
        pj.restart_project()
        pj.close()


if __name__ == '__main__':
    project_configs = load_configs()
    if len(sys.argv) <= 1:
        print("参数传入一个或多个以下项目名:")
        print([k for k in project_configs.sections()])
        sys.exit()

    project_names = sys.argv[1:]
    run_configs = []
    for name in project_names:
        if name not in project_configs.sections():
            print(f"项目名称[{name}]错误,参数传入以下项目名之一:")
            print([k for k in project_configs.sections()])
            sys.exit()
        run_configs.append(project_configs[name])

    run(run_configs)
