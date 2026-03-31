#pragma once

#include <Arduino.h>
#include "state_machine.h"
#include "sync_summary.h"
#include "sync_client.h"

class PetApp {
public:
    PetApp();

    void begin();
    void update();

    void setBound(bool bound);
    void setNetworkReady(bool ready);
    void setSyncEndpoint(const String& backend_base_url, const String& pet_id = NUONUO_DEFAULT_PET_ID);
    void pollSync(uint32_t now_ms);
    void applySyncMini(const SyncMiniSnapshot& snapshot);
    const PetState& state() const;

private:
    PetState state_;
    void updateEnergy(uint32_t now_ms);
    void updateMood();
    void logStateChange(const char* reason);
    void renderSyncMini(const SyncMiniSnapshot& snapshot);
    SyncMiniSnapshot last_sync_;
    uint32_t last_sync_render_ms_ = 0;
    SyncClient sync_client_;
    String backend_base_url_ = NUONUO_BACKEND_BASE_URL;
    String sync_pet_id_ = NUONUO_DEFAULT_PET_ID;
};

