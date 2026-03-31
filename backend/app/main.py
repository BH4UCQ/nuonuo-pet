from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    AssetsManifestItem,
    BindConfirmRequest,
    BindConfirmResponse,
    BindRequest,
    BindRequestResponse,
    ChatRequest,
    ChatResponse,
    DeviceCapabilityGradeResponse,
    DeviceDetailResponse,
    DeviceEventItem,
    DeviceEventListResponse,
    DeviceEventRequest,
    DeviceEventResponse,
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceStateRequest,
    DeviceStateResponse,
    MemoryItem,
    MemoryListResponse,
    MemorySummaryResponse,
    MemoryWriteRequest,
    ModelRouteConfigResponse,
    ModelRouteConfigUpdateRequest,
    ModelRouteItem,
    ModelRouteResolveRequest,
    ModelRouteResolveResponse,
    ModelRouteResponse,
    PetCreateRequest,
    PetDeviceLinkItem,
    PetDeviceLinkRequest,
    PetDeviceLinkResponse,
    PetDeviceListResponse,
    PetDevicePrimaryRequest,
    PetDevicePrimaryResponse,
    PetDeviceSyncSummaryResponse,
    PetDeviceUnlinkRequest,
    PetDeviceUnlinkResponse,
    PetSyncDeviceItem,
    PetSyncSummaryResponse,
    PetBroadcastItem,
    PetBroadcastSummaryResponse,
    DeviceSyncSummaryResponse,
    PetEventRequest,
    PetEventResponse,
    PetGrowthSummaryResponse,
    PetPreviewResponse,
    PetProfileResponse,
    PetUpdateRequest,
    PreviewLayerItem,
    PreviewSampleResponse,
    ProtocolInfo,
    ResourcePackActionResponse,
    ResourcePackDetailResponse,
    ResourcePackEnableRequest,
    ResourcePackImportRequest,
    ResourcePackImportResponse,
    ResourcePackListResponse,
    ResourcePackManifest,
    ResourcePackRecordItem,
    ResourcePackValidateRequest,
    ResourcePackValidateResponse,
    ResourceSlotItem,
    SpeciesTemplateItem,
    SpeciesTemplateResponse,
    TemplateSelectionResponse,
    ThemePackItem,
    ThemePackResponse,
    ThemePackValidateRequest,
    ThemePackValidateResponse,
)
from .storage import DEVICES, PETS, MEMORY, EVENTS, ASSET_MANIFEST, MODEL_ROUTES, MODEL_ROUTE_CONFIG, SPECIES_TEMPLATES, THEME_PACKS, RESOURCE_SLOT_RULES, DEFAULT_PREVIEW_SELECTION, DeviceRecord, PetRecord, MemoryRecord, EventRecord, new_bind_code, now_iso, save_state, load_state

