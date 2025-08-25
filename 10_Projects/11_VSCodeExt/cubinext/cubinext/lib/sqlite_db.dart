import 'package:cubinext/sqlite_db_wrapper.dart';
import 'package:flutter/services.dart';

class DB {
  //ignore: undefined_class
  DBWrapper? _wrapper;
  DB();

  bool get loaded => _wrapper != null;

  Future<DB> init(Uint8List bytes) async {
    if(_wrapper != null) return this;
    //ignore: undefined_method
    _wrapper = await DBWrapper().init(bytes);
    return this;
  }

  Future<DB> initFromLocalBytes(Uint8List bytes) async {
    if(_wrapper != null) return this;
    //ignore: undefined_method
    _wrapper = await DBWrapper().initFromLocalBytes(bytes);
    return this;
  }

  Future<List<Object?>> testCase() async {
    if(_wrapper == null){
      throw StateError("DB is not initialized!");
    }
    var res = await _wrapper!.testCase();
    return res;
  }

  Future<List<List<dynamic>>> select(String stmt) async {
    if(_wrapper == null){
      throw StateError("DB is not initialized!");
    }
    var res = await _wrapper!.select(stmt);
    return res;
  }

  Uint8List toBytes(){
    if(_wrapper == null){
      throw StateError("DB is not initialized!");
    }
    return _wrapper!.toBytes();
  }

  void dispose(){
    if(_wrapper == null){
      return;
    }
    _wrapper!.dispose();
  }
}