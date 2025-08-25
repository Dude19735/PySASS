import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';
import 'package:cubinext/comm.dart';
import 'package:cubinext/sqlite_proxy.dart';
import 'package:cubinext/head_bar_view.dart';
import 'package:cubinext/instr_view.dart';

class KernelView extends StatefulWidget {
  final Comm comm;
  final DropdownComm dropdownComm;
  final void Function(void Function()) setCommState;

  final double leftSideWidth = 2;
  final double rightSideWidth = 2;
  final double dropdownHeight = 40;
  final double tabBarHeight = 50;
  final double tabBarTextWidth = 200;
  final double tabEntryWidth = 50;
  final double tabBarLead = 100;
  final double menuButtonPadding = 8;

  const KernelView({super.key, required this.comm, required this.dropdownComm, required this.setCommState});

  @override
  State<KernelView> createState() => _KernelView();
}

class _KernelView extends State<KernelView> with TickerProviderStateMixin {
  late final TabController _tabBarController;

  int expandedId = 0;

  @override
  void initState() {
    super.initState();
    _tabBarController = TabController(vsync: this, length: 3);
  }

  static TabBar getTabBar(
    BuildContext context,
    TabController tabController,
    final double tabEntryWidth
  ) {
    return TabBar(
      tabAlignment: TabAlignment.start,
      padding: EdgeInsets.zero,
      labelPadding: EdgeInsets.zero,
      controller: tabController,
      isScrollable: true,
      tabs: [
        SizedBox(
          width: tabEntryWidth,
          child: Tab(icon: Icon(Icons.menu_rounded)),
        ),
        SizedBox(
          width: tabEntryWidth,
          child: Tab(icon: Icon(Icons.menu_book)),
        ),
        SizedBox(
          width: tabEntryWidth,
          child: Tab(icon: Icon(Icons.settings)),
        ),
      ],
    );
  }

  static TabBarView getTabBarView(
    BuildContext context,
    BoxConstraints constraints, 
    TabController tabBarController,
    InstrView instrView
  ){
    return TabBarView(
      controller: tabBarController,
      children: [
        instrView,
        Container(color: StaticStyles.backgroundColor()),
        Container(color: StaticStyles.backgroundColor(), child: Image.asset('fonts/rbegg.png')),
    ]);
  }

  static Widget getDropdownMenuRow(
    final DropdownComm dropdownComm,
    final Comm comm,
    final double centerBoxWidth, 
    final double dropdownHeight,
    final double tabBarHeight,
    final double menuButtonPadding,
    void Function(void Function()) setCommState
  ) {
    return HeadBar(
      dropdownComm: dropdownComm, 
      comm: comm,
      centerBoxWidth: centerBoxWidth, 
      height: tabBarHeight, 
      menuButtonPadding: menuButtonPadding,
      setCommState: setCommState);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: widget.dropdownComm.futureDropdownContent, 
      builder: (BuildContext context, AsyncSnapshot<void> snapshot){
        if(snapshot.connectionState == ConnectionState.waiting){
          return const Center(child: CircularProgressIndicator());
        }
        else if(snapshot.hasError){
          return Center(child: Text("DB Request Error: ${snapshot.error}"));
        }

        widget.dropdownComm.dropdownContent = snapshot.data as TDropdown;
        DropdownComm.init(widget.dropdownComm);

        return LayoutBuilder(
          builder: (BuildContext context, BoxConstraints constraints) {
            if(constraints.minWidth < 500){
              return Center(
                child: Text("Too narrow >oO<")
              );
            }

            final double tabBarMargin = constraints.maxWidth - (widget.leftSideWidth + widget.rightSideWidth) - 3*widget.tabEntryWidth;
            final double centerBoxWidth = constraints.maxWidth - widget.leftSideWidth - widget.rightSideWidth;
            
            var instrView = InstrView(comm: widget.dropdownComm, constraints: constraints);
            var dropDownMenuRow = _KernelView.getDropdownMenuRow(
              widget.dropdownComm, widget.comm, centerBoxWidth, widget.dropdownHeight, widget.tabBarHeight, widget.menuButtonPadding, widget.setCommState);
            var tabBar = _KernelView.getTabBar(context, _tabBarController, widget.tabEntryWidth);
            var tabEntries = _KernelView.getTabBarView(context, constraints, _tabBarController, instrView);

            return Column(
              children: [
                dropDownMenuRow,
                Expanded(
                  child: Row(
                    children: [
                      /**
                       * This one is the placeholder for the stack so that
                       * the left sidebar doesn't overlap the tab view
                       */
                      Container(color: StaticStyles.leftSidelineColor(), width: widget.leftSideWidth),
                      Column(
                        children: [
                          
                          Align(
                            alignment: Alignment.topLeft,
                            child: 
                            Row(
                              children: [
                                Container(
                                  /**
                                   * This is the container that contains the buttons
                                   * of the tab view on the top left side
                                   * The EdgeInsets pushes the tab buttons to the left.
                                   */
                                  margin: EdgeInsets.only(right: tabBarMargin),
                                  height: widget.tabBarHeight,
                                  child: tabBar
                                )
                              ],
                            )
                          ),
                          Expanded(
                            /**
                             * This one contains the tab bar entries
                             */
                            child: Align(
                              alignment: Alignment.topLeft,
                              child: SizedBox(
                                width: centerBoxWidth,
                                child: tabEntries,
                              ),
                            ),
                          ),
                        ],
                      ),
                      Container(color: StaticStyles.rightSidelineColor(), width: widget.rightSideWidth),
                    ],
                  ),
                ),
              ]);
        });
      });
  }
}
