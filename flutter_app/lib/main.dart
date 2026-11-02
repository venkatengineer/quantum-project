import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/simulation_provider.dart';
import 'screens/dashboard_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const QuantumShieldApp());
}

class QuantumShieldApp extends StatelessWidget {
  const QuantumShieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SimulationProvider()..init()),
      ],
      child: MaterialApp(
        title: 'QuantumShield',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          brightness: Brightness.dark,
          scaffoldBackgroundColor: const Color(0xFF07090E),
          primaryColor: const Color(0xFF7C3AED),
          colorScheme: const ColorScheme.dark(
            primary: Color(0xFF7C3AED),
            secondary: Color(0xFF38BDF8),
            surface: Color(0xFF0F172A),
            error: Color(0xFFEF4444),
          ),
          fontFamily: 'monospace',
          useMaterial3: true,
        ),
        home: const DashboardScreen(),
      ),
    );
  }
}
