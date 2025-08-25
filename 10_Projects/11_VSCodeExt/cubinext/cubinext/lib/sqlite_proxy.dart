import 'package:collection/collection.dart';
import 'package:cubinext/sqlite_db.dart';
import 'package:pair/pair.dart';
import 'package:cubinext/instr_parts.dart';
import 'package:object_reference/object_reference.dart';

typedef TParentId = int;
typedef TTypeName = String;
typedef TMisc = Map<TParentId, Map<TTypeName, Misc>>;
class Misc {
  final int miscId;
  final int parentId;
  final String typeName;
  final String miscValue;
  final String additionalInfo;

  static const String _miscId = "MiscId";
  static const String _parentId = "ParentId";
  static const String _typeName = "TypeName";
  static const String _miscValue = "MiscValue";
  static const String _additionalInfo = "AdditionalInfo";

  Misc({required this.parentId, required this.typeName, required this.miscId, required this.miscValue, required this.additionalInfo});

  @override
  @override
  String toString() => 
    ["[ ${Misc._miscId}: $miscId",
    "${Misc._parentId}: $parentId",
    "${Misc._typeName}: $typeName",
    "${Misc._miscValue}: $miscValue",
    "${Misc._additionalInfo}: $additionalInfo ]"].join(", ");

  static Future<TMisc> get(DB db, String miscTableName, String parentTableName, int kernelId) async {
    String idName = "${miscTableName}Id";
    String parentIdName = "${parentTableName}Id";

    List<List<dynamic>> res = await db.select(
      """
        select 
          M.$parentIdName as ${Misc._parentId}, 
          T.Name as ${Misc._typeName},
          M.$idName as ${Misc._miscId},
          M.MiscValue as ${Misc._miscValue},
          M.AdditionalInfo as ${Misc._additionalInfo}
        from $miscTableName M
          inner join Type T on T.TypeId = M.TypeId
          inner join Instr I on I.InstrId = M.InstrId
        where I.KernelId = $kernelId      
        order by I.InstrId asc, M.InstrId, M.$idName asc
      """
    );
    return Misc.map(res);
  }

  static Map<int, Map<String, Misc>> map(List<List<dynamic>> vals){
    Map<int, Map<String, Misc>> res = {};
    for(final v in vals) {
      int parentId = v[0] as TParentId;
      String typeName = v[1] as TTypeName;
      if(!res.containsKey(parentId)){
        res[parentId] = {};
      }
      if(res[parentId]!.containsKey(typeName)){
        throw StateError("Misc table contains a TypeName twice! This is not allowed!");
      }
      res[parentId]![typeName] = Misc(
        parentId: parentId, 
        typeName: typeName, 
        miscId: v[2] as int, 
        miscValue: v[3] as String,
        additionalInfo: v[4] as String);
    } 
    return res;
  }
}

class BinaryProxy {
  final int binaryId;
  final int arch;
  final String name;
  // final int binaryDecoded;

  static const String _binaryId = "BinaryId";
  static const String _arch = "Arch";
  static const String _name = "Name";
  // static const String _binaryDecoded = "BinaryDecoded";

  BinaryProxy({required this.binaryId, required this.arch, required this.name}); //, required this.binaryDecoded});

  @override
  String toString() => "[ ${BinaryProxy._binaryId}: $binaryId, ${BinaryProxy._arch}: $arch, ${BinaryProxy._name}: $name ]";

  static Future<List<BinaryProxy>> getBinaries(DB db) async {
    List<List<dynamic>> res = await db.select(
      // """
      //   select 
      //     B.BinaryId as ${BinaryProxy._binaryId}, 
      //     B.Arch as ${BinaryProxy._arch}, 
      //     B.Name as ${BinaryProxy._name},
      //     M.MiscValue as ${BinaryProxy._binaryDecoded}
      //   from Binary B
      //     inner join BinaryMisc M on B.BinaryId = M.BinaryId and M.TypeId = (
      //       select TypeId from Type T where T.Category = 'BinaryMisc' and T.Name = 'BinaryDecoded'
      //     )
      //   order by M.MiscValue desc, B.BinaryId asc
      // """
      """
        select 
          B.BinaryId as ${BinaryProxy._binaryId}, 
          B.Arch as ${BinaryProxy._arch}, 
          B.Name as ${BinaryProxy._name}
        from Binary B
        order by B.BinaryId asc
      """
    );
    return BinaryProxy.map(res);
  }

