#!/usr/bin/env bash
#-*- coding: utf-8 -*-
: '
@ File Name    :   requirements.sh
@ Created Time :   2023/09/23 09:30:52

Copyright (C) <2023>  <Abdulrahman Alnaseer>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'
# Identify the operating system
OS="$(uname -s)"

# Install the libssl-dev package, Python 3, and venv
if [ "$OS" == "Linux" ]; then
    # Identify the Linux distribution
    DISTRO="$(lsb_release -is)"

    if [ "$DISTRO" == "Ubuntu" ] || [ "$DISTRO" == "Debian" ]; then
        # Update the package lists for upgrades and new package installations
        sudo apt-get update

        # Install the libssl-dev package
        sudo apt-get install -y libssl-dev

        # Install the python-is-python3 package
        sudo apt-get install -y python-is-python3

        # Install the python3-venv package
        sudo apt-get install -y python3-venv

        # Check if pip is installed, if not, install it
        if ! command -v pip &> /dev/null; then
            sudo apt-get install -y python3-pip
        fi

        # Create a Python virtual environment
        python3 -m venv venv

        # Activate the virtual environment
        source venv/bin/activate

        # Install the requirements from requirements.txt using pip
        pip install -r requirements.txt
    elif [ "$DISTRO" == "Arch" ]; then
        # Install the openssl package (equivalent to libssl-dev in Debian-based distributions)
        sudo pacman -Syu openssl

        # Install Python 3
        sudo pacman -Syu python

        # Check if pip is installed, if not, install it
        if ! command -v pip &> /dev/null; then
            sudo pacman -Syu python-pip
        fi

        # Create a Python virtual environment
        python -m venv venv

        # Activate the virtual environment
        source venv/bin/activate

        # Install the requirements from requirements.txt using pip
        pip install -r requirements.txt
    else
        echo "Unsupported Linux distribution. Please install the libssl-dev or openssl package, Python 3, pip, venv, and the requirements from requirements.txt manually."
    fi
else
    echo "Unsupported operating system. Please install the libssl-dev or openssl package, Python 3, pip, venv, and the requirements from requirements.txt manually."
fi


echo -e "\n\n\033[0;32mBefore you start using KernelBuilder in each new terminal session, remember to activate the Python virtual environment."
echo -e "You can do this by running the following command: \n'source venv/bin/activate'\033[0m\n"
