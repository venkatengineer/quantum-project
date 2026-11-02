import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/simulation_provider.dart';
import '../widgets/metric_card.dart';
import '../widgets/security_badge.dart';
import '../widgets/attack_alert_banner.dart';
import '../widgets/qber_line_chart.dart';
import 'results_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<SimulationProvider>();
    final sim = provider.currentSimulation;
    final metrics = sim?.metrics;

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.blur_on, color: Color(0xFFA78BFA)),
            const SizedBox(width: 8),
            const Text(
              'QUANTUMSHIELD',
              style: TextStyle(
                fontWeight: FontWeight.w800,
                letterSpacing: 1.2,
                fontSize: 16,
                color: Colors.white,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: provider.isBackendHealthy
                  ? const Color(0xFF10B981).withValues(alpha: 0.15)
                  : const Color(0xFFEF4444).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: provider.isBackendHealthy ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                width: 0.8,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircleAvatar(
                  radius: 3.5,
                  backgroundColor: provider.isBackendHealthy ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                ),
                const SizedBox(width: 5),
                Text(
                  provider.isBackendHealthy ? 'API READY' : 'OFFLINE',
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                    color: provider.isBackendHealthy ? const Color(0xFF34D399) : const Color(0xFFF87171),
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: Color(0xFF94A3B8)),
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen()));
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Attack Banner
            if (metrics != null)
              AttackAlertBanner(
                message: metrics.securityAssessment,
                isSuspicious: metrics.securityState == 'SUSPICIOUS',
              ),

            const SizedBox(height: 12),

            // Metrics Grid
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: 1.5,
              children: [
                MetricCard(
                  label: 'Transmitted Qubits',
                  value: metrics != null ? '${metrics.totalQubits}' : '${provider.config.numQubits}',
                  subtitle: 'Alice → Bob channel',
                ),
                MetricCard(
                  label: 'Sifted Key Length',
                  value: metrics != null ? '${metrics.siftedKeyLength}' : '-',
                  subtitle: metrics != null
                      ? 'Yield: ${(metrics.siftedKeyLength / metrics.totalQubits * 100).toStringAsFixed(1)}%'
                      : 'Matching bases',
                  valueColor: const Color(0xFF38BDF8),
                ),
                MetricCard(
                  label: 'Measured QBER',
                  value: metrics != null ? '${metrics.measuredQber.toStringAsFixed(1)}%' : '-',
                  subtitle: 'Threshold: ${provider.config.qberThreshold.toStringAsFixed(0)}%',
                  valueColor: (metrics != null && metrics.measuredQber > provider.config.qberThreshold)
                      ? const Color(0xFFEF4444)
                      : const Color(0xFF10B981),
                ),
                MetricCard(
                  label: 'Eve Intercept Rate',
                  value: metrics != null ? '${metrics.eveInterceptionRate.toStringAsFixed(0)}%' : (provider.config.enableEve ? 'Active' : '0%'),
                  subtitle: metrics != null ? '${metrics.eveInterceptedCount} tapped' : 'No attack',
                  valueColor: provider.config.enableEve ? const Color(0xFFF87171) : const Color(0xFF64748B),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Live QBER Chart Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'REAL-TIME QBER TRACKING',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                    color: Color(0xFF94A3B8),
                  ),
                ),
                if (metrics != null) SecurityBadge(state: metrics.securityState),
              ],
            ),
            const SizedBox(height: 8),

            // Chart
            QberLineChart(
              qberPoints: provider.qberHistory,
              threshold: provider.config.qberThreshold,
            ),

            const SizedBox(height: 24),

            // Controls Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A).withValues(alpha: 0.7),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'QUANTUM EXPERIMENT CONTROLS',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1,
                      color: Color(0xFFA78BFA),
                    ),
                  ),
                  const SizedBox(height: 14),

                  // Qubit count
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Alice Qubits:', style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 13)),
                      Text('${provider.config.numQubits}', style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
                    ],
                  ),
                  Slider(
                    value: provider.config.numQubits.toDouble(),
                    min: 100,
                    max: 2000,
                    divisions: 19,
                    activeColor: const Color(0xFF38BDF8),
                    inactiveColor: const Color(0xFF1E293B),
                    onChanged: (v) => provider.updateConfig(numQubits: v.toInt()),
                  ),

                  // Eve Toggle
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Eve Intercept-Resend Attack', style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 13, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 2),
                          Text(
                            provider.config.enableEve ? 'Active quantum eavesdropper in channel' : 'Untapped secure channel',
                            style: const TextStyle(color: Color(0xFF64748B), fontSize: 11),
                          ),
                        ],
                      ),
                      Switch(
                        value: provider.config.enableEve,
                        thumbColor: WidgetStateProperty.resolveWith((states) => states.contains(WidgetState.selected) ? const Color(0xFFEF4444) : Colors.grey),
                        trackColor: WidgetStateProperty.resolveWith((states) => states.contains(WidgetState.selected) ? const Color(0xFFEF4444).withAlpha(80) : Colors.black26),
                        onChanged: (v) => provider.updateConfig(enableEve: v),
                      ),
                    ],
                  ),

                  // Eve Interception Prob Slider
                  if (provider.config.enableEve) ...[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Interception Probability:', style: TextStyle(color: Color(0xFFE2E8F0), fontSize: 12)),
                        Text('${(provider.config.eveInterceptionProb * 100).toStringAsFixed(0)}%', style: const TextStyle(color: Color(0xFFF87171), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    Slider(
                      value: provider.config.eveInterceptionProb,
                      min: 0.1,
                      max: 1.0,
                      divisions: 9,
                      activeColor: const Color(0xFFEF4444),
                      inactiveColor: const Color(0xFF1E293B),
                      onChanged: (v) => provider.updateConfig(eveInterceptionProb: v),
                    ),
                  ],

                  const SizedBox(height: 12),

                  // Action Buttons
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF7C3AED),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: provider.isLoading ? null : () => provider.runSimulation(),
                          icon: provider.isLoading
                              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Icon(Icons.play_arrow),
                          label: Text(provider.isLoading ? 'SIMULATING...' : 'LAUNCH SIMULATION'),
                        ),
                      ),
                      const SizedBox(width: 10),
                      IconButton(
                        style: IconButton.styleFrom(
                          backgroundColor: const Color(0xFF1E293B),
                          padding: const EdgeInsets.all(12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                        icon: const Icon(Icons.refresh, color: Color(0xFF94A3B8)),
                        onPressed: () => provider.reset(),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Detailed Results Button
            if (sim != null)
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF38BDF8),
                    side: const BorderSide(color: Color(0xFF38BDF8)),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  icon: const Icon(Icons.list_alt),
                  label: const Text('VIEW DETAILED KEY & QUBIT RECORDS'),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => ResultsScreen(simulation: sim)),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
