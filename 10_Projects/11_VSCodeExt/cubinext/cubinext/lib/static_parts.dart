import 'dart:convert';
import 'dart:typed_data';
import 'dart:ui';
import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:archive/archive.dart';
import 'package:cubinext/sqlite_proxy.dart';

import 'comm.dart';

class StaticParts {
  static int idProvider = 0;

  static Container getOperatorSeparator(){
    return Container(color: StaticStyles.textSeparatorColor(), width: 15, height: 5, margin: EdgeInsets.only(left: 3, right: 3),);
  }

  static Container getLinkSeparator(){
    return Container(color: StaticStyles.textLinkMarkerColor(), width: 15, height: 5, margin: EdgeInsets.only(left: 3, right: 3));
  }

  static Widget getInstrHeadLeading(int index, int count, InstructionProxy instr){
    var binOffset = instr.misc[InstructionProxy.kTypeBinOffset]!;
    var cubinOffset = instr.misc[InstructionProxy.kTypeCubinOffset]!;
    var instrOffset = instr.misc[InstructionProxy.kTypeInstrOffset]!;
    String pIndex = index.toString().padLeft("$count".length, '0');
    return RichText(
      text: TextSpan(
        children: [
          TextSpan(
            text: "[",
            style: StaticStyles.defaultBlack()),
          TextSpan(
            text: "$pIndex, ${binOffset.miscValue}, ${cubinOffset.miscValue}, ${instrOffset.miscValue}",
            style: StaticStyles.instrLineNumbers()),
          TextSpan(
            text: "]", 
            style: StaticStyles.defaultBlack())
        ]
      ));
  }

  static Widget getInstrHeadFormat(int index, int count, InstructionProxy instr){
    return RichText(
      text: TextSpan(
        children: [
          TextSpan(
            text: "[${instr.code}]  ", 
            style: StaticStyles.instrLineCode()),
          TextSpan(
            text: "${instr.instrClass}     ",
            style: StaticStyles.instrLineClass()),
          TextSpan(
            text: "${instr.desc} ", 
            style: StaticStyles.instrLineDescription()),
          TextSpan(
            text: "[${instr.typeDesc}]", 
            style: StaticStyles.instrLineCategory())
        ]
      ));
  }

  static SizedBox getScrollField({required PageStorageKey key, required Widget child}){
    final scrollController = ScrollController();
    return SizedBox(
        width: 2000,
        child: Scrollbar(
          key: key,
          thumbVisibility: true,
          controller: scrollController,
          child: SingleChildScrollView(
            controller: scrollController,
            scrollDirection: Axis.horizontal,
            child: child
          ),
        ),
    );
  }

  static Widget expansionTileCreator({
    required PageStorageKey key, 
    required Widget title, 
    Widget? leading, 
    required EdgeInsetsGeometry childrenPadding, 
    required Icon trailing, 
    required List<Widget>? children}){
      if(children != null && children.isNotEmpty)
      {
        return ExpansionTile(
          key: key, minTileHeight: 0, 
          tilePadding: EdgeInsets.only(left: 5), dense: true, title: title, leading: leading, 
          childrenPadding: childrenPadding, trailing: trailing, 
          iconColor: StaticStyles.expansionTileExpandedIconColor(), 
          expandedAlignment: Alignment.centerLeft, expandedCrossAxisAlignment: CrossAxisAlignment.start, 
          children: children);
      }
      else{
        return Stack(
          children: [
            // we want to cover this up
            ExpansionTile(
              key: key, minTileHeight: 0, 
              tilePadding: EdgeInsets.only(left: 5), dense: true, title: title, leading: leading, 
              childrenPadding: childrenPadding, trailing: trailing, 
              iconColor: StaticStyles.expansionTileExpandedIconColor(), 
              expandedAlignment: Alignment.centerLeft, expandedCrossAxisAlignment: CrossAxisAlignment.start, 
              children: []),

            // The overlay that catches clicks
            Positioned.fill(
              child: GestureDetector(
                onTap: () {},
                behavior: HitTestBehavior.opaque, // Ensures the entire area catches taps
              ),
            ),
          ],
        );
      }
  }

  static ListTile listTileCreatorRichText({required PageStorageKey key, required String content}){
    return ListTile(
      title: StaticParts.getScrollField(key: key, child: SelectableText.rich(
          TextSpan(
            text: content, 
            style: StaticStyles.classDef()), 
        ),
      ),
    );
  }

