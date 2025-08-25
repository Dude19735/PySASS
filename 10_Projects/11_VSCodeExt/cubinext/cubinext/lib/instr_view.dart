import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/sqlite_proxy.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/instr_details_view.dart';
import 'package:cubinext/static_parts.dart';

class InstrView extends StatefulWidget {
  final DropdownComm comm;
  final BoxConstraints constraints;
  
  const InstrView({
    super.key, 
    required this.comm,
    required this.constraints
  });

  @override
  State<InstrView> createState() => _InstrView();
}

class _InstrView extends State<InstrView> {
  int _instrIdCounter = 0;
  TInstructions instructions = [];

  void refresh(){
    setState(() {});
  }

  @override
  void initState(){
    super.initState();
    widget.comm.refreshInstrViewCallback = refresh;
  }

  static Table instrLatsToTable(TInstrLatency lats){
    var rows = lats[InstrLatencyProxy.kRows]!;
    return Table(
      columnWidths: {
        for(int i=0; i<rows[0].length; ++i) i:IntrinsicColumnWidth()
      },
      border: TableBorder.all(color: StaticStyles.latenciesTableBorders()),
      children: List.generate(
        rows.length,
        (rowIndex) => TableRow(
          children: List.generate(
            rows[rowIndex].length,
            (colIndex) {
              return Padding(
                padding: const EdgeInsets.all(2.0),
                child: Text('${rows[rowIndex][colIndex]}'),
              );
              // int itemIndex = rowIndex * columns + colIndex;
              // return itemIndex < items.length
              //     ? Padding(
              //         padding: EdgeInsets.all(8),
              //         child: Text('${items[itemIndex]}'),
              //       )
              //     : Container(); // Empty cell if out of range
            },
          ),
        ),
      ),
    );
  }

  Future<List<Widget>> detailsLoader(final int instrId, final int universeCount, final bool expanded) async {
    if(!expanded){
      return [];
    }
    var instrUniverses = await UniverseProxy.get(widget.comm.db, [instrId], {instrId: universeCount});
    var defs = await InstrClassDefProxy.get(widget.comm.db, instrId);
    TUniverseEvalMap evals = await UniverseEvalEncodingProxy.get(widget.comm.db, instrId, universeCount);
    var lats = await InstrLatencyProxy.get(widget.comm.db, instrId);

    var universes = instrUniverses[instrId]!;
    List<Widget> widgets = [];
    int universeIndex = 0;
    for(final universe in universes){
      universe.addUlivator(evals[universe.universeIndex]!);
      widgets.add(universe.materialize(universeIndex));
      universeIndex++;
    }

    widgets.addAll([
      StaticParts.expansionTileCreator(key: PageStorageKey('classDef-${_instrIdCounter++}'), title: const Text("Class Def"), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypeFormat}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypeFormat.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypeFormat]!.content)
          ],
        ),
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypeConditions}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypeConditions.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypeConditions]!.content)
          ],
        ),
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypeProperties}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypeProperties.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypeProperties]!.content)
          ],
        ),
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypePredicates}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypePredicates.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypePredicates]!.content)
          ],
        ),
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypeOpcodes}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypeOpcodes.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypeOpcodes]!.content)
          ],
        ),
        StaticParts.expansionTileCreator(key: PageStorageKey('${InstrClassDefProxy.kTypeEncoding}-${_instrIdCounter++}'), title: Text(InstrClassDefProxy.kTypeEncoding.toUpperCase()), childrenPadding: EdgeInsets.only(left: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
            StaticParts.listTileCreatorRichText(key: PageStorageKey('listtyle-${_instrIdCounter++}'), content: defs[InstrClassDefProxy.kTypeEncoding]!.content)
          ],
        )
      ]),
      StaticParts.expansionTileCreator(key: PageStorageKey('InstrClassLat-${_instrIdCounter++}'), title: const Text("Latencies"), childrenPadding: EdgeInsets.only(left: 10, bottom: 10), trailing: Icon(Icons.arrow_drop_down_circle), children: [
        StaticParts.getScrollField(key: PageStorageKey('instrlattable-${StaticParts.idProvider++}'), child: _InstrView.instrLatsToTable(lats))
      ])
    ],);
    
    return widgets;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
        future: widget.comm.futureInstructions, 
        builder: (BuildContext context, AsyncSnapshot<void> snapshot){
          if(snapshot.connectionState == ConnectionState.waiting){
            return const Center(child: CircularProgressIndicator());
          }
          else if(snapshot.hasError){
            return Center(child: Text("DB Request Error: ${snapshot.error}"));
          }

          instructions = snapshot.data as TInstructions;
          return ListView.builder(
            addAutomaticKeepAlives: true,
            itemCount: instructions.length,
            itemBuilder: (context, index){
              return LazyExpansionTile(
                key: PageStorageKey(InstructionProxy.getUniqueId(index, instructions)),
                dbId: instructions[index].instrId,
                dbLen: instructions[index].universeCount,
                leading: StaticParts.getInstrHeadLeading(index, instructions.length, instructions[index]),
                title: StaticParts.getInstrHeadFormat(index, instructions.length, instructions[index]),
                trailing: Icon(Icons.arrow_drop_down_circle),
                childrenPadding: EdgeInsets.only(left: 20),
                futureDetails: detailsLoader,
              );
            }
          );
    });
  }
}