PROTOCOL_VERSION = "0.1.0"
app = FastAPI(title="nuonuo-pet backend", version=PROTOCOL_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_load_state() -> None:
    load_state()


@app.on_event("shutdown")
def shutdown_save_state() -> None:
    save_state()


@app.get("/")
def root():
    return {
        "name": "nuonuo-pet backend",
        "version": PROTOCOL_VERSION,
        "server_time": server_time(),
        "endpoints": [
            "/health",
            "/api/protocol",
            "/api/device/register",
            "/api/device/bind/request",
            "/api/device/bind/confirm",
            "/api/device/{device_id}",
            "/api/device/{device_id}/health",
            "/api/device/{device_id}/events",
            "/api/device/heartbeat",
            "/api/device/{device_id}/event",
            "/api/device/state",
            "/api/species/templates",
            "/api/model/routes",
            "/api/model/routes/config",
            "/api/model/routes/resolve",
            "/api/model/routes/apply/{pet_id}",
            "/api/theme/packs",
            "/api/theme/compatibility",
            "/api/theme/validate",
            "/api/resource/packs",
            "/api/resource/packs/{pack_id}",
            "/api/resource/packs/import",
            "/api/resource/packs/{pack_id}/enable",
            "/api/resource/packs/{pack_id}/rollback",
            "/api/resource/manifest/sample",
            "/api/resource/validate",
            "/api/preview/{species_id}/{theme_id}",
            "/api/preview/sample",
            "/api/pet/create",
            "/api/pet/{pet_id}",
            "/api/pet/{pet_id}/event",
            "/api/pet/{pet_id}/memory/summary",
            "/api/chat",
            "/api/memory/{pet_id}",
            "/api/assets/manifest",
            "/api/assets/manifest/sample",
        ],
    }


def bind_expires_iso(timestamp: float | None) -> str | None:
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def initialize_preferences(pet: PetRecord) -> None:
    if not getattr(pet, "growth_preferences", None):
        pet.growth_preferences = {"play": 0, "care": 0, "rest": 0, "feed": 0, "chat": 0, "praise": 0}
    if not getattr(pet, "preference_notes", None):
        pet.preference_notes = []



def event_category_for(kind: str) -> str:
    kind = (kind or "").strip().lower()
    if kind in {"feed", "eat", "meal"}:
        return "care"
    if kind in {"play", "game"}:
        return "play"
    if kind in {"sleep", "rest"}:
        return "rest"
    if kind in {"praise", "pet", "reward", "bond"}:
        return "bond"
    if kind in {"chat", "listen", "respond"}:
        return "chat"
    if kind.startswith("device-") or kind in {"offline", "online", "resume", "heartbeat", "state"}:
        return "system"
    return "other"


def evolve_growth_preferences(pet: PetRecord, kind: str, text: str, actions: list[str]) -> None:
    initialize_preferences(pet)
    kind = (kind or "").strip().lower()
    score_delta = {
        "play": 2,
        "game": 2,
        "chat": 2,
        "feed": 1,
        "meal": 1,
        "eat": 1,
        "sleep": 1,
        "rest": 1,
        "praise": 2,
        "pet": 2,
        "reward": 2,
        "scold": -2,
        "ignore": -2,
        "punish": -2,
    }
    key = kind if kind in pet.growth_preferences else None
    if key is None:
        if any(tag in kind for tag in ("play", "chat", "game")):
            key = "play"
        elif any(tag in kind for tag in ("feed", "meal", "eat")):
            key = "feed"
        elif any(tag in kind for tag in ("sleep", "rest")):
            key = "rest"
        elif any(tag in kind for tag in ("praise", "pet", "reward")):
            key = "praise"
        elif any(tag in kind for tag in ("care", "help", "wash")):
            key = "care"
        else:
            key = "chat"
    delta = score_delta.get(kind, 1 if key in {"chat", "play"} else 0)
    pet.growth_preferences[key] = pet.growth_preferences.get(key, 0) + delta
    if delta > 0 and key not in pet.preference_notes:
        pet.preference_notes.append(f"likes_{key}")
    if delta < 0:
        pet.preference_notes.append(f"avoid_{key}")
    pet.preference_notes = pet.preference_notes[-8:]
    if "birthday" in text.lower() or "生日" in text:
        pet.growth_preferences["praise"] = pet.growth_preferences.get("praise", 0) + 1
    if "chat" in actions and pet.growth_preferences.get("chat", 0) >= 6:
        pet.mood = "curious"
    if pet.growth_preferences.get("play", 0) >= 6 and pet.energy > 40:
        pet.mood = "excited"
    if pet.growth_preferences.get("rest", 0) >= 6 and pet.energy < 80:
        pet.mood = "sleepy"
    if pet.growth_preferences.get("feed", 0) >= 6 and pet.hunger > 50:
        pet.mood = "hungry"
    if pet.growth_preferences.get("praise", 0) >= 8 and pet.affection >= 60:
        pet.mood = "happy"


def normalize_bounds(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def growth_stage_for_level(level: int) -> str:
    if level >= 12:
        return "adult"
    if level >= 7:
        return "teen"
    if level >= 4:
        return "juvenile"
    if level >= 2:
        return "baby"
    return "egg"


def level_up_if_needed(pet: PetRecord) -> int:
    level_ups = 0
    while pet.exp >= pet.level * 10:
        pet.exp -= pet.level * 10
        pet.level += 1
        level_ups += 1
    pet.growth_stage = growth_stage_for_level(pet.level)
    return level_ups


def apply_event_to_pet(pet: PetRecord, kind: str, text: str) -> list[str]:
    actions: list[str] = []
    kind = (kind or "").strip().lower()

    if kind in {"feed", "eat", "meal"}:
        pet.hunger = normalize_bounds(pet.hunger - 25)
        pet.affection = normalize_bounds(pet.affection + 3)
        pet.exp += 4
        pet.mood = "happy"
        actions.append("eat")
    elif kind in {"play", "game", "chat"}:
        pet.energy = normalize_bounds(pet.energy - 8)
        pet.affection = normalize_bounds(pet.affection + 6)
        pet.exp += 6
        pet.mood = "happy"
        actions.append("play")
    elif kind in {"sleep", "rest"}:
        pet.energy = normalize_bounds(pet.energy + 25)
        pet.hunger = normalize_bounds(pet.hunger + 4)
        pet.exp += 2
        pet.mood = "sleepy"
        actions.append("sleep")
    elif kind in {"praise", "pet", "reward"}:
        pet.affection = normalize_bounds(pet.affection + 8)
        pet.exp += 5
        pet.mood = "happy"
        actions.append("bond")
    elif kind in {"scold", "ignore", "punish"}:
        pet.affection = normalize_bounds(pet.affection - 6)
        pet.energy = normalize_bounds(pet.energy - 3)
        pet.exp += 1
        pet.mood = "sad"
        actions.append("withdraw")
    else:
        pet.exp += 2
        actions.append("notice")

    if "生日" in text or "birthday" in text.lower():
        pet.affection = normalize_bounds(pet.affection + 10)
        pet.exp += 8
        actions.append("celebrate")

    if pet.energy < 20:
        pet.mood = "sleepy"
    elif pet.hunger > 80:
        pet.mood = "hungry"
    elif pet.affection >= 80:
        pet.mood = "happy"
    elif pet.affection <= 20:
        pet.mood = "lonely"

    return actions


def species_template_for(species_id: str) -> dict | None:
    return next((item for item in SPECIES_TEMPLATES if item["id"] == species_id), None)


def model_route_for(route_id: str | None) -> dict | None:
    if route_id is None:
        return MODEL_ROUTES[0] if MODEL_ROUTES else None
    return next((item for item in MODEL_ROUTES if item["id"] == route_id), None)


def align_pet_to_species(pet: PetRecord) -> None:
    template = species_template_for(pet.species_id)
    if template is None:
        return
    if not pet.theme_id or pet.theme_id not in template.get("allowed_theme_ids", []):
        pet.theme_id = template.get("default_theme_id", pet.theme_id)


def record_device_event(device_id: str, kind: str, message: str, meta: dict | None = None) -> None:
    DEVICE_EVENTS.setdefault(device_id, []).append(
        DeviceEventRecord(
            device_id=device_id,
            kind=kind,
            message=message,
            created_at=server_time(),
            meta=dict(meta or {}),
        )
    )
    save_state()


def device_touch(rec: DeviceRecord) -> None:
    rec.last_seen_at = server_time()
    rec.connection_state = "online"
    rec.offline_reason = None
    save_state()


def device_is_offline(rec: DeviceRecord, stale_after_seconds: int = 300) -> bool:
    if rec.last_seen_at is None:
        return not rec.bound
    try:
        last_seen = datetime.fromisoformat(rec.last_seen_at)
    except ValueError:
        return True
    age = (datetime.now(timezone.utc) - last_seen).total_seconds()
    return age > stale_after_seconds


def device_health_snapshot(rec: DeviceRecord, stale_after_seconds: int = 300) -> dict:
    offline = device_is_offline(rec, stale_after_seconds=stale_after_seconds)
    connection_state = rec.connection_state
    offline_reason = rec.offline_reason
    if offline:
        connection_state = "offline"
        if offline_reason is None:
            offline_reason = "heartbeat expired"
    elif not rec.bound:
        connection_state = "paired" if rec.bind_code else "unbound"
    return {
        "device_id": rec.device_id,
        "bound": rec.bound,
        "connection_state": connection_state,
        "last_seen_at": rec.last_seen_at,
        "is_offline": offline,
        "offline_reason": offline_reason,
        "stale_after_seconds": stale_after_seconds,
        "server_time": server_time(),
    }


def validate_resource_pack(manifest: ResourcePackManifest) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if manifest.pack_type not in {"species-template", "theme-pack", "audio-pack", "sprite-pack"}:
        errors.append(f"unsupported pack_type: {manifest.pack_type}")

    if not manifest.slots:
        warnings.append("resource pack has no slots")

    for slot in manifest.slots:
        rule = RESOURCE_SLOT_RULES.get(slot.slot_id)
        if rule is None:
            warnings.append(f"unknown slot: {slot.slot_id}")
            continue
        if slot.resource_type != rule["resource_type"]:
            errors.append(f"slot {slot.slot_id} expects {rule['resource_type']}, got {slot.resource_type}")
        if slot.width is not None and slot.width > rule["max_width"]:
            errors.append(f"slot {slot.slot_id} width exceeds limit")
        if slot.height is not None and slot.height > rule["max_height"]:
            errors.append(f"slot {slot.slot_id} height exceeds limit")
        if slot.format is not None and slot.format.lower() not in rule["formats"]:
            errors.append(f"slot {slot.slot_id} format not allowed")

    return len(errors) == 0, errors, warnings


def validate_theme_pack(theme: ThemePackItem) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    species = species_template_for(theme.species_id)
    if species is None:
        errors.append(f"unknown species_id: {theme.species_id}")
    else:
        allowed = set(species.get("allowed_theme_ids", []))
        if allowed and theme.theme_id not in allowed:
            errors.append(f"theme {theme.theme_id} is not allowed for species {theme.species_id}")

    if not theme.version:
        warnings.append("theme version is empty")
    if theme.min_firmware_version and theme.max_firmware_version and theme.min_firmware_version > theme.max_firmware_version:
        errors.append("min_firmware_version is greater than max_firmware_version")

    for slot_id in theme.slot_map.keys():
        if slot_id not in RESOURCE_SLOT_RULES:
            warnings.append(f"slot {slot_id} is not defined in slot rules")
    if theme.compatible_slot_ids:
        for slot_id in theme.compatible_slot_ids:
            if slot_id not in RESOURCE_SLOT_RULES:
                warnings.append(f"compatible slot {slot_id} is not defined in slot rules")

    if not theme.palette:
        warnings.append("theme palette is empty")

    return len(errors) == 0, errors, warnings


def model_route_for(route_id: str | None) -> dict | None:
    if route_id is None:
        return MODEL_ROUTES[0] if MODEL_ROUTES else None
    return next((item for item in MODEL_ROUTES if item["id"] == route_id), None)


def model_route_item_from_dict(route: dict[str, Any]) -> ModelRouteItem:
    return ModelRouteItem(**route)


def model_route_candidates(route_id: str | None, fallback_route_ids: list[str] | None = None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    def push(route: dict[str, Any] | None) -> None:
        if route is None:
            return
        route_id_local = route.get("id")
        if route_id_local and route_id_local not in seen:
            candidates.append(route)
            seen.add(route_id_local)

    if route_id:
        push(model_route_for(route_id))

    for fallback_id in fallback_route_ids or []:
        push(model_route_for(fallback_id))

    push(model_route_for(MODEL_ROUTE_CONFIG.get("default_route_id")))
    for fallback_id in MODEL_ROUTE_CONFIG.get("fallback_route_ids", []):
        push(model_route_for(fallback_id))

    for route in MODEL_ROUTES:
        push(route)

    return candidates


def resolve_model_route(route_id: str | None = None, fallback_route_ids: list[str] | None = None, prefer_enabled: bool = True, allow_fallback: bool = True) -> tuple[dict[str, Any] | None, bool, str | None, list[str]]:
    available_ids = [route["id"] for route in MODEL_ROUTES]
    candidates = model_route_candidates(route_id, fallback_route_ids if allow_fallback else [])
    if not candidates:
        return None, False, "no model routes configured", available_ids

    for route in candidates:
        if route is None:
            continue
        if prefer_enabled and not route.get("enabled", True):
            continue
        return route, route_id is not None and route.get("id") != route_id, None, available_ids

    if not allow_fallback:
        return None, False, "requested route disabled or unavailable", available_ids

    for route in candidates:
        if route is None:
            continue
        return route, route_id is not None and route.get("id") != route_id, "requested route unavailable; fallback selected", available_ids

    return None, False, "no usable model route found", available_ids


def resource_pack_item_from_record(record: dict[str, Any]) -> ResourcePackRecordItem:
    return ResourcePackRecordItem(**record)


def resource_pack_manifest_to_record(manifest: ResourcePackManifest, enabled: bool = False, previous_versions: list[str] | None = None) -> dict[str, Any]:
    return {
        "pack_id": manifest.pack_id,
        "pack_type": manifest.pack_type,
        "version": manifest.version,
        "species_id": manifest.species_id,
        "theme_id": manifest.theme_id,
        "name": manifest.name,
        "description": manifest.description,
        "enabled": enabled,
        "active_version": manifest.version,
        "imported_at": server_time(),
        "updated_at": server_time(),
        "previous_versions": list(previous_versions or []),
        "manifest": manifest.model_dump(),
    }


def resource_pack_record_for(pack_id: str) -> dict[str, Any] | None:
    return RESOURCE_PACKS.get(pack_id)


def resource_pack_history(record: dict[str, Any]) -> list[str]:
    return list(record.get("previous_versions", []))


def enable_resource_pack(pack_id: str, enabled: bool = True) -> dict[str, Any]:
    record = resource_pack_record_for(pack_id)
    if record is None:
        raise HTTPException(status_code=404, detail="resource pack not found")
    record["enabled"] = enabled
    record["updated_at"] = server_time()
    save_state()
    return record


def rollback_resource_pack(pack_id: str, version: str | None = None) -> dict[str, Any]:
    record = resource_pack_record_for(pack_id)
    if record is None:
        raise HTTPException(status_code=404, detail="resource pack not found")
    manifest = dict(record.get("manifest", {}))
    previous_versions = list(record.get("previous_versions", []))
    if version is None:
        if not previous_versions:
            raise HTTPException(status_code=400, detail="no previous version available for rollback")
        version = previous_versions[-1]
    if manifest:
        manifest["version"] = version
    record["previous_versions"] = previous_versions[:-1] if previous_versions and previous_versions[-1] == version else previous_versions
    record["active_version"] = version
    record["manifest"] = manifest or record.get("manifest", {})
    record["updated_at"] = server_time()
    save_state()
    return record
def pets_for_device(device_id: str) -> list[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


def pet_linked_device_ids(pet: PetRecord) -> list[str]:
    ids = list(getattr(pet, "linked_device_ids", []) or [])
    if pet.device_id:
        ids.insert(0, pet.device_id)
    deduped: list[str] = []
    for device_id in ids:
        if device_id and device_id not in deduped:
            deduped.append(device_id)
    return deduped


def pets_claiming_device(device_id: str) -> list[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


def record_device_conflict(device_id: str, pet_ids: list[str], note: str) -> None:
    created_at = server_time()
    payload = {
        "device_id": device_id,
        "pet_ids": list(pet_ids),
        "note": note,
        "conflict": True,
    }
    DEVICE_EVENTS.setdefault(device_id, []).append(
        DeviceEventRecord(
            device_id=device_id,
            kind="sync-conflict",
            message=note,
            created_at=created_at,
            meta=payload,
        )
    )
    for pet_id in pet_ids:
        EVENTS.setdefault(pet_id, []).append(
            EventRecord(
                kind="sync-conflict",
                text=note,
                tags=["system", "sync", "conflict", "category:system"],
                created_at=created_at,
            )
        )


def recommended_action_for_sync(
    occupancy_state: str,
    conflict_device_ids: list[str],
    offline_devices: int,
    missing_devices: int,
    primary_device_online: bool,
    total_devices: int,
) -> str:
    if conflict_device_ids or occupancy_state == "conflicted":
        return "resolve_device_conflict"
    if missing_devices > 0:
        return "reconnect_missing_device"
    if offline_devices > 0:
        return "wake_offline_device"
    if not primary_device_online and total_devices > 0:
        return "switch_primary_or_reconnect"
    if total_devices == 0:
        return "link_a_device"
    return "normal"


def health_level_for_sync(occupancy_state: str, conflict_device_ids: list[str], offline_devices: int, missing_devices: int, primary_device_online: bool, total_devices: int) -> str:
    if conflict_device_ids or occupancy_state == "conflicted":
        return "critical"
    if missing_devices > 0:
        return "degraded"
    if offline_devices > 0:
        return "warning"
    if not primary_device_online and total_devices > 0:
        return "warning"
    if total_devices == 0:
        return "idle"
    return "normal"


def summary_line_for_sync(total_devices: int, online_devices: int, offline_devices: int, missing_devices: int, conflict_count: int) -> str:
    parts = [f"{total_devices} device(s)"]
    parts.append(f"{online_devices} online")
    if offline_devices:
        parts.append(f"{offline_devices} offline")
    if missing_devices:
        parts.append(f"{missing_devices} missing")
    if conflict_count:
        parts.append(f"{conflict_count} conflict")
    return ", ".join(parts)


def primary_hint_for_sync(primary_device_id: str | None, primary_device_online: bool, primary_device_present: bool, occupancy_state: str) -> str:
    if not primary_device_id:
        return "先绑定一台主设备。"
    if occupancy_state == "conflicted":
        return f"主设备 {primary_device_id} 存在占用冲突，先处理冲突。"
    if not primary_device_present:
        return f"主设备 {primary_device_id} 不在线或不存在。"
    if not primary_device_online:
        return f"主设备 {primary_device_id} 当前离线，建议重新连接。"
    return f"主设备 {primary_device_id} 在线。"


def action_hint_for_sync(recommended_action: str, primary_device_id: str | None) -> str:
    if recommended_action == "resolve_device_conflict":
        return "先解除设备冲突，再继续同步。"
    if recommended_action == "reconnect_missing_device":
        return "补回缺失设备，重新拉取状态。"
    if recommended_action == "wake_offline_device":
        return "唤醒离线设备或检查网络。"
    if recommended_action == "switch_primary_or_reconnect":
        return f"可切换主设备 {primary_device_id} 或重新连接。" if primary_device_id else "可切换主设备或重新连接。"
    if recommended_action == "link_a_device":
        return "先给宠物绑定一台设备。"
    return "状态正常，继续观察即可。"


def pet_device_owner(device_id: str) -> PetRecord | None:
    return next((pet for pet in PETS.values() if pet.device_id == device_id), None)


def pet_device_recent_events(device_id: str, limit: int = 5) -> list[dict[str, object]]:
    items = DEVICE_EVENTS.get(device_id, [])[-max(1, min(limit, 20)) :]
    return [
        {
            "kind": item.kind,
            "message": item.message,
            "created_at": item.created_at,
            "meta": dict(item.meta),
        }
        for item in items
    ]


def pet_recent_events(pet_id: str, limit: int = 5) -> list[dict[str, object]]:
    items = EVENTS.get(pet_id, [])[-max(1, min(limit, 20)) :]
    return [
        {
            "kind": item.kind,
            "text": item.text,
            "tags": list(item.tags),
            "created_at": item.created_at,
        }
        for item in items
    ]


def build_pet_sync_summary(pet: PetRecord) -> PetSyncSummaryResponse:
    linked_ids = pet_linked_device_ids(pet)
    device_items: list[PetSyncDeviceItem] = []
    recent_device_events: dict[str, list[dict[str, object]]] = {}
    sync_notes: list[str] = []
    conflict_notes: list[str] = []
    conflict_device_ids: list[str] = []
    online_devices = 0
    offline_devices = 0
    missing_devices = 0
    primary_device_present = False
    primary_device_online = False
    for idx, device_id in enumerate(linked_ids):
        device = DEVICES.get(device_id)
        health = device_health_snapshot(device) if device is not None else None
        recent_device_events[device_id] = pet_device_recent_events(device_id)
        claims = [item.pet_id for item in pets_claiming_device(device_id)]
        if len(claims) > 1:
            conflict_device_ids.append(device_id)
            conflict_notes.append(f"device {device_id} claimed by {', '.join(sorted(set(claims)))}")
        if health is None:
            missing_devices += 1
            sync_notes.append(f"device {device_id} missing")
        elif health["is_offline"]:
            offline_devices += 1
            sync_notes.append(f"device {device_id} offline")
        else:
            online_devices += 1
        is_primary = idx == 0
        if is_primary:
            primary_device_present = device is not None
            primary_device_online = bool(health and not health["is_offline"])
        device_items.append(
            PetSyncDeviceItem(
                device_id=device_id,
                is_primary=is_primary,
                connection_state=health["connection_state"] if health else None,
                last_seen_at=health["last_seen_at"] if health else None,
                is_online=bool(health and not health["is_offline"]),
                offline_reason=health["offline_reason"] if health else None,
                event_count=len(DEVICE_EVENTS.get(device_id, [])),
            )
        )
    recent_pet = pet_recent_events(pet.pet_id)
    if pet.device_id and pet.device_id not in linked_ids:
        sync_notes.append(f"primary device {pet.device_id} is not linked")
    occupancy_state = "conflicted" if conflict_device_ids else "claimed" if linked_ids else "free"
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=primary_device_online,
        total_devices=len(device_items),
    )
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=primary_device_online,
        total_devices=len(device_items),
    )
    return PetSyncSummaryResponse(
        pet_id=pet.pet_id,
        server_time=server_time(),
        primary_device_id=pet.device_id,
        linked_device_ids=linked_ids,
        total_devices=len(device_items),
        online_devices=online_devices,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        conflict_device_ids=conflict_device_ids,
        conflict_notes=conflict_notes,
        primary_device_present=primary_device_present,
        primary_device_online=primary_device_online,
        recommended_action=recommended_action,
        health_level=health_level,
        summary_line=summary_line_for_sync(len(device_items), online_devices, offline_devices, missing_devices, len(conflict_device_ids)),
        primary_hint=primary_hint_for_sync(pet.device_id, primary_device_online, primary_device_present, occupancy_state),
        action_hint=action_hint_for_sync(recommended_action, pet.device_id),
        device_items=device_items,
        recent_pet_events=recent_pet,
        recent_device_events=recent_device_events,
        sync_notes=sync_notes,
    )


def build_device_sync_summary(device_id: str) -> DeviceSyncSummaryResponse:
    device = DEVICES.get(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="device not found")
    pets = pets_claiming_device(device_id)
    pet = next((item for item in pets if item.device_id == device_id), None)
    summary = build_pet_sync_summary(pet) if pet is not None else None
    linked_pet_ids = [item.pet_id for item in pets]
    conflict_notes: list[str] = []
    if len(linked_pet_ids) > 1:
        conflict_notes.append(f"device {device_id} claimed by {', '.join(sorted(linked_pet_ids))}")
    occupancy_state = "free"
    if linked_pet_ids:
        occupancy_state = "conflicted" if len(linked_pet_ids) > 1 else "claimed"
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=[device_id] if len(linked_pet_ids) > 1 else [],
        offline_devices=1 if device.connection_state == "offline" else 0,
        missing_devices=0,
        primary_device_online=bool(pet and pet.device_id == device_id and device.connection_state != "offline"),
        total_devices=len(linked_pet_ids),
    )
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=[device_id] if len(linked_pet_ids) > 1 else [],
        offline_devices=1 if device.connection_state == "offline" else 0,
        missing_devices=0,
        primary_device_online=bool(pet and pet.device_id == device_id and device.connection_state != "offline"),
        total_devices=len(linked_pet_ids),
    )
    summary_line = summary_line_for_sync(len(linked_device_ids := (pet_linked_device_ids(pet) if pet else [])), 1 if device.connection_state != "offline" else 0, 1 if device.connection_state == "offline" else 0, 0, len(conflict_notes))
    return DeviceSyncSummaryResponse(
        device_id=device_id,
        server_time=server_time(),
        pet_id=pet.pet_id if pet else None,
        primary_device_id=pet.device_id if pet else None,
        linked_device_ids=linked_device_ids,
        linked_pet_ids=linked_pet_ids,
        occupancy_state=occupancy_state,
        conflict_notes=conflict_notes,
        recommended_action=recommended_action,
        health_level=health_level,
        summary_line=summary_line,
        primary_hint=primary_hint_for_sync(pet.device_id if pet else None, bool(pet and pet.device_id == device_id and device.connection_state != "offline"), bool(pet), occupancy_state),
        action_hint=action_hint_for_sync(recommended_action, pet.device_id if pet else None),
        device_state=dict(device.state),
        recent_events=pet_device_recent_events(device_id),
        pet_summary=summary,
    )


def broadcast_device_event_to_pet(pet: PetRecord, source_device_id: str, kind: str, message: str, meta: dict | None = None) -> None:
    payload = dict(meta or {})
    payload["source_device_id"] = source_device_id
    payload["broadcast"] = True
    EVENTS.setdefault(pet.pet_id, []).append(
        EventRecord(
            kind=kind,
            text=message,
            tags=["device", "broadcast", "system"],
            created_at=server_time(),
        )
    )
    if source_device_id:
        DEVICE_EVENTS.setdefault(source_device_id, []).append(
            DeviceEventRecord(
                device_id=source_device_id,
                kind=f"broadcast:{kind}",
                message=message,
                created_at=server_time(),
                meta=payload,
            )
        )
    for linked_device_id in pet_linked_device_ids(pet):
        if linked_device_id == source_device_id:
            continue
        DEVICE_EVENTS.setdefault(linked_device_id, []).append(
            DeviceEventRecord(
                device_id=linked_device_id,
                kind=f"sync:{kind}",
                message=message,
                created_at=server_time(),
                meta=payload,
            )
        )


def detach_device_from_pet(pet: PetRecord, device_id: str) -> bool:
    changed = False
    if pet.device_id == device_id:
        pet.device_id = None
        pet.primary_device_id = None
        changed = True
    linked = list(getattr(pet, "linked_device_ids", []) or [])
    if device_id in linked:
        linked = [item for item in linked if item != device_id]
        pet.linked_device_ids = linked
        changed = True
    return changed


def attach_device_to_pet(pet: PetRecord, device_id: str, make_primary: bool = False) -> None:
    linked = list(getattr(pet, "linked_device_ids", []) or [])
    if device_id not in linked:
        linked.append(device_id)
    pet.linked_device_ids = linked
    if make_primary or not pet.device_id:
        pet.device_id = device_id
        pet.primary_device_id = device_id


def sync_pets_with_device(rec: DeviceRecord, reason: str, meta: dict | None = None) -> None:
    pets = pets_for_device(rec.device_id)
    if not pets:
        return

    for pet in pets:
        if rec.connection_state == "offline":
            pet.mood = "lonely" if pet.affection < 40 else pet.mood
            broadcast_device_event_to_pet(pet, rec.device_id, "device-offline", reason, meta)
        elif reason in {"reconnect", "resume", "heartbeat"}:
            pet.energy = normalize_bounds(pet.energy + 5)
            if pet.mood == "lonely":
                pet.mood = "curious"
            broadcast_device_event_to_pet(pet, rec.device_id, "device-reconnect", reason, meta)
        elif meta:
            broadcast_device_event_to_pet(pet, rec.device_id, "device-state", reason, meta)
    save_state()


def pet_payload(pet: PetRecord) -> PetProfileResponse:
    device = DEVICES.get(pet.device_id) if pet.device_id else None
    health = device_health_snapshot(device) if device is not None else None
    initialize_preferences(pet)
    linked_ids = pet_linked_device_ids(pet)
    return PetProfileResponse(
        pet_id=pet.pet_id,
        name=pet.name,
        species_id=pet.species_id,
        theme_id=pet.theme_id,
        model_route_id=pet.model_route_id,
        model_provider=pet.model_provider,
        model_name=pet.model_name,
        growth_stage=pet.growth_stage,
        level=pet.level,
        exp=pet.exp,
        mood=pet.mood,
        energy=pet.energy,
        hunger=pet.hunger,
        affection=pet.affection,
        owner_id=pet.owner_id,
        device_id=pet.device_id,
        linked_device_ids=linked_ids,
        device_connection_state=health["connection_state"] if health else None,
        device_last_seen_at=health["last_seen_at"] if health else None,
        device_is_offline=health["is_offline"] if health else None,
        device_offline_reason=health["offline_reason"] if health else None,
        growth_preferences=dict(getattr(pet, "growth_preferences", {}) or {}),
        preference_notes=list(getattr(pet, "preference_notes", []) or []),
        server_time=server_time(),
    )


def grade_device_capabilities(hardware_model: str | None = None, capabilities: list[str] | None = None) -> dict:
    caps = [item.lower() for item in (capabilities or [])]
    hardware = (hardware_model or "").lower()
    signals = set(caps)
    if hardware:
        signals.add(hardware)

    if any("voice" in item or "audio" in item for item in signals):
        device_class = "voice-first"
        display_mode = "voice-only"
        display_hint = "no-screen or minimal-screen interaction"
        confidence = "medium"
    elif any("oled" in item for item in signals):
        device_class = "oled"
        display_mode = "oled-high-contrast"
        display_hint = "prefer dark background and large expressions"
        confidence = "high"
    elif any("lcd" in item or "screen" in item for item in signals):
        device_class = "lcd"
        display_mode = "color-lcd"
        display_hint = "use compact pet portrait and simple UI slots"
        confidence = "high"
    elif any("touch" in item for item in signals):
        device_class = "touch-rich"
        display_mode = "rich-lcd"
        display_hint = "support richer animations and tap targets"
        confidence = "medium"
    else:
        device_class = "unknown"
        display_mode = "generic"
        display_hint = "fallback to template-safe rendering"
        confidence = "low"

    return {
        "server_time": server_time(),
        "hardware_model": hardware_model,
        "capabilities": list(capabilities or []),
        "device_class": device_class,
        "display_mode": display_mode,
        "display_hint": display_hint,
        "confidence": confidence,
    }


def select_default_preview(hardware_model: str | None = None, capabilities: list[str] | None = None) -> dict:
    caps = [item.lower() for item in (capabilities or [])]
    hardware = (hardware_model or "").lower()

    if any("oled" in item for item in caps) or "oled" in hardware:
        key = "oled"
    elif any("voice" in item or "audio" in item for item in caps) or "voice" in hardware:
        key = "voice"
    elif any("lcd" in item or "screen" in item for item in caps) or "lcd" in hardware:
        key = "lcd"
    elif any("touch" in item for item in caps) or "touch" in hardware:
        key = "rich"
    else:
        key = "default"

    selection = DEFAULT_PREVIEW_SELECTION[key]
    return {
        "server_time": server_time(),
        "hardware_model": hardware_model,
        "capabilities": list(capabilities or []),
        "species_id": selection["species_id"],
        "theme_id": selection["theme_id"],
        "reason": selection["reason"],
        "matched_signals": list(selection["signals"]),
        "display_mode": selection.get("display_mode", "generic"),
        "display_hint": grade_device_capabilities(hardware_model, capabilities)["display_hint"],
    }


def theme_compatibility_items(species_id: str | None = None, firmware_version: str | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for theme in THEME_PACKS:
        compatible = True
        reasons: list[str] = []
        warnings: list[str] = []
        if species_id and theme.get("species_id") not in {species_id, None}:
            compatible = False
            reasons.append(f"theme is for {theme.get('species_id')} not {species_id}")
        theme_min = theme.get("min_firmware_version")
        theme_max = theme.get("max_firmware_version")
        if firmware_version and theme_min and firmware_version < theme_min:
            compatible = False
            reasons.append(f"firmware {firmware_version} is below minimum {theme_min}")
        if firmware_version and theme_max and firmware_version > theme_max:
            compatible = False
            reasons.append(f"firmware {firmware_version} is above maximum {theme_max}")
        if not theme.get("slot_map"):
            warnings.append("theme has no slot map")
        items.append({
            "theme_id": theme.get("theme_id"),
            "species_id": theme.get("species_id"),
            "version": theme.get("version", "0.1.0"),
            "compatible": compatible,
            "reasons": reasons,
            "warnings": warnings,
        })
    return items


def build_device_capability_summary(hardware_model: str | None = None, firmware_version: str | None = None, capabilities: list[str] | None = None) -> dict:
    grade = grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities)
    selection = select_default_preview(hardware_model=hardware_model, capabilities=capabilities)
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == selection["theme_id"]), None)
    species = species_template_for(selection["species_id"])
    compatible_theme_count = sum(1 for item in theme_compatibility_items(species_id=selection["species_id"], firmware_version=firmware_version) if item.get("compatible"))
    compatible_resource_pack_count = sum(
        1 for record in RESOURCE_PACKS.values()
        if record.get("enabled") and (record.get("species_id") in {None, selection["species_id"]})
    )
    ui_slot_count = len(species.get("ui_slots", [])) if species else 0
    notes = [
        f"selected species {selection['species_id']} for {selection['reason']}",
        f"display mode {grade['display_mode']}",
    ]
    if theme:
        notes.append(f"theme version {theme.get('version', '0.1.0')}")
    if firmware_version:
        notes.append(f"firmware {firmware_version}")
    return {
        "server_time": server_time(),
        "hardware_model": hardware_model,
        "firmware_version": firmware_version,
        "capabilities": list(capabilities or []),
        "device_class": grade["device_class"],
        "display_mode": grade["display_mode"],
        "display_hint": grade["display_hint"],
        "confidence": grade["confidence"],
        "recommended_species_id": selection["species_id"],
        "recommended_theme_id": selection["theme_id"],
        "recommended_theme_version": theme.get("version") if theme else None,
        "recommended_theme_name": theme.get("name") if theme else None,
        "recommended_preview_asset": theme.get("preview_asset") if theme else None,
        "ui_slot_count": ui_slot_count,
        "compatible_theme_count": compatible_theme_count,
        "compatible_resource_pack_count": compatible_resource_pack_count,
        "notes": notes,
    }



    if species is None:
        notes.append(f"unknown species: {species_id}")
    if theme is None:
        notes.append(f"unknown theme: {theme_id}")

    palette = theme.get("palette", {}) if theme else {}
    ui_slots = species.get("ui_slots", []) if species else []
    slot_map = theme.get("slot_map", {}) if theme else {}

    if species and theme and theme["theme_id"] not in species.get("allowed_theme_ids", []):
        notes.append("theme not allowed by species template; preview is best-effort only")

    for slot_id in ui_slots:
        rule = RESOURCE_SLOT_RULES.get(slot_id, {})
        layers.append(
            {
                "slot_id": slot_id,
                "resource_path": slot_map.get(slot_id),
                "resource_type": rule.get("resource_type"),
                "width": rule.get("max_width"),
                "height": rule.get("max_height"),
                "format": (rule.get("formats") or [None])[0],
                "notes": None,
            }
        )

    hint = PREVIEW_HINTS.get(species_id, {})
    if hint:
        notes.append(hint.get("headline", ""))

    if pet is not None:
        notes.append(f"pet mood: {pet.mood}, stage: {pet.growth_stage}, level: {pet.level}")

    display_mode, display_hint = preview_display_profile(species_id, theme_id)

    return {
        "server_time": server_time(),
        "species_id": species_id,
        "theme_id": theme_id,
        "pet_id": pet.pet_id if pet else None,
        "name": pet.name if pet else None,
        "growth_stage": pet.growth_stage if pet else None,
        "palette": palette,
        "ui_slots": ui_slots,
        "layers": layers,
        "notes": [item for item in notes if item],
        "display_mode": display_mode,
        "display_hint": display_hint,
    }