  static List<BinaryProxy> map(List<List<dynamic>> vals){
    return [
      for(final v in vals) BinaryProxy(binaryId: v[0] as int, arch: v[1] as int, name: v[2] as String)
    ];
  }
}

class KernelProxy {
  final int kernelId;
  final int binaryId;
  final String name;
  // final int kernelDecoded;

  static const String _kernelId = "KernelId";
  static const String _binaryId = "BinaryId";
  static const String _name = "Name";
  // static const String _kernelDecoded = "KernelDecoded";

  KernelProxy({required this.kernelId, required this.binaryId, required this.name}); //, required this.kernelDecoded});

  @override
  String toString() => "[ ${KernelProxy._kernelId}: $kernelId, ${KernelProxy._binaryId}: $binaryId, ${KernelProxy._name}: $name ]";

  static Future<List<KernelProxy>> getKernels(DB db, int binaryId) async {
    List<List<dynamic>> res = await db.select(
      // """
      //   select 
      //     K.KernelId as ${KernelProxy._kernelId}, 
      //     K.BinaryId as ${KernelProxy._binaryId}, 
      //     K.Name as ${KernelProxy._name},
      //     M.MiscValue as ${KernelProxy._kernelDecoded}
      //   from Kernel K
      //   inner join KernelMisc M on K.KernelId = M.KernelId and M.TypeId = (
      //     select TypeId from Type T where T.Category = 'KernelMisc' and T.Name = 'KernelDecoded'
      //   )
      //   where K.BinaryId = $binaryId
      //   order by M.MiscValue desc, K.KernelId asc
      // """
      """
        select 
          K.KernelId as ${KernelProxy._kernelId}, 
          K.BinaryId as ${KernelProxy._binaryId}, 
          K.Name as ${KernelProxy._name}
        from Kernel K
        where K.BinaryId = $binaryId
        order by K.KernelId asc
      """
    );
    return KernelProxy.map(res);
  }

  static List<KernelProxy> map(List<List<dynamic>> vals){
    return [
      for(final v in vals) KernelProxy(kernelId: v[0] as int, binaryId: v[1] as int, name: v[2] as String)
    ];
  }
}

typedef TDropdown = Map<String, Pair<BinaryProxy, Map<String, KernelProxy>>>;
class BinaryKernelProxy {
  
  final TDropdown data;

  BinaryKernelProxy({required this.data});

  static Future<TDropdown> get(DB db) async {
    var binaries = await BinaryProxy.getBinaries(db);

    TDropdown res = {};
    for(final b in binaries){
      var x = await KernelProxy.getKernels(db, b.binaryId);
      Map<String, KernelProxy> xx = { for (var x in x) x.name : x };
      
      res[b.name] = Pair<BinaryProxy, Map<String, KernelProxy>>(b, xx);
    }

    return res;
  }
}

typedef TInstrClass = Map<String, InstrClassDefProxy>;
class InstrClassDefProxy {
  final String typeName;
  final int seqNr;
  final String content;
  final String additionalInfo;

  static const String _typeName = "TypeName";
  static const String _seqNr = "SeqNr";
  static const String _content = "Content";
  static const String _additionalInfo = "AdditionalInfo";

  // These must be the same names as the Types the data base in InstrClassDef
  static const String kTypeFormat = "format";
  static const String kTypeConditions = "conditions";
  static const String kTypeProperties = "properties";
  static const String kTypePredicates = "predicates";
  static const String kTypeOpcodes = "opcodes";
  static const String kTypeEncoding = "encoding";

  InstrClassDefProxy({
    required this.typeName,
    required this.seqNr,
    required this.content,
    required this.additionalInfo
  });

