/**
 * @file audio_endpoint.cpp
 * @brief Implementation of Windows WASAPI volume control
 */

#include "audio_endpoint.h"

#ifdef _WIN32

#include <stdexcept>
#include <string>

namespace jarvis {

// Helper function to convert HRESULT to string
static std::string HResultToString(HRESULT hr) {
    _com_error err(hr);
    LPCTSTR errMsg = err.ErrorMessage();
    #ifdef UNICODE
    // Convert wide string to narrow string
    int size = WideCharToMultiByte(CP_UTF8, 0, errMsg, -1, nullptr, 0, nullptr, nullptr);
    std::string result(size - 1, '\0');
    WideCharToMultiByte(CP_UTF8, 0, errMsg, -1, &result[0], size, nullptr, nullptr);
    return result;
    #else
    return std::string(errMsg);
    #endif
}

AudioEndpoint::AudioEndpoint() {
    initialize();
}

AudioEndpoint::AudioEndpoint(AudioEndpoint&& other) noexcept
    : deviceEnumerator_(other.deviceEnumerator_),
      device_(other.device_),
      endpointVolume_(other.endpointVolume_),
      comInitialized_(other.comInitialized_)
{
    other.deviceEnumerator_ = nullptr;
    other.device_ = nullptr;
    other.endpointVolume_ = nullptr;
    other.comInitialized_ = false;
}

AudioEndpoint& AudioEndpoint::operator=(AudioEndpoint&& other) noexcept {
    if (this != &other) {
        cleanup();
        
        deviceEnumerator_ = other.deviceEnumerator_;
        device_ = other.device_;
        endpointVolume_ = other.endpointVolume_;
        comInitialized_ = other.comInitialized_;
        
        other.deviceEnumerator_ = nullptr;
        other.device_ = nullptr;
        other.endpointVolume_ = nullptr;
        other.comInitialized_ = false;
    }
    return *this;
}

AudioEndpoint::~AudioEndpoint() {
    cleanup();
}

void AudioEndpoint::initialize() {
    HRESULT hr;
    
    // Initialize COM
    hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) {
        throw std::runtime_error("Failed to initialize COM: " + HResultToString(hr));
    }
    comInitialized_ = true;
    
    // Create device enumerator
    hr = CoCreateInstance(
        __uuidof(MMDeviceEnumerator),
        nullptr,
        CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator),
        reinterpret_cast<void**>(&deviceEnumerator_)
    );
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to create device enumerator: " + HResultToString(hr));
    }
    
    // Get default audio endpoint
    hr = deviceEnumerator_->GetDefaultAudioEndpoint(
        eRender,  // Playback devices
        eConsole, // Console role
        &device_
    );
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to get default audio endpoint: " + HResultToString(hr));
    }
    
    // Activate audio endpoint volume interface
    hr = device_->Activate(
        __uuidof(IAudioEndpointVolume),
        CLSCTX_ALL,
        nullptr,
        reinterpret_cast<void**>(&endpointVolume_)
    );
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to activate endpoint volume: " + HResultToString(hr));
    }
}

void AudioEndpoint::cleanup() {
    if (endpointVolume_) {
        endpointVolume_->Release();
        endpointVolume_ = nullptr;
    }
    if (device_) {
        device_->Release();
        device_ = nullptr;
    }
    if (deviceEnumerator_) {
        deviceEnumerator_->Release();
        deviceEnumerator_ = nullptr;
    }
    if (comInitialized_) {
        CoUninitialize();
        comInitialized_ = false;
    }
}

void AudioEndpoint::setMasterVolume(float level) {
    if (level < 0.0f || level > 1.0f) {
        throw std::invalid_argument("Volume level must be between 0.0 and 1.0");
    }
    
    if (!endpointVolume_) {
        throw std::runtime_error("Audio endpoint not initialized");
    }
    
    HRESULT hr = endpointVolume_->SetMasterVolumeLevelScalar(level, nullptr);
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to set volume: " + HResultToString(hr));
    }
}

float AudioEndpoint::getMasterVolume() const {
    if (!endpointVolume_) {
        throw std::runtime_error("Audio endpoint not initialized");
    }
    
    float level = 0.0f;
    HRESULT hr = endpointVolume_->GetMasterVolumeLevelScalar(&level);
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to get volume: " + HResultToString(hr));
    }
    
    return level;
}

void AudioEndpoint::setMute(bool muted) {
    if (!endpointVolume_) {
        throw std::runtime_error("Audio endpoint not initialized");
    }
    
    HRESULT hr = endpointVolume_->SetMute(muted ? TRUE : FALSE, nullptr);
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to set mute: " + HResultToString(hr));
    }
}

bool AudioEndpoint::getMute() const {
    if (!endpointVolume_) {
        throw std::runtime_error("Audio endpoint not initialized");
    }
    
    BOOL muted = FALSE;
    HRESULT hr = endpointVolume_->GetMute(&muted);
    if (FAILED(hr)) {
        throw std::runtime_error("Failed to get mute state: " + HResultToString(hr));
    }
    
    return muted == TRUE;
}

} // namespace jarvis

#endif // _WIN32