  static void fetchDbAndReload(Comm comm, FilePickerResult? result, DisplayMode mode, void Function(void Function()) setCommState){
    List<Uint8List> bits = [Uint8List.fromList([50])];

    if((comm.singleOrAll == LoadMode.single || comm.singleOrAll == LoadMode.all) && comm.selectedBinary == ""){
      // init mode
      bits.add(Uint8List.fromList([1]));
    }
    else{
      bits.add(Uint8List.fromList([0]));
    }

    if(comm.singleOrAll == LoadMode.single){
      bits.add(Uint8List.fromList([1]));
    }
    else if(comm.singleOrAll == LoadMode.all){
      bits.add(Uint8List.fromList([2]));
    }
    else{
      throw Exception("Selected LoadMode is not supported in WebAPI!");
    }

    String binaryName = comm.selectedBinary;
    Uint8List bBinaryName = utf8.encode(binaryName);
    ByteData lBinaryNameD = ByteData(4);
    lBinaryNameD.setUint32(0, bBinaryName.length, Endian.big);
    bits.add(Uint8List.fromList(lBinaryNameD.buffer.asUint8List()));
    bits.add(bBinaryName);

    String kernelName = comm.selectedKernel;
    Uint8List bKernelName = utf8.encode(kernelName);
    ByteData lKernelNameD = ByteData(4);
    lKernelNameD.setUint32(0, bKernelName.length, Endian.big);
    bits.add(Uint8List.fromList(lKernelNameD.buffer.asUint8List()));
    bits.add(bKernelName);

    if (result != null){
      for(var ff in result.files){
        String filePath = (ff.path ?? "");
        Uint8List bFilePath = utf8.encode(filePath);
        ByteData lFilePathD = ByteData(4);
        lFilePathD.setUint32(0, bFilePath.length, Endian.big);
        bits.add(Uint8List.fromList(lFilePathD.buffer.asUint8List()));
        bits.add(bFilePath);

        String fileName = ff.name;
        Uint8List bFileName = utf8.encode(fileName);
        ByteData lFileNameD = ByteData(4);
        lFileNameD.setUint32(0, bFileName.length, Endian.big);
        bits.add(Uint8List.fromList(lFileNameD.buffer.asUint8List()));
        bits.add(bFileName);

        // File file = File(ff.path!);
        // var pathParts = ff.path!.split('/');
        if(ff.bytes == null){
          throw Exception("Bytes in uploaded file don't exist!");
        }

        Uint8List bb = ff.bytes!;
        final enc = GZipEncoderWeb();
        Uint8List bbEncode = Uint8List.fromList(enc.encodeBytes(bb));
        ByteData lBbEncodeD = ByteData(4);
        lBbEncodeD.setUint32(0, bbEncode.length, Endian.big);
        bits.add(Uint8List.fromList(lBbEncodeD.buffer.asUint8List()));
        bits.add(bbEncode);
      }
    }
    
    Uint8List allBits = bits.reduce((x,y) => Uint8List.fromList(x+y));
    ByteBuffer buffer = allBits.buffer;
    // must set to null to allow reload otherwise it will redraw the one it already has!
    comm.futureDB = null;
    comm.mode = mode;
    comm.futureDB = Comm.fetchDB(comm, buffer);
    setCommState(() {});
  }

  static void fetchHelperDbAndReload(Comm comm, void Function(void Function()) setCommState){
    List<Uint8List> bits = [Uint8List.fromList([99])];
    
    Uint8List allBits = bits.reduce((x,y) => Uint8List.fromList(x+y));
    ByteBuffer buffer = allBits.buffer;
    // must set to null to allow reload otherwise it will redraw the one it already has!
    comm.futureDB = null;
    comm.mode = DisplayMode.helper;
    comm.futureDB = Comm.fetchDB(comm, buffer);
    setCommState(() {});
  }

  static Container getLeftColumn(double iconSize, StringBuffer lastPath, ByteBuffer buffer, Comm comm, void Function(void Function()) setCommState){
    return Container(
      color: StaticStyles.backgroundColor(),
      child: Column(
        children: [
          IconButton(
            onPressed: () async {
              // var ff = wff.OpenFile.open(filePath);
              FilePickerResult? result = await FilePicker.platform.pickFiles(
                dialogTitle: "Select Cubins",
                allowMultiple: true,
                initialDirectory: lastPath.toString(),
                withData: true
              );
              if(result != null){
                // We got files => clear the buffer and construct a new one
                lastPath.write(result.files.first.path!);

                // We probably want to load a new binary => reset to init state
                comm.selectedBinary = "";
                comm.selectedKernel = "";
      
                StaticParts.fetchDbAndReload(comm, result, DisplayMode.decoder, setCommState);
              }
            },
            icon: Icon(Icons.file_open_rounded),
            iconSize: iconSize, // Optional size adjustment
            tooltip: 'Open Files', // Accessibility hint
          ),
          IconButton(
            onPressed: () async {
              FilePickerResult? result = await FilePicker.platform.pickFiles(
                dialogTitle: "Select existing DB",
                allowMultiple: false,
                type: FileType.custom,
                allowedExtensions: List<String>.from(["sqlite3"]),
                withData: true
              );
              if(result != null){
                Uint8List bytes = result.files.first.bytes!;
                comm.mode = DisplayMode.decoder;
                comm.futureDB = null;
                comm.futureDB = Comm.fromBytes(comm, bytes);
                setCommState(() {});
              }
            },
            icon: Icon(Icons.file_upload_outlined),
            iconSize: iconSize, // Optional size adjustment
            tooltip: 'Open existing decoding result', // Accessibility hint
          ),
          IconButton(
            onPressed: () async {
              StaticParts.fetchHelperDbAndReload(comm, setCommState);
            },
            icon: Icon(Icons.help_rounded),
            iconSize: iconSize, // Optional size adjustment
            tooltip: 'Open existing decoding result', // Accessibility hint
          ),
        ],
      ),
    );
  }
}