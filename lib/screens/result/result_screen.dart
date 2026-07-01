import 'package:dr_retino/screens/home/home_screen.dart';
import 'package:flutter/material.dart';
import 'dart:io';

class ResultScreen extends StatelessWidget {
  final File imageFile;
  final Map<String, dynamic> result;

  const ResultScreen({
    super.key,
    required this.imageFile,
    required this.result,
  });

  Color _getGradeColor(int grade) {
    switch (grade) {
      case 0:
        return const Color(0xFF2E7D32);
      case 1:
        return const Color(0xFFF9A825);
      case 2:
        return const Color(0xFFEF6C00);
      case 3:
        return const Color(0xFFB71C1C);
      case 4:
        return const Color(0xFF880E4F);
      default:
        return Colors.grey;
    }
  }

  IconData _getGradeIcon(int grade) {
    switch (grade) {
      case 0:
        return Icons.check_circle;
      case 1:
        return Icons.info;
      case 2:
        return Icons.warning;
      case 3:
        return Icons.error;
      case 4:
        return Icons.dangerous;
      default:
        return Icons.help;
    }
  }

  @override
  Widget build(BuildContext context) {
    final int grade = result['grade'];
    final String label = result['label'];
    final double confidence = result['confidence'];
    final String recommendation = result['recommendation'];
    final Color gradeColor = _getGradeColor(grade);

    return Scaffold(
      backgroundColor: const Color(0xFFF5F9FF),
      appBar: AppBar(
        title: const Text('Analysis Result'),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const SizedBox(height: 10),
            // Result card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: gradeColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: gradeColor.withValues(alpha: 0.3)),
              ),
              child: Column(
                children: [
                  Icon(_getGradeIcon(grade), color: gradeColor, size: 60),
                  const SizedBox(height: 12),
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: gradeColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                    decoration: BoxDecoration(
                      color: gradeColor,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Grade $grade • ${confidence.toInt()}% confidence',
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            // Image
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.file(
                imageFile,
                height: 200,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
            ),
            const SizedBox(height: 20),
            // Recommendation
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withValues(alpha: 0.1),
                    blurRadius: 10,
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.medical_services, color: Color(0xFF1565C0)),
                      SizedBox(width: 8),
                      Text(
                        'Recommendation',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1565C0),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    recommendation,
                    style: const TextStyle(
                        fontSize: 15, color: Colors.black87, height: 1.5),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            // Disclaimer
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.orange),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'This result is for screening purposes only. Always consult a qualified medical professional for diagnosis.',
                      style: TextStyle(fontSize: 12, color: Colors.orange),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // Scan Again button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () => Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const HomeScreen()),
                  (route) => false,
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1565C0),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  'Scan Another Image',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
