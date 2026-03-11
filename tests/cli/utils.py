import os
import shlex
import subprocess


def run_cmd(app, cmd, is_app=True):
    if is_app:
        os.environ["RAVYN_DEFAULT_APP"] = app
    cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd
    process = subprocess.run(
        cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False
    )
    stdout = process.stdout
    stderr = process.stderr
    print("\n$ " + (cmd if isinstance(cmd, str) else " ".join(cmd_list)))
    print(stdout)
    print(stderr)
    return stdout, stderr, process.returncode