@app.get("/api/device/capability/grade", response_model=DeviceCapabilityGradeResponse)
def device_capability_grade(hardware_model: str | None = None, capabilities: list[str] | None = None) -> DeviceCapabilityGradeResponse:
    return DeviceCapabilityGradeResponse(**grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities))


@app.get("/api/device/capability/summary", response_model=DeviceCapabilitySummaryResponse)
def device_capability_summary(hardware_model: str | None = None, firmware_version: str | None = None, capabilities: list[str] | None = None) -> DeviceCapabilitySummaryResponse:
    return DeviceCapabilitySummaryResponse(**build_device_capability_summary(hardware_model=hardware_model, firmware_version=firmware_version, capabilities=capabilities))


@app.post("/api/device/capability/summary", response_model=DeviceCapabilitySummaryBatchResponse)
def device_capability_summary_post(req: DeviceCapabilitySummaryRequest) -> DeviceCapabilitySummaryBatchResponse:
    item = build_device_capability_summary(hardware_model=req.hardware_model, firmware_version=req.firmware_version, capabilities=req.capabilities)
    return DeviceCapabilitySummaryBatchResponse(server_time=server_time(), item=DeviceCapabilitySummaryResponse(**item))


@app.get("/api/preview/sample", response_model=PreviewSampleResponse)
def preview_sample(hardware_model: str | None = None, capabilities: list[str] | None = None, pet_id: str | None = None) -> PreviewSampleResponse:
    selection = select_default_preview(hardware_model=hardware_model, capabilities=capabilities)
    pet = PETS.get(pet_id) if pet_id else None
    preview = build_preview(selection["species_id"], selection["theme_id"], pet)
    display_mode, display_hint = preview_display_profile(selection["species_id"], selection["theme_id"], hardware_model=hardware_model, capabilities=capabilities)
    preview["display_mode"] = display_mode
    preview["display_hint"] = display_hint
    return PreviewSampleResponse(
        server_time=server_time(),
        selection=TemplateSelectionResponse(**selection),
        preview=PetPreviewResponse(
            server_time=preview["server_time"],
            species_id=preview["species_id"],
            theme_id=preview["theme_id"],
            pet_id=preview["pet_id"],
            name=preview["name"],
            growth_stage=preview["growth_stage"],
            palette=preview["palette"],
            ui_slots=preview["ui_slots"],
            layers=[PreviewLayerItem(**item) for item in preview["layers"]],
            notes=preview["notes"],
            display_mode=preview.get("display_mode"),
            display_hint=preview.get("display_hint"),
        ),
    )


