### Create module
* activate virtual environment
  ```
  source /home/lol/.venvs/standard/bin/activate
  ```
* cd into the folder that contains the setup.py
  ```
  python3 -m build
  ```
* install newly created module 
    * new install
      ```
      pip install ./dist/test_mod-0.0.7-py3-none-any.whl
      ```
        * [NOTE]: this requires a new version number
    * upgrade install
      ```
      pip install ./dist/test_mod-0.0.7-py3-none-any.whl --upgrade
      ```
        * [NOTE]: this requires a new version number
        * [NOTE]: this leaves resources not in MANIFEST.in untouched
* run finalization script
  ```
  py_sass_install_finalize
  ```
    * [NOTE]: this is only necessary from a complete fresh install
    * [NOTE]: this calculates all data necessary to load an SM_SASS(..)
    * [NOTE]: if this step is omitted, each time an SM_SASS(.X.) is created for the first time, the relevant data will be calculated
