import React, { useState } from "react";
import FileUploader from "@commonComponents/FileUploader";
import StyledButton from "@integratedComponents/StyledButton";
import { AudioServiceService } from "./audio_service_pb_service";
import { AudioRequest } from "./audio_service_pb";
import "./style.css";

const AUDIO_TYPE = "mp3";
const AUDIO_CONTENT_TYPE = `data:audio/${AUDIO_TYPE}`;

const WazobiaAudioService = ({ serviceClient, isComplete }) => {
    const [audioB64Src, setAudioB64Src] = useState();

    const createAudioBase64Url = (data) => {
        return `${AUDIO_CONTENT_TYPE};base64,` + data;
    }

    const downloadAudio = (src) => {
        const link = document.createElement("a");
        link.href = src;
        link.download = `wazobia_response_${Date.now()}.wav`;
        link.click();
    }

    const ServiceInput = () => {
        const [audio, setAudio] = useState();
        const [audioSrc, setAudioSrc] = useState();
        const [audioData, setAudioData] = useState();
        const [isAudioUploaded, setIsAudioUploaded] = useState(false);

        const handleAudioUpload = (audioFiles) => {
            const audioFile = audioFiles[0];

            // Accept mp3, wav, m4a files
            const validFormats = ['mp3', 'wav', 'm4a'];
            const fileExtension = audioFile.name.split('.').pop().toLowerCase();
            
            if (!validFormats.includes(fileExtension)) {
                alert(`Please upload a valid audio file (${validFormats.join(', ')})`);
                return;
            }

            setAudio(audioFile);

            const fileReader = new FileReader();

            fileReader.onload = (event) => {
                const { result } = event.target;
                const data = new Uint8Array(result);
                const blob = new Blob([data], { type: `audio/${fileExtension}` });
                const audioUrl = URL.createObjectURL(blob);

                setAudioSrc(audioUrl);
                setAudioData(data);
            }

            fileReader.readAsArrayBuffer(audioFile);
        }

        const isAllowedToRun = () => {
            return !!audioData && isAudioUploaded;
        };

        const onActionEnd = (response) => {
            const { message, status, statusMessage } = response;

            if (status !== 0) {
                throw new Error(statusMessage);
            }

            // Check if service returned success
            if (!message.getSuccess()) {
                const errorMsg = message.getErrorMessage() || "Unknown error occurred";
                throw new Error(errorMsg);
            }

            // Get response audio data as base64
            const responseAudioB64 = message.getAudioData_asB64();
            const audioB64SourceUrl = `data:audio/wav;base64,${responseAudioB64}`;

            setAudioB64Src(audioB64SourceUrl);
        };

        const submitAction = () => {
            const methodDescriptor = AudioServiceService.ProcessAudio;
            const request = new methodDescriptor.requestType();

            // Set request fields
            request.setAudioData(audioData);
            request.setFilename(audio.name);
            
            // Extract file format
            const fileFormat = audio.name.split('.').pop().toLowerCase();
            request.setFormat(fileFormat);

            const props = {
                request,
                preventCloseServiceOnEnd: false,
                onEnd: onActionEnd,
            };

            serviceClient.unary(methodDescriptor, props);
        };

        return (
            <div className={"content-box"}>
                <h4>{"Wazobia Voice Agent - Upload Audio"}</h4>
                <p className={"service-description"}>
                    Upload an audio file with your question in any language (English, Yoruba, Hausa, Pidgin, Igbo). 
                    The agent will respond with an audio answer.
                </p>
                <div className={"content-box"}>
                    <FileUploader
                        type={"file"}
                        uploadedFiles={audio}
                        handleFileUpload={handleAudioUpload}
                        setValidationStatus={setIsAudioUploaded}
                        fileAccept={".mp3,.wav,.m4a"}
                    />
                    {isAudioUploaded && audioSrc && (
                        <div className={"audio-container"}>
                            <p className={"audio-label"}>Preview your uploaded audio:</p>
                            <audio src={audioSrc} controls style={{ width: "100%" }} />
                        </div>
                    )}
                </div>
                <div className={"content-box"}>
                    <StyledButton
                        btnText={"Get Response"}
                        variant={"contained"}
                        onClick={submitAction}
                        disabled={!isAllowedToRun()}
                    />
                </div>
            </div>
        );
    };

    const ServiceOutput = () => {
        if (!audioB64Src) {
            return (
                <div className={"content-box"}>
                    <h4>{"Something went wrong..."}</h4>
                    <p>No response received from the agent. Please try again.</p>
                </div>
            );
        }

        return (
            <div className={"content-box"}>
                <h4>{"Wazobia Agent Response"}</h4>
                <p className={"service-description"}>
                    Listen to the agent's response below:
                </p>
                <div className={"content-box"}>
                    <div className={"audio-container"}>
                        <audio src={audioB64Src} controls autoPlay style={{ width: "100%" }} />
                    </div>
                    <div className={"button-group"}>
                        <StyledButton 
                            btnText={"Download Response"}
                            variant={"outlined"}
                            disabled={!audioB64Src}
                            onClick={() => downloadAudio(audioB64Src)}
                        />
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className={"service-container"}>
            <div className={"service-header"}>
                <h2>🎤 Wazobia Multilingual Voice Agent</h2>
            </div>
            {!isComplete ? <ServiceInput /> : <ServiceOutput />}
        </div>
    );
};

export default WazobiaAudioService;
