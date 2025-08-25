import 'package:cubinext/static_parts.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/static_styles.dart';

enum DropdownType {
  binary, kernel
}

class HeadBar extends StatefulWidget {
  final DropdownComm dropdownComm;
  final Comm comm;
  final double centerBoxWidth;
  final double height;
  final double menuButtonPadding;
  final void Function(void Function()) setCommState;

  const HeadBar({
    super.key, 
    required this.dropdownComm, 
    required this.comm,
    required this.centerBoxWidth, 
    required this.height, 
    required this.menuButtonPadding,
    required this.setCommState
  });

  @override
  State<HeadBar> createState() => _HeadBar();
}

class _HeadBar extends State<HeadBar> {
  static List<DropdownMenuItem<String>> getItems(List<String> entries) {
    return entries.map<DropdownMenuItem<String>>((String value) {
      return DropdownMenuItem<String>(
        value: value,
        child: Padding(
          padding: const EdgeInsets.only(left: 5),
          child: Text(value),
        ),
      );
    }).toList();
  }

  @override
  void initState(){
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: StaticStyles.backgroundColor(),
      child: Row(
          children: [
            Container(
              width: widget.centerBoxWidth*0.25 - 10,
              height: widget.height,
              margin: EdgeInsets.all(5),
              child: DropdownButton<String>(
                value: widget.dropdownComm.selectedBinary,
                icon: const Icon(Icons.arrow_downward),
                elevation: 16,
                style: StaticStyles.dropDown(),
                isExpanded: true,
                onChanged: (String? value) {
                  if(value! == widget.dropdownComm.selectedBinary){
                    return;
                  }
                  if(widget.comm.singleOrAll == LoadMode.single){
                    // Do this one manually becaues we will load a completely new thing...
                    widget.dropdownComm.selectedBinary = value;
                    widget.comm.selectedBinary = widget.dropdownComm.selectedBinary;
                    widget.comm.selectedKernel = "";
                    StaticParts.fetchDbAndReload(widget.comm, null, widget.comm.mode, widget.setCommState);
                  }
                  else {
                    // This is called when the user selects an item.
                    DropdownComm.updateBinary(widget.dropdownComm, value);
                    DropdownComm.updateInstructions(widget.dropdownComm);
                    setState(() {});
                  }
                },
                items: _HeadBar.getItems(widget.dropdownComm.binaryEntries),
              )
            ),
            Container(
              width: 3*widget.height,
              height: widget.height,
              margin: EdgeInsets.all(0),
              child:Row(
                children: [
                  Spacer(),
                  Text("Single"),
                  Radio<LoadMode>(
                    value: LoadMode.single,
                    groupValue: widget.comm.singleOrAll,
                    onChanged: (LoadMode? value) {
                      setState(() {
                        widget.comm.singleOrAll = value!;
                        widget.comm.selectedBinary = widget.dropdownComm.selectedBinary;
                        widget.comm.selectedKernel = widget.dropdownComm.selectedKernel;
                      });
                    },
                  ),
                  Spacer(),
                  Text("All"),
                  Radio<LoadMode>(
                    value: LoadMode.all,
                    groupValue: widget.comm.singleOrAll,
                    onChanged: (LoadMode? value) {
                      setState(() {
                        // In here, we can't hit the init state...
                        //  => selectedBinary is not allowed to be reset unless we have a list of newly selected files to send which is never the case in here
                        widget.comm.singleOrAll = value!;
                        widget.comm.selectedBinary = widget.dropdownComm.selectedBinary;
                        widget.comm.selectedKernel = "";
                      });
                      StaticParts.fetchDbAndReload(widget.comm, null, widget.comm.mode, widget.setCommState);
                    },
                  ),
                  Spacer(),
              ],
            ),
            ),
            Container(
              width: widget.centerBoxWidth*0.5 - 10,
              height: widget.height,
              margin: EdgeInsets.all(5),
              child: DropdownButton<String>(
                value: widget.dropdownComm.selectedKernel,
                icon: const Icon(Icons.arrow_downward),
                elevation: 16,
                style: StaticStyles.dropDown(),
                isExpanded: true,
                onChanged: (String? value) {
                  if(value! == widget.dropdownComm.selectedKernel){
                    return;
                  }
                  // This is called when the user selects an item.
                  setState(() {
                      widget.dropdownComm.selectedKernel = value;
                    },);
                  if(widget.comm.singleOrAll == LoadMode.single){
                    widget.comm.selectedBinary = widget.dropdownComm.selectedBinary;
                    widget.comm.selectedKernel = widget.dropdownComm.selectedKernel;
                    StaticParts.fetchDbAndReload(widget.comm, null, widget.comm.mode, widget.setCommState);
                  }
                  else {
                    DropdownComm.updateInstructions(widget.dropdownComm);
                  }
                },
                items: _HeadBar.getItems(widget.dropdownComm.kernelEntries)
              )
            ),
            IconButton(
              icon: Icon(Icons.save_alt_rounded),
              padding: EdgeInsets.all(widget.menuButtonPadding),
              iconSize: widget.height - 2*widget.menuButtonPadding, // Adjust the size of the icon
              tooltip: "Save", // Tooltip displayed on long press
              onPressed: () {
                DropdownComm.saveToFile(widget.dropdownComm);
              },
            ),
            SizedBox(
              width: widget.centerBoxWidth*0.25 - 4*widget.height,
              height: widget.height
            )
          ],
      ),
    );
  }
}