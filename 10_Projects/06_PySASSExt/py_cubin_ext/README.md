# Py_SASS_Ext

This module contains Py_SASS CPP extensions

### More information
Check out Nanobind website at https://nanobind.readthedocs.io/en/latest/packaging.html

### How to include
All the modules are available as
```Python
from py_sass_ext import *
```

### How to install localy
* make sure to activate the correct virtual environment
    * for example 
      ```Bash
      source /home/lol/.venvs/standard/bin/activate
      ```
* cd into py_sass_ext folder
* do
  ```Bash
  pip install . --verbose
  ```
* this installs the module independently of if it's already installed or not or specified verisions.

### How to create whl file
* make sure to activate the correct virtual environment
    * for example 
      ```Bash
      source /home/lol/.venvs/standard/bin/activate
      ```
* cd into py_sass_ext folder
* do
  ```Bash
  pip wheel .
  ```
* then
  ```Bash
  pip install ....whl
  ```
* this will complain if the module is already installed with the same version number

### How to add new module
* add CPP code with hpp, cpp, h files
* add new includes in ```py_sass_ext/src/py_sass_ext/__init__.py```
* add src/module_main_X.cpp and define the bindings
    * use '_' as prefix for ```NB_MODULE(...)```
* add new module target at the top of src/CMakeLists.txt
    * open py_sass_ext/CMakeLists.txt
    * add ```set(MODULE_NAME_X "[new module name]")```
    * add build targets in both ```NOT SKBUILD``` and the other section
        * copy the pattern of the modules that are already there
        * make sure that any additional source files are ```*.cpp```. It doesn't work if they are only ```*.c```. If it doesn't work, the stub generator will throw an ```unknown symbol BlaBla``` error.
        * Don' forget to extend the ```install()``` directive at the bottom for the ```SKBUILD``` version.
* possibly increase the version number in ```pyproject.toml```
    * this is not necessary if ```pip install .``` is used
    * there is no need to change anything else in this file
