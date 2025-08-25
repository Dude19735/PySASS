import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:cubinext/sqlite_db.dart';
import 'package:cubinext/sqlite_proxy.dart';
import 'package:file_picker/file_picker.dart';

typedef VoidCallback = void Function();

enum LoadMode {
  single, all
}

enum DisplayMode {
  decoder, helper
}

class Comm {
  Future<DB?>? futureDB;
  LoadMode singleOrAll = LoadMode.single;
  String selectedBinary = "";
  String selectedKernel = "";
  String conIpPort;
  DisplayMode mode = DisplayMode.decoder;

  Comm({required this.conIpPort});

  static Future<DB?> fetchDB(Comm comm, ByteBuffer buffer) async {
    String addr = comm.conIpPort;
    
    if(comm.futureDB != null){
      return comm.futureDB; 
    }
    if(buffer.lengthInBytes == 0) {
      return null;
    }

    final response = await http.post(
      Uri.parse('http://$addr'),
      headers: {'content-length': "${buffer.asUint8List().lengthInBytes}"}, //{'Content-Type': 'text/html', 'Access-Control-Allow-Origin': '*'},
      body: buffer.asUint8List(),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to send data');
    }

    var db = DB();
    var bytes = response.bodyBytes;
    await db.init(bytes);
    return db;
  }

  static Future<DB?> fromBytes(Comm comm, Uint8List bytes) async {
    if(comm.futureDB != null){
      return comm.futureDB;
    }
    var db = DB();
    await db.initFromLocalBytes(bytes);
    return db;
  }
}

class HelperComm {
  late DB db;

  late Future<TDistinctSmIdProxy> futureSmIds;
  late Future<TEnum> futureEnum;

  setDb(DB newDb) {
    db = newDb;
    futureSmIds = DistinctSmIdProxy.getDistinctSmIds(db);
    futureEnum = EnumProxy.getDistinctEnums(db);
  }
}

class DropdownComm {
  late DB db;

  TDropdown dropdownContent = {};
  String selectedBinary = "";
  String selectedKernel = "";
  List<String> binaryEntries = [];
  List<String> kernelEntries = [];

  late Future<TDropdown> futureDropdownContent;
  late Future<TInstructions> futureInstructions;

  VoidCallback? refreshInstrViewCallback;

  setDb(DB newDb){
    db = newDb;
    futureDropdownContent = BinaryKernelProxy.get(db);
    futureInstructions = InstructionProxy.getInstructions(db, 0);
  }

  static void saveToFile(DropdownComm comm){
    DateTime now = DateTime.now();
    String dd = "${now.year}-${now.month.toString().padLeft(2,"0")}-${now.day.toString().padLeft(2,"0")}";
    String tt = "${now.hour.toString().padLeft(2,"0")}-${now.minute.toString().padLeft(2,"0")}-${now.second.toString().padLeft(2,"0")}";
    Uint8List bytes = comm.db.toBytes();
    FilePicker.platform.saveFile(
      dialogTitle: "Save decoded Cubin to disk",
      fileName: "cubin.$dd.$tt.sqlite3", 
      bytes: bytes);
  }

  static void init(DropdownComm comm){
    if(comm.selectedBinary == ""){
      comm.selectedBinary = comm.dropdownContent.keys.first;
    }
    else{
      if(!comm.dropdownContent.containsKey(comm.selectedBinary)){
        comm.selectedBinary = comm.dropdownContent.keys.first;
      }
    }
    if(comm.selectedKernel == ""){
      comm.selectedKernel = comm.dropdownContent[comm.selectedBinary]!.value.keys.first;
    }
    else{
      if(!comm.dropdownContent[comm.selectedBinary]!.value.containsKey(comm.selectedKernel)){
        comm.selectedKernel = comm.dropdownContent[comm.selectedBinary]!.value.keys.first;
      }
    }
    comm.binaryEntries = comm.dropdownContent.keys.toList();
    comm.kernelEntries = comm.dropdownContent[comm.selectedBinary]!.value.keys.toList();
    comm.futureInstructions = InstructionProxy.getInstructions(comm.db, DropdownComm.selectedKernekId(comm));
  }

  static void updateBinary(DropdownComm comm, String selectedBinary){
    comm.selectedBinary = selectedBinary;
    comm.selectedKernel = comm.dropdownContent[comm.selectedBinary]!.value.keys.first;
    comm.kernelEntries = comm.dropdownContent[comm.selectedBinary]!.value.keys.toList();
    comm.futureInstructions = InstructionProxy.getInstructions(comm.db, DropdownComm.selectedKernekId(comm));
  }

  static void updateInstructions(DropdownComm comm){
    if(comm.refreshInstrViewCallback == null) {
      throw StateError("InstrView is not initialized yet. Don't call updateInstructions before you initialize InstrView!");
    }
    comm.futureInstructions = InstructionProxy.getInstructions(comm.db, DropdownComm.selectedKernekId(comm));
    comm.refreshInstrViewCallback!();
  }

  static int selectedKernekId(DropdownComm comm){
    var kk = comm.dropdownContent[comm.selectedBinary]!.value[comm.selectedKernel]!;
    return kk.kernelId;
  }
}