#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@ File Name    :   build_kernel.py
@ Author       :   Abdalrohman Alnaseer
@ Created Time :   2023/09/19 06:17:37

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
# Import modules
import os
from pathlib import Path

from utils import (
    CONFIG_FILE,
    compiler_options,
    download,
    export_path,
    extract_tar_gz,
    load_config,
    log,
    prepare_folders,
    run_command,
    check_commands,
)

# Intilize important variable which is later must be moved to config.ini to load from config
BASE_DIR = Path(__file__).parent

KERNEL_NAME = load_config(CONFIG_FILE, "KERNEL", "kernel_name")
KERNEL_URL = load_config(CONFIG_FILE, "KERNEL", "kernel_url")
KERNEL_BRANCH = load_config(CONFIG_FILE, "KERNEL", "kernel_branch")
SRC_DIR = BASE_DIR / "src"
KERNEL_ROOT = SRC_DIR / KERNEL_NAME
KERNEL_CONFIG = load_config(CONFIG_FILE, "KERNEL", "kernel_config")
BUILD_DIR = BASE_DIR / load_config(CONFIG_FILE, "KERNEL", "kernel_build_dir")

REQ_DIR = BASE_DIR / "requirements"


CLANG_URL = load_config(CONFIG_FILE, "CLANG", "clang_url")
CLANG_PATH = REQ_DIR / load_config(CONFIG_FILE, "CLANG", "clang_name")
CLANG_FILE_NAME = REQ_DIR / f"{load_config(CONFIG_FILE, 'CLANG', 'clang_name')}.tar.gz"


ANYKERNEL3_URL = load_config(CONFIG_FILE, "ANYKERNEL3", "anykernel3_url")
ANYKERNEL3_PATH = REQ_DIR / load_config(CONFIG_FILE, "ANYKERNEL3", "anykernel3_folder")
ANYKERNEL3_BRANCH = load_config(CONFIG_FILE, "ANYKERNEL3", "anykernel3_branch")


if __name__ == "__main__":
    check_commands(["make"])

    # create folders
    prepare_folders([REQ_DIR, BUILD_DIR, SRC_DIR])

    # download kernel
    download(KERNEL_URL, KERNEL_ROOT, KERNEL_BRANCH)

    # download clang
    download(CLANG_URL, CLANG_FILE_NAME)
    extract_tar_gz(CLANG_FILE_NAME, CLANG_PATH)

    # download anykernel3
    download(ANYKERNEL3_URL, ANYKERNEL3_PATH, ANYKERNEL3_BRANCH)

    # export environmental path
    export_path(f"{CLANG_PATH}/bin")

    make_opts = compiler_options(BUILD_DIR)
    make_defconfig = make_opts + [KERNEL_CONFIG]
    make_clean = make_opts + ["clean"]
    make_mrproper = make_opts + ["mrproper"]

    # chang to kernel directory
    if os.path.exists(KERNEL_ROOT):
        os.chdir(KERNEL_ROOT)
    else:
        log(f"{KERNEL_ROOT} not exist.", level="error")
        exit(1)

    run_command(make_defconfig, verbose=True)

    run_command(make_opts, verbose=True)
