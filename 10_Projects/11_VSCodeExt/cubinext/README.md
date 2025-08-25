# cubinext README

This is a VSCode extension featuring the Cuda SASS decoder.

## Requirements

This extension requires Py_Cubin's server **py_cubin_smd_service** to run.

## How to package
* install vsce
  ```bash
  npm install -g vsce
  ```
* build Flutter app as web-release
  ```bash
  cd cubinext
  flutter build web --release
  ```
* navigate into the folder that contains *package.json* and run
  ```bash
  vsce package
  ```
* install the extension
  ```bash
  code --install-extension cubinext-0.0.1.vsix
  ```