  @override
  String toString() => 
    ["[ ${InstrClassDefProxy._typeName}: $typeName",
    "${InstrClassDefProxy._seqNr}: $seqNr",
    "${InstrClassDefProxy._content}: $content",
    "${InstrClassDefProxy._additionalInfo}: $additionalInfo ]"].join(", ");

  static Future<TInstrClass> get(DB db, int instrId) async {
    List<List<dynamic>> res = await db.select(
      """
        select 
          T.Name as ${InstrClassDefProxy._typeName},
          I.SeqNr as ${InstrClassDefProxy._seqNr},
          I.Content as ${InstrClassDefProxy._content},
          I.AdditionalInfo as ${InstrClassDefProxy._additionalInfo}
        from InstrClassDef I
        inner join Type T on T.TypeId = I.TypeId
        where I.InstrId = $instrId
      """
    );

    return InstrClassDefProxy.map(res);
  }

  static TInstrClass map(List<List<dynamic>> vals){
    TInstrClass res = {};
    for(final v in vals) {
      String typeName = v[0];
      int seqNr = v[1];
      String content = v[2];
      String additionalInfo = v[3];
      res[typeName] = InstrClassDefProxy(typeName: typeName, seqNr: seqNr, content: content, additionalInfo: additionalInfo);
    }
    return res;
  }
}

typedef TInstructions = List<InstructionProxy>;
class InstructionProxy {
  final int instrId;
  final int kernelId;
  final int binaryId;
  final String code;
  final String instrClass;
  final String desc;
  final String typeDesc;
  final int universeCount;
  final Map<TTypeName, Misc> misc;

  static const String _instrId = "InstrId";
  static const String _kernelId = "KernelId";
  static const String _binaryId = "BinaryId";
  static const String _code = "Code";
  static const String _instrClass = "InstrClass";
  static const String _desc = "Desc";
  static const String _typeDesc = "TypeDesc";
  static const String _universeCount = "UniverseCount";

  // These must be the same names as the Types the data base in InstrMisc
  static const String kTypeBinOffset = "BinOffset";
  static const String kTypeCubinOffset = "CubinOffset";
  static const String kTypeInstrOffset = "InstrOffset";
  static const String kTypeClassName = "ClassName";
  static const String kTypeInstrBits = "InstrBits";

  InstructionProxy({
    required this.instrId,
    required this.kernelId, 
    required this.binaryId, 
    required this.code,
    required this.instrClass,
    required this.desc,
    required this.typeDesc,
    required this.universeCount,
    required this.misc
  });

  static String getUniqueId(int index, List<InstructionProxy> instructions){
    var i = instructions[index];
    return 'instr-$index-${i.binaryId}-${i.kernelId}-${i.instrId}-${i.hashCode}';
  }

  @override
  String toString() => 
    ["[ ${InstructionProxy._instrId}: $instrId",
    "${InstructionProxy._kernelId}: $kernelId",
    "${InstructionProxy._binaryId}: $binaryId",
    "${InstructionProxy._code}: $code",
    "${InstructionProxy._instrClass}: $instrClass",
    "${InstructionProxy._desc}: $desc",
    "${InstructionProxy._typeDesc}: $typeDesc ]"].join(", ");

  static Future<TInstructions> getInstructions(DB db, int kernelId) async {
    List<List<dynamic>> res = await db.select(
      """
        select 
          I.InstrId as ${InstructionProxy._instrId},
          I.KernelId as ${InstructionProxy._kernelId},
          K.BinaryId as ${InstructionProxy._binaryId},
          I.Code as ${InstructionProxy._code},
          I.Class as ${InstructionProxy._instrClass},
          I.Desc as ${InstructionProxy._desc},
          I.TypeDesc as ${InstructionProxy._typeDesc},
          count(U.UniverseId) as ${InstructionProxy._universeCount}
        from Kernel K
          inner join Instr I on I.KernelId = K.KernelId
          inner join Universe U on U.InstrId = I.InstrId
        where K.KernelId = $kernelId
        group by I.InstrId
        order by K.KernelId asc, I.InstrId asc
      """
    );

    TMisc misc = await Misc.get(db, 'InstrMisc', 'Instr', kernelId);
    return InstructionProxy.map(res, misc);
  }

