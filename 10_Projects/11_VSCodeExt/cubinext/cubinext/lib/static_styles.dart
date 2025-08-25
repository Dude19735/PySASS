import 'package:flutter/material.dart';

class StaticStyles {
  static const fontFamily = 'Prompt';
  static ThemeData themeData = ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
    fontFamily: 'Coda'
  );

  /// ==================================================================================
  /// All color definitions
  static Color backgroundColor(){
    return StaticStyles.themeData.colorScheme.surface;
  }

  static Color leftSidelineColor(){
    return Colors.black26;
  }

  static Color rightSidelineColor(){
    return Colors.black26;
  }

  static Color expansionTileFoldedIconColor(){
    return StaticStyles.themeData.colorScheme.surface;
  }

  static Color expansionTileExpandedIconColor(){
    return Colors.red;
  }

  static Color expansionTileExpandedTitleColor(){
    return Colors.black12;
  }

  static Color expansionTileFoldedTitleColor(){
    return Colors.transparent;
  }

  static Color textSeparatorColor(){
    return Colors.black12;
  }

  static Color textLinkMarkerColor(){
    return Colors.red;
  }

  static Color latenciesTableBorders(){
    return Colors.black26;
  }

  /// ==================================================================================
  /// General styles
  static TextStyle defaultBlack(){
    return TextStyle(color: Colors.black, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle dropDown(){
    return TextStyle(color: Colors.deepPurple, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle valueColor(){
    return TextStyle(color: Colors.blue[900], fontFamily: StaticStyles.fontFamily);
  }

  /// ==================================================================================
  /// Styles for the main instruction line display
  static TextStyle instrLineNumbers(){
    return valueColor(); 
  }

  static TextStyle instrLineCode(){
    return TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 15, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle instrLineClass(){
    return TextStyle(color: Colors.redAccent);
  }

  static TextStyle instrLineDescription(){
    return StaticStyles.defaultBlack();
  }

  static TextStyle instrLineCategory(){
    return TextStyle(color: Colors.blueGrey);
  }

  /// ==================================================================================
  /// Styles for the instruction details views
  static TextStyle opcode(){
    return TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle pred(){
    return TextStyle(color: Colors.blue[900], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle dstReg(){
    return TextStyle(color: Colors.purple, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle srcReg(){
    return TextStyle(color: Colors.red, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle cashType(){
    return TextStyle(color: Colors.green[900], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle cashTypeAddedLater(){
    return TextStyle(color: Colors.deepOrangeAccent[700], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle cashVal(){
    return StaticStyles.valueColor();
  }

  static TextStyle cashSet(){
    return TextStyle(color: Colors.purple[600], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle cashValName(){
    return TextStyle(color: Colors.yellow[800], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle constVal(){
    return StaticStyles.valueColor();
  }

  static TextStyle op(){
    return TextStyle(color: Colors.black45, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle ext(){
    return TextStyle(color: Colors.green[900], fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle funcType(){
    return TextStyle(color: Colors.black45, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle funcArg(){
    return StaticStyles.valueColor();
  }

  static TextStyle larg(){
    return TextStyle(color: Colors.black, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle attrList(){
    return TextStyle(color: Colors.black, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle attr(){
    return TextStyle(color: Colors.black, fontFamily: StaticStyles.fontFamily);
  }

  static TextStyle classDef(){
    return TextStyle(color: Colors.black, fontSize: 12, fontFamily: StaticStyles.fontFamily);
  }

  /// ==================================================================================
  /// Styles for the evaluation
  static TextStyle evalExpr(){
    return TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontFamily: StaticStyles.fontFamily);
  }
}