# PySASS

### What is this?
PySASS is part of the results of a master thesis and is an assembler/diassembler for Nvidia CUDA kernels containing
* disassemble CUDA kernels from SM 50 up to SM 120
* assemble CUDA kernels from SM 70 up to SM 120 (SM 50 to 62 has a different encoding scheme that was never implemented for the assembly direction because probably none of them exist anymore in real life)
* random valid-instructions-generator
* a way to create new kernels using Python, Python SASS instruction wrappers and a CUDA kernel template

PySASS was created and tested only on Linux with Python 3.12. The Python parts will probably also run without issues on Windows and Mac. The C++ extensions do load a file every now and then and may run into issues with slash/backslash of the file paths. As of time of writing Python 3.12++ should be fine. C++ extensions are included, using less than Python 3.12 may cause trouble.

The report is available in `05_Report` of this repository. The original is available in the ETH Zürich library.
 
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

# How to install
Unfortunately there is no pip module yet. The following shows how to install all modules using Python 3.13
1. create a new virtual environment and activate it
   ```bash
   $> python3.13 -m venv ~/venvs313/pysass
   $> source ~/venvs313/pysass/bin/activate
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
    * run py_cubin as a server for indicated SM versions
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
5. Install the VSCode extension. This one is included in the repository for convenience. Note: `cubinext` is short for `CUDA binary extension`.
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
    * build Flutter app as web-release, cd into `10_Projects/11_VSCodeExt/cubinext/cubinext`
      ```bash
      $> flutter build web --release
      ```
    * navigate into the folder that contains *package.json* (`cd ..` from the previous location) and run
      ```bash
      $> vsce package
      ```
    * install the extension from the same folder
      ```bash
      $> code --install-extension cubinext-0.0.1.vsix
      ```
6. Start the py_cubin service using, for example
    ```bash
    $> py_cubin_smd_service [86]
    ```
    or any other architecture, for example [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120] to load all of them.
    * Not running the py_cubin server and trying to decode a CUDA binary will cause an error.
    * Trying to load a binary of a not preloaded SM architecture will also cause an error.
7. open Cubinext in VSCode
    * press `ctrl+p`
    * type `Open empty Cubinext`
    * this will open a view with the 'open' and 'upload' buttons.
      ||
      |:-------------------------:|
      | ![](img/empty-cubinext.png){width=80%} |
    * press the 'open' (top one) button and navigate to `PySASS/10_Projects/08_PyCubin/py_cubin/test_bins`. That folder contains a small CUDA kernel that does nothing useful but is present for every architecture and can be decoded to test the extension.
    * loading the SM 86 test binary should show the following
      ||
      |:-------------------------:|
      | ![](img/sm86-cubinext.png){width=80%} |
    * a decoded binary can be downloaded using the *arrow-down* button on the right and uploaded again with the *arrow-up* button, also shown in the empty cubinext. The decoded data is stored in an sqlite database and can also be opened with any tool that can open sqlite databases.

# Custom CUDA kernels
`13_PySASSCreate` contains all tutorial scripts (Section 6 in the report) and all benchmark scripts (Section 7 in the report) and the scripts to create CUDA templates.

##### CUDA templates
Creating custom CUDA kernels requires a template with enough "instruction slots" to avoid having to write a correct C++ embedded CUDA binary from scratch. A good approach are loops with a certain number of loop unrolling, type casts, and other things where the CUDA compiler feels like spreading out a bit.

* check out all the `kernel_w_loop_template_gen...py` scripts. All the scripts create CUDA templates using components and configurations. The goal is to create a template that
    * `kernel_w_loop_template_gen_kk.py`: create a template that contains `k` kernels. 3000 kernel will fill about 25 GB of RAM to compile. This is the template used for bulk benchmark generation.
    * `kernel_w_loop_template_gen_single_no_loop.py`: create a template with one kernel with encompassing C++ that only runs the kernel once.
    * `kernel_w_loop_template_gen_single.py`: create a template with only one kernel with encompassing C++ that runs the kernel N times.

Creating CUDA kernel with an approximate number of instructions and some encompassing C++, useful for benchmarking, is the only reason the template scripts do what they do.

Various template projects are already available in `template_projects`. In fact, they are the reason why 30ish percent of this repo is CUDA, even though the actual CUDA code is useless.
* `template_1k`: 1 kernel per CUDA binary, roughly 60 instruction slots, encompassing C++ runs the kernel N times in a loop
* `template_1k_120`: 1 kernel per CUDA binary, roughly 120 instruction slots, encompassing C++ runs the kernel N times in a loop
* `template_1k_no_loop`: 1 kernel per CUDA binary, roughly 60 instruction slots, encompassing C++ runs the kernel once
* `template_1k_no_loop_120`: 1 kernel per CUDA binary, roughly 120 instruction slots, encompassing C++ runs the kernel once
* `template_1k_no_loop_240`: 1 kernel per CUDA binary, roughly 120 instruction slots, encompassing C++ runs the kernel once
* `template_30k`: 30 kernel per CUDA binary, roughly 60 instruction slots each, encompassing C++ runs the kernel N times in a loop
* `template_500k`: 500 kernel per CUDA binary, roughly 60 instruction slots each, encompassing C++ runs the kernel N times in a loop
* `template_1000k`: 1000 kernel per CUDA binary, roughly 60 instruction slots each, encompassing C++ runs the kernel N times in a loop
* `template_3000k`: 3000 kernel per CUDA binary, roughly 60 instruction slots each, encompassing C++ runs the kernel N times in a loop
* `template_3600k`: 3600 kernel per CUDA binary, roughly 60 instruction slots each, encompassing C++ runs the kernel N times in a loop

**NOTE**: the kernel have to be compiled first. Make sure to build in *release* mode. The resulting binaries are moved into the subfolder `benchmark_binaries`. Building is set up to just open the respective project in VSCode, running the CMakeLists configuration and press 'build'. Note that compiling the larger templates (3000 kernel and above) will use up a giant amount of RAM.

#### Custom CUDA tutorials
The scripts `tutorial_0...py` up to `tutorial_5...py` outline a couple of useful techniques and are described in detail in chapter 6 of the report.

#### Custom CUDA benchmarks
The scripts `benchmark_....py` contain Python scripts that create and run CUDA kernel that will benchmark one specific instruction. For example `benchmark_dadd.py` will benchmark the `DADD` (double precision add) instruction.

The scripts containing `...bulk_gen...` aim at creating 100'000ds of CUDA kernels for the same number of SASS instruction configurations. Maybe, don't test this repo with those scripts.

For example, running benchmark script `benchmark_ffma.py` as is will produce roughly the following output. The benchmark script runs the kernel with the FFMA (single precition fused multiply add) instruction with an increasing number of wait cycles afterwards until the result is correct. `Wait time: 5` means, there was a `Wait time: 1...4` beforehand where the result was wrong. Thus on SM 86, the instruction requires 5 cycles to complete.
```bash
$> .../PySASS/10_Projects/13_PySASSCreate/benchmark_ffma.py 
Loading sass 86 object

Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_instructions.txt.in.pickle...loaded 1271 instruction classes
Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_classes_.pickle...
Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_skipped_classes_.pickle...
Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_instr_desc.json...
Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_opc_refs_.pickle...
Open .../venvs313/pysass/lib/python3.13/site-packages/py_sass/DocumentSASS/sm_86_lookup.pickle...
... ok [4.3052427768707275]
Calc KK_Instr...
... ok [1.6689300537109375e-06]
0.0.bin
0.1.bin
0.2.bin
0.3.bin
0.4.bin
0.5.bin
0.6.bin
0.7.bin
0.8.bin
create_modified_binaries is finished