  static List<InstructionProxy> map(List<List<dynamic>> vals, TMisc misc){
    return [
      for(final v in vals) InstructionProxy(
        instrId: v[0] as int,
        kernelId: v[1] as int, 
        binaryId: v[2] as int, 
        code: v[3] as String,
        instrClass: v[4] as String,
        desc: v[5] as String,
        typeDesc: v[6] as String,
        universeCount: v[7] as int,
        misc: misc[v[0] as TParentId]!
      )
    ];
  }
}

typedef TUniverseId = int;
typedef TInstrPart = String;
typedef TInstrId = int;
typedef TInstrUniverse = Map<TInstrId, List<Universe>>;
class UniverseProxy {
  static const String _instrId = "InstrId"; static const int _instrIdIndex = 0;
  static const String _universeId = "UniverseId";   static const int _universeIdIndex = 1;
  static const String _universeComponentId = "UniverseComponentId";   static const int _universeComponentIdIndex = 2;
  static const String _level = "Level";   static const int _levelIndex = 3;
  static const String _selfParentId = "SelfParentId";   static const int _selfParentIdIndex = 4;
  static const String _seqNr = "SeqNr";   static const int _seqNrIndex = 5;
  static const String _typeName = "TypeName";   static const int _typeNameIndex = 6;
  static const String _alias = "Alias";   static const int _aliasIndex = 7;
  static const String _bitFrom = "BitFrom";   static const int _bitFromIndex = 8;
  static const String _bitTo = "BitTo";   static const int _bitToIndex = 9;
  static const String _sassBits = "SassBits";   static const int _sassBitsIndex = 10;
  static const String _valueName = "ValueName";   static const int _valueNameIndex = 11;
  static const String _valueType = "ValueType";   static const int _valueTypeIndex = 12;
  static const String _classDef = "ClassDef";   static const int _classDefIndex = 13;

  static Future<TInstrUniverse> get(DB db, List<int> instrIds, Map<int, int> universeCount) async {
    List<List<dynamic>> res = await db.select(
      """
        with RECURSIVE hierarchy as (
          select
            I.InstrId as ${UniverseProxy._instrId},
            C.UniverseId as ${UniverseProxy._universeId},
            C.UniverseComponentId as ${UniverseProxy._universeComponentId}, 
            1 as ${UniverseProxy._level},
            0 as ${UniverseProxy._selfParentId},
            C.SeqNr as ${UniverseProxy._seqNr},
            T.Name as ${UniverseProxy._typeName},
            C.InstrFieldAlias as ${UniverseProxy._alias},
            C.BitFrom as ${UniverseProxy._bitFrom},
            C.BitTo as ${UniverseProxy._bitTo},
            C.SassBits as ${UniverseProxy._sassBits},
            C.ValueName as ${UniverseProxy._valueName},
            C.ValueType as ${UniverseProxy._valueType},
            C.ClassDef as ${UniverseProxy._classDef}
          from UniverseComponent C
            inner join Universe U on U.UniverseId = C.UniverseId
            inner join Instr I on I.InstrId = U.InstrId
            inner join Type T on T.TypeId = C.TypeId
          where I.InstrId in (${instrIds.join(",")}) and C.SelfParentId is NULL
          union all
          select 
            P.InstrId as ${UniverseProxy._instrId},
            P.UniverseId as ${UniverseProxy._universeId},
            C.UniverseComponentId as ${UniverseProxy._universeComponentId}, 
            P.Level+1 as ${UniverseProxy._level},
            C.SelfParentId as ${UniverseProxy._selfParentId},
            C.SeqNr as ${UniverseProxy._seqNr},
            T.Name as ${UniverseProxy._typeName},
            C.InstrFieldAlias as ${UniverseProxy._alias},
            C.BitFrom as ${UniverseProxy._bitFrom},
            C.BitTo as ${UniverseProxy._bitTo},
            C.SassBits as ${UniverseProxy._sassBits},
            C.ValueName as ${UniverseProxy._valueName},
            C.ValueType as ${UniverseProxy._valueType},
            C.ClassDef as ${UniverseProxy._classDef}
          from UniverseComponent C
            inner join Type T on T.TypeId = C.TypeId
            inner join hierarchy P on P.UniverseComponentId = C.SelfParentId
        )
        select * from hierarchy
        order by ${UniverseProxy._instrId} asc, ${UniverseProxy._universeId} asc, ${UniverseProxy._universeComponentId} asc, ${UniverseProxy._level} asc, ${UniverseProxy._seqNr} asc
      """
    );

    var gp = groupBy(res, (List<dynamic> item) => item[UniverseProxy._instrIdIndex]);

    TInstrUniverse result = {};
    for(final instr in gp.entries){
      var universes = UniverseProxy.map(res, instr.key);
      if(universes.length != universeCount[instr.key]){
        throw StateError("The algo didn't get enough universes! There should be [$universeCount] but there are only [${universes.length}]!");
      }
      result[instr.key] = universes;
    }
    return result;
  }

