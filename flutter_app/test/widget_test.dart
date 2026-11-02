import 'package:flutter_test/flutter_test.dart';
import 'package:quantumshield_mobile/main.dart';

void main() {
  testWidgets('QuantumShield basic smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const QuantumShieldApp());
    expect(find.text('QUANTUMSHIELD'), findsOneWidget);
  });
}