@app.get("/api/preview/{species_id}/{theme_id}", response_model=PetPreviewResponse)
def preview_combo(species_id: str, theme_id: str, pet_id: str | None = None) -> PetPreviewResponse:
    pet = PETS.get(pet_id) if pet_id else None
    preview = build_preview(species_id, theme_id, pet)
    display_mode, display_hint = preview_display_profile(species_id, theme_id)
    preview["display_mode"] = display_mode
    preview["display_hint"] = display_hint
    return PetPreviewResponse(
        server_time=preview["server_time"],
        species_id=preview["species_id"],
        theme_id=preview["theme_id"],
        pet_id=preview["pet_id"],
        name=preview["name"],
        growth_stage=preview["growth_stage"],
        palette=preview["palette"],
        ui_slots=preview["ui_slots"],
        layers=[PreviewLayerItem(**item) for item in preview["layers"]],
        notes=preview["notes"],
        display_mode=preview.get("display_mode"),
        display_hint=preview.get("display_hint"),
    )


@app.get("/api/species/templates", response_model=SpeciesTemplateResponse)
def species_templates() -> SpeciesTemplateResponse:
    return SpeciesTemplateResponse(
        server_time=server_time(),
        items=[SpeciesTemplateItem(**item) for item in SPECIES_TEMPLATES],
    )


