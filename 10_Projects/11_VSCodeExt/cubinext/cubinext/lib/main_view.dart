import 'dart:typed_data';
import 'package:cubinext/sqlite_db.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/kernel_view.dart';
import 'package:cubinext/helper_view.dart';

class MainView extends StatefulWidget {
  final ByteBuffer buffer;
  final Comm comm;
  final void Function(void Function()) setCommState;

  const MainView({super.key, required this.buffer, required this.comm, required this.setCommState});

  @override
  State<MainView> createState() => _MainView();
}

class _MainView extends State<MainView> with TickerProviderStateMixin {
  late Future<DB?> futureDataRunner;
  late final DropdownComm _dropdownComm;
  late final HelperComm _helperComm;

  @override
  void initState() {
    super.initState();
    _dropdownComm = DropdownComm();
    _helperComm = HelperComm();
    // futureDataRunner = fetchDataRunner(widget.initMsg, widget.buffer);
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      child: FutureBuilder<DB?>(
      future: widget.comm.futureDB,
      builder: (BuildContext context, AsyncSnapshot<void> snapshot){
        if(snapshot.connectionState == ConnectionState.waiting){
          return const Center(child: CircularProgressIndicator());
        }
        else if(snapshot.hasError){
          return Center(child: Text("DB Request Error: ${snapshot.error}"));
        }
        else {
          DB? db = snapshot.data as DB?;
          // if(db == null){
          //   return Center(child: const Text("Load Cubin"));
          // }
          if(db == null){
            return Center(child: const Text("Load Cubin"));
          }
          if(widget.comm.mode == DisplayMode.decoder) {
            _dropdownComm.setDb(db);
            return KernelView(comm:widget.comm, dropdownComm:_dropdownComm, setCommState: widget.setCommState);
          }
          else if(widget.comm.mode == DisplayMode.helper) {
            _helperComm.setDb(db);
            return HelperView(comm:widget.comm, helperComm:_helperComm, setCommState: widget.setCommState);
          }
          else {
            throw UnimplementedError("A view with DisplayMode ${widget.comm.mode} is not implemented!");
          }
        }
      }
    ));
  }
}
