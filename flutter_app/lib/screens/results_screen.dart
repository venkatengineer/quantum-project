import 'package:flutter/material.dart';
import '../models/simulation_models.dart';

class ResultsScreen extends StatefulWidget {
  final SimulationResponse simulation;

  const ResultsScreen({super.key, required this.simulation});

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  bool _revealKeys = false;

  String _formatKey(String key) {
    if (key.isEmpty) return '(Empty)';
    if (key.startsWith('DISCARDED')) return key;
    if (_revealKeys) return key;
    return '•' * (key.length > 64 ? 64 : key.length);
  }

  @override
  Widget build(BuildContext context) {
    final keys = widget.simulation.keys;
    final records = widget.simulation.recordsSample ?? [];

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('EXPERIMENT RESULTS & KEYS', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Disclaimer
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF475569)),
              ),
              child: const Text(
                '⚠️ Educational Simulator Notice: Simulated quantum demonstration data. Production BB84 requires authenticated channels, error reconciliation, and privacy amplification.',
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
              ),
            ),
            const SizedBox(height: 16),

            // Key Display Header & Toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'CRYPTOGRAPHIC KEYS',
                  style: TextStyle(color: Color(0xFFA78BFA), fontWeight: FontWeight.bold, fontSize: 12),
                ),
                Row(
                  children: [
                    const Text('Reveal Bits:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    Switch(
                      value: _revealKeys,
                      activeTrackColor: const Color(0xFF38BDF8),
                      onChanged: (v) => setState(() => _revealKeys = v),
                    ),
                  ],
                ),
              ],
            ),

            if (keys != null) ...[
              _buildKeyBox("Alice's Sifted Key", _formatKey(keys.aliceSiftedKey), const Color(0xFF38BDF8)),
              const SizedBox(height: 10),
              _buildKeyBox("Bob's Sifted Key", _formatKey(keys.bobSiftedKey), const Color(0xFF38BDF8)),
              const SizedBox(height: 10),
              _buildKeyBox(
                "Candidate Secret Key",
                _formatKey(keys.candidateKey),
                keys.candidateKey.startsWith('DISCARDED') ? const Color(0xFFEF4444) : const Color(0xFF34D399),
              ),
              if (keys.finalKeyHash != null) ...[
                const SizedBox(height: 10),
                Text(
                  'SHA-256 Fingerprint: ${keys.finalKeyHash}',
                  style: const TextStyle(color: Color(0xFF64748B), fontSize: 10, fontFamily: 'monospace'),
                ),
              ],
            ],

            const SizedBox(height: 24),

            // Qubit Transmission Inspector
            Text(
              'QUBIT TRANSMISSION RECORDS (${records.length} shown)',
              style: const TextStyle(color: Color(0xFFA78BFA), fontWeight: FontWeight.bold, fontSize: 12),
            ),
            const SizedBox(height: 10),

            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: records.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (context, i) {
                final r = records[i];
                final isMatch = r.basisMatched;
                final isError = isMatch && (r.siftedMatch == false);

                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F172A).withValues(alpha: 0.6),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: r.eveIntercepted ? const Color(0xFFEF4444).withValues(alpha: 0.5) : const Color(0xFF334155),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Qubit #${r.index}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                          const SizedBox(height: 4),
                          Text(
                            'Alice: ${r.aliceBit} in ${r.aliceBasis} (${r.aliceState}) → Bob: ${r.bobMeasured} in ${r.bobBasis}',
                            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          if (r.eveIntercepted)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEF4444).withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text('EVE INTERCEPTED', style: TextStyle(color: Color(0xFFF87171), fontSize: 9, fontWeight: FontWeight.bold)),
                            ),
                          const SizedBox(height: 4),
                          Text(
                            isMatch ? (isError ? '❌ BIT ERROR' : '✅ SIFT MATCH') : 'DISCARDED',
                            style: TextStyle(
                              color: isMatch ? (isError ? const Color(0xFFEF4444) : const Color(0xFF10B981)) : const Color(0xFF64748B),
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeyBox(String label, String value, Color textColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
        const SizedBox(height: 4),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color(0xFF030712),
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: const Color(0xFF1F2937)),
          ),
          child: Text(
            value,
            style: TextStyle(color: textColor, fontFamily: 'monospace', fontSize: 12),
          ),
        ),
      ],
    );
  }
}
