import 'package:flutter/material.dart';

class CheckboxWithState extends StatefulWidget {
  final int id;
  final String text;
  const CheckboxWithState({super.key, required this.id, required this.text});

  @override
  State<CheckboxWithState> createState() => _CheckboxWithState();
}

class _CheckboxWithState extends State<CheckboxWithState> {
  bool checkbox = true;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          Text(widget.text),
          Checkbox(
            value: checkbox,
            onChanged: (bool? value) {
              setState(() {
                checkbox = value!;
              });
            },
          ),
        ],
      ),
    );
  }
}
