
import 'dart:convert';
import 'dart:typed_data';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';
import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/main_view.dart';
import 'package:web/web.dart' as web;
import 'package:cubinext/comm.dart';
import 'package:cubinext/static_parts.dart';

@JS()
external void vscodePostMessage(JSAny param);

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cubinext @W',
      theme: StaticStyles.themeData,
      home: MyHomePage(title: 'Cubinext'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;
  static const double sideBarWidth = 50;
  static StringBuffer lastPath = StringBuffer(".");
  static bool onVsCode = true;
  static bool vsCodeLoaded = false;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  ByteBuffer buffer = Uint8List(0).buffer;
  final Comm comm = Comm(conIpPort: "127.0.0.1:8180");

  late final listener =
      ((JSObject event) {
        if (event.has("data") == false) {
          vscodePostMessage("[ERROR] Message has no data!".toJS);
        }

        final data = event["data"];

        if (data.isA<JSString>()) {
            var dataStr = (data as JSString).toDart;
            vscodePostMessage("[ERROR] Got string [$dataStr] for some reason...".toJS);
            return;
        }
        else if(data.isA<JSArrayBuffer>()){
          if(MyHomePage.vsCodeLoaded){
            return;
          }

          var dd = (data as JSArrayBuffer).toDart;
          int bb = dd.asByteData().getUint32(0, Endian.big);
          String addr = utf8.decode(dd.asUint8List(4, bb));
          if(!addr.contains(":")) {
            vscodePostMessage("[ERROR] Message should contain [IP:PORT] pattern but has [$addr]".toJS);
            return;
          }

          final sourceView = dd.asUint8List(bb+4);
          ByteBuffer rem = Uint8List(sourceView.length).buffer;
          final destView = rem.asUint8List(0);
          destView.setRange(0, rem.lengthInBytes, sourceView);

          int shouldBeLength = dd.lengthInBytes - 4 - bb;
          if(rem.lengthInBytes != shouldBeLength) {
            vscodePostMessage("[ERROR] Buffer has wrong length ${rem.lengthInBytes} $shouldBeLength".toJS);
            return;
          }

          MyHomePage.vsCodeLoaded = false;
          buffer = rem;
          comm.futureDB = null;
          comm.futureDB = Comm.fetchDB(comm, buffer);
          setState(() {
            MyHomePage.vsCodeLoaded = true;
          });

          vscodePostMessage("Requesting decoding from: $bb $addr".toJS);
        }
        else {
          vscodePostMessage("[ERROR] No idea what happened...".toJS);
        }
      }).toJS;

  @override
  void initState() {
    super.initState();

    web.window.addEventListener("message", listener);
    try{
      vscodePostMessage("__GetCubinFilePath__".toJS);
    // ignore: unused_catch_clause
    } on NoSuchMethodError catch (e){
      MyHomePage.onVsCode = false;
    }
    // comm.futureDB = Comm.fetchDB(comm, conIpPort, buffer);
  }

  @override
  void dispose() {
    web.window.removeEventListener("message", listener);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: MyHomePage.sideBarWidth,
          child: StaticParts.getLeftColumn(MyHomePage.sideBarWidth - 15, MyHomePage.lastPath, buffer, comm, setState)
        ),
        Expanded(
          child: MainView(buffer: buffer, comm: comm, setCommState: setState)
        ),
      ],
    );
  }
}