@app.get("/api/model/routes", response_model=ModelRouteResponse)
def model_routes() -> ModelRouteResponse:
    return ModelRouteResponse(
        server_time=server_time(),
        items=[ModelRouteItem(**item) for item in MODEL_ROUTES],
    )


@app.get("/api/model/routes/config", response_model=ModelRouteConfigResponse)
def model_routes_config() -> ModelRouteConfigResponse:
    return ModelRouteConfigResponse(
        server_time=server_time(),
        default_route_id=MODEL_ROUTE_CONFIG.get("default_route_id"),
        fallback_route_ids=list(MODEL_ROUTE_CONFIG.get("fallback_route_ids", [])),
        prefer_enabled=bool(MODEL_ROUTE_CONFIG.get("prefer_enabled", True)),
        allow_manual_override=bool(MODEL_ROUTE_CONFIG.get("allow_manual_override", True)),
        routing_notes=str(MODEL_ROUTE_CONFIG.get("routing_notes", "")),
    )


@app.patch("/api/model/routes/config", response_model=ModelRouteConfigResponse)
def model_routes_config_update(req: ModelRouteConfigUpdateRequest) -> ModelRouteConfigResponse:
    if req.default_route_id is not None:
        MODEL_ROUTE_CONFIG["default_route_id"] = req.default_route_id
    if req.fallback_route_ids is not None:
        MODEL_ROUTE_CONFIG["fallback_route_ids"] = list(dict.fromkeys(req.fallback_route_ids))
    if req.prefer_enabled is not None:
        MODEL_ROUTE_CONFIG["prefer_enabled"] = req.prefer_enabled
    if req.allow_manual_override is not None:
        MODEL_ROUTE_CONFIG["allow_manual_override"] = req.allow_manual_override
    if req.routing_notes is not None:
        MODEL_ROUTE_CONFIG["routing_notes"] = req.routing_notes
    save_state()
    return model_routes_config()


@app.post("/api/model/routes/resolve", response_model=ModelRouteResolveResponse)
def model_routes_resolve(req: ModelRouteResolveRequest) -> ModelRouteResolveResponse:
    route, fallback_used, fallback_reason, available_ids = resolve_model_route(
        route_id=req.route_id,
        fallback_route_ids=req.fallback_route_ids or None,
        prefer_enabled=req.prefer_enabled,
        allow_fallback=req.allow_fallback,
    )
    if route is None:
        raise HTTPException(status_code=404, detail=fallback_reason or "no route available")
    return ModelRouteResolveResponse(
        server_time=server_time(),
        requested_route_id=req.route_id,
        selected_route=model_route_item_from_dict(route),
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        available_route_ids=available_ids,
        config_default_route_id=MODEL_ROUTE_CONFIG.get("default_route_id"),
    )


@app.post("/api/model/routes/apply/{pet_id}", response_model=PetProfileResponse)
def apply_route_to_pet(pet_id: str, req: ModelRouteResolveRequest) -> PetProfileResponse:
    pet = pet_or_404(pet_id)
    resolved, fallback_used, fallback_reason, _ = resolve_model_route(
        route_id=req.route_id or pet.model_route_id,
        fallback_route_ids=req.fallback_route_ids or None,
        prefer_enabled=req.prefer_enabled,
        allow_fallback=req.allow_fallback,
    )
    if resolved is None:
        raise HTTPException(status_code=404, detail=fallback_reason or "no route available")
    pet.model_route_id = resolved["id"]
    pet.model_provider = resolved["provider"]
    pet.model_name = resolved["model_name"]
    save_state()
    payload = pet_payload(pet)
    return payload


@app.get("/api/protocol", response_model=ProtocolInfo)
def protocol_info() -> ProtocolInfo:
    return ProtocolInfo(server_time=server_time())


@app.post("/api/device/register", response_model=DeviceRegisterResponse)
def device_register(req: DeviceRegisterRequest) -> DeviceRegisterResponse:
    rec = DEVICES.get(req.device_id)
    if rec is None:
        rec = DeviceRecord(
            device_id=req.device_id,
            hardware_model=req.hardware_model,
            firmware_version=req.firmware_version,
            capabilities=list(req.capabilities),
        )
        DEVICES[req.device_id] = rec
    else:
        rec.hardware_model = req.hardware_model
        rec.firmware_version = req.firmware_version
        rec.capabilities = list(req.capabilities)
    device_touch(rec)
    rec.connection_state = "paired" if rec.bound else "unbound"
    record_device_event(
        req.device_id,
        "register",
        "device registered or refreshed",
        {"hardware_model": req.hardware_model, "firmware_version": req.firmware_version, "bound": rec.bound},
    )
    return DeviceRegisterResponse(
        device_id=req.device_id,
        registered=True,
        binding_required=not rec.bound,
        server_time=server_time(),
        next_step="request_binding" if not rec.bound else "ready",
    )


