/**
 * @file audio_endpoint.h
 * @brief Windows Audio Session API (WASAPI) volume control
 * 
 * Provides system-level volume control using Core Audio APIs.
 * Demonstrates low-level Windows API programming and OOP principles.
 */

#pragma once

#ifdef _WIN32

#include <windows.h>
#include <mmdeviceapi.h>
#include <endpointvolume.h>
#include <comdef.h>
#include <memory>
#include <stdexcept>

namespace jarvis {

/**
 * @class AudioEndpoint
 * @brief RAII wrapper for Windows audio endpoint control
 * 
 * Demonstrates C++ OOP principles:
 * - RAII (Resource Acquisition Is Initialization)
 * - Exception safety
 * - Smart pointers for COM object management
 */
class AudioEndpoint {
public:
    /**
     * @brief Constructor - initializes COM and gets default audio endpoint
     * @throws std::runtime_error if initialization fails
     * 
     * Time complexity: O(1)
     * Space complexity: O(1)
     */
    AudioEndpoint();
    
    /**
     * @brief Destructor - releases COM resources
     * 
     * Ensures proper cleanup following RAII principles
     */
    ~AudioEndpoint();
    
    // Prevent copying (COM objects shouldn't be copied)
    AudioEndpoint(const AudioEndpoint&) = delete;
    AudioEndpoint& operator=(const AudioEndpoint&) = delete;
    
    // Allow moving
    AudioEndpoint(AudioEndpoint&&) noexcept;
    AudioEndpoint& operator=(AudioEndpoint&&) noexcept;
    
    /**
     * @brief Set master volume level
     * @param level Volume level (0.0 to 1.0)
     * @throws std::invalid_argument if level out of range
     * @throws std::runtime_error if operation fails
     * 
     * Time complexity: O(1)
     */
    void setMasterVolume(float level);
    
    /**
     * @brief Get current master volume level
     * @return Volume level (0.0 to 1.0)
     * @throws std::runtime_error if operation fails
     * 
     * Time complexity: O(1)
     */
    float getMasterVolume() const;
    
    /**
     * @brief Set mute state
     * @param muted True to mute, false to unmute
     * @throws std::runtime_error if operation fails
     * 
     * Time complexity: O(1)
     */
    void setMute(bool muted);
    
    /**
     * @brief Get current mute state
     * @return True if muted, false otherwise
     * @throws std::runtime_error if operation fails
     * 
     * Time complexity: O(1)
     */
    bool getMute() const;

private:
    /**
     * @brief Initialize COM interfaces
     * @throws std::runtime_error if initialization fails
     */
    void initialize();
    
    /**
     * @brief Release COM resources
     */
    void cleanup();
    
    // COM interface pointers (using smart pointers for automatic cleanup)
    IMMDeviceEnumerator* deviceEnumerator_ = nullptr;
    IMMDevice* device_ = nullptr;
    IAudioEndpointVolume* endpointVolume_ = nullptr;
    bool comInitialized_ = false;
};

} // namespace jarvis

#endif // _WIN32



