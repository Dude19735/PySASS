### Notable Dependencies
* elftools
  ```
  pip install pyelftools
  ```
* termcolor
  ```
  pip install termcolor
  ```
* graphviz
  ```
  sudo apt-get install graphviz graphviz-dev
  pip install pygraphviz
  ```
* networkx
  ```
  pip install networkx
  ```

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