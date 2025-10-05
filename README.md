# PySASS

### What is this?
PySASS is an assembler/diassembler for Nvidia CUDA kernels containing
* disassemble CUDA kernels from SM 50 up to SM 120
* assemble CUDA kernels from SM 70 up to SM 120 (SM 50 to 62 has a different encoding scheme that was never implemented for the assembly direction because probably none of them exist anymore in real life)
* random valid-instructions-generator
* a way to create new kernels using Python and a kernel template
* PySASS was created and tested only on Linux with Python 3.12. The Python parts will probably also run without issues on Windows and Mac. The C++ extensions do load a file every now and then and may run into issues with slash/backslash of the file paths. As of time of writing Python 3.12++ should be fine.
* C++ extensions are included, using less than Python 3.12 may cause trouble.
 
##### 06_PySASSExt
This is the CPP extensions module for 07_PySASS. It contains various components implemented with C++, included with Nanobind.

##### 07_PySASS
This module contains everything to do with formalizing Nvidia SASS starting with parsing the output of https://github.com/0xD0GF00D/DocumentSASS. This module is explained in detail in Chapter 2 of the report.

##### 08_PyCubin
This module contains everything to do with decoding and encoding CUDA binaries. It runs as a server on the localhost. This module is explained in Chapter 5 of the report.

##### 10_PySASSCalc
This is not a module but a set of scripts that can be used to calculate the random instruction generator. The output of these scripts is included. If no changes are made to the random generator, they make for an interesting read.

##### 11_VSCodeExt
This is a VSCode extension made in Flutter that can visualize a CUDA binary using PyCubin server. It is outlined in Chapter 4 of the report.

##### 13_PySASSCreate
This is a collection of scripts containing especially how to create new CUDA kernel using Python
* how to load the random instruction generator
* how to create new SASS instruction mappings in Python
* how to decode and encode CUDA binaries
* the tutorial scripts of Chapter 6 in the report
* the benchmarking scripts described in Chapter 7 of the report

### How to install
Unfortunately there is no pip module yet. The following shows how to install all modules using Python 3.13
1. create a new virtual environment and activate it
   ```bash
   $>python3.13 -m venv ~/venvs313/pysass
   $>source ~/venvs313/pysass/bin/activate
   ```
   It may be necessary to install `sudo apt install python3-venv`
2. Install build module
   ```bash
   $> pip install build
   ```
3. `cd` into `PySASS/10_Projects/06_PySASSExt/py_sass_ext` and 
   ```bash
   $> pip install .
   ```
   This will install the PySASS C++ extensions
4. `cd` into `PySASS/10_Projects/07_PySASS`
   ```bash
   $> python3.13 -m build
   $> pip install ./dist/py_sass-0.0.57-py3-none-any.whl
   $> py_sass_install_all
   ```
   **NOTE**: running `py_sass_install_all` may take up to 10 minutes and will create a whole bunch of Python pickles. Each subsequent architecture tends to take more time to calculate, especially SM 90, 100 and 120, where progress may appear to stand still for a while. This is because these architectures feature rather long (up to 70Kb of characters) and complex equations that need evaluation. The evaluation is currently fully Python and recursive and not the quickest.

   For subsequent runs, in case things are changed, there is also a `py_sass_install_finalize_only`
4. `cd` into `PySASS/10_Projects/08_PyCubin`
   ```bash
   $> python3.13 -m build
   $> pip install ./dist/py_cubin-0.0.14-py3-none-any.whl
   ```

   Run py_sass as follows:
    * just run py_subin as a server for indicated SM versions
      ```bash
      $> py_cubin_smd_service [86] 
      $> py_cubin_smd_service [86, 90, 100]
      ```
    * to include the random instruction generator for SM 86, add a `.S`. `S` stands for 'small' and loads the small random generator. There is a large one too, that can be loaded with `.E` and may use a lot of RAM for nothing => stick with the small one. Note: the `.S` has to be passed for each individual SM architecture.
      ```bash
      $> py_cubin_smd_service [86.S, 90, 120]
      $> py_cubin_smd_service [86.S, 90.S, 120]
      $> py_cubin_smd_service [86.S, 90.S, 120.S]
      ```
    * The random instruction generator is **not** needed for decoding and encoding CUDA kernels. It is only required to create new Python wrappers for SASS instructions. Even there, it is not strictly required, but it will generate a valid template that only needs to be modified.
    * the `py_cubin` module includes a non-server version too that can be run with `smd`
      ```
      $> smd -help
      ```
    * `py_cubin_service.py` and `py_cubin_smd.py` contain both respectively. Especially `py_cubin_smd.py` can be modified to run the py_cubin service for example as debug session.
       ```Python
       if __name__ == '__main__':
          ...
       ```
       change to
       ```Python
       if __name__ == '__main__' or True:
          ...
       ```
       to run the module directly from VSCode (or any other editor) directly.
5. Install the VSCode extension. This one is included in the repository for convenience.
    * `cd` into `PySASS/10_Projects/11_VSCodeExt/cubinext`
      ```bash
      $> code --install-extension cubinext-0.0.1.vsix
      ```
   
   To build the extension from scratch
    * install Flutter
    * install vsce
      ```bash
      $> npm install -g vsce
      ```
    * build Flutter app as web-release
      ```bash
      $> cd cubinext
      $> flutter build web --release
      ```
    * navigate into the folder that contains *package.json* and run
      ```bash
      $> vsce package
      ```
    * install the extension
      ```bash
      $> code --install-extension cubinext-0.0.1.vsix
      ```
