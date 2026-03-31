#include <Arduino.h>

#pragma once

enum class DeviceState {
    Booting,
    Connecting,
    Binding,
    Ready,
    Sleeping,
    LowPower,
    Error
};

enum class PetMood {
    Neutral,
    Happy,
    Curious,
    Sleepy,
    Hungry,
    Lonely,
    Sad,
    Angry
};

enum class PetActivity {
    Idle,
    Listening,
    Talking,
    Playing,
    Eating,
    Sleeping,
    Recovering
};

struct PetState {
    DeviceState device_state = DeviceState::Booting;
    PetMood mood = PetMood::Neutral;
    PetActivity activity = PetActivity::Idle;
    bool network_ready = false;
    bool is_bound = false;
    uint8_t bind_retry_count = 0;
    uint8_t sync_fail_count = 0;
    uint32_t energy = 100;
    uint32_t happiness = 50;
    uint32_t hunger = 20;
    uint32_t last_tick_ms = 0;
    uint32_t last_sync_ok_ms = 0;
    uint32_t last_sync_fail_ms = 0;
};

inline const char* deviceStateName(DeviceState state) {
    switch (state) {
        case DeviceState::Booting: return "Booting";
        case DeviceState::Connecting: return "Connecting";
        case DeviceState::Binding: return "Binding";
        case DeviceState::Ready: return "Ready";
        case DeviceState::Sleeping: return "Sleeping";
        case DeviceState::LowPower: return "LowPower";
        case DeviceState::Error: return "Error";
        default: return "Unknown";
    }
}

inline const char* moodName(PetMood mood) {
    switch (mood) {
        case PetMood::Neutral: return "Neutral";
        case PetMood::Happy: return "Happy";
        case PetMood::Curious: return "Curious";
        case PetMood::Sleepy: return "Sleepy";
        case PetMood::Hungry: return "Hungry";
        case PetMood::Lonely: return "Lonely";
        case PetMood::Sad: return "Sad";
        case PetMood::Angry: return "Angry";
        default: return "Unknown";
    }
}

