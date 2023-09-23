#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@ File Name    :   utils.py
@ Author       :   Abdalrohman Alnaseer
@ Created Time :   2023/09/19 17:30:43

KernelBuilder
Copyright (C) 2023 Abdalrohman Alnaseer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import configparser
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from git import GitCommandError, RemoteProgress, Repo
from loguru import logger
from tqdm import tqdm

CONFIG_FILE = "./config.ini"


# Create a function to write and load from the config file using configparser
def write_default_config(filename):
    config = configparser.ConfigParser()
    config["KERNEL"] = {
        "kernel_name": "super",
        "kernel_url": "https://github.com/sanjeevstunner/android_kernel_xiaomi_vayu.git",
        "kernel_branch": "main",
        "kernel_config": "vayu_defconfig",
        "kernel_build_dir": "build",
    }
    config["CLANG"] = {
        "clang_url": "https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/+archive/fb69815b96ce8dd4821078dd36ac92dde80a23e1/clang-r383902.tar.gz",
        "clang_name": "aosp_clang",
        "ARCH": "arm64",
        "SUBARCH": "",
        "CC": "clang",
        "CC_CCACHE": "ccache clang",
        "CLANG_TRIPLE": "aarch64-linux-gnu-",
        "CROSS_COMPILE": "aarch64-linux-gnu-",
        "CROSS_COMPILE_ARM32": "arm-linux-gnueabi-",
        "LLVM": "1",
        "LLVM_IAS": "1",
        "LTO": "1",
        "extra_options": "",
    }
    config["ANYKERNEL3"] = {
        "anykernel3_url": "https://github.com/osm0sis/AnyKernel3.git",
        "anykernel3_branch": "master",
        "anykernel3_folder": "anykernel3",
    }

    with open(filename, "w") as configfile:
        config.write(configfile)


def load_config(filename, section, key):
    if not os.path.exists(filename):
        write_default_config(filename)

    config = configparser.ConfigParser()
    config.read(filename)

    if key in config[section]:
        return config[section][key]
    else:
        return None