  static List<Universe> map(List<List<dynamic>> vals, int instrId){
    List<Universe> res = [];

    // Some useful vars...
    int universeId = -1; // vals[0][0];

    // In here, we have the same instruction but multiple universes
    //  => if the universe id changes => new universe
    Universe? cur;
    final vIndex = 0.ref<int>();

    // get the first one as initial value
    universeId = vals[0][UniverseProxy._universeIdIndex];
    cur = Universe(universeIndex: universeId, instrIndex: instrId);

    while(vIndex.value < vals.length){
      var v = vals[vIndex.value];
      if(v[UniverseProxy._universeIdIndex] != universeId){
        // New universe
        universeId = v[UniverseProxy._universeIdIndex];
        if(cur != null) res.add(cur);
        cur = Universe(universeIndex: universeId, instrIndex: instrId);
      }
      if(cur == null) {
        throw StateError("Current Universe is null => this is a bug!");
      }
      var parts = mapRec(vals, universeId, 1, vIndex);
      cur.add(parts);
    }
    if(cur == null) {
      throw StateError("There is no universe here. This is a bug!");
    }
    res.add(cur);
    return res;
  }

  static List<UniverseComponent> mapRec(List<List<dynamic>> vals, int universeId, int cLevel, MutableRef<int> vIndex){
    List<UniverseComponent> parts = [];
    while(vIndex.value < vals.length){
      var v = vals[vIndex.value];
      int newUniverseId = v[UniverseProxy._universeIdIndex];
      if(newUniverseId != universeId){
        return parts;
      }
      int level = v[UniverseProxy._levelIndex];
      if(level > cLevel){
        parts.last.children = mapRec(vals, newUniverseId, level, vIndex);
        continue;
      }
      else if(level == cLevel) {
        // Advance the index by 1
        vIndex.value++;
      }
      else {
        return parts;
      }

      // Cast dynamic entries
      int instrId = v[UniverseProxy._instrIdIndex];
      int universeComponentId = v[UniverseProxy._universeComponentIdIndex];
      int selfParentId = v[UniverseProxy._selfParentIdIndex];
      int seqId = v[UniverseProxy._seqNrIndex];
      String typeName = v[UniverseProxy._typeNameIndex];
      String alias = v[UniverseProxy._aliasIndex];
      int bitFrom = v[UniverseProxy._bitFromIndex];
      int bitTo = v[UniverseProxy._bitToIndex];
      String sassBits = v[UniverseProxy._sassBitsIndex];
      String valueName = v[UniverseProxy._valueNameIndex];
      String valueType = v[UniverseProxy._valueTypeIndex];
      String classDef = v[UniverseProxy._classDefIndex];
      parts.add(Universe.getInstrPart(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, typeName: typeName, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef));

    }
    return parts;
  }
}

