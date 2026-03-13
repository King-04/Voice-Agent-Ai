// package: wazobia
// file: audio_service.proto

var audio_service_pb = require("./audio_service_pb");
var grpc = require("@improbable-eng/grpc-web").grpc;

var AudioService = (function () {
  function AudioService() {}
  AudioService.serviceName = "wazobia.AudioService";
  return AudioService;
}());

AudioService.ProcessAudio = {
  methodName: "ProcessAudio",
  service: AudioService,
  requestStream: false,
  responseStream: false,
  requestType: audio_service_pb.AudioRequest,
  responseType: audio_service_pb.AudioResponse
};

AudioService.HealthCheck = {
  methodName: "HealthCheck",
  service: AudioService,
  requestStream: false,
  responseStream: false,
  requestType: audio_service_pb.HealthRequest,
  responseType: audio_service_pb.HealthResponse
};

exports.AudioService = AudioService;
exports.AudioServiceService = AudioService; // Alias for compatibility

function AudioServiceClient(serviceHost, options) {
  this.serviceHost = serviceHost;
  this.options = options || {};
}

AudioServiceClient.prototype.processAudio = function processAudio(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AudioService.ProcessAudio, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

AudioServiceClient.prototype.healthCheck = function healthCheck(requestMessage, metadata, callback) {
  if (arguments.length === 2) {
    callback = arguments[1];
  }
  var client = grpc.unary(AudioService.HealthCheck, {
    request: requestMessage,
    host: this.serviceHost,
    metadata: metadata,
    transport: this.options.transport,
    debug: this.options.debug,
    onEnd: function (response) {
      if (callback) {
        if (response.status !== grpc.Code.OK) {
          var err = new Error(response.statusMessage);
          err.code = response.status;
          err.metadata = response.trailers;
          callback(err, null);
        } else {
          callback(null, response.message);
        }
      }
    }
  });
  return {
    cancel: function () {
      callback = null;
      client.close();
    }
  };
};

exports.AudioServiceClient = AudioServiceClient;
