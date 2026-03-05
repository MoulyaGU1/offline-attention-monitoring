import os
import subprocess


def build():

    command = [
        "pyinstaller",
        "--onefile",
        "--name",
        "AttentionMapper",
        "--clean",
        "../run_app.py"
    ]

    subprocess.run(command)


if __name__ == "__main__":

    print("Building executable...")

    build()

    print("Build complete. Check dist/ folder.")