typedef TUniverseEvalList = List<UniverseEvalEncoding>;
typedef TUniverseEvalMap = Map<TUniverseId, TUniverseEvalList>;
class UniverseEvalEncodingProxy {
  static const String _universeId = "UniverseId";
  static const String _universeEvalEncodingId = "UniverseEvalEncodingId";
  static const String _selfParentId = "SelfParentId";
  static const String _seqNr = "SeqNr";
  static const String _level = "Level";
  static const String _typeName = "TypeName";
  static const String _expr = "Expr";
  static const String _sassBitsStr = "SassBitsStr";
  static const String _bitFrom = "BitFrom";
  static const String _bitTo = "BitTo";
  static const String _universeComponentId = "UniverseComponentId";

  // These must be the same names as the Types the data base in UniverseEvalEncoding
  static const String kTypeDynamic = "dynamic";
  static const String kTypeFixed = "fixed";
  static const String kTypeFunc = "func";
  static const String kTypeTable = "table";

  static Future<TUniverseEvalMap> get(DB db, int instrId, int universeCount) async {
    List<List<dynamic>> res = await db.select(
      """
        with RECURSIVE hierarchy as (
        select
          U.UniverseId as ${UniverseEvalEncodingProxy._universeId},
          E.UniverseEvalEncodingId as ${UniverseEvalEncodingProxy._universeEvalEncodingId},
          0 as ${UniverseEvalEncodingProxy._selfParentId},
          E.SeqNr as ${UniverseEvalEncodingProxy._seqNr},
          1 as ${UniverseEvalEncodingProxy._level},
          T.Name as ${UniverseEvalEncodingProxy._typeName},
          E.Expr as ${UniverseEvalEncodingProxy._expr},
          E.SassBitsStr as ${UniverseEvalEncodingProxy._sassBitsStr},
          E.BitFrom as ${UniverseEvalEncodingProxy._bitFrom},
          E.BitTo as ${UniverseEvalEncodingProxy._bitTo},
          E.Ref0_UniverseComponentId as ${UniverseEvalEncodingProxy._universeComponentId}
        from UniverseEvalEncoding E 
          inner join Type T on T.TypeId = E.TypeId
          inner join UniverseEval U on U.UniverseEvalId = E.UniverseEvalId
          inner join Universe UV on UV.UniverseId = U.UniverseId
          inner join Instr I on I.InstrId = UV.InstrId
        where UV.InstrId = $instrId
        union all
        select
          P.UniverseId as ${UniverseEvalEncodingProxy._universeId},
          E.UniverseEvalEncodingId as ${UniverseEvalEncodingProxy._universeEvalEncodingId},
          E.SelfParentId as ${UniverseEvalEncodingProxy._selfParentId},
          E.SeqNr as ${UniverseEvalEncodingProxy._seqNr},
          P.Level + 1 as ${UniverseEvalEncodingProxy._level},
          T.Name as ${UniverseEvalEncodingProxy._typeName},
          E.Expr as ${UniverseEvalEncodingProxy._expr},
          E.SassBitsStr as ${UniverseEvalEncodingProxy._sassBitsStr},
          E.BitFrom as ${UniverseEvalEncodingProxy._bitFrom},
          E.BitTo as ${UniverseEvalEncodingProxy._bitTo},
          E.Ref0_UniverseComponentId as ${UniverseEvalEncodingProxy._universeComponentId}
        from UniverseEvalEncoding E 
          inner join Type T on T.TypeId = E.TypeId
          inner join hierarchy P on P.${UniverseEvalEncodingProxy._universeEvalEncodingId} = E.SelfParentId
        )
        select * from hierarchy
        order by ${UniverseEvalEncodingProxy._universeId}, ${UniverseEvalEncodingProxy._universeEvalEncodingId}, ${UniverseEvalEncodingProxy._level}
      """
    );

    var universeEvals = UniverseEvalEncodingProxy.map(res);
    if(universeEvals.length != universeCount){
      throw StateError("The algo didn't get enough universes! There should be [$universeCount] but there are only [${universeEvals.length}]!");
    }
    return universeEvals;
  }

