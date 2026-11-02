// Data models for QuantumShield Mobile Client

class SimulationConfig {
  final int numQubits;
  final bool enableEve;
  final double eveInterceptionProb;
  final bool enableNoise;
  final double noiseProbability;
  final double qberThreshold;
  final double sampleFraction;
  final int? randomSeed;

  SimulationConfig({
    this.numQubits = 500,
    this.enableEve = false,
    this.eveInterceptionProb = 1.0,
    this.enableNoise = false,
    this.noiseProbability = 0.02,
    this.qberThreshold = 11.0,
    this.sampleFraction = 0.30,
    this.randomSeed,
  });

  Map<String, dynamic> toJson() => {
    'num_qubits': numQubits,
    'enable_eve': enableEve,
    'eve_interception_prob': eveInterceptionProb,
    'enable_noise': enableNoise,
    'noise_probability': noiseProbability,
    'qber_threshold': qberThreshold,
    'sample_fraction': sampleFraction,
    if (randomSeed != null) 'random_seed': randomSeed,
  };

  factory SimulationConfig.fromJson(Map<String, dynamic> json) => SimulationConfig(
    numQubits: json['num_qubits'] ?? 500,
    enableEve: json['enable_eve'] ?? false,
    eveInterceptionProb: (json['eve_interception_prob'] as num?)?.toDouble() ?? 1.0,
    enableNoise: json['enable_noise'] ?? false,
    noiseProbability: (json['noise_probability'] as num?)?.toDouble() ?? 0.02,
    qberThreshold: (json['qber_threshold'] as num?)?.toDouble() ?? 11.0,
    sampleFraction: (json['sample_fraction'] as num?)?.toDouble() ?? 0.30,
    randomSeed: json['random_seed'],
  );
}

class SimulationMetrics {
  final int totalQubits;
  final int matchingBasesCount;
  final int siftedKeyLength;
  final int parameterSampleLength;
  final int candidateKeyLength;
  final int siftedErrors;
  final double measuredQber;
  final double sampleQber;
  final double ciLow;
  final double ciHigh;
  final double theoreticalQber;
  final String securityState;
  final String securityAssessment;
  final int eveInterceptedCount;
  final double eveInterceptionRate;
  final double executionTime;
  final double threshold;

  SimulationMetrics({
    required this.totalQubits,
    required this.matchingBasesCount,
    required this.siftedKeyLength,
    required this.parameterSampleLength,
    required this.candidateKeyLength,
    required this.siftedErrors,
    required this.measuredQber,
    required this.sampleQber,
    required this.ciLow,
    required this.ciHigh,
    required this.theoreticalQber,
    required this.securityState,
    required this.securityAssessment,
    required this.eveInterceptedCount,
    required this.eveInterceptionRate,
    required this.executionTime,
    required this.threshold,
  });

  factory SimulationMetrics.fromJson(Map<String, dynamic> json) => SimulationMetrics(
    totalQubits: json['total_qubits'] ?? 0,
    matchingBasesCount: json['matching_bases_count'] ?? 0,
    siftedKeyLength: json['sifted_key_length'] ?? 0,
    parameterSampleLength: json['parameter_sample_length'] ?? 0,
    candidateKeyLength: json['candidate_key_length'] ?? 0,
    siftedErrors: json['sifted_errors'] ?? 0,
    measuredQber: (json['measured_qber'] as num?)?.toDouble() ?? 0.0,
    sampleQber: (json['sample_qber'] as num?)?.toDouble() ?? 0.0,
    ciLow: (json['qber_confidence_interval_low'] as num?)?.toDouble() ?? 0.0,
    ciHigh: (json['qber_confidence_interval_high'] as num?)?.toDouble() ?? 0.0,
    theoreticalQber: (json['theoretical_expected_qber'] as num?)?.toDouble() ?? 0.0,
    securityState: json['security_state'] ?? 'INCONCLUSIVE',
    securityAssessment: json['security_assessment'] ?? '',
    eveInterceptedCount: json['eve_intercepted_count'] ?? 0,
    eveInterceptionRate: (json['eve_interception_rate'] as num?)?.toDouble() ?? 0.0,
    executionTime: (json['execution_time_seconds'] as num?)?.toDouble() ?? 0.0,
    threshold: (json['threshold'] as num?)?.toDouble() ?? 11.0,
  );
}

class KeyDisplay {
  final String aliceSiftedKey;
  final String bobSiftedKey;
  final String candidateKey;
  final int candidateKeyLength;
  final String? finalKeyHash;

  KeyDisplay({
    required this.aliceSiftedKey,
    required this.bobSiftedKey,
    required this.candidateKey,
    required this.candidateKeyLength,
    this.finalKeyHash,
  });

  factory KeyDisplay.fromJson(Map<String, dynamic> json) => KeyDisplay(
    aliceSiftedKey: json['alice_sifted_key'] ?? '',
    bobSiftedKey: json['bob_sifted_key'] ?? '',
    candidateKey: json['candidate_key'] ?? '',
    candidateKeyLength: json['candidate_key_length'] ?? 0,
    finalKeyHash: json['final_key_hash'],
  );
}

class QubitRecord {
  final int index;
  final int aliceBit;
  final String aliceBasis;
  final String aliceState;
  final bool eveIntercepted;
  final String? eveBasis;
  final int? eveMeasured;
  final String bobBasis;
  final int bobMeasured;
  final bool basisMatched;
  final bool? siftedMatch;

  QubitRecord({
    required this.index,
    required this.aliceBit,
    required this.aliceBasis,
    required this.aliceState,
    required this.eveIntercepted,
    this.eveBasis,
    this.eveMeasured,
    required this.bobBasis,
    required this.bobMeasured,
    required this.basisMatched,
    this.siftedMatch,
  });

  factory QubitRecord.fromJson(Map<String, dynamic> json) => QubitRecord(
    index: json['index'] ?? 0,
    aliceBit: json['alice_bit'] ?? 0,
    aliceBasis: json['alice_basis'] ?? '+',
    aliceState: json['alice_state'] ?? '|0⟩',
    eveIntercepted: json['eve_intercepted'] ?? false,
    eveBasis: json['eve_basis'],
    eveMeasured: json['eve_measured'],
    bobBasis: json['bob_basis'] ?? '+',
    bobMeasured: json['bob_measured'] ?? 0,
    basisMatched: json['basis_matched'] ?? false,
    siftedMatch: json['sifted_match'],
  );
}

class SimulationResponse {
  final String simulationId;
  final String status;
  final SimulationConfig config;
  final SimulationMetrics? metrics;
  final KeyDisplay? keys;
  final List<QubitRecord>? recordsSample;
  final String? errorMessage;

  SimulationResponse({
    required this.simulationId,
    required this.status,
    required this.config,
    this.metrics,
    this.keys,
    this.recordsSample,
    this.errorMessage,
  });

  factory SimulationResponse.fromJson(Map<String, dynamic> json) => SimulationResponse(
    simulationId: json['simulation_id'] ?? '',
    status: json['status'] ?? 'PENDING',
    config: SimulationConfig.fromJson(json['config'] ?? {}),
    metrics: json['metrics'] != null ? SimulationMetrics.fromJson(json['metrics']) : null,
    keys: json['keys'] != null ? KeyDisplay.fromJson(json['keys']) : null,
    recordsSample: json['records_sample'] != null
        ? (json['records_sample'] as List).map((r) => QubitRecord.fromJson(r)).toList()
        : null,
    errorMessage: json['error_message'],
  );
}
