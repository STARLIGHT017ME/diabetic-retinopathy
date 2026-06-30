import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;

class Classifier {
  Interpreter? _interpreter;

  static const int INPUT_SIZE = 224;

  static const List<String> LABELS = [
    'No DR',
    'Mild DR',
    'Moderate DR',
    'Severe DR',
    'Proliferative DR',
  ];

  static const List<String> RECOMMENDATIONS = [
    'Your retina appears healthy. Continue regular check-ups.',
    'Mild changes detected. Please consult an eye doctor soon.',
    'Moderate DR detected. Please see an eye doctor as soon as possible.',
    'Severe DR detected. Urgent medical attention recommended.',
    'Proliferative DR detected. Please seek immediate medical attention.',
  ];

  Future<void> loadModel() async {
    try {
      _interpreter = await Interpreter.fromAsset('assets/dr_model.tflite');
      print('✅ Model loaded successfully');
    } catch (e) {
      print('❌ Error loading model: $e');
    }
  }

  Map<String, dynamic> predict(img.Image image) {
    // Resize image to 224x224
    img.Image resized = img.copyResize(
      image,
      width: INPUT_SIZE,
      height: INPUT_SIZE,
    );

    // Convert to float array [1, 224, 224, 3]
    var input = List.generate(
      1,
      (_) => List.generate(
        INPUT_SIZE,
        (y) => List.generate(
          INPUT_SIZE,
          (x) {
            final pixel = resized.getPixel(x, y);
            return [
              pixel.r / 255.0,
              pixel.g / 255.0,
              pixel.b / 255.0,
            ];
          },
        ),
      ),
    );

    // Output shape [1, 5]
    var output = List.generate(1, (_) => List.filled(5, 0.0));

    // Run inference
    _interpreter!.run(input, output);

    // Get result
    List<double> scores = List<double>.from(output[0]);
    int maxIndex = scores.indexOf(scores.reduce((a, b) => a > b ? a : b));
    double confidence = (scores[maxIndex] * 100).roundToDouble();

    return {
      'grade': maxIndex,
      'label': LABELS[maxIndex],
      'confidence': confidence,
      'recommendation': RECOMMENDATIONS[maxIndex],
      'scores': scores,
    };
  }

  void dispose() {
    _interpreter?.close();
  }
}