  static TUniverseEvalMap map(List<List<dynamic>> vals){
    TUniverseEvalMap res = {};

    // Some useful vars...
    int universeId = -1; // vals[0][0];

    // In here, we have the same instruction but multiple universes
    //  => if the universe id changes => new universe
    TUniverseEvalList cur = [];
    final vIndex = 0.ref<int>();

    // get the first one as initial value
    universeId = vals[0][0];

    while(vIndex.value < vals.length){
      var v = vals[vIndex.value];
      if(v[0] != universeId){
        // New universe
        if(cur.isNotEmpty) res[universeId] = cur;
        universeId = v[0];
        cur = [];
      }
      var parts = mapRec(vals, universeId, 1, vIndex);
      cur.addAll(parts);
    }
    if(cur.isEmpty) {
      throw StateError("There is no universe encoding eval here. This is a bug!");
    }
    res[universeId] = cur;
    return res;
  }

  static List<UniverseEvalEncoding> mapRec(List<List<dynamic>> vals, int universeId, int cLevel, MutableRef<int> vIndex){
    List<UniverseEvalEncoding> parts = [];
    while(vIndex.value < vals.length){
      var v = vals[vIndex.value];
      int newUniverseId = v[0];
      if(newUniverseId != universeId){
        return parts;
      }
      int level = v[4];
      if(level > cLevel){
        parts.last.children = mapRec(vals, newUniverseId, level, vIndex);
        continue;
      }
      else if(level == cLevel) {
        // Advance the index by 1
        vIndex.value++;
      }
      else {
        return parts;
      }

      int universeEvalEncodingId = v[1];
      int selfParentId = v[2];
      int seqNr = v[3];
      String typeName = v[5];
      String expr = v[6];
      String sassBitsStr = v[7];
      int bitFrom = v[8];
      int bitTo = v[9];
      int? universeComponentId = v[10];

      parts.add(Universe.getEvalEncoding(universeEvalEncodingId: universeEvalEncodingId, selfParentId: selfParentId, seqNr: seqNr, level: level, typeName: typeName, expr: expr, sassBitsStr: sassBitsStr, bitFrom: bitFrom, bitTo: bitTo, universeComponentId: universeComponentId));

    }
    return parts;
  }
}

typedef TInstrLatency = Map<String, List<List<Object>>>;
class InstrLatencyProxy {
  final int instrLatencyId;
  final int seqNr;
  final String typeName;
  final String input;
  final String tableName;
  final String row;
  final String col;
  final String cross;
  final int val;

  static const String _instrLatencyId = "InstrLatencyId";
  static const String _seqNr = "SeqNr";
  static const String _typeName = "TypeName";
  static const String _input = "Input";
  static const String _tableName = "TableName";
  static const String _row = "Row";
  static const String _col = "Col";
  static const String _cross = "Cross";
  static const String _val = "Val";

  static const String kRows = 'rows';
  static const String kValues = 'vals';

  InstrLatencyProxy({
    required this.instrLatencyId,
    required this.seqNr,
    required this.typeName,
    required this.input,
    required this.tableName,
    required this.row,
    required this.col,
    required this.cross,
    required this.val
  });

  @override
  String toString() => 
  ["[ ", 
  "$_instrLatencyId: ",
  instrLatencyId,
  "$_seqNr: ",
  seqNr,
  "$_typeName: ",
  typeName,
  "$_input: ",
  input,
  "$_tableName: ",
  tableName,
  "$_row: ",
  row,
  "$_col: ",
  col,
  "$_cross: ",
  cross,
  "$_val: ",
  val,
  " ]"].join(', ');

