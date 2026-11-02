import 'package:flutter/foundation.dart';
import '../models/simulation_models.dart';
import '../services/api_service.dart';

class SimulationProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  SimulationResponse? _currentSimulation;
  bool _isLoading = false;
  bool _isBackendHealthy = false;
  String? _errorMessage;
  final List<double> _qberHistory = [];

  SimulationConfig _config = SimulationConfig(
    numQubits: 500,
    enableEve: false,
    eveInterceptionProb: 1.0,
    qberThreshold: 11.0,
    sampleFraction: 0.30,
  );

  SimulationResponse? get currentSimulation => _currentSimulation;
  bool get isLoading => _isLoading;
  bool get isBackendHealthy => _isBackendHealthy;
  String? get errorMessage => _errorMessage;
  List<double> get qberHistory => List.unmodifiable(_qberHistory);
  SimulationConfig get config => _config;

  Future<void> init() async {
    await checkHealth();
  }

  Future<void> checkHealth() async {
    _isBackendHealthy = await _api.checkHealth();
    notifyListeners();
  }

  void updateConfig({
    int? numQubits,
    bool? enableEve,
    double? eveInterceptionProb,
    bool? enableNoise,
    double? noiseProbability,
    double? qberThreshold,
    double? sampleFraction,
  }) {
    _config = SimulationConfig(
      numQubits: numQubits ?? _config.numQubits,
      enableEve: enableEve ?? _config.enableEve,
      eveInterceptionProb: eveInterceptionProb ?? _config.eveInterceptionProb,
      enableNoise: enableNoise ?? _config.enableNoise,
      noiseProbability: noiseProbability ?? _config.noiseProbability,
      qberThreshold: qberThreshold ?? _config.qberThreshold,
      sampleFraction: sampleFraction ?? _config.sampleFraction,
    );
    notifyListeners();
  }

  Future<void> runSimulation() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _api.startSimulation(_config);
      _currentSimulation = res;
      _isBackendHealthy = true;

      if (res.metrics != null) {
        _qberHistory.add(res.metrics!.measuredQber);
      }
    } catch (e) {
      _errorMessage = e.toString();
      _isBackendHealthy = false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void reset() {
    _currentSimulation = null;
    _qberHistory.clear();
    _errorMessage = null;
    notifyListeners();
  }
}
