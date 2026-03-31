#include <Arduino.h>
#include "pet_app.h"
#include "device_profile.h"

namespace {
PetApp app;
}

PetApp::PetApp() {
    state_.device_state = DeviceState::Booting;
    state_.mood = PetMood::Neutral;
    state_.activity = PetActivity::Idle;
}

void PetApp::begin() {
    Serial.begin(115200);
    delay(200);
    Serial.println("[nuonuo] boot");
    Serial.print("[nuonuo] device=");
    Serial.println(NUONUO_DEVICE_NAME);
    Serial.print("[nuonuo] fw=");
    Serial.println(NUONUO_FIRMWARE_VERSION);
    state_.device_state = DeviceState::Connecting;
    state_.last_tick_ms = millis();
}

void PetApp::update() {
    uint32_t now_ms = millis();
    updateEnergy(now_ms);
    updateMood();

    if (state_.device_state == DeviceState::Connecting && state_.network_ready) {
        state_.device_state = state_.is_bound ? DeviceState::Ready : DeviceState::Binding;
        logStateChange("network_ready");
    }

    if (state_.device_state == DeviceState::Binding && state_.is_bound) {
        state_.device_state = DeviceState::Ready;
        logStateChange("bound");
    }

    if (state_.energy < 10 && state_.device_state == DeviceState::Ready) {
        state_.device_state = DeviceState::LowPower;
        state_.activity = PetActivity::Sleeping;
        logStateChange("low_energy");
    }

    if (state_.energy == 0) {
        state_.device_state = DeviceState::Sleeping;
        state_.activity = PetActivity::Sleeping;
    }

    state_.last_tick_ms = now_ms;
}

void PetApp::setBound(bool bound) {
    state_.is_bound = bound;
    if (bound && state_.device_state == DeviceState::Binding) {
        state_.device_state = DeviceState::Ready;
        logStateChange("setBound");
    }
}

void PetApp::setNetworkReady(bool ready) {
    state_.network_ready = ready;
    if (ready && state_.device_state == DeviceState::Connecting) {
        state_.device_state = state_.is_bound ? DeviceState::Ready : DeviceState::Binding;
        logStateChange("setNetworkReady");
    }
}

const PetState& PetApp::state() const {
    return state_;
}

void PetApp::updateEnergy(uint32_t now_ms) {
    if (now_ms - state_.last_tick_ms < 1000) {
        return;
    }
    if (state_.energy > 0) {
        state_.energy -= 1;
    }
    if (state_.hunger < 100) {
        state_.hunger += 1;
    }
}

void PetApp::updateMood() {
    if (state_.hunger > 70) {
        state_.mood = PetMood::Hungry;
    } else if (state_.energy < 20) {
        state_.mood = PetMood::Sleepy;
    } else if (state_.is_bound) {
        state_.mood = PetMood::Happy;
    } else {
        state_.mood = PetMood::Curious;
    }
}

void PetApp::logStateChange(const char* reason) {
    Serial.print("[nuonuo] state=");
    Serial.print(deviceStateName(state_.device_state));
    Serial.print(" mood=");
    Serial.print(moodName(state_.mood));
    Serial.print(" reason=");
    Serial.println(reason);
}

void setup() {
    app.begin();
    app.setNetworkReady(true);
}

void loop() {
    app.update();
    delay(50);
}
