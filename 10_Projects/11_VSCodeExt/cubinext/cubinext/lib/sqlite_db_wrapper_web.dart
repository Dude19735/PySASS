import 'dart:async';
import 'dart:typed_data';
import 'dart:js_interop' as jsi;
import 'package:archive/archive.dart';

@jsi.JS()
extension type SqliteDES._(jsi.JSObject _jsObject) {
  external SqliteDES();
  external void deserialize(jsi.JSUint8Array data);
  external jsi.JSUint8Array serialize();
  external jsi.JSArray select(String stmt);
  external void close();
  external String lastError();
}

@jsi.JS()
external jsi.JSPromise<jsi.JSObject> testRunJS(SqliteDES dbObj);
@jsi.JS()
external jsi.JSPromise<jsi.JSObject> initJS();

class DBWrapper {
  SqliteDES? _db;

  SqliteDES get db {
    if(_db != null) {
      return _db!;
    } else {
      throw StateError("DBWrapper (Web) is not initialized!");
    }
  }

  Future<DBWrapper> init(Uint8List bytes) async {
    if(_db != null) {
      _db!.close();
    }
    GZipDecoder decoder = GZipDecoder();
    var dBytes = decoder.decodeBytes(bytes);
    var dbObjJs = initJS();
    var dbObjD = await dbObjJs.toDart;
    _db = dbObjD.dartify() as SqliteDES;
    _db!.deserialize(dBytes.toJS);
    return this;
  }

  Future<DBWrapper> initFromLocalBytes(Uint8List bytes) async {
    if(_db != null) {
      _db!.close();
    }
    var dbObjJs = initJS();
    var dbObjD = await dbObjJs.toDart;
    _db = dbObjD.dartify() as SqliteDES;
    _db!.deserialize(bytes.toJS);
    return this;
  }

  Future<List<Object?>> testCase() async {
    if(_db == null) throw StateError("DBWrapper (Web) not initialized!");
    var res = testRunJS(_db!);
    var resVals = res.toDart;
    var futureRes = await resVals;
    var dartified = futureRes.dartify() as List<Object?>;
    return dartified;
  }

  Future<List<List<dynamic>>> select(String stmt) async {
    if(_db == null) throw StateError("DBWrapper (Web) not initialized!");
    var res = _db!.select(stmt.trim());
    String le = _db!.lastError();
    if(le != ""){
      throw StateError("DB call ended with error: [$le]");
    }

    var resVals = res.toDart as List<dynamic>;
    if(resVals.isEmpty) return [];
    List<List<dynamic>> retVal = [];
    for(var obj in resVals){
      retVal.add(obj as List<dynamic>);
    }
    return retVal;
  }

  Uint8List toBytes() {
    if(_db == null) throw StateError("DBWrapper (Web) is not initialized!");
    Uint8List bb = _db!.serialize().toDart;
    return bb;
  }

  void dispose(){
    if(_db == null) return;
    _db!.close();
  }
}
