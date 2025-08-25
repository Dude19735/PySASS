import 'package:flutter/material.dart';
import 'package:cubinext/static_parts.dart';
import 'package:cubinext/static_styles.dart';

class UCHelpers {
  static Map<String, String> convertSassBitsStr(String sassBitsStr, {bool isBarrier=false}){
    var parts = sassBitsStr.split(':');
    String num = parts[0].substring(0, parts[0].length-1);
    String hnum = "0x${int.parse(num).toRadixString(16)}";
    String bar = '';
    if(isBarrier){
      List<String> bnum = int.parse(num).toRadixString(2).split('');
      List<int> req = [];
      for(int i=0; i<bnum.length; ++i) {
        if(bnum[i] == '1'){
          req.add(bnum.length-i-1);
        }
      }
      bar = "{${req.join(',')}}";
    }
    String sign = parts[0][parts[0].length-1];
    String bitNum= parts[1].substring(0, parts[1].length-1);
    return {'d': num, 'h': hnum, 'b': bar, 'sign': sign, 'bits': bitNum};
  }
}

typedef TUniverseComponentId = int;
class UniverseComponent {
  // These are the fields of the database table
  final TUniverseComponentId universeComponentId;
  final int selfParentId;
  final int seqId;
  final int level;
  final String alias;
  final int bitFrom;
  final int bitTo;
  final String sassBits;
  final String valueName;
  final String valueType;
  final String classDef;

  // Every field can have a generalized list of child elements
  List<UniverseComponent> children = [];

  UniverseComponent({required this.universeComponentId, required this.selfParentId, required this.seqId, required this.level, required this.alias, required this.bitFrom, required this.bitTo, required this.sassBits, required this.valueName, required this.valueType, required this.classDef});
  Widget materialize(){
    return Placeholder();
  }
  Widget evalView(){
    List<Widget> result = [];
    result.add(materialize());
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$classDef]", style: StaticStyles.defaultBlack())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$sassBits]", style: StaticStyles.defaultBlack())));
    return Row(children: result);
  }
}

class Op extends UniverseComponent {
  static const String typeName = "op";
  Op({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    return RichText(text: TextSpan(text: "[$valueName]", style: StaticStyles.op()));
  }
}

class Ext extends UniverseComponent {
  static const String typeName = "ext";
  Ext({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    return RichText(text: TextSpan(text: ".$valueName", style: StaticStyles.ext()));
  }
}

class Operand extends UniverseComponent {
  Operand({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});  
  @override
  Widget materialize(){
    throw UnimplementedError("Operand has no custom materialize method!");
  }
}

class DstReg extends Operand {
  static const String typeName = "dst_reg";
  DstReg({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: valueName, style: StaticStyles.dstReg())));
    result.addAll([for(final ex in ext) ex.materialize()]);

    return Row(children: result);
  }
}

class SrcReg extends Operand {
  static const String typeName = "src_reg";
  SrcReg({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: valueName, style: StaticStyles.srcReg())));
    result.addAll([for(final ex in ext) ex.materialize()]);

    return Row(children: result);
  }
}

class Func extends Operand {
  static const String typeName = "func";
  Func({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: "$valueType(", style: StaticStyles.funcType())));
    result.add(RichText(text: TextSpan(text: valueName, style: StaticStyles.funcArg())));
    result.add(RichText(text: TextSpan(text: ")", style: StaticStyles.funcType())));
    return Row(children: result);
  }
}

class Larg extends UniverseComponent {
  static const String typeName = "larg";
  Larg({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: "[", style: StaticStyles.larg())));
    for(int i=0; i<children.length; ++i) {
      result.add(children[i].materialize());
      if(i < children.length-1){
        result.add(RichText(text: TextSpan(text: ",", style: StaticStyles.defaultBlack())));
      }
    }
    result.add(RichText(text: TextSpan(text: "]", style: StaticStyles.larg())));
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
  @override
  Widget evalView(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: "[", style: StaticStyles.larg())));
    for(int i=0; i<children.length; ++i) {
      result.add(children[i].evalView());
      if(i < children.length-1){
        result.add(RichText(text: TextSpan(text: ",", style: StaticStyles.defaultBlack())));
      }
    }
    result.add(RichText(text: TextSpan(text: "]", style: StaticStyles.larg())));
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
}

