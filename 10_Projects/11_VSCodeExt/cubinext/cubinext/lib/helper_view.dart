import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/sqlite_proxy.dart';
import 'package:cubinext/head_bar_view.dart';
import 'package:cubinext/instr_view.dart';
import 'package:cubinext/state_checkbox.dart';

class HelperView extends StatefulWidget {
  final Comm comm;
  final HelperComm helperComm;
  final void Function(void Function()) setCommState;

  final double leftSideWidth = 2;
  final double rightSideWidth = 2;
  final double dropdownHeight = 40;
  final double tabBarHeight = 50;
  final double tabBarTextWidth = 200;
  final double tabEntryWidth = 50;
  final double tabBarLead = 100;
  final double menuButtonPadding = 8;

  const HelperView({super.key, required this.comm, required this.helperComm, required this.setCommState});

  @override
  State<HelperView> createState() => _HelperView();
}

class _HelperView extends State<HelperView> with TickerProviderStateMixin {
  // late final TabController _tabBarController;
  int expandedId = 0;

  @override
  void initState() {
    super.initState();
  }

  static Widget createCheckboxRow(String leadText, double spacingWidth, List<int> id, List<String> text) {
    return Wrap(
        spacing: 20,
        children: [
          Column(
            children: [
              RichText(
              text: TextSpan(
                text: leadText,
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, fontFamily: StaticStyles.fontFamily)
              )),
              Text(""),
          ]),
          SizedBox(width: spacingWidth),
          Wrap(
            children: [
              for(int i=0; i<id.length; ++i)
                CheckboxWithState(id: id[i], text: text[i])
            ],
          ),
        ],
    );
  }

  @override
  Widget build(BuildContext context) {

    return FutureBuilder<void>(
      future: widget.helperComm.futureSmIds, 
      builder: (BuildContext context, AsyncSnapshot<void> snapshot){
        if(snapshot.connectionState == ConnectionState.waiting){
          return const Center(child: CircularProgressIndicator());
        }
        else if(snapshot.hasError){
          return Center(child: Text("DB Request Error: ${snapshot.error}"));
        }

        var content = snapshot.data as TDistinctSmIdProxy;

        return 
          Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(height: 20,),
              createCheckboxRow("SM Nr", 20, [for(final x in content) x.smId], [for(final x in content) "${x.smId}"]),
              Center(
                child: Container(height: 3, color: Colors.black87,),
              ),
              FutureBuilder<void>(
                future: widget.helperComm.futureEnum, 
                builder: (BuildContext context, AsyncSnapshot<void> snapshot){
                  if(snapshot.connectionState == ConnectionState.waiting){
                    return const Center(child: CircularProgressIndicator());
                  }
                  else if(snapshot.hasError){
                    return Center(child: Text("DB Request Error: ${snapshot.error}"));
                  }
          
                  TEnum enums = snapshot.data as TEnum;
                  
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for(final e in enums.entries) Column(
                        children: [
                          createCheckboxRow(e.key, 20, [for(final x in e.value) x.enumId], [for(final x in e.value) x.value]),
                          Center(
                            child: Container(height: 3, color: Colors.black38,),
                          ),
                        ],
                      ),

                      
                    ],
                  );
                }
              )
            ],
        );
      });
  }
}