  static Future<TInstrLatency> get(DB db, int instrId) async {
    List<List<dynamic>> res = await db.select(
      """
        select 
          L.InstrLatencyId as ${InstrLatencyProxy._instrLatencyId},
          L.SeqNr as ${InstrLatencyProxy._seqNr},
          L.TypeName as ${InstrLatencyProxy._typeName},
          L.Input as ${InstrLatencyProxy._input},
          L.TableName as ${InstrLatencyProxy._tableName},
          L.Row as ${InstrLatencyProxy._row},
          L.Col as ${InstrLatencyProxy._col},
          L.Cross as ${InstrLatencyProxy._cross},
          L.Val as ${InstrLatencyProxy._val}
        from InstrLatency L
        where L.InstrId = $instrId
        order by L.SeqNr asc
      """
    );

    return InstrLatencyProxy.map(res);
  }

  static TInstrLatency map(List<List<dynamic>> vals){
    TInstrLatency res = {};
    res[InstrLatencyProxy.kRows] = [];
    res[InstrLatencyProxy.kRows]!.add([
      InstrLatencyProxy._typeName,
      InstrLatencyProxy._input,
      InstrLatencyProxy._tableName,
      InstrLatencyProxy._row,
      InstrLatencyProxy._col,
      InstrLatencyProxy._cross,
      InstrLatencyProxy._val,

      ]);

    List<InstrLatencyProxy> values = [];
    for(final v in vals) {
      int instrLatencyId = v[0];
      int seqNr = v[1];
      String typeName = v[2];
      String input = v[3];
      String tableName = v[4];
      String row = v[5];
      String col = v[6];
      String cross = v[7];
      int val = v[8];
      values.add(InstrLatencyProxy(instrLatencyId: instrLatencyId, seqNr: seqNr, typeName: typeName, input: input, tableName: tableName, row: row, col: col, cross: cross, val: val));
      res[InstrLatencyProxy.kRows]!.add([typeName, input, tableName, row, col, cross, val]);
    }
    res[InstrLatencyProxy.kValues] = [values];
    return res;
  }
}

typedef TDistinctSmIdProxy = List<DistinctSmIdProxy>;
class DistinctSmIdProxy {
  final int smId;

  static const String _smId = "SmId";

  DistinctSmIdProxy({required this.smId});

  @override
  String toString() => "[ ...Not Implemented ^^... ]";

  static Future<TDistinctSmIdProxy> getDistinctSmIds(DB db) async {
    List<List<dynamic>> res = await db.select(
      """
      select 
        distinct SmId as ${DistinctSmIdProxy._smId}
      from Search
      order by SmId asc
      """
    );
    return DistinctSmIdProxy.map(res);
  }

  static TDistinctSmIdProxy map(List<List<dynamic>> vals){
    return [
      for(final v in vals) DistinctSmIdProxy(smId: v[0] as int)
    ];
  }
}

typedef TEnumName = String;
typedef TEnum = Map<TEnumName, List<EnumProxy>>;
class EnumProxy {
  final int enumId;
  final String value;

  static const String _enumId = "EnumId";
  static const String _name = "Name";
  static const String _value = "Value";

  EnumProxy({required this.enumId, required this.value});

  @override
  String toString() => "[ $enumId, $value ]";

  static Future<TEnum> getDistinctEnums(DB db) async {
    List<List<dynamic>> res = await db.select(
      """
      select 
        distinct Name as ${EnumProxy._name}
      from Enum
      order by Name asc
      """
    );
    var enumNames = EnumProxy.mapEnumName(res);

    TEnum result = {};
    for(final en in enumNames) {
      List<List<dynamic>> x = await db.select(
        """
        select 
          EnumId as ${EnumProxy._enumId},
          Value as ${EnumProxy._value}
        from Enum
        where Name = '$en'
        order by ${EnumProxy._value} asc
        """
      );

      result[en] = EnumProxy.mapEnum(x);
    }

    return result;
  }

  static List<String> mapEnumName(List<List<dynamic>> vals){
    return [
      for(final v in vals) v[0] as String
    ];
  }

  static List<EnumProxy> mapEnum(List<List<dynamic>> vals){
    return [
      for(final v in vals) EnumProxy(enumId: v[0] as int, value: v[1] as String)
    ];
  }
}