import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/simulation_models.dart';

class ApiService {
  static const String _defaultUrl = 'http://10.0.2.2:8000';
  static const String _prefsKey = 'backend_base_url';

  Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_prefsKey) ?? _defaultUrl;
  }

  Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKey, url.trim().replaceAll(RegExp(r'/+$'), ''));
  }

  Future<bool> checkHealth() async {
    try {
      final baseUrl = await getBaseUrl();
      final res = await http.get(Uri.parse('$baseUrl/api/health')).timeout(const Duration(seconds: 3));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<SimulationResponse> startSimulation(SimulationConfig config) async {
    final baseUrl = await getBaseUrl();
    final res = await http.post(
      Uri.parse('$baseUrl/api/simulation/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(config.toJson()),
    ).timeout(const Duration(seconds: 30));

    if (res.statusCode == 200) {
      return SimulationResponse.fromJson(jsonDecode(res.body));
    } else {
      throw Exception('Failed to start simulation: ${res.statusCode} ${res.body}');
    }
  }

  Future<SimulationResponse> getSimulation(String id) async {
    final baseUrl = await getBaseUrl();
    final res = await http.get(Uri.parse('$baseUrl/api/simulation/$id'));
    if (res.statusCode == 200) {
      return SimulationResponse.fromJson(jsonDecode(res.body));
    } else {
      throw Exception('Failed to fetch simulation: ${res.statusCode}');
    }
  }

  Future<void> stopSimulation(String id) async {
    final baseUrl = await getBaseUrl();
    await http.post(Uri.parse('$baseUrl/api/simulation/$id/stop'));
  }

  Future<void> resetSimulation(String id) async {
    final baseUrl = await getBaseUrl();
    await http.post(Uri.parse('$baseUrl/api/simulation/$id/reset'));
  }

  Future<List<dynamic>> getHistory(String id) async {
    final baseUrl = await getBaseUrl();
    final res = await http.get(Uri.parse('$baseUrl/api/simulation/$id/history'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return [];
  }
}
