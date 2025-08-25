import 'package:cubinext/static_styles.dart';
import 'package:flutter/material.dart';

class LazyExpansionTile extends StatefulWidget {
  final int dbId; // id of the parent on the db
  final int dbLen; // expected number of children
  final Widget leading;
  final Widget title;
  final Icon trailing;
  final EdgeInsetsGeometry childrenPadding;
  final Future<List<Widget>> Function(int, int, bool) futureDetails;

  const LazyExpansionTile({
    super.key, 
    required this.dbId,
    required this.dbLen,
    required this.leading,
    required this.title, 
    required this.trailing,
    required this.childrenPadding,
    required this.futureDetails});

  @override
  State<LazyExpansionTile> createState() => _LazyExpansionTile();
}

class _LazyExpansionTile extends State<LazyExpansionTile> with AutomaticKeepAliveClientMixin {
  bool _isExpanded = false;
  Future<List<Widget>>? _futureChildren;

  @override
  bool get wantKeepAlive => _isExpanded;

  List<Widget> _doTheEval(){
    return [FutureBuilder<List<Widget>>(
      future: _futureChildren, 
      builder: (context, snapshot){
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        } else if (snapshot.hasError) {
          return ListTile(title: Text('Error: ${snapshot.error}'));
        }
        // _children = snapshot.data as List<Widget>;
        return Column(children: snapshot.data as List<Widget>,);
    })];
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return ExpansionTile(
      tilePadding: EdgeInsets.only(left: 10, right: 10),
      leading: SizedBox(width: 250, child: widget.leading),
      title: Container(
        padding: EdgeInsets.only(left: 7, right: 7, top: 3, bottom: 3), 
        color: _isExpanded ? StaticStyles.expansionTileExpandedTitleColor() : StaticStyles.expansionTileFoldedTitleColor(), 
        child: widget.title),
      trailing: widget.trailing,
      iconColor: StaticStyles.expansionTileExpandedIconColor(),
      childrenPadding: widget.childrenPadding,
      
      onExpansionChanged: (expanded) {
        setState(() {
          _isExpanded = expanded;
          if(expanded){
            _futureChildren = widget.futureDetails(widget.dbId, widget.dbLen, expanded);
          }
        });
      },
      children: _doTheEval()
    );
  }
}
