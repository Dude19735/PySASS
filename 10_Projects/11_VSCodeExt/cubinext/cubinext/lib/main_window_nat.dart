import 'dart:typed_data';
import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/main_view.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/static_parts.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cubinext @N',
      theme: StaticStyles.themeData,
      home: MyHomePage(title: 'Cubinext'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;
  static const double sideBarWidth = 50;
  static StringBuffer lastPath = StringBuffer(".");

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  // String message = "@@GetCubinFilePath@@|14|127.0.0.1:8180|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_50|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_52|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_53|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_60|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_61|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_62|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_70|132|/home/lol/Documents/repos/MasterThesis/10_GadgetExperiments/09_PyCubinAnalysis/py_cubin_analysis/templates/experiment.mc.template_72";
  ByteBuffer buffer = Uint8List(0).buffer;
  String lastPath = "";
  final Comm comm = Comm(conIpPort: "127.0.0.1:8180");

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: MyHomePage.sideBarWidth,
          child: StaticParts.getLeftColumn(MyHomePage.sideBarWidth - 15, MyHomePage.lastPath, buffer, comm, setState)
        ),
        Expanded(
          child: MainView(buffer: buffer, comm: comm, setCommState: setState)
        ),
      ],
    );
  }
}
