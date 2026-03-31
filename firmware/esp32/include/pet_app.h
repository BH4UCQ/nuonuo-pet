#pragma once

#include <Arduino.h>
#include "state_machine.h"

class PetApp {
public:
    PetApp();

    void begin();
    void update();

    void setBound(bool bound);
    void setNetworkReady(bool ready);
    const PetState& state() const;

private:
    PetState state_;
    void updateEnergy(uint32_t now_ms);
    void updateMood();
    void logStateChange(const char* reason);
};
