import 'package:flutter/material.dart';

class SecurityBadge extends StatelessWidget {
  final String state;

  const SecurityBadge({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color border;
    Color text;
    String label;
    IconData icon;

    switch (state) {
      case 'SECURE':
        bg = const Color(0xFF10B981).withValues(alpha: 0.15);
        border = const Color(0xFF10B981);
        text = const Color(0xFF34D399);
        label = 'SECURE';
        icon = Icons.verified_user;
        break;
      case 'SUSPICIOUS':
        bg = const Color(0xFFEF4444).withValues(alpha: 0.15);
        border = const Color(0xFFEF4444);
        text = const Color(0xFFF87171);
        label = 'ATTACK ALERT';
        icon = Icons.warning_rounded;
        break;
      default:
        bg = const Color(0xFFF59E0B).withValues(alpha: 0.15);
        border = const Color(0xFFF59E0B);
        text = const Color(0xFFFBBF24);
        label = 'INCONCLUSIVE';
        icon = Icons.help_outline;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: border.withValues(alpha: 0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: text, size: 14),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(color: text, fontWeight: FontWeight.bold, fontSize: 11),
          ),
        ],
      ),
    );
  }
}