Test results with no barrier [0]
 Wait time: 5                            
This one should be empty: CudaErr:  
This one should be 815:  815 [OK]
This one must match the required loop_count 10:  10 [OK]
This is the executed loop_count 10:  10 [OK]
This is the the cycle count of the last iteration:  5
This is the kernel index and should be 0:  0 [OK]
This is the shader stage index and should be 0:  0 [OK]
This ones should all be 170.0:  [170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0] [OK]
All clock cycles:  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
Test results with no barrier [1]
 Wait time: 5                            
This one should be empty: CudaErr:  
This one should be 815:  815 [OK]
This one must match the required loop_count 10:  10 [OK]
This is the executed loop_count 10:  10 [OK]
This is the the cycle count of the last iteration:  5
This is the kernel index and should be 0:  0 [OK]
This is the shader stage index and should be 0:  0 [OK]
This ones should all be 170.0:  [170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0] [OK]
All clock cycles:  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
Test results with no barrier [2]
 Wait time: 5                            
This one should be empty: CudaErr:  
This one should be 815:  815 [OK]
This one must match the required loop_count 10:  10 [OK]
This is the executed loop_count 10:  10 [OK]
This is the the cycle count of the last iteration:  5
This is the kernel index and should be 0:  0 [OK]
This is the shader stage index and should be 0:  0 [OK]
This ones should all be 170.0:  [170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0] [OK]
All clock cycles:  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
Test results with no barrier [3]
 Wait time: 5                            