class AttrList extends Operand {
  static const String typeName = "list";
  AttrList({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    if(alias != '') result.add(RichText(text: TextSpan(text: alias, style: StaticStyles.attrList())));
    result.add(children[0].materialize()); // at least one child
    if(children.length > 1){
      result.add(children[1].materialize()); // maybe a second one ^^
    }
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
  @override
  Widget evalView(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    if(alias != '') result.add(RichText(text: TextSpan(text: alias, style: StaticStyles.attrList())));
    result.add(children[0].evalView()); // at least one child
    if(children.length > 1){
      result.add(children[1].evalView()); // maybe a second one ^^
    }
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
}

class Attr extends Operand {
  static const String typeName = "attr";
  Attr({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: alias, style: StaticStyles.attr())));
    result.add(children[0].materialize()); // at least one child
    if(children.length > 1){
      result.add(children[1].materialize()); // maybe a second one ^^
    }
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
  @override
  Widget evalView(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    if(alias != '') result.add(RichText(text: TextSpan(text: alias, style: StaticStyles.attrList())));
    result.add(children[0].evalView()); // at least one child
    if(children.length > 1){
      result.add(children[1].evalView()); // maybe a second one ^^
    }
    result.addAll([for(final ex in ext) ex.materialize()]);
    return Row(children: result,);
  }
}

class Pred extends UniverseComponent {
  static const String typeName = "pred";
  Pred({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: valueName, style: StaticStyles.pred())));
    result.addAll([for(final ex in ext) ex.materialize()]);

    return Row(children: result);
  }
  @override
  Widget evalView(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.evalView()]);
    if(ops.isNotEmpty) result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$classDef", style: StaticStyles.pred())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "$sassBits]", style: StaticStyles.pred())));
    if(ext.isNotEmpty) result.add(StaticParts.getOperatorSeparator());
    result.addAll([for(final ex in ext) ex.evalView()]);

    return Row(children: result);
  }
}

class Opcode extends UniverseComponent {
  static const String typeName = "opcode";
  Opcode({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.addAll([for(final op in ops) op.materialize()]);
    result.add(RichText(text: TextSpan(text: valueName, style: StaticStyles.opcode())));
    result.addAll([for(final ex in ext) ex.materialize()]);

    return Row(children: result);
  }
  @override
  Widget evalView(){
    var ext = children.whereType<Ext>().toList();
    var ops = children.whereType<Op>().toList();

    List<Widget> result = [];
    result.add(materialize());
    result.add(StaticParts.getOperatorSeparator());
    result.addAll([for(final op in ops) op.evalView()]);
    if(ops.isNotEmpty) result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$classDef", style: StaticStyles.pred())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "$sassBits]", style: StaticStyles.pred())));
    if(ext.isNotEmpty) result.add(StaticParts.getOperatorSeparator());
    result.addAll([for(final ex in ext) ex.evalView()]);

    return Row(children: result);
  }
}

class Cash extends UniverseComponent {
  static const String typeName = "cash";
  Cash({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    List<Widget> result = [];
    if(valueName.startsWith('RD') || valueName.startsWith('WR') || valueName.startsWith('WR_EARLY')){
      var conv = UCHelpers.convertSassBitsStr(sassBits);
      result.add(RichText(text: TextSpan(text: "\$$valueName", style: valueName.endsWith("**") ? StaticStyles.cashTypeAddedLater() : StaticStyles.cashType())));
      result.add(RichText(text: TextSpan(text: "=", style: StaticStyles.defaultBlack())));
      result.add(RichText(text: TextSpan(text: conv['h'], style: StaticStyles.cashVal())));
    }
    else if (valueName.startsWith('REQ')){
      var conv = UCHelpers.convertSassBitsStr(sassBits, isBarrier: true);
      result.add(RichText(text: TextSpan(text: "\$$valueName", style: valueName.endsWith("**") ? StaticStyles.cashTypeAddedLater() : StaticStyles.cashType())));
      result.add(RichText(text: TextSpan(text: "=", style: StaticStyles.defaultBlack())));
      result.add(RichText(text: TextSpan(text: conv['b'], style: StaticStyles.cashSet())));
    }
    else{
      var conv = UCHelpers.convertSassBitsStr(sassBits);
      result.add(RichText(text: TextSpan(text: "\$$valueName", style: valueName.endsWith("**") ? StaticStyles.cashTypeAddedLater() : StaticStyles.cashType())));
      result.add(RichText(text: TextSpan(text: ":[", style: StaticStyles.defaultBlack())));
      result.add(RichText(text: TextSpan(text: valueType, style: StaticStyles.cashValName())));
      result.add(RichText(text: TextSpan(text: "]=", style: StaticStyles.defaultBlack())));
      result.add(RichText(text: TextSpan(text: conv['h'], style: StaticStyles.cashVal())));
    }
    return Row(children: result,);
  }
  @override
  Widget evalView(){
    List<Widget> result = [];
    result.add(materialize());
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$sassBits", style: StaticStyles.defaultBlack())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "$classDef]", style: StaticStyles.defaultBlack())));
    return Row(children: result,);
  }
}