@app.post("/api/device/bind/request", response_model=BindRequestResponse)
def device_bind_request(req: BindRequest) -> BindRequestResponse:
    rec = DEVICES.setdefault(req.device_id, DeviceRecord(device_id=req.device_id))
    rec.bind_code = new_bind_code()
    rec.bind_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
    return BindRequestResponse(
        device_id=req.device_id,
        bind_code=rec.bind_code,
        expires_in_seconds=600,
        expires_at=bind_expires_iso(rec.bind_expires_at),
    )


@app.post("/api/device/bind/confirm", response_model=BindConfirmResponse)
def device_bind_confirm(req: BindConfirmRequest) -> BindConfirmResponse:
    rec = DEVICES.get(req.device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not registered; register before binding")
    if not rec.bind_code:
        raise HTTPException(status_code=400, detail="bind code not requested; call /api/device/bind/request first")
    if rec.bind_code != req.bind_code:
        raise HTTPException(status_code=400, detail="invalid bind code; request a fresh code and try again")
    if rec.bind_expires_at and datetime.now(timezone.utc).timestamp() > rec.bind_expires_at:
        rec.bind_code = None
        rec.bind_expires_at = None
        raise HTTPException(status_code=400, detail="bind code expired; request a new code")
    rec.bound = True
    rec.owner_id = req.owner_id
    rec.connection_state = "paired"
    device_touch(rec)
    record_device_event(req.device_id, "bind_confirm", "device binding confirmed", {"owner_id": req.owner_id})
    rec.bind_code = None
    rec.bind_expires_at = None
    if req.device_id not in PETS:
        pet_id = f"pet-{req.device_id}"
        PETS[pet_id] = PetRecord(pet_id=pet_id, owner_id=req.owner_id, device_id=req.device_id)
    else:
        pet_id = next((pid for pid, pet in PETS.items() if pet.device_id == req.device_id), None)
    save_state()
    return BindConfirmResponse(device_id=req.device_id, bound=True, owner_id=req.owner_id, pet_id=pet_id, server_time=server_time())


@app.get("/api/device/{device_id}", response_model=DeviceDetailResponse)
def device_detail(device_id: str) -> DeviceDetailResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    health = device_health_snapshot(rec)
    return DeviceDetailResponse(
        device_id=rec.device_id,
        hardware_model=rec.hardware_model,
        firmware_version=rec.firmware_version,
        capabilities=list(rec.capabilities),
        bound=rec.bound,
        owner_id=rec.owner_id,
        bind_code=rec.bind_code,
        bind_expires_at=bind_expires_iso(rec.bind_expires_at),
        state={
            **dict(rec.state),
            "connection_state": health["connection_state"],
            "last_seen_at": health["last_seen_at"],
            "offline_reason": health["offline_reason"],
            "event_count": len(DEVICE_EVENTS.get(device_id, [])),
        },
    )


@app.get("/api/device/{device_id}/health", response_model=DeviceHealthResponse)
def device_health(device_id: str, stale_after_seconds: int = 300) -> DeviceHealthResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    snapshot = device_health_snapshot(rec, stale_after_seconds=stale_after_seconds)
    if snapshot["is_offline"]:
        rec.offline_reason = snapshot["offline_reason"]
    return DeviceHealthResponse(**snapshot)


@app.get("/api/device/{device_id}/events", response_model=DeviceEventListResponse)
def device_events(device_id: str) -> DeviceEventListResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    items = DEVICE_EVENTS.get(device_id, [])
    return DeviceEventListResponse(
        device_id=device_id,
        server_time=server_time(),
        items=[DeviceEventItem(**item.__dict__) for item in items],
    )


@app.post("/api/device/{device_id}/event", response_model=DeviceEventResponse)
def device_event(device_id: str, req: DeviceEventRequest) -> DeviceEventResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    record_device_event(device_id, req.kind, req.message, req.meta)
    if req.kind == "offline":
        rec.connection_state = "offline"
        rec.offline_reason = req.message
    elif req.kind in {"reconnect", "heartbeat", "resume"}:
        device_touch(rec)
        rec.connection_state = "paired" if rec.bound else "unbound"
        rec.offline_reason = None
    save_state()
    return DeviceEventResponse(ok=True, device_id=device_id, event_count=len(DEVICE_EVENTS.get(device_id, [])), server_time=server_time())


@app.post("/api/device/heartbeat", response_model=DeviceHeartbeatResponse)
def device_heartbeat(req: DeviceHeartbeatRequest) -> DeviceHeartbeatResponse:
    rec = DEVICES.get(req.device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not registered")
    was_offline = device_is_offline(rec)
    device_touch(rec)
    rec.connection_state = "paired" if rec.bound else "unbound"
    record_device_event(req.device_id, "heartbeat", "device heartbeat received", {"note": req.note})
    if was_offline:
        record_device_event(req.device_id, "resume", "device recovered from offline via heartbeat", {"note": req.note})
        sync_pets_with_device(rec, "resume", {"note": req.note})
    save_state()
    return DeviceHeartbeatResponse(
        ok=True,
        device_id=rec.device_id,
        connection_state=rec.connection_state,
        last_seen_at=rec.last_seen_at,
        server_time=server_time(),
        state=dict(rec.state),
        hardware_model=rec.hardware_model,
        firmware_version=rec.firmware_version,
        capabilities=list(rec.capabilities),
        bound=rec.bound,
        owner_id=rec.owner_id,
        bind_code=rec.bind_code,
        bind_expires_at=bind_expires_iso(rec.bind_expires_at),
    )


@app.post("/api/device/state", response_model=DeviceStateResponse)
def device_state(req: DeviceStateRequest) -> DeviceStateResponse:
    rec = DEVICES.get(req.device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not registered")
    was_offline = device_is_offline(rec)
    rec.state = req.state
    device_touch(rec)
    rec.connection_state = "paired" if rec.bound else "unbound"
    if req.state.get("offline"):
        rec.connection_state = "offline"
        rec.offline_reason = str(req.state.get("offline_reason") or "device reported offline")
        record_device_event(req.device_id, "offline", rec.offline_reason, {"state": dict(req.state)})
        sync_pets_with_device(rec, rec.offline_reason, req.state)
    else:
        if rec.bound:
            record_device_event(req.device_id, "state", "device state updated", {"state": dict(req.state)})
        if was_offline or rec.connection_state == "offline":
            record_device_event(req.device_id, "resume", "device recovered from offline", {"state": dict(req.state)})
            sync_pets_with_device(rec, "resume", req.state)
        rec.connection_state = "paired" if rec.bound else "unbound"
        rec.offline_reason = None
    return DeviceStateResponse(
        ok=True,
        device_id=req.device_id,
        server_time=server_time(),
        binding_state="bound" if rec.bound else "unbound",
    )


@app.post("/api/pet/create", response_model=PetProfileResponse)
def pet_create(req: PetCreateRequest) -> PetProfileResponse:
    pet = PETS.get(req.pet_id)
    if pet is None:
        pet = PetRecord(
            pet_id=req.pet_id,
            name=req.name,
            species_id=req.species_id,
            theme_id=req.theme_id,
            model_route_id=req.model_route_id,
            owner_id=req.owner_id,
            primary_device_id=req.device_id,
            device_id=req.device_id,
        )
        PETS[req.pet_id] = pet
    align_pet_to_species(pet)
    apply_model_route_to_pet(pet)
    if pet.device_id:
        device = DEVICES.get(pet.device_id)
        if device is not None:
            snapshot = device_health_snapshot(device)
            pet.device_connection_state = snapshot["connection_state"]
            pet.device_last_seen_at = snapshot["last_seen_at"]
            pet.device_is_offline = snapshot["is_offline"]
            pet.device_offline_reason = snapshot["offline_reason"]
    return pet_payload(pet)


@app.get("/api/pet/{pet_id}", response_model=PetProfileResponse)
def pet_get(pet_id: str) -> PetProfileResponse:
    pet = pet_or_404(pet_id)
    return pet_payload(pet)


@app.patch("/api/pet/{pet_id}", response_model=PetProfileResponse)
def pet_update(pet_id: str, req: PetUpdateRequest) -> PetProfileResponse:
    pet = pet_or_404(pet_id)
    for key, value in req.model_dump(exclude_none=True).items():
        if key == "linked_device_ids":
            pet.linked_device_ids = list(value)
            continue
        setattr(pet, key, value)
    if req.level is not None and req.growth_stage is None:
        pet.growth_stage = growth_stage_for_level(pet.level)
    align_pet_to_species(pet)
    apply_model_route_to_pet(pet)
    if pet.device_id:
        device = DEVICES.get(pet.device_id)
        if device is not None:
            snapshot = device_health_snapshot(device)
            pet.device_connection_state = snapshot["connection_state"]
            pet.device_last_seen_at = snapshot["last_seen_at"]
            pet.device_is_offline = snapshot["is_offline"]
            pet.device_offline_reason = snapshot["offline_reason"]
    return pet_payload(pet)


@app.get("/api/pet/{pet_id}/devices", response_model=PetDeviceListResponse)
def pet_devices(pet_id: str) -> PetDeviceListResponse:
    pet = pet_or_404(pet_id)
    linked_ids = pet_linked_device_ids(pet)
    items: list[PetDeviceLinkItem] = []
    for idx, device_id in enumerate(linked_ids):
        device = DEVICES.get(device_id)
        health = device_health_snapshot(device) if device is not None else None
        items.append(
            PetDeviceLinkItem(
                device_id=device_id,
                hardware_model=device.hardware_model if device is not None else None,
                firmware_version=device.firmware_version if device is not None else None,
                connection_state=health["connection_state"] if health else None,
                last_seen_at=health["last_seen_at"] if health else None,
                is_primary=idx == 0,
                is_online=bool(health and not health["is_offline"]),
            )
        )
    return PetDeviceListResponse(
        pet_id=pet_id,
        server_time=server_time(),
        primary_device_id=linked_ids[0] if linked_ids else None,
        linked_device_ids=linked_ids,
        total=len(items),
        items=items,
    )


@app.post("/api/pet/{pet_id}/devices/link", response_model=PetDeviceLinkResponse)
def link_pet_device(pet_id: str, req: PetDeviceLinkRequest) -> PetDeviceLinkResponse:
    pet = pet_or_404(pet_id)
    device = DEVICES.get(req.device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="device not found")
    owner = pet_device_owner(req.device_id)
    if owner is not None and owner.pet_id != pet.pet_id:
        if req.make_primary:
            detach_device_from_pet(owner, req.device_id)
            record_device_conflict(req.device_id, [owner.pet_id, pet.pet_id], f"device {req.device_id} reassigned to {pet.pet_id}")
        else:
            record_device_conflict(req.device_id, [owner.pet_id, pet.pet_id], f"device {req.device_id} already linked to another pet")
            save_state()
            raise HTTPException(status_code=409, detail="device already linked to another pet")
    attach_device_to_pet(pet, req.device_id, make_primary=req.make_primary)
    save_state()
    return PetDeviceLinkResponse(ok=True, pet_id=pet_id, primary_device_id=pet.device_id, linked_device_ids=pet_linked_device_ids(pet), server_time=server_time())


@app.post("/api/pet/{pet_id}/devices/unlink", response_model=PetDeviceUnlinkResponse)
def unlink_pet_device(pet_id: str, req: PetDeviceUnlinkRequest) -> PetDeviceUnlinkResponse:
    pet = pet_or_404(pet_id)
    target_id = req.device_id or pet.device_id
    if not target_id:
        raise HTTPException(status_code=400, detail="device_id required")
    changed = detach_device_from_pet(pet, target_id)
    if req.remove_primary and pet.device_id == target_id:
        pet.device_id = None
        pet.primary_device_id = None
        changed = True
    if not changed:
        raise HTTPException(status_code=404, detail="device not linked to this pet")
    if pet.device_id is None and pet.linked_device_ids:
        pet.device_id = pet.linked_device_ids[0]
        pet.primary_device_id = pet.device_id
    save_state()
    return PetDeviceUnlinkResponse(ok=True, pet_id=pet_id, primary_device_id=pet.device_id, linked_device_ids=pet_linked_device_ids(pet), server_time=server_time())


@app.post("/api/pet/{pet_id}/devices/primary", response_model=PetDevicePrimaryResponse)
def set_pet_primary_device(pet_id: str, req: PetDevicePrimaryRequest) -> PetDevicePrimaryResponse:
    pet = pet_or_404(pet_id)
    if req.device_id not in pet_linked_device_ids(pet):
        raise HTTPException(status_code=404, detail="device not linked to this pet")
    previous_primary = pet.device_id
    pet.device_id = req.device_id
    pet.primary_device_id = req.device_id
    if previous_primary != req.device_id:
        record_device_conflict(req.device_id, [pet.pet_id], f"pet {pet.pet_id} primary device switched to {req.device_id}")
    save_state()
    return PetDevicePrimaryResponse(ok=True, pet_id=pet_id, primary_device_id=pet.device_id, linked_device_ids=pet_linked_device_ids(pet), server_time=server_time())


@app.get("/api/device/{device_id}/pet", response_model=PetProfileResponse)
def device_pet(device_id: str) -> PetProfileResponse:
    device = DEVICES.get(device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="device not found")
    pet = pet_device_owner(device_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="pet not found for this device")
    return pet_payload(pet)


@app.get("/api/pet/{pet_id}/sync", response_model=PetSyncSummaryResponse)
def pet_sync_summary(pet_id: str) -> PetSyncSummaryResponse:
    pet = pet_or_404(pet_id)
    return build_pet_sync_summary(pet)


@app.get("/api/device/{device_id}/sync", response_model=DeviceSyncSummaryResponse)
def device_sync_summary(device_id: str) -> DeviceSyncSummaryResponse:
    return build_device_sync_summary(device_id)


@app.get("/api/pet/{pet_id}/broadcast", response_model=PetBroadcastSummaryResponse)
def pet_broadcast_summary(pet_id: str) -> PetBroadcastSummaryResponse:
    pet = pet_or_404(pet_id)
    linked_ids = pet_linked_device_ids(pet)
    device_items: list[PetSyncDeviceItem] = []
    broadcast_items: list[PetBroadcastItem] = []
    sync_notes: list[str] = []
    conflict_notes: list[str] = []
    conflict_device_ids: list[str] = []
    online_devices = 0
    offline_devices = 0
    missing_devices = 0
    for idx, device_id in enumerate(linked_ids):
        device = DEVICES.get(device_id)
        health = device_health_snapshot(device) if device is not None else None
        claims = [item.pet_id for item in pets_claiming_device(device_id)]
        if len(claims) > 1:
            conflict_device_ids.append(device_id)
            conflict_notes.append(f"device {device_id} claimed by {', '.join(sorted(set(claims)))}")
        if health is None:
            missing_devices += 1
            sync_notes.append(f"device {device_id} missing")
        elif health["is_offline"]:
            offline_devices += 1
            sync_notes.append(f"device {device_id} offline")
        else:
            online_devices += 1
        device_items.append(
            PetSyncDeviceItem(
                device_id=device_id,
                is_primary=idx == 0,
                connection_state=health["connection_state"] if health else None,
                last_seen_at=health["last_seen_at"] if health else None,
                is_online=bool(health and not health["is_offline"]),
                offline_reason=health["offline_reason"] if health else None,
                event_count=len(DEVICE_EVENTS.get(device_id, [])),
            )
        )
        for item in pet_device_recent_events(device_id, limit=3):
            broadcast_items.append(
                PetBroadcastItem(
                    device_id=device_id,
                    kind=item["kind"],
                    message=item["message"],
                    created_at=item["created_at"],
                    meta=dict(item["meta"]),
                )
            )
    occupancy_state = "conflicted" if conflict_device_ids else "claimed" if linked_ids else "free"
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=bool(device_items and device_items[0].is_online),
        total_devices=len(device_items),
    )
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=bool(device_items and device_items[0].is_online),
        total_devices=len(device_items),
    )
    return PetBroadcastSummaryResponse(
        pet_id=pet.pet_id,
        server_time=server_time(),
        total_devices=len(device_items),
        online_devices=online_devices,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        conflict_device_ids=conflict_device_ids,
        conflict_notes=conflict_notes,
        primary_device_id=pet.device_id,
        linked_device_ids=linked_ids,
        recommended_action=recommended_action,
        health_level=health_level,
        summary_line=summary_line_for_sync(len(device_items), online_devices, offline_devices, missing_devices, len(conflict_device_ids)),
        primary_hint=primary_hint_for_sync(pet.device_id, bool(device_items and device_items[0].is_online), bool(linked_ids), occupancy_state),
        action_hint=action_hint_for_sync(recommended_action, pet.device_id),
        broadcast_items=broadcast_items[-15:],
        device_items=device_items,
        sync_notes=sync_notes,
    )


@app.post("/api/pet/{pet_id}/event", response_model=PetEventResponse)
def pet_event(pet_id: str, req: PetEventRequest) -> PetEventResponse:
    pet = pet_or_404(pet_id)
    initialize_preferences(pet)
    kind = (req.kind or "").strip().lower()
    event_tags = list(req.tags)
    event_tags.append(f"category:{event_category_for(kind)}")
    EVENTS.setdefault(pet_id, []).append(
        EventRecord(kind=kind, text=req.text, tags=event_tags, created_at=server_time())
    )
    actions = apply_event_to_pet(pet, kind, req.text)
    evolve_growth_preferences(pet, kind, req.text, actions)
    level_ups = level_up_if_needed(pet)
    recent_kind = kind
    if level_ups:
        growth_kind = "growth"
        EVENTS[pet_id].append(
            EventRecord(
                kind=growth_kind,
                text=f"leveled up {level_ups} time(s) to level {pet.level}",
                tags=["growth", "system", "category:system"],
                created_at=server_time(),
            )
        )
        recent_kind = growth_kind
    save_state()
    return PetEventResponse(ok=True, pet_id=pet_id, event_count=len(EVENTS[pet_id]), recent_kind=recent_kind, server_time=server_time())


@app.get("/api/pet/{pet_id}/memory/summary", response_model=MemorySummaryResponse)
def pet_memory_summary(pet_id: str) -> MemorySummaryResponse:
    pet_or_404(pet_id)
    memories = MEMORY.get(pet_id, [])
    short_term = sum(1 for item in memories if item.kind == "short")
    long_term = sum(1 for item in memories if item.kind == "long")
    event_count = len(EVENTS.get(pet_id, []))
    return MemorySummaryResponse(
        pet_id=pet_id,
        short_term=short_term,
        long_term=long_term,
        event_count=event_count,
        server_time=server_time(),
    )


@app.get("/api/pet/{pet_id}/growth", response_model=PetGrowthSummaryResponse)
def pet_growth_summary(pet_id: str) -> PetGrowthSummaryResponse:
    pet = pet_or_404(pet_id)
    initialize_preferences(pet)
    species = species_template_for(pet.species_id) or {}
    growth_curve = dict(species.get("growth_curve", {}))
    recent_events = [
        {
            "kind": item.kind,
            "text": item.text,
            "tags": list(item.tags),
            "created_at": item.created_at,
        }
        for item in EVENTS.get(pet_id, [])[-5:]
    ]
    next_level_exp = pet.level * 10
    return PetGrowthSummaryResponse(
        pet_id=pet.pet_id,
        name=pet.name,
        species_id=pet.species_id,
        growth_stage=pet.growth_stage,
        level=pet.level,
        exp=pet.exp,
        next_level_exp=next_level_exp,
        growth_curve=growth_curve,
        recent_events=recent_events,
        growth_preferences=dict(getattr(pet, "growth_preferences", {}) or {}),
        preference_notes=list(getattr(pet, "preference_notes", []) or []),
        server_time=server_time(),
    )


@app.get("/api/pet/{pet_id}/events", response_model=PetEventSummaryResponse)
def pet_events_summary(pet_id: str) -> PetEventSummaryResponse:
    pet_or_404(pet_id)
    items = EVENTS.get(pet_id, [])
    categories: dict[str, int] = {}
    summary_items: dict[str, PetEventSummaryItem] = {}
    recent_items = [
        {
            "kind": item.kind,
            "text": item.text,
            "tags": list(item.tags),
            "created_at": item.created_at,
        }
        for item in items[-10:]
    ]
    for item in items:
        category = event_category_for(item.kind)
        categories[category] = categories.get(category, 0) + 1
        current = summary_items.get(item.kind)
        if current is None:
            summary_items[item.kind] = PetEventSummaryItem(
                kind=item.kind,
                count=1,
                last_text=item.text,
                last_created_at=item.created_at,
            )
        else:
            current.count += 1
            current.last_text = item.text
            current.last_created_at = item.created_at
    return PetEventSummaryResponse(
        pet_id=pet_id,
        server_time=server_time(),
        total=len(items),
        recent_event_count=min(len(items), 10),
        categories=categories,
        recent_items=recent_items,
        items=list(summary_items.values()),
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    pet = pet_or_404(req.pet_id)
    reply = f"收到啦，我会记住你刚刚说的：{req.user_text[:80]}"
    initialize_preferences(pet)
    actions = ["listen", "respond"]
    if pet.energy < 20:
        actions.append("sleep")
    elif pet.hunger > 80:
        actions.append("eat")
    if req.context.get("mode") == "comfort":
        pet.affection = normalize_bounds(pet.affection + 1)
        pet.mood = "curious" if pet.mood == "neutral" else pet.mood
    evolve_growth_preferences(pet, "chat", req.user_text, actions)
    MEMORY.setdefault(req.pet_id, []).append(
        MemoryRecord(
            kind="short",
            text=req.user_text,
            tags=["chat", "context"],
            created_at=server_time(),
        )
    )
    save_state()
    return ChatResponse(reply_text=reply, emotion=pet.mood, actions=actions, server_time=server_time())


@app.get("/api/memory/{pet_id}", response_model=MemoryListResponse)
def read_memory(pet_id: str, kind: str | None = None, keyword: str | None = None, limit: int = 20) -> MemoryListResponse:
    pet_or_404(pet_id)
    items = MEMORY.get(pet_id, [])
    filtered: list[MemoryRecord] = []
    for item in items:
        if kind and item.kind != kind:
            continue
        if keyword and keyword.lower() not in item.text.lower() and not any(keyword.lower() in tag.lower() for tag in item.tags):
            continue
        filtered.append(item)
    filtered = filtered[-max(1, min(limit, 100)) :]
    return MemoryListResponse(
        pet_id=pet_id,
        server_time=server_time(),
        total=len(items),
        short_term=sum(1 for item in items if item.kind == "short"),
        long_term=sum(1 for item in items if item.kind == "long"),
        event_count=sum(1 for item in items if item.kind == "event"),
        items=[MemoryItem(kind=item.kind, text=item.text, tags=list(item.tags), created_at=item.created_at) for item in filtered],
    )


@app.post("/api/memory/{pet_id}")
def write_memory(pet_id: str, req: MemoryWriteRequest):
    pet = pet_or_404(pet_id)
    MEMORY.setdefault(pet_id, []).append(
        MemoryRecord(
            kind=req.item.kind,
            text=req.item.text,
            tags=req.item.tags,
            created_at=req.item.created_at or server_time(),
        )
    )
    initialize_preferences(pet)
    if req.item.kind == "short":
        pet.exp += 1
        evolve_growth_preferences(pet, "chat", req.item.text, ["listen"])
    elif req.item.kind == "long":
        pet.affection = normalize_bounds(pet.affection + 1)
        pet.exp += 2
        evolve_growth_preferences(pet, "praise", req.item.text, ["bond"])
    elif req.item.kind == "event":
        pet.exp += 3
        evolve_growth_preferences(pet, "care", req.item.text, ["notice"])
    level_up_if_needed(pet)
    save_state()
    return {"ok": True, "pet_id": pet_id, "server_time": server_time(), "count": len(MEMORY[pet_id])}


@app.get("/api/resource/packs", response_model=ResourcePackListResponse)
def resource_packs() -> ResourcePackListResponse:
    items = [resource_pack_item_from_record(record) for record in RESOURCE_PACKS.values()]
    return ResourcePackListResponse(server_time=server_time(), items=items)


@app.get("/api/resource/packs/{pack_id}", response_model=ResourcePackDetailResponse)
def resource_pack_detail(pack_id: str) -> ResourcePackDetailResponse:
    record = resource_pack_record_for(pack_id)
    if record is None:
        raise HTTPException(status_code=404, detail="resource pack not found")
    return ResourcePackDetailResponse(server_time=server_time(), item=resource_pack_item_from_record(record))


@app.post("/api/resource/packs/import", response_model=ResourcePackImportResponse)
def resource_pack_import(req: ResourcePackImportRequest) -> ResourcePackImportResponse:
    valid, errors, warnings = validate_resource_pack(req.manifest)
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors, "warnings": warnings})
    existing = RESOURCE_PACKS.get(req.manifest.pack_id)
    previous_versions = list(existing.get("previous_versions", [])) if existing else []
    if existing and existing.get("active_version"):
        previous_versions.append(existing["active_version"])
    record = resource_pack_manifest_to_record(req.manifest, enabled=req.enabled, previous_versions=previous_versions)
    if existing and not req.replace:
        record["previous_versions"] = previous_versions + [existing.get("active_version")] if existing.get("active_version") else previous_versions
    RESOURCE_PACKS[req.manifest.pack_id] = record
    save_state()
    return ResourcePackImportResponse(
        ok=True,
        pack_id=req.manifest.pack_id,
        imported=True,
        enabled=record["enabled"],
        active_version=record.get("active_version"),
        server_time=server_time(),
        warnings=warnings,
    )