This one should be empty: CudaErr:  
This one should be 815:  815 [OK]
This one must match the required loop_count 10:  10 [OK]
This is the executed loop_count 10:  10 [OK]
This is the the cycle count of the last iteration:  5
This is the kernel index and should be 0:  0 [OK]
This is the shader stage index and should be 0:  0 [OK]
This ones should all be 170.0:  [170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0] [OK]
All clock cycles:  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
Test results with no barrier [4]
 Wait time: 5                            
This one should be empty: CudaErr:  
This one should be 815:  815 [OK]
This one must match the required loop_count 10:  10 [OK]
This is the executed loop_count 10:  10 [OK]
This is the the cycle count of the last iteration:  5
This is the kernel index and should be 0:  0 [OK]
This is the shader stage index and should be 0:  0 [OK]
This ones should all be 170.0:  [170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0, 170.0] [OK]
All clock cycles:  [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
All test results with no barrier [4]
[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
Finished
```

#### Python SASS instruction wrappers
The scripts `sass_create_75.py` and `sass_create_86.py` contain plenty of instruction wrappers. The steps are as follows:
1. run py_cubin service with the random instruction generator. For example for SM 86, use
   ```bash
   $> py_cubin_smd_service [86.S]
   ```
   There is a `.E` as well. That random generator was used to create the encoder and decoder and contains much more variation than is necessary to create simple instruction wrappers. Generally, stick to the `.S`.
2. Find the instruction class to wrap in `PySASS/py_sass/DocumentSASS/sm_[SM]_instructions.txt`. Instruction classes are described in detail in the report. There is a half finished instruction lookup in the *dev* branch. Until that one is finished, selecting instructions manually is necessary.
3. for the F2F instruction class `f2f_f64_upconvert__R_R32_R_RRR`, the wrapper looks as follows
   ```Python
   class SASS_KK__f2f_f64_upconvert__R_R32_R_RRR:
    # Make the wrapper configurable by passing registers, barriers and predicates... Only pass arguments for things worth changing.
    # Some bits just like to be some constant value or 0.
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, 
                 Rd:tuple,
                 Rb_negate:bool, Rb_absolute:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = 'f2f_f64_upconvert__R_R32_R_RRR'

        # This is the random instruction generator: uncomment this to generate a valid but random 'enc_vals' dictionary...
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        # ... then modify this dictionary to one's liking
        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Rb': SASS_Create_Utils.sass_bits_from_str('37U:8b'),           # set by param
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('38U:8b'),           # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # set by param
            'dstfmt.srcfmt': SASS_Create_Utils.sass_bits_from_str('19U:5b'),# keep 19, only 32 to 64 available, which is 19
            'ftz': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0, .noftz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0, .RN
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # set by param
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        # Use the params of the wrapper and overwrite the respective aliases with the parameterized values. For example
        # use the passed destination register 'Rd' instead of R38 in the 'enc_vals' above
        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        # Run this script to check if the configuration is valid.
        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Assign to some accessible field. Keep using self.class_name and self.enc_vals.
        self.class_name = class_name
        self.enc_vals = enc_vals
   ```