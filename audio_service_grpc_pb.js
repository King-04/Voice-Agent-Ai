// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var audio_service_pb = require('./audio_service_pb.js');

function serialize_wazobia_AudioRequest(arg) {
  if (!(arg instanceof audio_service_pb.AudioRequest)) {
    throw new Error('Expected argument of type wazobia.AudioRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_wazobia_AudioRequest(buffer_arg) {
  return audio_service_pb.AudioRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_wazobia_AudioResponse(arg) {
  if (!(arg instanceof audio_service_pb.AudioResponse)) {
    throw new Error('Expected argument of type wazobia.AudioResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_wazobia_AudioResponse(buffer_arg) {
  return audio_service_pb.AudioResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_wazobia_HealthRequest(arg) {
  if (!(arg instanceof audio_service_pb.HealthRequest)) {
    throw new Error('Expected argument of type wazobia.HealthRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_wazobia_HealthRequest(buffer_arg) {
  return audio_service_pb.HealthRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_wazobia_HealthResponse(arg) {
  if (!(arg instanceof audio_service_pb.HealthResponse)) {
    throw new Error('Expected argument of type wazobia.HealthResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_wazobia_HealthResponse(buffer_arg) {
  return audio_service_pb.HealthResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


// Wazobia Audio Service
var AudioServiceService = exports.AudioServiceService = {
  // Process audio file and get response
processAudio: {
    path: '/wazobia.AudioService/ProcessAudio',
    requestStream: false,
    responseStream: false,
    requestType: audio_service_pb.AudioRequest,
    responseType: audio_service_pb.AudioResponse,
    requestSerialize: serialize_wazobia_AudioRequest,
    requestDeserialize: deserialize_wazobia_AudioRequest,
    responseSerialize: serialize_wazobia_AudioResponse,
    responseDeserialize: deserialize_wazobia_AudioResponse,
  },
  // Check server health
healthCheck: {
    path: '/wazobia.AudioService/HealthCheck',
    requestStream: false,
    responseStream: false,
    requestType: audio_service_pb.HealthRequest,
    responseType: audio_service_pb.HealthResponse,
    requestSerialize: serialize_wazobia_HealthRequest,
    requestDeserialize: deserialize_wazobia_HealthRequest,
    responseSerialize: serialize_wazobia_HealthResponse,
    responseDeserialize: deserialize_wazobia_HealthResponse,
  },
};

exports.AudioServiceClient = grpc.makeGenericClientConstructor(AudioServiceService, 'AudioService');