def log(*args, **kwargs):
    """
    Logs a message with a specific level using Loguru.
    Parameters:
    *args: The message to be logged.
    **kwargs: The level of the log (could be "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    # Extract the log level from kwargs and set it to "INFO" if not provided
    level = kwargs.pop("level", "INFO").upper()

    # Convert args to a string for logging
    message = " ".join(map(str, args))

    logger.remove()  # Remove any existing handlers
    logger.add(
        sys.stdout,
        format="<green>[{time:HH:mm:ss}]</green> | <level>{level}</level> | <white>{message}</white>",
        level=level,  # Set to lowest level
    )

    # Log the message with the appropriate level
    logger.log(level, message)


def prepare_folders(folders: list = []):
    if folders:
        folders = folders
    else:
        folders = ["requirements", "src", "build"]
    for folder in folders:
        if not os.path.exists(folder):
            log(f"Creating folder {folder}", level="INFO")
        os.makedirs(folder, exist_ok=True)


# Create a function to check the required commands and raise an error if not available
def check_commands(commands):
    """
    This function checks if the required commands are available in the system.
    If a command is not available, it raises an error.

    Parameters:
        commands (list): A list of commands to check.
    """
    for command in commands:
        if shutil.which(command) is None:
            log(f"Error: Command '{command}' not found.", level="ERROR")
            exit(1)


# Create a function to run a command using subprocess and show the output live
def run_command(
    args: List[Union[str, Path]],
    env: Optional[Dict[str, str]] = None,
    verbose: bool = True,
    capture_output: bool = True,
    **kwargs: Any,
) -> Tuple[str, int]:
    """
    Runs a command and prints the output live.
    Parameters:
        args (List[Union[str, Path]]): The command and its arguments.
        env (Optional[Dict[str, str]]): Additional environment variables. Default is None.
        verbose (bool): Whether to print verbose logs. Default is True.
        capture_output (bool): Whether to capture the command's output. Default is True.
        kwargs (Any): Additional arguments to subprocess.Popen().
    Returns:
        Tuple[str, int]: An empty string and the exit code of the command.
    Raises:
        subprocess.CalledProcessError: If the command exits with a non-zero return code.
        KeyboardInterrupt: If the execution is interrupted by Ctrl+C.
        Exception: If any other exception occurs.
    """
    start_time = time.time()

    # Convert all elements in arg to string
    arg = [str(a) for a in args]

    if env is not None:
        log("Env: {}", env)
        env_copy = os.environ.copy()
        env_copy.update(env)
        kwargs.setdefault("env", env_copy)

    if verbose:
        log(f"Running: {shlex.join(arg)}")

    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.STDOUT)
        kwargs.setdefault("universal_newlines", True)

    try:
        proc = subprocess.Popen(arg, **kwargs)
        while True:
            output = proc.stdout.read(1)
            if output == "" and proc.poll() is not None:
                break
            if output:
                sys.stdout.write(output)
                sys.stdout.flush()
    except subprocess.CalledProcessError as exc:
        log(
            f"Failed to run command '{shlex.join(arg)}' (exit code {exc.returncode}):\n{exc.output}",
            level="error",
        )
        raise
    except KeyboardInterrupt as exc:
        log("\nTerminating...")
        raise SystemExit(1) from exc
    except Exception as exc:
        log(f"Failed to run command '{shlex.join(arg)}': {exc}", level="error")
        raise SystemExit(1) from exc

    runtime = time.time() - start_time
    if verbose:
        log(f"Execution time: {runtime} seconds")

    return "", proc.returncode


# Create a function to download files from git repo or other sources
class GitProgress(RemoteProgress):
    """
    A class that extends RemoteProgress to provide a progress bar for git operations.

    Attributes:
        pbar (tqdm): A tqdm progress bar object.
        message (str): A message to display in the progress bar.
    """

    def __init__(self, pbar, message=""):
        super().__init__()
        self.pbar = pbar
        self.message = message

    def __call__(self, op_code, cur_count, max_count=None, message=""):
        if op_code == self.RECEIVING:
            if max_count:
                self.pbar.total = max_count
            self.pbar.update(cur_count - self.pbar.n)  # will also set self.pbar.n = cur_count

    def __exit__(self, type, value, traceback):
        self.pbar.close()


def is_git_repo(url: str) -> bool:
    """
    Checks if a URL is a git repository.

    Parameters:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a git repository, False otherwise.
    """
    check_url = url.rstrip("/") + "/info/refs?service=git-upload-pack"
    response = requests.get(check_url, timeout=10)
    return response.status_code == 200  # check represents HTTP 200 OK status.


def download(url: str, destination: str, branch: str = "master"):
    """
    Downloads a file from a URL to a destination.
    If the URL is a git repository, it clones the repository.

    Parameters:
        url (str): The URL of the file to download.
        destination (str): The path to save the downloaded file.
        branch (str): The branch to clone from the git repository. Default is 'master'.

    Usage:
        download("https://github.com/example/repo.git", "./destination", "main")
        download("https://file.tar.gz", "./file.tar.gz")
    """
    try:
        if is_git_repo(url):
            if os.path.exists(destination):
                log(f"Updated git repository at [{destination}]")
                repo = Repo(destination)
                with tqdm(
                    total=0, unit="obj", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
                ) as progress:
                    git_progress = GitProgress(progress)
                    repo.remotes.origin.pull(progress=git_progress)
            else:
                log(f"Cloned git repository from [{url}] to [{destination}]")
                with tqdm(total=0, unit="obj") as progress:
                    git_progress = GitProgress(progress)
                    Repo.clone_from(
                        url,
                        destination,
                        branch=branch,
                        depth=1,
                        single_branch=True,
                        progress=git_progress,
                    )
        else:
            if not os.path.exists(destination):
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                block_size = 4096  # 4 Kibibyte
                t = tqdm(total=total_size, unit="iB", unit_scale=True)
                start_time = time.time()
                with open(destination, "wb") as f:
                    for data in response.iter_content(block_size):
                        t.update(len(data))
                        f.write(data)
                        elapsed_time = time.time() - start_time
                        download_speed = t.n / elapsed_time
                        estimated_time = (total_size - t.n) / download_speed
                        t.set_postfix(
                            file_size=str(int((t.n / (1024 * 1024)) + 1)) + "MB",
                            speed=f"{download_speed / (1024 * 1024):.2f}MB/s",
                            eta=f"{estimated_time:.2f}s",
                            refresh=True,
                        )
                t.close()
                log(f"Downloaded file from {url} to {destination}")
                if total_size != 0 and t.n != total_size:
                    log("ERROR, something went wrong", level="error")
            else:
                log(f"{destination} already exists. Skipping download.", level="warning")
    except (requests.exceptions.RequestException, GitCommandError, IOError) as err:
        log(f"Error: Failed to download file from {url}. Error: {err}", level="error")
        raise SystemExit(1) from err


# Create a function to extract .tar.gz and .gz files using tarfile module
def extract_tar_gz(file_name, destination_folder):
    if not os.path.isfile(file_name):
        raise FileNotFoundError(f"File does not exist: {file_name}")

    if not os.path.isdir(destination_folder):
        os.makedirs(destination_folder)

    # Check if destination directory is empty
    if os.listdir(destination_folder):
        overwrite = input(
            f"{destination_folder} is not empty. Do you want to overwrite existing files? (y/n): "
        )
        if overwrite.lower() == "y":
            # Remove all files and subdirectories in the destination directory
            for file in os.scandir(destination_folder):
                if file.is_file():
                    os.remove(file.path)
                elif file.is_dir():
                    shutil.rmtree(file.path)
        else:
            log("Extraction cancelled.")
            return

    with tarfile.open(file_name, "r:gz") as tar:
        tar.extractall(path=destination_folder)

    log(f"Finished extracting {file_name} to {destination_folder}.")


# Create a function to set environment variables
class SystemDetector:
    def __init__(self):
        """
        Constructs all the necessary attributes for the SystemDetector object.
        """
        self.system: str = platform.system()
        self.machine: str = platform.machine()
        self.platform: str = platform.platform()

    def get_architecture(self) -> str:
        """
        Returns the system architecture.
        """
        return "Amd64" if self.machine == "x86_64" else self.machine

    def get_os_type(self) -> str:
        """
        Returns the operating system type.
        """
        if self.system == "Linux":
            if "Microsoft".lower() in self.platform:
                wsl_version: str = self.detect_wsl_version()
                if wsl_version:
                    return f"WSL {wsl_version}"
                else:
                    return "Linux"
            elif "CYGWIN" in self.platform:
                return "Cygwin"
            elif "Android" in self.platform:
                return "Termux"
            else:
                return "Linux"
        elif self.system == "Windows":
            return "Windows"
        elif self.system == "Darwin":
            return "macOS"
        else:
            return "Unknown system"

    def detect_wsl_version(self) -> str or None:
        """
        Detects and returns the version of Windows Subsystem for Linux (WSL) if detected.
        """
        try:
            with open("/proc/version", "r", encoding="utf-8") as version_file:
                version_info: str = version_file.read()
                if "microsoft" in version_info.lower():
                    if "wsl2" in version_info.lower():
                        return "2"
                    else:
                        return "1"
        except FileNotFoundError:
            pass

    def get_system_info(self) -> tuple[str, str, str]:
        """
        Returns a tuple containing the system architecture, operating system type, and platform information.
        """
        architecture: str = self.get_architecture()
        os_type: str = self.get_os_type()

        return architecture, os_type, self.platform


def export_path(bin_dir):
    # Get the current PATH
    _, os_type, _ = SystemDetector().get_system_info()

    if "wsl" in os_type.lower():
        current_path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin"
    else:
        current_path = os.environ.get("PATH", "")

    # Add the new binary directory to the PATH
    new_path = f"{bin_dir}:{current_path}"

    # Export the new PATH
    os.environ["PATH"] = new_path

    log(f"PATH: {os.environ.get('PATH')}")


# TODO adapte this with other compiler
def compiler_options(out_dir=""):
    # Calculate process number to be passed to -j
    j = str(os.cpu_count())

    # Set the out dir read it from the config file
    if out_dir:
        out_dir = out_dir
    else:
        out_dir = load_config(CONFIG_FILE, "KERNEL", "build_dir")

    # Set ARCH and SUBARCH read it from the config file
    arch = load_config(CONFIG_FILE, "CLANG", "ARCH")
    subarch = load_config(CONFIG_FILE, "CLANG", "SUBARCH")

    # Set CC to be clang and if ccache is installed set it to be ccache clang
    cc = (
        load_config(CONFIG_FILE, "CLANG", "CC_CCACHE")
        if shutil.which("ccache")
        else load_config(CONFIG_FILE, "CLANG", "CC")
    )

    # Set CLANG_TRIPLE, CROSS_COMPILE, CROSS_COMPILE_ARM32
    clang_triple = load_config(CONFIG_FILE, "CLANG", "CLANG_TRIPLE")
    cross_compile = load_config(CONFIG_FILE, "CLANG", "CROSS_COMPILE")
    cross_compile_arm32 = load_config(CONFIG_FILE, "CLANG", "CROSS_COMPILE_ARM32")

    # Because the new clang use llvm instead of gcc set the compiler to be llvm LLVM=1
    llvm = "1" if load_config(CONFIG_FILE, "CLANG", "LLVM") == "1" else ""

    # LLVM_IAS=1, add option to use lto LTO=1
    llvm_ias = "1" if load_config(CONFIG_FILE, "CLANG", "LLVM_IAS") == "1" else ""
    lto = "1" if load_config(CONFIG_FILE, "CLANG", "LTO") == "1" else ""

    # Read extra options from the config file
    extra_options = load_config(
        CONFIG_FILE, "CLANG", "extra_options"
    )  # TODO if not empty then set this option else don't set this option

    make_command = [
        "make",
        f"-j{j}",
        f"O={out_dir}",
    ]

    if arch:
        make_command.append(f"ARCH={arch}")

    if subarch:
        make_command.append(f"SUBARCH={subarch}")

    if cc:
        make_command.append(f"CC={cc}")

    if clang_triple:
        make_command.append(f"CLANG_TRIPLE={clang_triple}")

    if cross_compile:
        make_command.append(f"CROSS_COMPILE={cross_compile}")

    if cross_compile_arm32:
        make_command.append(f"CROSS_COMPILE_ARM32={cross_compile_arm32}")

    if llvm:
        make_command.append("LLVM=1")

    if llvm_ias:
        make_command.append("LLVM_IAS=1")

    if lto:
        make_command.append("LTO=1")

    if extra_options:
        make_command.extend(extra_options.split(" "))

    return [make_command for make_command in make_command if make_command]


def apply_patch():
    # TODO
    pass