class Const extends UniverseComponent {
  static const String typeName = "const";
  Const({required super.universeComponentId, required super.selfParentId, required super.seqId, required super.level, required super.alias, required super.bitFrom, required super.bitTo, required super.sassBits, required super.valueName, required super.valueType, required super.classDef});
  @override
  Widget materialize(){
    List<Widget> result = [];
    var conv = UCHelpers.convertSassBitsStr(sassBits);
    result.add(RichText(text: TextSpan(text: "C[$bitFrom:$bitTo]=", style: StaticStyles.defaultBlack())));
    result.add(RichText(text: TextSpan(text: conv['h'], style: StaticStyles.constVal())));
    return Row(children: result,);
  }
  @override
  Widget evalView(){
    List<Widget> result = [];
    result.add(materialize());
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$sassBits", style: StaticStyles.defaultBlack())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "$classDef]", style: StaticStyles.defaultBlack())));
    return Row(children: result,);
  }
}

class UniverseEvalEncoding {
  // These are the fields of the database table
  final int universeEvalEncodingId;
  final int selfParentId;
  final int seqNr;
  final int level;
  final String expr;
  final String sassBitsStr;
  final int bitFrom;
  final int bitTo;
  final int? universeComponentId;
  // Every field can have a generalized list of child elements
  List<UniverseEvalEncoding> children = [];
  UniverseComponent? ref;

  UniverseEvalEncoding({required this.universeEvalEncodingId, required this.selfParentId, required this.seqNr, required this.level, required this.expr, required this.sassBitsStr, required this.bitFrom, required this.bitTo, required this.universeComponentId});
  
  Widget materialize(){
    return const Text("[Placeholder]");
  }
  void addReference(UniverseComponent? component){
    ref = component;
  }
}

