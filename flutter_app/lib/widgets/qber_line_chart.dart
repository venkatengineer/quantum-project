import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class QberLineChart extends StatelessWidget {
  final List<double> qberPoints;
  final double threshold;

  const QberLineChart({
    super.key,
    required this.qberPoints,
    required this.threshold,
  });

  @override
  Widget build(BuildContext context) {
    if (qberPoints.isEmpty) {
      return Container(
        height: 180,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A).withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFF334155)),
        ),
        child: const Text(
          'Run a simulation to generate live QBER chart',
          style: TextStyle(color: Color(0xFF64748B), fontSize: 12),
        ),
      );
    }

    final spots = <FlSpot>[];
    for (int i = 0; i < qberPoints.length; i++) {
      spots.add(FlSpot(i.toDouble(), qberPoints[i]));
    }

    return Container(
      height: 200,
      padding: const EdgeInsets.only(top: 16, right: 16, left: 10, bottom: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: LineChart(
        LineChartData(
          minY: 0,
          maxY: 40,
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (value) => FlLine(
              color: const Color(0xFF1E293B),
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 32,
                getTitlesWidget: (val, meta) => Text(
                  '${val.toInt()}%',
                  style: const TextStyle(color: Color(0xFF64748B), fontSize: 10),
                ),
              ),
            ),
            bottomTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          extraLinesData: ExtraLinesData(
            horizontalLines: [
              HorizontalLine(
                y: threshold,
                color: const Color(0xFFF59E0B),
                strokeWidth: 1.5,
                dashArray: [5, 5],
                label: HorizontalLineLabel(
                  show: true,
                  alignment: Alignment.topRight,
                  labelResolver: (line) => 'Threshold (${threshold.toInt()}%)',
                  style: const TextStyle(color: Color(0xFFF59E0B), fontSize: 10),
                ),
              ),
            ],
          ),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: const Color(0xFF38BDF8),
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                getDotPainter: (spot, percent, barData, index) {
                  final isAbove = spot.y > threshold;
                  return FlDotCirclePainter(
                    radius: 4,
                    color: isAbove ? const Color(0xFFEF4444) : const Color(0xFF10B981),
                    strokeWidth: 1.5,
                    strokeColor: Colors.black,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: true,
                color: const Color(0xFF38BDF8).withValues(alpha: 0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
