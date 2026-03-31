#pragma once

#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include "device_profile.h"
#include "sync_summary.h"

class SyncClient {
public:
    void begin(const String& backend_base_url, const String& pet_id) {
        backend_base_url_ = backend_base_url;
        pet_id_ = pet_id;
        last_fetch_ms_ = 0;
        last_ok_ms_ = 0;
        last_fail_ms_ = 0;
        fail_count_ = 0;
    }

    bool ready() const {
        return backend_base_url_.length() > 0 && pet_id_.length() > 0 && WiFi.status() == WL_CONNECTED;
    }

    bool fetchMini(SyncMiniSnapshot& out) {
        if (!ready()) {
            fail_count_++;
            last_fail_ms_ = millis();
            return false;
        }
        HTTPClient http;
        String url = backend_base_url_;
        if (!url.endsWith("/")) {
            url += "/";
        }
        url += "api/pet/" + pet_id_ + "/sync/minimal";
        http.begin(url);
        int status = http.GET();
        if (status != 200) {
            http.end();
            fail_count_++;
            last_fail_ms_ = millis();
            return false;
        }
        String body = http.getString();
        http.end();
        if (!parseMini(body, out)) {
            fail_count_++;
            last_fail_ms_ = millis();
            return false;
        }
        last_fetch_ms_ = millis();
        last_ok_ms_ = last_fetch_ms_;
        fail_count_ = 0;
        out.last_sync_ok_ms = last_ok_ms_;
        out.last_sync_fail_ms = last_fail_ms_;
        out.sync_fail_count = fail_count_;
        return true;
    }

    bool shouldFetch(uint32_t now_ms) const {
        return now_ms - last_fetch_ms_ >= NUONUO_SYNC_INTERVAL_MS;
    }

    uint32_t lastFetchMs() const {
        return last_fetch_ms_;
    }

    uint32_t lastOkMs() const {
        return last_ok_ms_;
    }

    uint32_t lastFailMs() const {
        return last_fail_ms_;
    }

    uint8_t failCount() const {
        return fail_count_;
    }

private:
    String backend_base_url_;
    String pet_id_;
    uint32_t last_fetch_ms_ = 0;
    uint32_t last_ok_ms_ = 0;
    uint32_t last_fail_ms_ = 0;
    uint8_t fail_count_ = 0;

    static String readStringField(const String& json, const char* key) {
        String needle = String("\"") + key + "\":";
        int start = json.indexOf(needle);
        if (start < 0) {
            return String();
        }
        start += needle.length();
        while (start < (int)json.length() && isspace((unsigned char)json[start])) {
            start++;
        }
        if (start >= (int)json.length()) {
            return String();
        }
        if (json[start] == '"') {
            start++;
            String out;
            while (start < (int)json.length()) {
                char c = json[start++];
                if (c == '\\') {
                    if (start < (int)json.length()) {
                        char esc = json[start++];
                        switch (esc) {
                            case '"': out += '"'; break;
                            case '\\': out += '\\'; break;
                            case 'n': out += '\n'; break;
                            case 'r': out += '\r'; break;
                            case 't': out += '\t'; break;
                            default: out += esc; break;
                        }
                    }
                    continue;
                }
                if (c == '"') {
                    break;
                }
                out += c;
            }
            return out;
        }
        int end = start;
        while (end < (int)json.length()) {
            char c = json[end];
            if (c == ',' || c == '}' || isspace((unsigned char)c)) {
                break;
            }
            end++;
        }
        return json.substring(start, end);
    }

    static uint16_t readUIntField(const String& json, const char* key, uint16_t fallback = 0) {
        String value = readStringField(json, key);
        if (value.length() == 0) {
            return fallback;
        }
        return static_cast<uint16_t>(value.toInt());
    }

    static bool parseMini(const String& json, SyncMiniSnapshot& out) {
        out.subject_id = readStringField(json, "subject_id");
        out.subject_type = readStringField(json, "subject_type");
        out.health_level = readStringField(json, "health_level");
        out.summary_line = readStringField(json, "summary_line");
        out.primary_device_id = readStringField(json, "primary_device_id");
        out.primary_hint = readStringField(json, "primary_hint");
        out.action_hint = readStringField(json, "action_hint");
        out.recommended_action = readStringField(json, "recommended_action");
        out.occupancy_state = readStringField(json, "occupancy_state");
        out.status_hint = readStringField(json, "status_hint");
        out.online_devices = readUIntField(json, "online_devices", 0);
        out.offline_devices = readUIntField(json, "offline_devices", 0);
        out.missing_devices = readUIntField(json, "missing_devices", 0);
        out.conflict_count = readUIntField(json, "conflict_count", 0);
        out.device_count = readUIntField(json, "device_count", 0);
        out.last_sync_ok_ms = 0;
        out.last_sync_fail_ms = 0;
        out.sync_fail_count = 0;
        return out.subject_id.length() > 0 && out.health_level.length() > 0;
    }
};