class UlivatorEncDynamic extends UniverseEvalEncoding {
  static const String typeName = "dynamic";
  UlivatorEncDynamic({required super.universeEvalEncodingId, required super.selfParentId, required super.seqNr, required super.level, required super.expr, required super.sassBitsStr, required super.bitFrom, required super.bitTo, required super.universeComponentId});
  @override
  Widget materialize(){
    List<Widget> result = [];
    result.add(RichText(text: TextSpan(text: expr, style: StaticStyles.evalExpr())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$sassBitsStr]", style: StaticStyles.defaultBlack())));
    if(ref != null){
      result.add(StaticParts.getLinkSeparator());
      result.add(ref!.evalView());
      result.add(StaticParts.getLinkSeparator());
    }
    return StaticParts.getScrollField(key: PageStorageKey('universe-${StaticParts.idProvider++}'), child:Row(children: result));
  }
}

class UlivatorEncFixed extends UniverseEvalEncoding {
  static const String typeName = "fixed";
  UlivatorEncFixed({required super.universeEvalEncodingId, required super.selfParentId, required super.seqNr, required super.level, required super.expr, required super.sassBitsStr, required super.bitFrom, required super.bitTo, required super.universeComponentId});
  @override
  Widget materialize(){
    List<Widget> result = [];
    result.add(RichText(text: TextSpan(text: expr, style: StaticStyles.evalExpr())));
    result.add(StaticParts.getOperatorSeparator());
    result.add(RichText(text: TextSpan(text: "[$sassBitsStr]", style: StaticStyles.defaultBlack())));
    if(ref != null){
      result.add(StaticParts.getLinkSeparator());
      result.add(ref!.evalView());
      result.add(StaticParts.getLinkSeparator());
    }
    return StaticParts.getScrollField(key: PageStorageKey('universe-enc-sf-${StaticParts.idProvider++}'), child: Row(children: result));
  }
}

class UlivatorEncFunc extends UniverseEvalEncoding {
  static const String typeName = "func";
  UlivatorEncFunc({required super.universeEvalEncodingId, required super.selfParentId, required super.seqNr, required super.level, required super.expr, required super.sassBitsStr, required super.bitFrom, required super.bitTo, required super.universeComponentId});
  @override
  Widget materialize(){
    List<Widget> result = [];
    var tt = RichText(text: TextSpan(text: expr, style: StaticStyles.evalExpr()));
    result.add(children[0].materialize()); // at least one child
    if(children.length > 1){
      result.add(children[1].materialize()); // maybe a second one ^^
    }
    var evalTile = StaticParts.expansionTileCreator(key: PageStorageKey('universe-${StaticParts.idProvider++}'), title: tt, childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: result);
    return evalTile;
  }
}

class UlivatorEncTable extends UniverseEvalEncoding {
  static const String typeName = "table";
  UlivatorEncTable({required super.universeEvalEncodingId, required super.selfParentId, required super.seqNr, required super.level, required super.expr, required super.sassBitsStr, required super.bitFrom, required super.bitTo, required super.universeComponentId});
  @override
  Widget materialize(){
    List<Widget> result = [];
    var tt = RichText(text: TextSpan(text: expr, style: StaticStyles.evalExpr()));
    result.addAll([for(final c in children) c.materialize()]); // at least one child
    var evalTile = StaticParts.expansionTileCreator(key: PageStorageKey('universe-${StaticParts.idProvider++}'), title: tt, childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: result);
    return evalTile;
  }
}

class Universe {
  int instrIndex;
  int universeIndex;
  Pred? pred;
  late Opcode opcode;
  List<Operand> operands = [];
  List<Cash> cashs = [];
  List<Const> consts = [];
  List<UniverseEvalEncoding> evalEncoding = [];
  Map<TUniverseComponentId, UniverseComponent> componentMap = {};

  Universe({required this.instrIndex, required this.universeIndex});
  void add(List<UniverseComponent> parts){
    for(final part in parts){
      part is Pred ? pred = part
      : part is Opcode ? opcode = part
      : part is Operand ? operands.add(part)
      : part is Cash ? cashs.add(part)
      : part is Const ? consts.add(part)
      : throw StateError("Part has a type that can't be directly added to a Universe!");

      // store local references to the children
      componentMap[part.universeComponentId] = part;
      for(final c in part.children){
        componentMap[c.universeComponentId] = c;
      }
    }
  }

  void addUlivator(List<UniverseEvalEncoding> ulivators){
    for(final ulivator in ulivators){
      if(ulivator.universeComponentId != null){
        if(componentMap.containsKey(ulivator.universeComponentId)){
          ulivator.addReference(componentMap[ulivator.universeComponentId]);
        }
      }
      for(final subUlivator in ulivator.children){
        if(subUlivator.universeComponentId != null){
          if(componentMap.containsKey(subUlivator.universeComponentId)){
            subUlivator.addReference(componentMap[subUlivator.universeComponentId]);
          }
        }
      }
    }
    evalEncoding.addAll(ulivators);
  }

