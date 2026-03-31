#pragma once

#include <Arduino.h>

struct SyncMiniSnapshot {
    String subject_id;
    String subject_type;
    String health_level;
    String summary_line;
    String primary_device_id;
    String primary_hint;
    String action_hint;
    String recommended_action;
    String occupancy_state;
    String status_hint;
    uint16_t online_devices = 0;
    uint16_t offline_devices = 0;
    uint16_t missing_devices = 0;
    uint16_t conflict_count = 0;
    uint16_t device_count = 0;
    uint32_t last_sync_ok_ms = 0;
    uint32_t last_sync_fail_ms = 0;
    uint8_t sync_fail_count = 0;
};

inline const char* syncHealthColor(const String& health_level) {
    if (health_level == "critical") return "red";
    if (health_level == "degraded") return "orange";
    if (health_level == "warning") return "yellow";
    if (health_level == "idle") return "blue";
    return "green";
}