@app.patch("/api/resource/packs/{pack_id}/enable", response_model=ResourcePackActionResponse)
def resource_pack_enable(pack_id: str, req: ResourcePackEnableRequest) -> ResourcePackActionResponse:
    record = enable_resource_pack(pack_id, req.enabled)
    return ResourcePackActionResponse(
        ok=True,
        pack_id=pack_id,
        enabled=record.get("enabled", False),
        active_version=record.get("active_version"),
        previous_versions=list(record.get("previous_versions", [])),
        server_time=server_time(),
        note="enabled" if req.enabled else "disabled",
    )


@app.post("/api/resource/packs/{pack_id}/rollback", response_model=ResourcePackActionResponse)
def resource_pack_rollback(pack_id: str, version: str | None = None) -> ResourcePackActionResponse:
    record = rollback_resource_pack(pack_id, version)
    return ResourcePackActionResponse(
        ok=True,
        pack_id=pack_id,
        enabled=record.get("enabled", False),
        active_version=record.get("active_version"),
        previous_versions=list(record.get("previous_versions", [])),
        server_time=server_time(),
        note=f"rolled back to {record.get('active_version')}",
    )


@app.get("/api/theme/compatibility", response_model=ThemePackCompatibilityResponse)
def theme_compatibility(species_id: str | None = None, firmware_version: str | None = None) -> ThemePackCompatibilityResponse:
    return ThemePackCompatibilityResponse(
        server_time=server_time(),
        items=[ThemePackCompatibilityItem(**item) for item in theme_compatibility_items(species_id=species_id, firmware_version=firmware_version)],
    )


