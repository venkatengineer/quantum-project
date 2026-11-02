import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/simulation_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final ApiService _api = ApiService();
  final TextEditingController _urlController = TextEditingController();
  bool _testing = false;
  String? _testResult;
  bool _testSuccess = false;

  @override
  void initState() {
    super.initState();
    _loadUrl();
  }

  Future<void> _loadUrl() async {
    final url = await _api.getBaseUrl();
    _urlController.text = url;
  }

  Future<void> _testConnection() async {
    setState(() {
      _testing = true;
      _testResult = null;
    });

    final success = await _api.checkHealth();
    if (mounted) {
      setState(() {
        _testing = false;
        _testSuccess = success;
        _testResult = success
            ? 'Connected successfully to QuantumShield FastAPI Backend!'
            : 'Could not connect. Verify server is running on the specified host & port.';
      });
      context.read<SimulationProvider>().checkHealth();
    }
  }

  Future<void> _saveUrl() async {
    await _api.setBaseUrl(_urlController.text);
    await _testConnection();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Backend URL saved.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('BACKEND SETTINGS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'FASTAPI BACKEND URL',
              style: TextStyle(color: Color(0xFFA78BFA), fontWeight: FontWeight.bold, fontSize: 12),
            ),
            const SizedBox(height: 8),

            TextField(
              controller: _urlController,
              style: const TextStyle(color: Colors.white, fontSize: 13),
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF0F172A),
                hintText: 'http://10.0.2.2:8000',
                hintStyle: const TextStyle(color: Color(0xFF475569)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
            const SizedBox(height: 12),

            // Presets
            const Text('Quick Presets:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
            const SizedBox(height: 6),
            Wrap(
              spacing: 8,
              children: [
                ActionChip(
                  label: const Text('Android Emulator (10.0.2.2)', style: TextStyle(fontSize: 11)),
                  backgroundColor: const Color(0xFF1E293B),
                  onPressed: () {
                    _urlController.text = 'http://10.0.2.2:8000';
                  },
                ),
                ActionChip(
                  label: const Text('Localhost (127.0.0.1)', style: TextStyle(fontSize: 11)),
                  backgroundColor: const Color(0xFF1E293B),
                  onPressed: () {
                    _urlController.text = 'http://127.0.0.1:8000';
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF7C3AED),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    onPressed: _saveUrl,
                    child: const Text('SAVE & CONNECT'),
                  ),
                ),
                const SizedBox(width: 10),
                OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF38BDF8),
                    side: const BorderSide(color: Color(0xFF38BDF8)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  onPressed: _testing ? null : _testConnection,
                  child: _testing
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('TEST'),
                ),
              ],
            ),

            if (_testResult != null) ...[
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _testSuccess ? const Color(0xFF10B981).withValues(alpha: 0.15) : const Color(0xFFEF4444).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: _testSuccess ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                  ),
                ),
                child: Text(
                  _testResult!,
                  style: TextStyle(
                    color: _testSuccess ? const Color(0xFF34D399) : const Color(0xFFF87171),
                    fontSize: 12,
                  ),
                ),
              ),
            ],

            const SizedBox(height: 28),

            const Text(
              'NETWORK CONFIGURATION GUIDE',
              style: TextStyle(color: Color(0xFFA78BFA), fontWeight: FontWeight.bold, fontSize: 12),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A).withValues(alpha: 0.7),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: const Text(
                '• Android Studio Emulator: Use http://10.0.2.2:8000 to reach host machine localhost.\n'
                '• iOS Simulator / Desktop: Use http://127.0.0.1:8000.\n'
                '• Physical Mobile Device: Ensure phone and PC are on the same Wi-Fi, and set URL to your PC LAN IP (e.g., http://192.168.1.100:8000).',
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12, height: 1.5),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
