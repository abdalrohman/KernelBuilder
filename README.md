# KernelBuilder

KernelBuilder is a script that automates the process of building a Linux kernel. It downloads the kernel source code, Clang compiler, and then compiles the kernel.

## Prerequisites

- Python 3.x
- `make` command-line utility

Before running the script, please ensure that you have the necessary packages installed on your system. You can do this by running the `requirements.sh` script:

```bash
chmod +x requirements.sh
./requirements.sh
```

This script will install the `libssl-dev` and `python-is-python3` packages, check if `pip` is installed and if not, install it, and finally install the requirements from `requirements.txt` using `pip`.

After the script finishes installing the necessary packages and setting up the Python virtual environment, remember to activate the Python virtual environment in each new terminal session before using KernelBuilder. You can do this by running the following command:

```bash
source venv/bin/activate
```

## Configuration

The script uses a configuration file (`config.ini`) to load various settings. Here's how you can modify it:

1. Open the `config.ini` file in a text editor.
2. You will see different sections like `[KERNEL]`, `[CLANG]`, and `[ANYKERNEL3]`. Each section contains different configuration options for the kernel, Clang, and AnyKernel3 respectively.
3. Change the value of the configuration options as per your requirements.

Here's a brief description of each configuration option:

- `[KERNEL]`:
  - `kernel_name`: The name of the kernel. This is also used as the name of the folder where the kernel source code is stored.
  - `kernel_url`: The URL of the kernel source code.
  - `kernel_branch`: The branch of the kernel source code to use.
  - `kernel_config`: The kernel configuration to use.
  - `kernel_build_dir`: The directory where the kernel should be built.

- `[CLANG]`:
  - `clang_name`: The name of the Clang compiler. This is also used as the name of the folder where the Clang compiler is stored.
  - `clang_url`: The URL of the Clang compiler.
  - `extra_options`: Extra compiler options. This allows you to customize the compiler behavior according to your needs.
  - Other options are compiler options.

- `[ANYKERNEL3]`:
  - `anykernel3_url`: The URL of AnyKernel3.
  - `anykernel3_branch`: The branch of AnyKernel3 to use.
  - `anykernel3_folder`: The folder where AnyKernel3 should be downloaded.

Please ensure that these configurations are correct before running the script. If you encounter any issues, feel free to ask for help!

## Usage

To run the script, use the following command:

```bash
python3 build.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

KernelBuilder is licensed under the GNU General Public License v3.0. This means you can freely use, modify, and distribute it, but you must disclose your source code and changes. For more details, see the [GNU General Public License](http://www.gnu.org/licenses/). 

Please note that this program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

Copyright (C) 2023 Abdalrohman Alnaseer
