import 'dart:io';
import 'dart:typed_data';
import 'package:sqlite3/sqlite3.dart';

class DBWrapper {
  Database? _db;

  Database get db {
    if(_db != null){
      return _db!;
    } else {
      throw StateError("DBWrapper (Nat) is not initialized!");
    }
  }

  Future<List<Object?>> testCase() async {
    if(_db == null) throw StateError("DBWrapper (Nat) not initialized!");
    throw UnimplementedError("This method is only implemented for the Web version of this one!");
  }

  Future<DBWrapper> init(Uint8List bytes) async {
    if(_db != null){
      _db!.dispose();
    }
    var dBytes = gzip.decode(bytes);
    File ff = File("./temp.db");
    ff.writeAsBytesSync(dBytes);
    _db = sqlite3.open("./temp.db");
    return this;
  }

  Future<DBWrapper> initFromLocalBytes(Uint8List bytes) async {
    if(_db != null){
      _db!.dispose();
    }
    File ff = File("./temp.db");
    ff.writeAsBytesSync(bytes);
    _db = sqlite3.open("./temp.db");
    return this;
  }

  Future<List<List<dynamic>>> select(String stmt) async {
    if(_db == null) throw StateError("DBWrapper (Nat) not initialized!");
    var result =_db!.select(stmt.trim());
    if(result.isEmpty) return [];
    List<List<dynamic>> retVal = result.rows as List<List<dynamic>>;
    return retVal;
  }

  Uint8List toBytes(){
    File ff = File('./temp.db');
    Uint8List bytes = ff.readAsBytesSync();
    ff.delete();
    return bytes;
  }

  void dispose(){
    if(_db == null) return;
    _db!.dispose();
  }
}