@app.post("/api/theme/validate", response_model=ThemePackValidateResponse)
def theme_validate(req: ThemePackValidateRequest) -> ThemePackValidateResponse:
    valid, errors, warnings = validate_theme_pack(req.theme)
    return ThemePackValidateResponse(
        ok=True,
        valid=valid,
        theme_id=req.theme.theme_id,
        errors=errors,
        warnings=warnings,
        server_time=server_time(),
    )


@app.post("/api/resource/validate", response_model=ResourcePackValidateResponse)
def resource_validate(req: ResourcePackValidateRequest) -> ResourcePackValidateResponse:
    valid, errors, warnings = validate_resource_pack(req.manifest)
    return ResourcePackValidateResponse(
        ok=True,
        valid=valid,
        pack_id=req.manifest.pack_id,
        errors=errors,
        warnings=warnings,
        server_time=server_time(),
    )


@app.get("/api/assets/manifest")
def assets_manifest():
    return {"server_time": server_time(), "items": ASSET_MANIFEST}


@app.get("/api/assets/manifest/sample")
def assets_manifest_sample():
    return {
        "server_time": server_time(),
        "items": [
            AssetsManifestItem(id="cat-default", type="species-template", version="0.1.0").model_dump(),
            AssetsManifestItem(id="cat-gold-day", type="theme-pack", version="0.1.0").model_dump(),
        ],
    }
