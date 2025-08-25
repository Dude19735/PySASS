# cubinext

### Build for debug
```bash
flutter run -d chrome
flutter run -d edge
flutter run -d chrome --wasm
```

### Build for web
* NOTE: the `-d` on the bash is short for `-device` not debug
```bash
flutter build web --release
flutter build web --wasm
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0
```

### Build locally
```bash
flutter build linux --release
# maybe:
sudo apt-get install libgtk-3-0 libblkid1 liblzma5
```