  Widget materialize(int index){
    List<Widget> tChildren = [];
    if(pred != null){
      tChildren.add(pred!.materialize());
      tChildren.add(StaticParts.getOperatorSeparator());
    }
    tChildren.add(opcode.materialize());
    tChildren.add(StaticParts.getOperatorSeparator());
    for(int i=0; i<operands.length; ++i){
      var op = operands[i];
      tChildren.add(op.materialize());
      if(i<operands.length-1){
        tChildren.add(StaticParts.getOperatorSeparator());
      }
    }
    var tt = StaticParts.getScrollField(key: PageStorageKey('universe-part-tt-${StaticParts.idProvider++}'), child: Row(children: tChildren,));

    List<Widget> cashsAndConsts = [];
    if(cashs.isNotEmpty){
      List<Widget> cc = [];
      for(int i=0; i<cashs.length; ++i) {
        cc.add(cashs[i].materialize());
        if(i<cashs.length-1){
          cc.add(StaticParts.getOperatorSeparator());
        }
      }
      cashsAndConsts.add(ListTile(
        leading: const Text("[Cashs]"), 
        title: StaticParts.getScrollField(key: PageStorageKey('universe-part-cash-${StaticParts.idProvider++}'), child: Row(children: cc)),
      ));
    }
    if(consts.isNotEmpty){
      List<Widget> cc = [];
      for(int i=0; i<consts.length; ++i) {
        cc.add(consts[i].materialize());
        if(i<consts.length-1){
          cc.add(StaticParts.getOperatorSeparator());
        }
      }
      cashsAndConsts.add(ListTile(
        leading: const Text("[Consts]"), 
        title: StaticParts.getScrollField(key: PageStorageKey('universe-part-const-${StaticParts.idProvider++}'), child: Row(children: cc)),
      ));
    }

    // final scrollController = ScrollController();
    List<Widget> evalC = [for(final eval in evalEncoding) eval.materialize()];
    var evalTile = StaticParts.expansionTileCreator(key: PageStorageKey('universe-${StaticParts.idProvider++}'), title: const Text("Class Eval"), childrenPadding: EdgeInsets.only(left: 10, bottom: 5), trailing: Icon(Icons.arrow_drop_down_circle), children: evalC);
    cashsAndConsts.add(evalTile);

    return StaticParts.expansionTileCreator(key: PageStorageKey('universe-${StaticParts.idProvider++}'), title: tt, leading: Text("[U$index]"), childrenPadding: EdgeInsets.only(left: 10, bottom: 10), trailing: Icon(Icons.arrow_drop_down_circle), 
      children: cashsAndConsts);
  }

  static UniverseComponent getInstrPart({required int universeComponentId, required int selfParentId, required int seqId, required int level, required String typeName, required String alias, required int bitFrom, required int bitTo, required String sassBits, required String valueName, required String valueType, required String classDef}){
    switch(typeName){
      case Op.typeName: return Op(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Ext.typeName: return Ext(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case DstReg.typeName: return DstReg(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case SrcReg.typeName: return SrcReg(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Func.typeName: return Func(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Larg.typeName: return Larg(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Attr.typeName: return Attr(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case AttrList.typeName: return AttrList(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Pred.typeName: return Pred(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Opcode.typeName: return Opcode(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Cash.typeName: return Cash(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      case Const.typeName: return Const(universeComponentId: universeComponentId, selfParentId: selfParentId, seqId: seqId, level: level, alias: alias, bitFrom: bitFrom, bitTo: bitTo, sassBits: sassBits, valueName: valueName, valueType: valueType, classDef: classDef);
      default: throw StateError("Invalid part designation [$typeName]! It doesn't exist!");
    }
  }

  static UniverseEvalEncoding getEvalEncoding({required int universeEvalEncodingId, required int selfParentId, required int seqNr, required int level, required String typeName, required String expr, required String sassBitsStr, required int bitFrom, required int bitTo, required int? universeComponentId}){
    switch(typeName){
      case UlivatorEncDynamic.typeName: return UlivatorEncDynamic(universeEvalEncodingId: universeEvalEncodingId, selfParentId: selfParentId, seqNr: seqNr, level: level, expr: expr,sassBitsStr: sassBitsStr, bitFrom: bitFrom, bitTo: bitTo, universeComponentId: universeComponentId);
      case UlivatorEncFixed.typeName: return UlivatorEncFixed(universeEvalEncodingId: universeEvalEncodingId, selfParentId: selfParentId, seqNr: seqNr, level: level, expr: expr,sassBitsStr: sassBitsStr, bitFrom: bitFrom, bitTo: bitTo, universeComponentId: universeComponentId);
      case UlivatorEncFunc.typeName: return UlivatorEncFunc(universeEvalEncodingId: universeEvalEncodingId, selfParentId: selfParentId, seqNr: seqNr, level: level, expr: expr,sassBitsStr: sassBitsStr, bitFrom: bitFrom, bitTo: bitTo, universeComponentId: universeComponentId);
      case UlivatorEncTable.typeName: return UlivatorEncTable(universeEvalEncodingId: universeEvalEncodingId, selfParentId: selfParentId, seqNr: seqNr, level: level, expr: expr,sassBitsStr: sassBitsStr, bitFrom: bitFrom, bitTo: bitTo, universeComponentId: universeComponentId);
      default: throw StateError("Invalid ulivator designation [$typeName]! It doesn't exist!");
    }
  }
}