#include <Arduino.h>
#include "pet_app.h"
#include "device_profile.h"
#include "sync_summary.h"
#include "sync_client.h"

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

    SyncMiniSnapshot demo;
    demo.subject_id = "demo-pet";
    demo.subject_type = "pet";
    demo.health_level = "normal";
    demo.summary_line = "1 device(s), 1 online";
    demo.primary_device_id = "demo-device";
    demo.primary_hint = "主设备 demo-device 在线。";
    demo.action_hint = "状态正常，继续观察即可。";
    demo.recommended_action = "normal";
    demo.occupancy_state = "claimed";
    demo.online_devices = 1;
    demo.offline_devices = 0;
    demo.missing_devices = 0;
    demo.conflict_count = 0;
    demo.device_count = 1;
    applySyncMini(demo);
}

void PetApp::update() {
    uint32_t now_ms = millis();
    updateEnergy(now_ms);
    updateMood();
    pollSync(now_ms);

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

    if (last_sync_.subject_id.length() > 0 && now_ms - last_sync_render_ms_ > 5000) {
        renderSyncMini(last_sync_);
        last_sync_render_ms_ = now_ms;
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

void PetApp::setSyncEndpoint(const String& backend_base_url, const String& pet_id) {
    backend_base_url_ = backend_base_url;
    sync_pet_id_ = pet_id;
    sync_client_.begin(backend_base_url_, sync_pet_id_);
    Serial.print("[nuonuo] sync_endpoint=");
    Serial.print(backend_base_url_);
    Serial.print(" pet=");
    Serial.println(sync_pet_id_);
}

void PetApp::pollSync(uint32_t now_ms) {
    if (!sync_client_.shouldFetch(now_ms)) {
        return;
    }
    if (!sync_client_.ready()) {
        Serial.println("[nuonuo] sync=skip reason=not_ready");
        return;
    }
    SyncMiniSnapshot snapshot;
    if (sync_client_.fetchMini(snapshot)) {
        applySyncMini(snapshot);
        Serial.print("[nuonuo] sync=ok at=");
        Serial.println(now_ms);
    } else {
        Serial.println("[nuonuo] sync=fail");
    }
}

void PetApp::applySyncMini(const SyncMiniSnapshot& snapshot) {
    last_sync_ = snapshot;
    renderSyncMini(snapshot);
    last_sync_render_ms_ = millis();
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

void PetApp::renderSyncMini(const SyncMiniSnapshot& snapshot) {
    Serial.print("[nuonuo] sync=");
    Serial.print(snapshot.subject_type);
    Serial.print(":");
    Serial.print(snapshot.subject_id);
    Serial.print(" health=");
    Serial.print(snapshot.health_level);
    Serial.print(" color=");
    Serial.print(syncHealthColor(snapshot.health_level));
    Serial.print(" summary=");
    Serial.println(snapshot.summary_line);
    if (snapshot.primary_hint.length() > 0) {
        Serial.print("[nuonuo] primary_hint=");
        Serial.println(snapshot.primary_hint);
    }
    if (snapshot.action_hint.length() > 0) {
        Serial.print("[nuonuo] action_hint=");
        Serial.println(snapshot.action_hint);
    }
}

void setup() {
    app.begin();
    app.setSyncEndpoint(NUONUO_BACKEND_BASE_URL, NUONUO_DEFAULT_PET_ID);
    app.setNetworkReady(true);
}

void loop() {
    app.update();
    delay(50);
}

