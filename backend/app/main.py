from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from html import escape
import json
from typing import Any, Optional, Dict, Tuple, List

from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from .models import (
    AssetsManifestItem,
    BindConfirmRequest,
    BindConfirmResponse,
    BindRequest,
    BindRequestResponse,
    ChatRequest,
    ChatResponse,
    LLMRequest,
    LLMResponse,
    LLMConfigResponse,
    LLMConfigUpdateRequest,
    LLMHealthCheckResponse,
    ConversationListResponse,
    ConversationDetailResponse,
    ConversationHistory,
    DeviceCapabilityGradeResponse,
    DeviceCapabilitySummaryBatchResponse,
    DeviceCapabilitySummaryRequest,
    DeviceCapabilitySummaryResponse,
    DeviceDetailResponse,
    DeviceDisplayProfileBatchResponse,
    DeviceDisplayProfileResponse,
    DeviceEventItem,
    DeviceEventListResponse,
    DeviceEventRequest,
    DeviceEventResponse,
    DeviceHealthResponse,
    DeviceHeartbeatRequest,
    DeviceHeartbeatResponse,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceStateRequest,
    DeviceStateResponse,
    DeviceSummaryMiniResponse,
    DeviceSummaryResponse,
    DeviceSyncSummaryResponse,
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
    PetEventRequest,
    PetEventResponse,
    PetEventSummaryItem,
    PetEventSummaryResponse,
    PetGrowthSummaryResponse,
    PetPreviewResponse,
    PetProfileResponse,
    PetSyncDeviceItem,
    PetSyncSummaryResponse,
    PetBroadcastItem,
    PetBroadcastSummaryResponse,
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
    TemplateSelectionDetailResponse,
    TemplateSelectionResponse,
    ThemePackCompatibilityItem,
    ThemePackCompatibilityResponse,
    ThemePackItem,
    ThemePackResponse,
    ThemePackValidateRequest,
    ThemePackValidateResponse,
    SyncMiniResponse,
 )
from .storage import DEVICES, DEVICE_EVENTS, PETS, MEMORY, EVENTS, ASSET_MANIFEST, MODEL_ROUTES, MODEL_ROUTE_CONFIG, SPECIES_TEMPLATES, THEME_PACKS, RESOURCE_PACKS, RESOURCE_SLOT_RULES, DEFAULT_PREVIEW_SELECTION, PREVIEW_HINTS, DeviceRecord, DeviceEventRecord, PetRecord, MemoryRecord, EventRecord, new_bind_code, now_iso, save_state, load_state
from .llm_api import router as llm_router
from .ui_helpers import (
    kv_table as _kv_table,
    notice_html as _notice_html,
    options_html as _options_html,
    page_shell as _page_shell,
    parse_bulk_ids as _parse_bulk_ids,
    parse_json_object as _parse_json_object,
    redirect_with_message as _redirect_with_message,
    render_rows as _render_rows,
    status_badge as _status_badge,
    textarea_json as _textarea_json,
)
from .ui_pages import (
    render_actions_page,
    render_assets_page,
    render_bind_request_page,
    render_chat_page,
    render_config_page,
    render_dashboard_device_card,
    render_dashboard_page,
    render_dashboard_pet_card,
    render_device_detail_page,
    render_device_management_row,
    render_devices_page,
    render_events_page,
    render_memory_page,
    render_pet_detail_page,
    render_pet_management_row,
    render_pets_page,
    render_recent_event_card,
    render_resources_page,
    render_system_page,
)
from .ui_bulk_ops import handle_bulk_device_op, handle_bulk_pet_op
from .ui_context_builders import (
    build_chat_context,
    build_config_context,
    build_dashboard_context,
    build_device_detail_context,
    build_devices_page_context,
    build_memory_context,
    build_pet_detail_context,
    build_pets_page_context,
    build_resources_context,
    build_system_context,
)

PROTOCOL_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_state()
    try:
        yield
    finally:
        save_state()


app = FastAPI(title="nuonuo-pet backend", version=PROTOCOL_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include LLM routes
app.include_router(llm_router)


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
            "/api/device/{device_id}/display/profile",
            "/api/device/{device_id}/template/selection",
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
            "/api/llm/chat",
            "/api/llm/health",
            "/api/llm/config",
            "/api/llm/conversations/{pet_id}",
        ],
    }


def server_time() -> str:
    return datetime.now(timezone.utc).isoformat()



def _dashboard_snapshot() -> Dict[str, object]:
    device_ids = sorted(DEVICES.keys())
    pet_ids = sorted(PETS.keys())
    online_devices = 0
    offline_devices = 0
    bound_devices = 0
    for device_id in device_ids:
        rec = DEVICES[device_id]
        health = device_health_snapshot(rec)
        if health["is_offline"]:
            offline_devices += 1
        else:
            online_devices += 1
        if rec.bound:
            bound_devices += 1
    total_device_events = sum(len(items) for items in DEVICE_EVENTS.values())
    total_pet_events = sum(len(items) for items in EVENTS.values())
    total_memories = sum(len(items) for items in MEMORY.values())
    return {
        "server_time": server_time(),
        "protocol_version": PROTOCOL_VERSION,
        "device_count": len(device_ids),
        "pet_count": len(pet_ids),
        "bound_device_count": bound_devices,
        "online_device_count": online_devices,
        "offline_device_count": offline_devices,
        "device_event_count": total_device_events,
        "pet_event_count": total_pet_events,
        "memory_count": total_memories,
        "resource_pack_count": len(RESOURCE_PACKS),
        "theme_pack_count": len(THEME_PACKS),
        "species_template_count": len(SPECIES_TEMPLATES),
        "model_route_count": len(MODEL_ROUTES),
    }


def _merged_event_stream(kind: str = "all", keyword: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    keyword_norm = (keyword or "").strip().lower()
    items: List[Dict[str, Any]] = []
    include_device = kind in {"all", "device"}
    include_pet = kind in {"all", "pet"}
    include_conflict = kind in {"all", "conflict"}

    if include_device or include_conflict:
        for device_id, records in DEVICE_EVENTS.items():
            for item in records:
                is_conflict = item.kind == "conflict"
                if is_conflict and not include_conflict and kind != "all":
                    continue
                if (not is_conflict) and not include_device and kind != "all":
                    continue
                text = item.message or ""
                meta_text = json.dumps(item.meta, ensure_ascii=False) if item.meta else ""
                haystack = f"device {device_id} {item.kind} {text} {meta_text}".lower()
                if keyword_norm and keyword_norm not in haystack:
                    continue
                items.append(
                    {
                        "created_at": item.created_at,
                        "source_type": "device",
                        "source_id": device_id,
                        "kind": item.kind,
                        "message": text,
                        "meta": dict(item.meta),
                        "detail_url": f"/ui/device/{device_id}",
                    }
                )

    if include_pet:
        for pet_id, records in EVENTS.items():
            for item in records:
                text = item.text or ""
                tags_text = " ".join(item.tags or [])
                haystack = f"pet {pet_id} {item.kind} {text} {tags_text}".lower()
                if keyword_norm and keyword_norm not in haystack:
                    continue
                items.append(
                    {
                        "created_at": item.created_at,
                        "source_type": "pet",
                        "source_id": pet_id,
                        "kind": item.kind,
                        "message": text,
                        "meta": {"tags": list(item.tags)},
                        "detail_url": f"/ui/pet/{pet_id}",
                    }
                )

    items.sort(key=lambda x: x["created_at"], reverse=True)
    return items[: max(1, min(limit, 200))]


def bind_expires_iso(timestamp: Optional[float]) -> Optional[str]:
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


def evolve_growth_preferences(pet: PetRecord, kind: str, text: str, actions: List[str]) -> None:
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


def pet_or_404(pet_id: str) -> PetRecord:
    pet = PETS.get(pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="pet not found")
    return pet



def apply_event_to_pet(pet: PetRecord, kind: str, text: str) -> List[str]:
    actions: List[str] = []
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


def species_template_for(species_id: str) -> Optional[dict]:
    return next((item for item in SPECIES_TEMPLATES if item["id"] == species_id), None)


def model_route_for(route_id: Optional[str]) -> Optional[dict]:
    if route_id is None:
        return MODEL_ROUTES[0] if MODEL_ROUTES else None
    return next((item for item in MODEL_ROUTES if item["id"] == route_id), None)


def align_pet_to_species(pet: PetRecord) -> None:
    template = species_template_for(pet.species_id)
    if template is None:
        return
    if not pet.theme_id or pet.theme_id not in template.get("allowed_theme_ids", []):
        pet.theme_id = template.get("default_theme_id", pet.theme_id)


def record_device_event(device_id: str, kind: str, message: str, meta: Optional[dict] = None) -> None:
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
        connection_state = "unbound"
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


def validate_resource_pack(manifest: ResourcePackManifest) -> Tuple[bool, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

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


def validate_theme_pack(theme: ThemePackItem) -> Tuple[bool, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

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


def model_route_for(route_id: Optional[str]) -> Optional[dict]:
    if route_id is None:
        return MODEL_ROUTES[0] if MODEL_ROUTES else None
    return next((item for item in MODEL_ROUTES if item["id"] == route_id), None)


def model_route_item_from_dict(route: Dict[str, Any]) -> ModelRouteItem:
    return ModelRouteItem(**route)


def model_route_candidates(route_id: Optional[str], fallback_route_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    seen: set[str] = set()

    def push(route: Optional[Dict[str, Any]]) -> None:
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


def resolve_model_route(route_id: Optional[str] = None, fallback_route_ids: Optional[List[str]] = None, prefer_enabled: bool = True, allow_fallback: bool = True) -> Tuple[Optional[Dict[str, Any]], bool, Optional[str], List[str]]:
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


def resource_pack_item_from_record(record: Dict[str, Any]) -> ResourcePackRecordItem:
    return ResourcePackRecordItem(**record)


def resource_pack_manifest_to_record(manifest: ResourcePackManifest, enabled: bool = False, previous_versions: Optional[List[str]] = None) -> Dict[str, Any]:
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


def resource_pack_record_for(pack_id: str) -> Optional[Dict[str, Any]]:
    return RESOURCE_PACKS.get(pack_id)


def resource_pack_history(record: Dict[str, Any]) -> List[str]:
    return list(record.get("previous_versions", []))


def enable_resource_pack(pack_id: str, enabled: bool = True) -> Dict[str, Any]:
    record = resource_pack_record_for(pack_id)
    if record is None:
        raise HTTPException(status_code=404, detail="resource pack not found")
    record["enabled"] = enabled
    record["updated_at"] = server_time()
    save_state()
    return record


def rollback_resource_pack(pack_id: str, version: Optional[str] = None) -> Dict[str, Any]:
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
def pets_for_device(device_id: str) -> List[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


def pet_linked_device_ids(pet: PetRecord) -> List[str]:
    ids = list(getattr(pet, "linked_device_ids", []) or [])
    if pet.device_id:
        ids.insert(0, pet.device_id)
    deduped: List[str] = []
    for device_id in ids:
        if device_id and device_id not in deduped:
            deduped.append(device_id)
    return deduped


def pets_claiming_device(device_id: str) -> List[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


def record_device_conflict(device_id: str, pet_ids: List[str], note: str) -> None:
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
    conflict_device_ids: List[str],
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


def health_level_for_sync(occupancy_state: str, conflict_device_ids: List[str], offline_devices: int, missing_devices: int, primary_device_online: bool, total_devices: int) -> str:
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


def primary_hint_for_sync(primary_device_id: Optional[str], primary_device_online: bool, primary_device_present: bool, occupancy_state: str) -> str:
    if not primary_device_id:
        return "先绑定一台主设备。"
    if occupancy_state == "conflicted":
        return f"主设备 {primary_device_id} 存在占用冲突，先处理冲突。"
    if not primary_device_present:
        return f"主设备 {primary_device_id} 不在线或不存在。"
    if not primary_device_online:
        return f"主设备 {primary_device_id} 当前离线，建议重新连接。"
    return f"主设备 {primary_device_id} 在线。"


def action_hint_for_sync(recommended_action: str, primary_device_id: Optional[str]) -> str:
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


def sync_mini_payload_from_pet(summary: PetSyncSummaryResponse) -> Dict[str, object]:
    return {
        "subject_id": summary.pet_id,
        "subject_type": "pet",
        "server_time": summary.server_time,
        "health_level": summary.health_level,
        "summary_line": summary.summary_line,
        "primary_device_id": summary.primary_device_id,
        "primary_hint": summary.primary_hint,
        "action_hint": summary.action_hint,
        "recommended_action": summary.recommended_action,
        "occupancy_state": "conflicted" if summary.conflict_device_ids else "claimed" if summary.linked_device_ids else "free",
        "online_devices": summary.online_devices,
        "offline_devices": summary.offline_devices,
        "missing_devices": summary.missing_devices,
        "conflict_count": len(summary.conflict_device_ids),
        "device_count": summary.total_devices,
        "notes": list(summary.sync_notes),
    }


def sync_mini_payload_from_device(summary: DeviceSyncSummaryResponse) -> Dict[str, object]:
    pet_summary = summary.pet_summary
    if pet_summary is not None:
        return sync_mini_payload_from_pet(pet_summary)
    return {
        "subject_id": summary.device_id,
        "subject_type": "device",
        "server_time": summary.server_time,
        "health_level": summary.health_level,
        "summary_line": summary.summary_line,
        "primary_device_id": summary.primary_device_id,
        "primary_hint": summary.primary_hint,
        "action_hint": summary.action_hint,
        "recommended_action": summary.recommended_action,
        "occupancy_state": summary.occupancy_state,
        "online_devices": 1 if summary.device_state else 0,
        "offline_devices": 1 if summary.occupancy_state == "free" else 0,
        "missing_devices": 0,
        "conflict_count": len(summary.conflict_notes),
        "device_count": len(summary.linked_device_ids),
        "notes": list(summary.conflict_notes),
    }


def pet_device_owner(device_id: str) -> Optional[PetRecord]:
    return next((pet for pet in PETS.values() if pet.device_id == device_id), None)


def pet_device_recent_events(device_id: str, limit: int = 5) -> List[Dict[str, object]]:
    items = DEVICE_EVENTS.get(device_id, [])[-max(1, min(limit, 20)) :]
    return [
        {
            "kind": item.kind,
            "message": item.message,
            "created_at": item.created_at,
            "meta": dict(getattr(item, "meta", {}) or {}),
        }
        for item in items
    ]


def pet_recent_events(pet_id: str, limit: int = 5) -> List[Dict[str, object]]:
    items = EVENTS.get(pet_id, [])[-max(1, min(limit, 20)) :]
    return [
        {
            "kind": item.kind,
            "text": item.text,
            "tags": list(getattr(item, "tags", []) or []),
            "created_at": item.created_at,
        }
        for item in items
    ]


def build_pet_sync_summary(pet: PetRecord) -> PetSyncSummaryResponse:
    linked_ids = pet_linked_device_ids(pet)
    device_items: List[PetSyncDeviceItem] = []
    recent_device_events: Dict[str, List[Dict[str, object]]] = {}
    sync_notes: List[str] = []
    conflict_notes: List[str] = []
    conflict_device_ids: List[str] = []
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
    conflict_notes: List[str] = []
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
    linked_device_ids = pet_linked_device_ids(pet) if pet else []
    summary_line = summary_line_for_sync(len(linked_device_ids), 1 if device.connection_state != "offline" else 0, 1 if device.connection_state == "offline" else 0, 0, len(conflict_notes))
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


def broadcast_device_event_to_pet(pet: PetRecord, source_device_id: str, kind: str, message: str, meta: Optional[dict] = None) -> None:
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


def sync_pets_with_device(rec: DeviceRecord, reason: str, meta: Optional[dict] = None) -> None:
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


def grade_device_capabilities(hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> dict:
    caps = [item.lower() for item in (capabilities or [])]
    hardware = (hardware_model or "").lower()
    signals = set(caps)
    if hardware:
        signals.add(hardware)

    has_oled = any("oled" in item for item in signals)
    has_lcd = any("lcd" in item or "screen" in item or "display" in item for item in signals)
    has_touch = any("touch" in item for item in signals)
    has_voice = any("voice" in item or "audio" in item for item in signals)

    if has_oled:
        device_class = "oled"
        display_mode = "oled-high-contrast"
        display_hint = "prefer dark background and large expressions"
        confidence = "high"
    elif has_lcd and has_touch:
        device_class = "touch-rich"
        display_mode = "rich-lcd"
        display_hint = "support richer animations and tap targets"
        confidence = "high"
    elif has_lcd:
        device_class = "lcd"
        display_mode = "color-lcd"
        display_hint = "use compact pet portrait and simple UI slots"
        confidence = "high"
    elif has_touch:
        device_class = "touch-rich"
        display_mode = "rich-lcd"
        display_hint = "support richer animations and tap targets"
        confidence = "medium"
    elif has_voice:
        device_class = "voice-first"
        display_mode = "voice-only"
        display_hint = "no-screen or minimal-screen interaction"
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


def device_has_screen_signal(hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> bool:
    caps = [item.lower() for item in (capabilities or [])]
    hardware = (hardware_model or "").lower()
    signals = set(caps)
    if hardware:
        signals.add(hardware)
    return any(
        any(token in item for token in ["oled", "lcd", "screen", "display"])
        for item in signals
    )


def enforce_non_voice_display_mode(display_mode: str, hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> str:
    if display_mode != "voice-only":
        return display_mode
    if not device_has_screen_signal(hardware_model=hardware_model, capabilities=capabilities):
        return display_mode
    grade = grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities)
    if grade["display_mode"] != "voice-only":
        return grade["display_mode"]
    if any("oled" in item.lower() for item in (capabilities or [])) or "oled" in (hardware_model or "").lower():
        return "oled-high-contrast"
    return "color-lcd"


def preview_layout_profile(species_id: str, theme_id: str) -> dict:
    species = species_template_for(species_id)
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == theme_id), None)
    layout_name = "generic"
    header_prefix = ""
    action_prefix = ""
    compact_mode = False
    swap_body_action = False
    badge_on_top = False
    scene_hint = "template-safe layout"

    if species_id.startswith("cat"):
        if theme_id.endswith("silver-night") or theme_id == "cat-silver-night":
            layout_name = "cat-silver"
            header_prefix = "🐱"
            action_prefix = "银色提醒"
            compact_mode = True
            scene_hint = "compact night layout for calm visuals"
        else:
            layout_name = "cat-golden"
            header_prefix = "🐱"
            action_prefix = "金色提醒"
            scene_hint = "standard cat layout with clear body/action split"
    elif species_id.startswith("monkey"):
        layout_name = "monkey-play"
        header_prefix = "🐒"
        action_prefix = "猴子提示"
        compact_mode = True
        swap_body_action = True
        scene_hint = "playful layout with action/body swap"
    elif species_id.startswith("dino"):
        layout_name = "dino-hero"
        header_prefix = "🦖"
        action_prefix = "恐龙提示"
        badge_on_top = True
        scene_hint = "hero layout with badge emphasized on top"
    else:
        if theme_id.endswith("silver"):
            layout_name = "neutral-silver"
            compact_mode = True
            scene_hint = "fallback compact silver layout"
        else:
            layout_name = "generic"
            scene_hint = "fallback safe layout"

    if theme is not None and species is not None and theme.get("theme_id") not in species.get("allowed_theme_ids", []):
        scene_hint = f"{scene_hint}; theme not fully aligned with species"

    return {
        "layout_name": layout_name,
        "header_prefix": header_prefix,
        "action_prefix": action_prefix,
        "compact_mode": compact_mode,
        "swap_body_action": swap_body_action,
        "badge_on_top": badge_on_top,
        "scene_hint": scene_hint,
    }


def preview_display_profile(species_id: str, theme_id: str, hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> Tuple[str, str, str]:
    grade = grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities)
    layout = preview_layout_profile(species_id, theme_id)
    base_display_mode = enforce_non_voice_display_mode(
        grade["display_mode"],
        hardware_model=hardware_model,
        capabilities=capabilities,
    )
    display_mode = base_display_mode
    if base_display_mode.startswith("oled"):
        display_mode = base_display_mode
    elif species_id.startswith("cat"):
        if base_display_mode == "voice-only":
            display_mode = "voice-only"
        elif layout["compact_mode"]:
            display_mode = "color-lcd-compact"
        else:
            display_mode = "color-lcd"
    elif species_id.startswith("monkey"):
        display_mode = "playful-lcd" if base_display_mode != "voice-only" else "voice-only"
    elif species_id.startswith("dino"):
        display_mode = "hero-lcd" if base_display_mode != "voice-only" else "voice-only"
    display_mode = enforce_non_voice_display_mode(
        display_mode,
        hardware_model=hardware_model,
        capabilities=capabilities,
    )
    display_hint = f"{grade['display_hint']}; {layout['scene_hint']}"
    return display_mode, display_hint, layout["layout_name"]


def select_default_preview(hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> dict:
    caps = [item.lower() for item in (capabilities or [])]
    hardware = (hardware_model or "").lower()

    has_oled = any("oled" in item for item in caps) or "oled" in hardware
    has_lcd = any("lcd" in item or "screen" in item or "display" in item for item in caps) or any(token in hardware for token in ["lcd", "screen", "display"])
    has_touch = any("touch" in item for item in caps) or "touch" in hardware
    has_voice = any("voice" in item or "audio" in item for item in caps) or "voice" in hardware or "audio" in hardware

    if has_oled:
        key = "oled"
    elif has_lcd and has_touch:
        key = "rich"
    elif has_lcd:
        key = "lcd"
    elif has_touch:
        key = "rich"
    elif has_voice:
        key = "voice"
    else:
        key = "default"

    selection = DEFAULT_PREVIEW_SELECTION[key]
    species = species_template_for(selection["species_id"])
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == selection["theme_id"]), None)
    compatible_theme_count = sum(1 for item in theme_compatibility_items(species_id=selection["species_id"]) if item.get("compatible"))
    compatible_resource_pack_count = sum(
        1 for record in RESOURCE_PACKS.values()
        if record.get("enabled") and (record.get("species_id") in {None, selection["species_id"]})
    )
    grade = grade_device_capabilities(hardware_model, capabilities)
    return {
        "server_time": server_time(),
        "hardware_model": hardware_model,
        "capabilities": list(capabilities or []),
        "species_id": selection["species_id"],
        "theme_id": selection["theme_id"],
        "reason": selection["reason"],
        "matched_signals": list(selection["signals"]),
        "species_name": species.get("name") if species else None,
        "theme_name": theme.get("name") if theme else None,
        "theme_version": theme.get("version") if theme else None,
        "preview_asset": theme.get("preview_asset") if theme else None,
        "display_mode": selection.get("display_mode", grade["display_mode"]),
        "display_hint": grade["display_hint"],
        "ui_slot_count": len(species.get("ui_slots", [])) if species else 0,
        "compatible_theme_count": compatible_theme_count,
        "compatible_resource_pack_count": compatible_resource_pack_count,
    }

def build_device_capability_summary(hardware_model: Optional[str] = None, firmware_version: Optional[str] = None, capabilities: Optional[List[str]] = None) -> dict:
    grade = grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities)
    selection = select_default_preview(hardware_model=hardware_model, capabilities=capabilities)
    species = species_template_for(selection["species_id"]) or {}
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == selection["theme_id"]), None)
    preview = preview_layout_profile(selection["species_id"], selection["theme_id"])
    notes: List[str] = [selection.get("reason", "")]
    if firmware_version:
        notes.append(f"firmware={firmware_version}")
    if preview.get("scene_hint"):
        notes.append(preview["scene_hint"])
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
        "recommended_theme_name": theme.get("name") if theme else None,
        "recommended_theme_version": theme.get("version") if theme else None,
        "recommended_preview_asset": theme.get("preview_asset") if theme else None,
        "ui_slot_count": len(species.get("ui_slots", [])),
        "compatible_theme_count": sum(1 for item in theme_compatibility_items(species_id=selection["species_id"], firmware_version=firmware_version) if item.get("compatible")),
        "compatible_resource_pack_count": sum(1 for record in RESOURCE_PACKS.values() if record.get("enabled") and (record.get("species_id") in {None, selection["species_id"]})),
        "notes": [item for item in notes if item],
    }



def build_template_selection(hardware_model: Optional[str] = None, firmware_version: Optional[str] = None, capabilities: Optional[List[str]] = None, pet_id: Optional[str] = None) -> dict:
    selection = select_default_preview(hardware_model=hardware_model, capabilities=capabilities)
    pet = PETS.get(pet_id) if pet_id else None
    preview = build_preview(selection["species_id"], selection["theme_id"], pet)
    display_mode, display_hint, layout_name = preview_display_profile(
        selection["species_id"],
        selection["theme_id"],
        hardware_model=hardware_model,
        capabilities=capabilities,
    )
    selection["display_mode"] = display_mode
    selection["display_hint"] = display_hint
    selection["layout_name"] = layout_name
    selection["scene_hint"] = preview.get("scene_hint")
    selection["notes"] = preview.get("notes")
    selection["preview"] = preview
    selection["firmware_version"] = firmware_version
    return selection


def build_device_template_selection(device_id: str) -> dict:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    pet = pet_device_owner(device_id)
    selection = build_template_selection(
        hardware_model=rec.hardware_model,
        firmware_version=rec.firmware_version,
        capabilities=list(rec.capabilities),
        pet_id=pet.pet_id if pet else None,
    )
    selection["device_id"] = device_id
    selection["connection_state"] = rec.connection_state
    selection["last_seen_at"] = rec.last_seen_at
    selection["bound"] = rec.bound
    selection["owner_id"] = rec.owner_id
    return selection
def theme_compatibility_items(species_id: Optional[str] = None, firmware_version: Optional[str] = None) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for theme in THEME_PACKS:
        compatible = True
        reasons: List[str] = []
        warnings: List[str] = []
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


def build_device_display_profile(device_id: str, hardware_model: Optional[str] = None, firmware_version: Optional[str] = None, capabilities: Optional[List[str]] = None) -> dict:
    summary = build_device_capability_summary(hardware_model=hardware_model, firmware_version=firmware_version, capabilities=capabilities)
    grade = grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities)
    selection = select_default_preview(hardware_model=hardware_model, capabilities=capabilities)
    preview = preview_layout_profile(selection["species_id"], selection["theme_id"])
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == selection["theme_id"]), None)
    final_display_mode = enforce_non_voice_display_mode(
        grade["display_mode"],
        hardware_model=hardware_model,
        capabilities=capabilities,
    )
    is_lcd = final_display_mode.endswith("lcd") or final_display_mode in {"rich-lcd", "color-lcd", "color-lcd-compact", "playful-lcd", "hero-lcd"}
    is_oled = final_display_mode.startswith("oled")
    panel_name = "lcd-panel" if is_lcd else ("oled-panel" if is_oled else "voice-only")
    width = 240 if final_display_mode != "voice-only" else 0
    height = 240 if final_display_mode != "voice-only" else 0
    panel_rotation = "portrait" if final_display_mode != "voice-only" else ""
    model_text = (hardware_model or "").lower()
    capability_text = " ".join((capabilities or [])).lower()
    if "1.85" in model_text or "360" in model_text or "st77916" in model_text or "round" in model_text:
        panel_name = "st77916"
        width = 360
        height = 360
        panel_rotation = "portrait"
    elif "gc9a01" in model_text:
        panel_name = "gc9a01"
    elif "st7789" in model_text:
        panel_name = "st7789"
    elif is_lcd and "touch" in capability_text and "compact" in capability_text:
        panel_name = "compact-lcd"
    return {
        "server_time": server_time(),
        "device_id": device_id,
        "hardware_model": hardware_model,
        "firmware_version": firmware_version,
        "capabilities": list(capabilities or []),
        "device_class": summary["device_class"],
        "display_mode": final_display_mode,
        "display_hint": summary["display_hint"],
        "confidence": grade["confidence"],
        "panel_name": panel_name,
        "panel_rotation": panel_rotation,
        "width": width,
        "height": height,
        "color_depth": 16 if is_lcd else (1 if is_oled else 0),
        "color": final_display_mode not in {"voice-only", "generic"},
        "touch": any("touch" in item.lower() for item in (capabilities or [])),
        "backlight": final_display_mode not in {"voice-only", "generic"},
        "compact": preview.get("compact_mode", False),
        "voice_first": grade["device_class"] == "voice-first",
        "recommended_species_id": selection["species_id"],
        "recommended_theme_id": selection["theme_id"],
        "recommended_theme_version": theme.get("version") if theme else None,
        "recommended_theme_name": theme.get("name") if theme else None,
        "recommended_preview_asset": theme.get("preview_asset") if theme else None,
        "layout_name": preview.get("layout_name"),
        "scene_hint": preview.get("scene_hint"),
        "ui_slot_count": summary["ui_slot_count"],
        "compatible_theme_count": summary["compatible_theme_count"],
        "compatible_resource_pack_count": summary["compatible_resource_pack_count"],
        "notes": summary["notes"] + [preview.get("scene_hint", "")],
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

    display_mode, display_hint, layout_name = preview_display_profile(species_id, theme_id)
    scene = preview_layout_profile(species_id, theme_id)

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
        "layout_name": layout_name,
        "scene_hint": scene.get("scene_hint"),
    }


def build_preview(species_id: str, theme_id: str, pet: Optional[PetRecord] = None) -> dict:
    species = species_template_for(species_id)
    theme = next((item for item in THEME_PACKS if item.get("theme_id") == theme_id), None)
    layers: List[Dict[str, Any]] = []
    notes: List[str] = []

    if species is None:
        notes.append(f"unknown species: {species_id}")
    if theme is None:
        notes.append(f"unknown theme: {theme_id}")

    palette = theme.get("palette", {}) if theme else {}
    ui_slots = species.get("ui_slots", []) if species else []
    slot_map = theme.get("slot_map", {}) if theme else {}

    if species and theme and theme.get("theme_id") not in species.get("allowed_theme_ids", []):
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

    display_mode, display_hint, layout_name = preview_display_profile(species_id, theme_id)
    scene = preview_layout_profile(species_id, theme_id)

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
        "layout_name": layout_name,
        "scene_hint": scene.get("scene_hint"),
    }


@app.get("/api/device/capability/grade", response_model=DeviceCapabilityGradeResponse)
def device_capability_grade(hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None) -> DeviceCapabilityGradeResponse:
    return DeviceCapabilityGradeResponse(**grade_device_capabilities(hardware_model=hardware_model, capabilities=capabilities))


@app.get("/api/device/capability/summary", response_model=DeviceCapabilitySummaryResponse)
def device_capability_summary(hardware_model: Optional[str] = None, firmware_version: Optional[str] = None, capabilities: Optional[List[str]] = None) -> DeviceCapabilitySummaryResponse:
    return DeviceCapabilitySummaryResponse(**build_device_capability_summary(hardware_model=hardware_model, firmware_version=firmware_version, capabilities=capabilities))


@app.post("/api/device/capability/summary", response_model=DeviceCapabilitySummaryBatchResponse)
def device_capability_summary_post(req: DeviceCapabilitySummaryRequest) -> DeviceCapabilitySummaryBatchResponse:
    item = build_device_capability_summary(hardware_model=req.hardware_model, firmware_version=req.firmware_version, capabilities=req.capabilities)
    return DeviceCapabilitySummaryBatchResponse(server_time=server_time(), item=DeviceCapabilitySummaryResponse(**item))


@app.get("/api/device/{device_id}/display/profile", response_model=DeviceDisplayProfileResponse)
def device_display_profile(device_id: str) -> DeviceDisplayProfileResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    return DeviceDisplayProfileResponse(**build_device_display_profile(device_id=device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities)))


@app.get("/api/device/{device_id}/display/profile/batch", response_model=DeviceDisplayProfileBatchResponse)
def device_display_profile_batch(device_id: str) -> DeviceDisplayProfileBatchResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    item = build_device_display_profile(device_id=device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities))
    return DeviceDisplayProfileBatchResponse(server_time=server_time(), item=DeviceDisplayProfileResponse(**item))


@app.get("/api/device/{device_id}/template/selection", response_model=TemplateSelectionDetailResponse)
def device_template_selection(device_id: str) -> TemplateSelectionDetailResponse:
    selection = build_device_template_selection(device_id)
    preview = selection.get("preview") or {}
    return TemplateSelectionDetailResponse(
        server_time=server_time(),
        hardware_model=selection.get("hardware_model"),
        firmware_version=selection.get("firmware_version"),
        capabilities=list(selection.get("capabilities") or []),
        species_id=selection["species_id"],
        species_name=selection.get("species_name"),
        theme_id=selection["theme_id"],
        theme_name=selection.get("theme_name"),
        theme_version=selection.get("theme_version"),
        preview_asset=selection.get("preview_asset"),
        reason=selection["reason"],
        matched_signals=selection.get("matched_signals", []),
        display_mode=selection.get("display_mode", "generic"),
        display_hint=selection.get("display_hint", ""),
        layout_name=selection.get("layout_name"),
        scene_hint=selection.get("scene_hint"),
        ui_slot_count=selection.get("ui_slot_count", 0),
        compatible_theme_count=selection.get("compatible_theme_count", 0),
        compatible_resource_pack_count=selection.get("compatible_resource_pack_count", 0),
        notes=[
            selection.get("reason", ""),
            f"device={device_id}",
            f"display={selection.get('display_mode', 'generic')}",
            f"preview={selection.get('preview_asset') or 'none'}",
        ],
        preview=PetPreviewResponse(
            server_time=preview.get("server_time"),
            species_id=preview.get("species_id", selection["species_id"]),
            theme_id=preview.get("theme_id", selection["theme_id"]),
            pet_id=preview.get("pet_id"),
            name=preview.get("name"),
            growth_stage=preview.get("growth_stage"),
            palette=preview.get("palette", {}),
            ui_slots=preview.get("ui_slots", []),
            layers=[PreviewLayerItem(**item) for item in preview.get("layers", [])],
            notes=preview.get("notes", []),
            display_mode=preview.get("display_mode"),
            display_hint=preview.get("display_hint"),
            layout_name=preview.get("layout_name"),
            scene_hint=preview.get("scene_hint"),
        ),
    )


@app.get("/api/template/selection", response_model=TemplateSelectionDetailResponse)
def template_selection(hardware_model: Optional[str] = None, firmware_version: Optional[str] = None, capabilities: Optional[List[str]] = None, pet_id: Optional[str] = None) -> TemplateSelectionDetailResponse:
    selection = build_template_selection(hardware_model=hardware_model, firmware_version=firmware_version, capabilities=capabilities, pet_id=pet_id)
    preview = selection.get("preview") or {}
    return TemplateSelectionDetailResponse(
        server_time=server_time(),
        hardware_model=hardware_model,
        firmware_version=firmware_version,
        capabilities=list(capabilities or []),
        species_id=selection["species_id"],
        species_name=selection.get("species_name"),
        theme_id=selection["theme_id"],
        theme_name=selection.get("theme_name"),
        theme_version=selection.get("theme_version"),
        preview_asset=selection.get("preview_asset"),
        reason=selection["reason"],
        matched_signals=selection.get("matched_signals", []),
        display_mode=selection.get("display_mode", "generic"),
        display_hint=selection.get("display_hint", ""),
        layout_name=selection.get("layout_name"),
        scene_hint=selection.get("scene_hint"),
        ui_slot_count=selection.get("ui_slot_count", 0),
        compatible_theme_count=selection.get("compatible_theme_count", 0),
        compatible_resource_pack_count=selection.get("compatible_resource_pack_count", 0),
        notes=[
            selection.get("reason", ""),
            f"display={selection.get('display_mode', 'generic')}",
            f"preview={selection.get('preview_asset') or 'none'}",
        ],
        preview=PetPreviewResponse(
            server_time=preview.get("server_time"),
            species_id=preview.get("species_id", selection["species_id"]),
            theme_id=preview.get("theme_id", selection["theme_id"]),
            pet_id=preview.get("pet_id"),
            name=preview.get("name"),
            growth_stage=preview.get("growth_stage"),
            palette=preview.get("palette", {}),
            ui_slots=preview.get("ui_slots", []),
            layers=[PreviewLayerItem(**item) for item in preview.get("layers", [])],
            notes=preview.get("notes", []),
            display_mode=preview.get("display_mode"),
            display_hint=preview.get("display_hint"),
            layout_name=preview.get("layout_name"),
            scene_hint=preview.get("scene_hint"),
        ),
    )


@app.get("/api/preview/sample", response_model=PreviewSampleResponse)
def preview_sample(hardware_model: Optional[str] = None, capabilities: Optional[List[str]] = None, pet_id: Optional[str] = None) -> PreviewSampleResponse:
    selection = build_template_selection(hardware_model=hardware_model, capabilities=capabilities, pet_id=pet_id)
    preview = selection.get("preview") or {}
    return PreviewSampleResponse(
        server_time=server_time(),
        selection=TemplateSelectionResponse(**selection),
        preview=PetPreviewResponse(
            server_time=preview.get("server_time"),
            species_id=preview.get("species_id", selection["species_id"]),
            theme_id=preview.get("theme_id", selection["theme_id"]),
            pet_id=preview.get("pet_id"),
            name=preview.get("name"),
            growth_stage=preview.get("growth_stage"),
            palette=preview.get("palette", {}),
            ui_slots=preview.get("ui_slots", []),
            layers=[PreviewLayerItem(**item) for item in preview.get("layers", [])],
            notes=preview.get("notes", []),
            display_mode=preview.get("display_mode"),
            display_hint=preview.get("display_hint"),
            layout_name=preview.get("layout_name"),
            scene_hint=preview.get("scene_hint"),
        ),
    )


@app.get("/api/preview/{species_id}/{theme_id}", response_model=PetPreviewResponse)
def preview_combo(species_id: str, theme_id: str, pet_id: Optional[str] = None) -> PetPreviewResponse:
    pet = PETS.get(pet_id) if pet_id else None
    preview = build_preview(species_id, theme_id, pet)
    display_mode, display_hint, layout_name = preview_display_profile(species_id, theme_id)
    scene = preview_layout_profile(species_id, theme_id)
    preview["display_mode"] = display_mode
    preview["display_hint"] = display_hint
    preview["layout_name"] = layout_name
    preview["scene_hint"] = scene.get("scene_hint")
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
        layout_name=preview.get("layout_name"),
        scene_hint=preview.get("scene_hint"),
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


def apply_model_route_to_pet(pet: PetRecord) -> None:
    resolved, _fallback_used, _fallback_reason, _available_ids = resolve_model_route(
        route_id=pet.model_route_id,
        fallback_route_ids=None,
        prefer_enabled=bool(MODEL_ROUTE_CONFIG.get("prefer_enabled", True)),
        allow_fallback=True,
    )
    if resolved is None:
        pet.model_provider = None
        pet.model_name = None
        return
    pet.model_route_id = resolved["id"]
    pet.model_provider = resolved.get("provider")
    pet.model_name = resolved.get("model_name")


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
        display_profile=build_device_display_profile(device_id=rec.device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities)),
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
    profile = build_device_display_profile(device_id=device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities))
    sync = build_device_sync_summary(device_id)
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
        server_time=server_time(),
        display_profile=profile,
        sync_minimal=sync.model_dump() if hasattr(sync, "model_dump") else sync.__dict__,
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


@app.get("/api/device/{device_id}/summary/minimal", response_model=DeviceSummaryMiniResponse)
def device_summary_minimal(device_id: str) -> DeviceSummaryMiniResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    health = device_health_snapshot(rec)
    profile = build_device_display_profile(device_id=device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities))
    sync = build_device_sync_summary(device_id)
    payload = sync_mini_payload_from_device(sync)
    return DeviceSummaryMiniResponse(
        device_id=rec.device_id,
        server_time=server_time(),
        bound=rec.bound,
        binding_state="bound" if rec.bound else "unbound",
        connection_state=health["connection_state"],
        health_level=payload.get("health_level", sync.health_level),
        summary_line=payload.get("summary_line", "") or sync.summary_line,
        primary_hint=payload.get("primary_hint", "") or sync.primary_hint,
        action_hint=payload.get("action_hint", "") or sync.action_hint,
        recommended_action=payload.get("recommended_action", "review"),
        display_mode=profile.get("display_mode", "unknown"),
        display_hint=profile.get("display_hint", ""),
        layout_name=profile.get("layout_name", ""),
        scene_hint=profile.get("scene_hint", ""),
        panel_name=profile.get("panel_name"),
        panel_rotation=profile.get("panel_rotation", ""),
        width=profile.get("width", 0),
        height=profile.get("height", 0),
        color_depth=profile.get("color_depth", 0),
        touch=profile.get("touch", False),
        backlight=profile.get("backlight", False),
        recent_event_count=len(DEVICE_EVENTS.get(device_id, [])),
    )


@app.get("/api/device/{device_id}/summary", response_model=DeviceSummaryResponse)
def device_summary(device_id: str) -> DeviceSummaryResponse:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="device not found")
    health = device_health_snapshot(rec)
    profile = build_device_display_profile(device_id=device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities))
    sync = build_device_sync_summary(device_id)
    return DeviceSummaryResponse(
        device_id=rec.device_id,
        server_time=server_time(),
        bound=rec.bound,
        connection_state=health["connection_state"],
        health_level=sync.health_level,
        display_profile=profile,
        sync_minimal=sync.model_dump() if hasattr(sync, "model_dump") else sync.__dict__,
        health=health,
        recent_event_count=len(DEVICE_EVENTS.get(device_id, [])),
        binding_state="bound" if rec.bound else "unbound",
        display_mode=profile.get("display_mode", "unknown"),
        display_hint=profile.get("display_hint", ""),
        layout_name=profile.get("layout_name", ""),
        scene_hint=profile.get("scene_hint", ""),
        panel_name=profile.get("panel_name"),
        panel_rotation=profile.get("panel_rotation", ""),
        width=profile.get("width", 0),
        height=profile.get("height", 0),
        color_depth=profile.get("color_depth", 0),
        touch=profile.get("touch", False),
        backlight=profile.get("backlight", False),
    )


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
        display_profile=build_device_display_profile(device_id=rec.device_id, hardware_model=rec.hardware_model, firmware_version=rec.firmware_version, capabilities=list(rec.capabilities)),
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
    items: List[PetDeviceLinkItem] = []
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


@app.get("/api/device/{device_id}/sync/minimal", response_model=SyncMiniResponse)
def device_sync_summary_minimal(device_id: str) -> SyncMiniResponse:
    summary = build_device_sync_summary(device_id)
    return SyncMiniResponse(**sync_mini_payload_from_device(summary))


@app.get("/api/pet/{pet_id}/sync/minimal", response_model=SyncMiniResponse)
def pet_sync_summary_minimal(pet_id: str) -> SyncMiniResponse:
    summary = build_pet_sync_summary(pet_or_404(pet_id))
    return SyncMiniResponse(**sync_mini_payload_from_pet(summary))


@app.get("/api/pet/{pet_id}/broadcast", response_model=PetBroadcastSummaryResponse)
def pet_broadcast_summary(pet_id: str) -> PetBroadcastSummaryResponse:
    pet = pet_or_404(pet_id)
    linked_ids = pet_linked_device_ids(pet)
    device_items: List[PetSyncDeviceItem] = []
    broadcast_items: List[PetBroadcastItem] = []
    sync_notes: List[str] = []
    conflict_notes: List[str] = []
    conflict_device_ids: List[str] = []
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
    categories: Dict[str, int] = {}
    summary_items: Dict[str, PetEventSummaryItem] = {}
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
    
    # 使用模型路由进行对话（简化实现，避免异步问题）
    try:
        # 简化：直接使用降级响应，避免在同步函数中调用异步代码
        reply = f"收到啦，我会记住你刚刚说的：{req.user_text[:80]}"
        metadata = {"model": "fallback", "reason": "sync_mode"}
    except Exception as e:
        # 降级到简单响应
        reply = f"收到啦，我会记住你刚刚说的：{req.user_text[:80]}"
        metadata = {"error": str(e), "fallback": True}
    
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
def read_memory(pet_id: str, kind: Optional[str] = None, keyword: Optional[str] = None, limit: int = 20) -> MemoryListResponse:
    pet_or_404(pet_id)
    items = MEMORY.get(pet_id, [])
    filtered: List[MemoryRecord] = []
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


# Enhanced Memory APIs
@app.get("/api/memory/{pet_id}/stats")
def memory_stats(pet_id: str):
    """Get memory statistics for a pet"""
    pet_or_404(pet_id)
    from .memory_enhanced import get_memory_stats
    return get_memory_stats(pet_id)


@app.get("/api/memory/{pet_id}/search")
def search_memory(pet_id: str, q: str = "", limit: int = 20):
    """Search memories by query"""
    pet_or_404(pet_id)
    from .memory_enhanced import search_memory as do_search
    results = do_search(pet_id, q, limit)
    return {
        "pet_id": pet_id,
        "query": q,
        "count": len(results),
        "items": [
            {"kind": item.kind, "text": item.text, "tags": list(item.tags), "created_at": item.created_at}
            for item in results
        ],
    }


@app.get("/api/memory/{pet_id}/summary")
def memory_summary(pet_id: str, max_items: int = 5):
    """Get memory summary for AI context"""
    pet_or_404(pet_id)
    from .memory_enhanced import get_memory_summary
    return get_memory_summary(pet_id, max_items)


@app.post("/api/memory/{pet_id}/cleanup")
def cleanup_memory(pet_id: str, max_age_days: int = 30, keep_long_term: bool = True):
    """Clean up old memories"""
    pet_or_404(pet_id)
    from .memory_enhanced import cleanup_old_memories
    cleaned = cleanup_old_memories(pet_id, max_age_days, keep_long_term)
    return {"ok": True, "pet_id": pet_id, "cleaned_count": cleaned}


@app.get("/api/memory/{pet_id}/export")
def export_memory(pet_id: str, kind: Optional[str] = None):
    """Export memories for backup"""
    pet_or_404(pet_id)
    from .memory_enhanced import export_memories
    items = export_memories(pet_id, kind)
    return {"pet_id": pet_id, "count": len(items), "items": items}


@app.get("/api/memory/{pet_id}/context")
def memory_context(pet_id: str, max_tokens: int = 500):
    """Get memory context for chat"""
    pet_or_404(pet_id)
    from .memory_enhanced import get_memory_context_for_chat
    context = get_memory_context_for_chat(pet_id, max_tokens)
    return {"pet_id": pet_id, "context": context}


# Model Health and Routing APIs
@app.get("/api/model/health")
def model_health():
    """Get model health status"""
    from .model_caller import get_model_health_status
    return get_model_health_status()


@app.get("/api/model/routes")
def model_routes():
    """Get all model routes"""
    return {
        "routes": MODEL_ROUTES,
        "config": MODEL_ROUTE_CONFIG,
    }


@app.post("/api/model/test")
def test_model_route(route_id: Optional[str] = None, test_message: str = "Hello"):
    """Test a specific model route"""
    from .model_caller import model_caller
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result, route_info = loop.run_until_complete(
        model_caller.call_with_fallback(
            test_message,
            preferred_route_id=route_id,
        )
    )
    
    return {
        "success": True,
        "result": result,
        "route_info": route_info,
    }


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
def resource_pack_rollback(pack_id: str, version: Optional[str] = None) -> ResourcePackActionResponse:
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
def theme_compatibility(species_id: Optional[str] = None, firmware_version: Optional[str] = None) -> ThemePackCompatibilityResponse:
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


@app.get("/health")
def health():
    snapshot = _dashboard_snapshot()
    return {
        "status": "ok",
        "server_time": snapshot["server_time"],
        "version": snapshot["protocol_version"],
        "counts": {
            "devices": snapshot["device_count"],
            "pets": snapshot["pet_count"],
            "online_devices": snapshot["online_device_count"],
            "offline_devices": snapshot["offline_device_count"],
            "device_events": snapshot["device_event_count"],
            "pet_events": snapshot["pet_event_count"],
            "memories": snapshot["memory_count"],
        },
    }



@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_dashboard_context(
        dashboard_snapshot=_dashboard_snapshot,
        device_health_snapshot=device_health_snapshot,
        build_device_sync_summary=build_device_sync_summary,
        build_pet_sync_summary=build_pet_sync_summary,
        render_dashboard_device_card=render_dashboard_device_card,
        render_dashboard_pet_card=render_dashboard_pet_card,
        render_recent_event_card=render_recent_event_card,
        status_badge=_status_badge,
    )
    return render_dashboard_page(
        snapshot=context['snapshot'],
        device_cards_html=context['device_cards_html'],
        pet_cards_html=context['pet_cards_html'],
        recent_events_html=context['recent_events_html'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/devices", response_class=HTMLResponse)
def ui_devices(
    connection_state: str = "all",
    bound: str = "all",
    keyword: Optional[str] = None,
    problem: str = "all",
    capability: str = "all",
    owner_scope: str = "all",
    sort_by: str = "device_id",
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    context = build_devices_page_context(
        connection_state=connection_state,
        bound=bound,
        keyword=keyword,
        problem=problem,
        capability=capability,
        owner_scope=owner_scope,
        sort_by=sort_by,
        device_health_snapshot=device_health_snapshot,
        build_device_sync_summary=build_device_sync_summary,
        pet_device_owner=pet_device_owner,
        render_device_management_row=render_device_management_row,
        status_badge=_status_badge,
        device_record_type=DeviceRecord,
    )
    return render_devices_page(
        rows_html=context['rows_html'],
        matched=context['matched'],
        online_count=context['online_count'],
        offline_count=context['offline_count'],
        bound_count=context['bound_count'],
        unbound_count=context['unbound_count'],
        conflict_count=context['conflict_count'],
        action_needed_count=context['action_needed_count'],
        capability_options_html=context['capability_options_html'],
        connection_state=connection_state,
        bound=bound,
        capability=capability,
        owner_scope=owner_scope,
        problem=problem,
        sort_by=sort_by,
        keyword=keyword,
        notice_html=_notice_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/pets", response_class=HTMLResponse)
def ui_pets(
    species_id: str = "all",
    mood: str = "all",
    keyword: Optional[str] = None,
    problem: str = "all",
    growth_stage: str = "all",
    device_scope: str = "all",
    sort_by: str = "pet_id",
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    context = build_pets_page_context(
        species_id=species_id,
        mood=mood,
        keyword=keyword,
        problem=problem,
        growth_stage=growth_stage,
        device_scope=device_scope,
        sort_by=sort_by,
        build_pet_sync_summary=build_pet_sync_summary,
        render_pet_management_row=render_pet_management_row,
        status_badge=_status_badge,
    )
    return render_pets_page(
        rows_html=context['rows_html'],
        matched=context['matched'],
        healthy_count=context['healthy_count'],
        warning_count=context['warning_count'],
        action_needed_count=context['action_needed_count'],
        species_options_html=context['species_options_html'],
        growth_stage_options_html=context['growth_stage_options_html'],
        species_id=species_id,
        growth_stage=growth_stage,
        mood=mood,
        device_scope=device_scope,
        problem=problem,
        sort_by=sort_by,
        keyword=keyword,
        notice_html=_notice_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )
@app.get("/ui/system", response_class=HTMLResponse)
def ui_system_status(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_system_context(
        dashboard_snapshot=_dashboard_snapshot,
        build_pet_sync_summary=build_pet_sync_summary,
        device_health_snapshot=device_health_snapshot,
        build_device_sync_summary=build_device_sync_summary,
        merged_event_stream=_merged_event_stream,
        status_badge=_status_badge,
    )
    return render_system_page(
        snapshot=context['snapshot'],
        warning_pets=context['warning_pets'],
        online_ok_devices=context['online_ok_devices'],
        offline_or_warn_devices=context['offline_or_warn_devices'],
        healthy_pets=context['healthy_pets'],
        check_cards_html=context['check_cards_html'],
        device_cards_html=context['device_cards_html'],
        pet_cards_html=context['pet_cards_html'],
        recent_cards_html=context['recent_cards_html'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )
@app.get("/ui/events", response_class=HTMLResponse)
def ui_events(kind: str = "all", keyword: Optional[str] = None, limit: int = 50, msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    stream = _merged_event_stream(kind=kind, keyword=keyword, limit=limit)
    cards: List[str] = []
    for item in stream:
        meta_html = f"<pre>{escape(json.dumps(item['meta'], ensure_ascii=False, indent=2))}</pre>" if item.get("meta") else '<div class="muted">无附加信息</div>'
        cards.append(
            f'''<div class="item"><div class="item-title"><div><strong>{escape(item['kind'])}</strong> <span class="mini">{escape(item['source_type'])}:{escape(item['source_id'])}</span></div><div>{_status_badge(item['source_type'])}</div></div><div class="mini">{escape(item['created_at'])}</div><div style="margin-top:8px;">{escape(item['message'])}</div><details style="margin-top:10px;"><summary class="mini">展开元数据</summary>{meta_html}</details><div class="actions"><a class="btn" href="{escape(item['detail_url'])}">查看详情</a></div></div>'''
        )
    return render_events_page(
        cards_html=''.join(cards),
        kind=kind,
        keyword=keyword,
        limit=limit,
        matched=len(stream),
        notice_html=_notice_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )




@app.get("/ui/config", response_class=HTMLResponse)
def ui_config_center(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_config_context(
        model_routes_config=model_routes_config,
        status_badge=_status_badge,
    )
    return render_config_page(
        route_ids=context['route_ids'],
        default_route_id=context['default_route_id'],
        fallback_route_ids=context['fallback_route_ids'],
        prefer_enabled=context['prefer_enabled'],
        allow_manual_override=context['allow_manual_override'],
        routing_notes=context['routing_notes'],
        route_cards_html=context['route_cards_html'],
        pet_cards_html=context['pet_cards_html'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        options_html=_options_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/resources", response_class=HTMLResponse)
def ui_resources_center(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_resources_context(
        theme_compatibility=theme_compatibility,
        resource_packs=resource_packs,
        status_badge=_status_badge,
    )
    return render_resources_page(
        species_count=context['species_count'],
        theme_count=context['theme_count'],
        resource_pack_count=context['resource_pack_count'],
        assets_manifest_count=context['assets_manifest_count'],
        species_cards_html=context['species_cards_html'],
        theme_cards_html=context['theme_cards_html'],
        resource_cards_html=context['resource_cards_html'],
        compatibility_cards_html=context['compatibility_cards_html'],
        notice_html=_notice_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/memory", response_class=HTMLResponse)
def ui_memory_center(pet_id: Optional[str] = None, kind: Optional[str] = None, keyword: Optional[str] = None, limit: int = 50, msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_memory_context(
        pet_id=pet_id,
        kind=kind,
        keyword=keyword,
        limit=limit,
        read_memory=read_memory,
        kv_table=_kv_table,
    )
    return render_memory_page(
        pet_ids=context['pet_ids'],
        selected_pet=context['selected_pet'],
        kind=kind,
        keyword=keyword,
        limit=limit,
        pet_overview_html=context['pet_overview_html'],
        summary_html=context['summary_html'],
        memory_cards_html=context['memory_cards_html'],
        notice_html=_notice_html,
        options_html=_options_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/chat", response_class=HTMLResponse)
def ui_chat_debug(pet_id: Optional[str] = None, msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_chat_context(
        pet_id=pet_id,
        read_memory=read_memory,
    )
    return render_chat_page(
        pet_ids=context['pet_ids'],
        selected_pet=context['selected_pet'],
        device_id=context['device_id'],
        mood=context['mood'],
        pet_snapshot=context['pet_snapshot'],
        memory_cards_html=context['memory_cards_html'],
        event_cards_html=context['event_cards_html'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        options_html=_options_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )
@app.get("/ui/assets", response_class=HTMLResponse)
def ui_assets_manifest(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    items = list(ASSET_MANIFEST)
    types = sorted({str(item.get('type', 'unknown')) for item in items})
    grouped: Dict[str, List[Dict[str, object]]] = {}
    for item in items:
        grouped.setdefault(str(item.get('type', 'unknown')), []).append(item)
    groups_html = ''.join(
        f'''<div class="card"><h2>{escape(type_name)}</h2>{_render_rows(rows, [('ID', 'id'), ('Version', 'version'), ('Description', 'description'), ('Path', 'path')])}</div>'''
        for type_name, rows in grouped.items()
    )
    return render_assets_page(
        item_count=len(items),
        type_count=len(types),
        server_time_value=server_time(),
        types=types,
        groups_html=groups_html,
        notice_html=_notice_html,
        kv_table=_kv_table,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )


@app.get("/ui/action/model-route-config")
def ui_action_model_route_config(
    default_route_id: Optional[str] = None,
    fallback_route_ids: str = "",
    prefer_enabled: str = "1",
    allow_manual_override: str = "1",
    routing_notes: str = "",
):
    req = ModelRouteConfigUpdateRequest(
        default_route_id=default_route_id or None,
        fallback_route_ids=[item.strip() for item in fallback_route_ids.split(',') if item.strip()],
        prefer_enabled=prefer_enabled not in {"0", "false", "False"},
        allow_manual_override=allow_manual_override not in {"0", "false", "False"},
        routing_notes=routing_notes,
    )
    model_routes_config_update(req)
    return _redirect_with_message("/ui/config", "模型路由配置已更新")


@app.get("/ui/action/resource-pack-enable")
def ui_action_resource_pack_enable(pack_id: str, enabled: str = "1"):
    resource_pack_enable(pack_id, ResourcePackEnableRequest(enabled=enabled not in {"0", "false", "False"}))
    return _redirect_with_message("/ui/resources", f"资源包 {pack_id} 状态已更新")


@app.get("/ui/action/resource-pack-rollback")
def ui_action_resource_pack_rollback(pack_id: str, version: Optional[str] = None):
    try:
        resource_pack_rollback(pack_id, version)
    except HTTPException as exc:
        return _redirect_with_message("/ui/resources", f"资源包回滚失败：{exc.detail}", "warn")
    return _redirect_with_message("/ui/resources", f"资源包 {pack_id} 已执行回滚")


@app.get("/ui/action/resource-pack-import-sample")
def ui_action_resource_pack_import_sample(
    pack_id: str = "pack-demo",
    name: str = "演示资源包",
    pack_type: str = "theme-assets",
    version: str = "0.1.0",
    species_id: Optional[str] = "cat-default",
    theme_id: Optional[str] = "cat-gold-day",
    enabled: Optional[str] = None,
):
    manifest = ResourcePackManifest(
        pack_id=pack_id,
        pack_type=pack_type,
        version=version,
        species_id=species_id or None,
        theme_id=theme_id or None,
        name=name,
        description="Imported from backend UI sample action.",
        slots=[],
    )
    try:
        resource_pack_import(ResourcePackImportRequest(manifest=manifest, enabled=bool(enabled), replace=True))
    except HTTPException as exc:
        return _redirect_with_message("/ui/resources", f"导入失败：{exc.detail}", "warn")
    return _redirect_with_message("/ui/resources", f"示例资源包 {pack_id} 已导入")


@app.get("/ui/actions", response_class=HTMLResponse)
def ui_actions(msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    device_ids = sorted(DEVICES.keys())
    pet_ids = sorted(PETS.keys())
    return render_actions_page(
        device_ids=device_ids,
        pet_ids=pet_ids,
        options_html=_options_html,
        notice_html=_notice_html,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )


@app.post("/ui/action/register-device")
def ui_action_register_device(
    device_id: str = Form(...),
    hardware_model: str = Form("esp32-s3"),
    firmware_version: str = Form("0.1.0"),
    capabilities: str = Form("lcd,touch,wifi"),
):
    req = DeviceRegisterRequest(
        device_id=device_id,
        hardware_model=hardware_model,
        firmware_version=firmware_version,
        capabilities=[item.strip() for item in capabilities.split(',') if item.strip()],
    )
    device_register(req)
    return _redirect_with_message("/ui", f"设备 {device_id} 已注册/刷新")


@app.get("/ui/action/heartbeat")
def ui_action_heartbeat(device_id: str, note: str = "manual heartbeat from ui"):
    device_heartbeat(DeviceHeartbeatRequest(device_id=device_id, note=note))
    return _redirect_with_message(f"/ui/device/{device_id}", f"已向 {device_id} 发送心跳")


@app.get("/ui/action/device-event")
def ui_action_device_event(device_id: str, kind: str = "resume", message: str = "manual device event from ui"):
    device_event(device_id, DeviceEventRequest(kind=kind, message=message, meta={"source": "ui"}))
    return _redirect_with_message(f"/ui/device/{device_id}", f"已写入设备事件：{kind}")


@app.post("/ui/action/bind-confirm")
def ui_action_bind_confirm(
    device_id: str = Form(...),
    bind_code: str = Form(...),
    owner_id: str = Form(...),
):
    try:
        result = device_bind_confirm(BindConfirmRequest(device_id=device_id, bind_code=bind_code, owner_id=owner_id))
    except HTTPException as exc:
        return _redirect_with_message(f"/ui/device/{device_id}", f"绑定确认失败：{exc.detail}", "warn")
    target = f"/ui/pet/{result.pet_id}" if result.pet_id else f"/ui/device/{device_id}"
    return _redirect_with_message(target, f"设备 {device_id} 已绑定到 owner={owner_id}")


@app.post("/ui/action/device-state")
def ui_action_device_state(
    device_id: str = Form(...),
    pet_id: Optional[str] = Form(None),
    state_json: str = Form("{}"),
):
    try:
        state = _parse_json_object(state_json)
    except (ValueError, json.JSONDecodeError):
        return _redirect_with_message(f"/ui/device/{device_id}", "state_json 不是合法 JSON 对象", "warn")
    try:
        device_state(DeviceStateRequest(device_id=device_id, pet_id=pet_id or None, state=state))
    except HTTPException as exc:
        return _redirect_with_message(f"/ui/device/{device_id}", f"设备状态提交失败：{exc.detail}", "warn")
    return _redirect_with_message(f"/ui/device/{device_id}", f"设备 {device_id} 状态已更新")


@app.post("/ui/action/create-pet")
def ui_action_create_pet(
    pet_id: str = Form(...),
    name: str = Form("nuonuo"),
    species_id: str = Form("cat-default"),
    theme_id: str = Form("cat-gold-day"),
    owner_id: Optional[str] = Form(None),
    device_id: Optional[str] = Form(None),
):
    req = PetCreateRequest(
        pet_id=pet_id,
        name=name,
        species_id=species_id,
        theme_id=theme_id,
        owner_id=owner_id or None,
        device_id=device_id or None,
    )
    pet_create(req)
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"宠物 {pet_id} 已创建")


@app.post("/ui/action/link-device")
def ui_action_link_device(
    pet_id: str = Form(...),
    device_id: str = Form(...),
    make_primary: Optional[str] = Form(None),
):
    try:
        link_pet_device(pet_id, PetDeviceLinkRequest(device_id=device_id, make_primary=bool(make_primary)))
    except HTTPException as exc:
        return _redirect_with_message("/ui/actions", f"绑定失败：{exc.detail}", "warn")
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"已将设备 {device_id} 绑定到宠物 {pet_id}")


@app.post("/ui/action/set-primary-device")
def ui_action_set_primary_device(
    pet_id: str = Form(...),
    device_id: str = Form(...),
):
    try:
        set_pet_primary_device(pet_id, PetDevicePrimaryRequest(device_id=device_id))
    except HTTPException as exc:
        return _redirect_with_message("/ui/actions", f"设置主设备失败：{exc.detail}", "warn")
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"主设备已切换为 {device_id}")


@app.post("/ui/action/unlink-device")
def ui_action_unlink_device(
    pet_id: str = Form(...),
    device_id: str = Form(...),
    remove_primary: Optional[str] = Form(None),
):
    try:
        unlink_pet_device(pet_id, PetDeviceUnlinkRequest(device_id=device_id, remove_primary=bool(remove_primary)))
    except HTTPException as exc:
        return _redirect_with_message("/ui/actions", f"解绑失败：{exc.detail}", "warn")
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"已解绑设备 {device_id}")


@app.post("/ui/action/update-device")
def ui_action_update_device(
    device_id: str = Form(...),
    hardware_model: str = Form(""),
    firmware_version: str = Form(""),
    capabilities: str = Form(""),
    owner_id: str = Form(""),
    connection_state: str = Form(""),
    offline_reason: str = Form(""),
    bound: Optional[str] = Form(None),
    state_json: str = Form("{}"),
):
    rec = DEVICES.get(device_id)
    if rec is None:
        return _redirect_with_message("/ui", f"设备 {device_id} 不存在", "warn")
    try:
        state = _parse_json_object(state_json)
    except (ValueError, json.JSONDecodeError):
        return _redirect_with_message(f"/ui/device/{device_id}", "state_json 不是合法 JSON 对象", "warn")
    rec.hardware_model = hardware_model.strip() or rec.hardware_model
    rec.firmware_version = firmware_version.strip() or rec.firmware_version
    rec.capabilities = [item.strip() for item in capabilities.split(',') if item.strip()]
    rec.owner_id = owner_id.strip() or None
    rec.connection_state = connection_state.strip() or rec.connection_state
    rec.offline_reason = offline_reason.strip() or None
    rec.bound = bool(bound)
    rec.state = state
    save_state()
    return _redirect_with_message(f"/ui/device/{device_id}", f"设备 {device_id} 已更新")


@app.post("/ui/action/import-resource-pack")
def ui_action_import_resource_pack(
    pack_id: str = Form(...),
    name: str = Form(...),
    pack_type: str = Form("theme-assets"),
    version: str = Form("0.1.0"),
    species_id: str = Form(""),
    theme_id: str = Form(""),
    description: str = Form(""),
    slots_json: str = Form("[]"),
    enabled: Optional[str] = Form(None),
    replace: Optional[str] = Form(None),
):
    try:
        parsed_slots = json.loads(slots_json or "[]")
        if not isinstance(parsed_slots, list):
            raise ValueError('slots_json must be a JSON array')
        slots = [ResourceSlotItem(**item) for item in parsed_slots]
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return _redirect_with_message("/ui/resources", f"slots_json 不合法：{exc}", "warn")
    manifest = ResourcePackManifest(
        pack_id=pack_id,
        name=name,
        pack_type=pack_type,
        version=version,
        species_id=species_id.strip() or None,
        theme_id=theme_id.strip() or None,
        description=description.strip() or None,
        slots=slots,
    )
    try:
        resource_pack_import(ResourcePackImportRequest(manifest=manifest, enabled=bool(enabled), replace=bool(replace)))
    except HTTPException as exc:
        return _redirect_with_message("/ui/resources", f"资源包导入失败：{exc.detail}", "warn")
    return _redirect_with_message("/ui/resources", f"资源包 {pack_id} 已导入")


@app.post("/ui/action/write-memory")
def ui_action_write_memory(
    pet_id: str = Form(...),
    kind: str = Form("short"),
    text: str = Form(...),
    tags: str = Form("manual,ui"),
):
    write_memory(
        pet_id,
        MemoryWriteRequest(
            item=MemoryItem(
                kind=kind,
                text=text,
                tags=[item.strip() for item in tags.split(',') if item.strip()],
            )
        ),
    )
    return _redirect_with_message(f"/ui/memory?pet_id={pet_id}", f"已为 {pet_id} 写入 {kind} 记忆")


@app.post("/ui/action/chat")
def ui_action_chat(
    pet_id: str = Form(...),
    user_text: str = Form(...),
    device_id: Optional[str] = Form(None),
    mode: Optional[str] = Form(None),
    context_json: str = Form("{}"),
):
    context: Dict[str, object] = {}
    try:
        parsed = json.loads(context_json or "{}")
        if isinstance(parsed, dict):
            context = parsed
    except json.JSONDecodeError:
        return _redirect_with_message(f"/ui/chat?pet_id={pet_id}", "context_json 不是合法 JSON", "warn")
    if mode:
        context["mode"] = mode
    result = chat(ChatRequest(pet_id=pet_id, device_id=device_id or None, user_text=user_text, context=context))
    message = f"回复：{result.reply_text}｜emotion={result.emotion}｜actions={','.join(result.actions)}"
    return _redirect_with_message(f"/ui/chat?pet_id={pet_id}", message)


@app.post("/ui/action/bulk-device-op")
def ui_action_bulk_device_op(
    device_ids: str = Form(...),
    operation: str = Form("heartbeat"),
    message: str = Form("manual bulk operation from devices page"),
    owner_id: str = Form(""),
    pet_id: str = Form(""),
):
    return handle_bulk_device_op(
        ids=_parse_bulk_ids(device_ids),
        operation=operation,
        message=message,
        owner_id=owner_id,
        pet_id=pet_id,
        server_time=server_time,
        save_state=save_state,
        device_heartbeat=device_heartbeat,
        device_event=device_event,
        pets_claiming_device=pets_claiming_device,
        link_pet_device=link_pet_device,
        unlink_pet_device=unlink_pet_device,
    )


@app.post("/ui/action/bulk-pet-op")
def ui_action_bulk_pet_op(
    pet_ids: str = Form(...),
    event_kind: str = Form("feed"),
    event_text: str = Form("manual bulk pet event from pets page"),
    device_id: str = Form(""),
    owner_id: str = Form(""),
):
    return handle_bulk_pet_op(
        ids=_parse_bulk_ids(pet_ids),
        event_kind=event_kind,
        event_text=event_text,
        device_id=device_id,
        owner_id=owner_id,
        save_state=save_state,
        link_pet_device=link_pet_device,
        unlink_pet_device=unlink_pet_device,
        pet_linked_device_ids=pet_linked_device_ids,
        set_pet_primary_device=set_pet_primary_device,
        pet_update=pet_update,
        pet_event=pet_event,
    )


@app.post("/ui/action/update-pet")
def ui_action_update_pet(
    pet_id: str = Form(...),
    name: str = Form(""),
    species_id: str = Form(""),
    theme_id: str = Form(""),
    model_route_id: str = Form(""),
    model_provider: str = Form(""),
    model_name: str = Form(""),
    growth_stage: str = Form(""),
    level: str = Form(""),
    exp: str = Form(""),
    mood: str = Form(""),
    energy: str = Form(""),
    hunger: str = Form(""),
    affection: str = Form(""),
    owner_id: str = Form(""),
    device_id: str = Form(""),
):
    def _parse_optional_int(value: str) -> Optional[int]:
        value = value.strip()
        if not value:
            return None
        return int(value)

    try:
        req = PetUpdateRequest(
            name=name.strip() or None,
            species_id=species_id.strip() or None,
            theme_id=theme_id.strip() or None,
            model_route_id=model_route_id.strip() or None,
            model_provider=model_provider.strip() or None,
            model_name=model_name.strip() or None,
            growth_stage=growth_stage.strip() or None,
            level=_parse_optional_int(level),
            exp=_parse_optional_int(exp),
            mood=mood.strip() or None,
            energy=_parse_optional_int(energy),
            hunger=_parse_optional_int(hunger),
            affection=_parse_optional_int(affection),
            owner_id=owner_id.strip() or None,
            device_id=device_id.strip() or None,
        )
    except ValueError:
        return _redirect_with_message(f"/ui/pet/{pet_id}", "数值字段格式不正确", "warn")
    pet_update(pet_id, req)
    save_state()
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"宠物 {pet_id} 已更新")


@app.get("/ui/action/pet-event")
def ui_action_pet_event(pet_id: str, kind: str = "play", text: str = "manual pet event from ui"):
    pet_event(pet_id, PetEventRequest(pet_id=pet_id, kind=kind, text=text, tags=["ui", "manual"]))
    return _redirect_with_message(f"/ui/pet/{pet_id}", f"已写入宠物事件：{kind}")


@app.get("/ui/action/bind-request", response_class=HTMLResponse)
def ui_action_bind_request(device_id: str):
    result = device_bind_request(BindRequest(device_id=device_id))
    return render_bind_request_page(
        device_id=result.device_id,
        bind_code=result.bind_code,
        expires_at=result.expires_at,
        expires_in_seconds=result.expires_in_seconds,
        kv_table=_kv_table,
        page_shell=_page_shell,
    )




@app.get("/ui/device/{device_id}", response_class=HTMLResponse)
def ui_device_detail(device_id: str, msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    try:
        context = build_device_detail_context(
            device_id=device_id,
            device_health_snapshot=device_health_snapshot,
            build_device_sync_summary=build_device_sync_summary,
            build_device_display_profile=build_device_display_profile,
            pet_device_owner=pet_device_owner,
            textarea_json=_textarea_json,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="device not found")
    rec = context['rec']
    return render_device_detail_page(
        device_id=device_id,
        hardware_model=rec.hardware_model,
        firmware_version=rec.firmware_version,
        owner_id=rec.owner_id,
        owner_pet_id=context['owner_pet_id'],
        basic_status_rows=context['basic_status_rows'],
        sync_rows=context['sync_rows'],
        display_rows=context['display_rows'],
        state_json_text=context['state_json_text'],
        default_state_json=context['default_state_json'],
        capabilities_csv=context['capabilities_csv'],
        connection_state=rec.connection_state,
        offline_reason=rec.offline_reason,
        bound=rec.bound,
        bind_code=rec.bind_code,
        events_html=context['events_html'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )

@app.get("/ui/pet/{pet_id}", response_class=HTMLResponse)
def ui_pet_detail(pet_id: str, msg: Optional[str] = None, level: str = "ok") -> HTMLResponse:
    context = build_pet_detail_context(
        pet_id=pet_id,
        pet_or_404=pet_or_404,
        build_pet_sync_summary=build_pet_sync_summary,
        pet_growth_summary=pet_growth_summary,
        build_preview=build_preview,
        pet_linked_device_ids=pet_linked_device_ids,
        options_html=_options_html,
    )
    pet = context['pet']
    return render_pet_detail_page(
        pet_id=pet_id,
        pet_name=pet.name,
        species_id=pet.species_id,
        theme_id=pet.theme_id,
        mood=pet.mood,
        level_value=pet.level,
        basic_rows=context['basic_rows'],
        sync_rows=context['sync_rows'],
        growth_rows=context['growth_rows'],
        preview_rows=context['preview_rows'],
        device_manage_html=context['device_manage_html'],
        events_html=context['events_html'],
        device_options_html=context['device_options_html'],
        form_defaults=context['form_defaults'],
        notice_html=_notice_html,
        kv_table=_kv_table,
        page_shell=_page_shell,
        msg=msg,
        level=level,
    )


# ============================================================================
# Voice Recognition APIs
# ============================================================================

from fastapi import UploadFile, File
import tempfile
import os
import base64

# Voice commands definition
VOICE_COMMANDS = [
    {"command_id": 0, "keyword": "你好", "description": "打招呼", "action": "greet"},
    {"command_id": 1, "keyword": "喂食", "description": "喂食宠物", "action": "feed"},
    {"command_id": 2, "keyword": "玩耍", "description": "与宠物玩耍", "action": "play"},
    {"command_id": 3, "keyword": "睡觉", "description": "宠物睡觉", "action": "sleep"},
    {"command_id": 4, "keyword": "状态", "description": "查看状态", "action": "status"},
    {"command_id": 5, "keyword": "设置", "description": "打开设置", "action": "settings"},
]


@app.post("/api/voice/recognize")
async def voice_recognize(
    pet_id: str,
    audio: UploadFile = File(...),
    audio_format: str = "wav",
    sample_rate: int = 16000,
    language: str = "zh-CN"
):
    """
    Voice recognition API
    
    Receives audio file, performs speech recognition, returns result
    """
    pet = pet_or_404(pet_id)
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as tmp:
        audio_data = await audio.read()
        tmp.write(audio_data)
        tmp_path = tmp.name
    
    try:
        # Call ASR service (simulated for now)
        recognized_text = await simulate_voice_recognition(tmp_path, language)
        
        # Check if it's a command
        is_command = False
        command_id = None
        for cmd in VOICE_COMMANDS:
            if cmd["keyword"] in recognized_text:
                is_command = True
                command_id = cmd["command_id"]
                
                # Execute command action
                await execute_voice_command(pet_id, cmd["action"])
                break
        
        return {
            "ok": True,
            "pet_id": pet_id,
            "text": recognized_text,
            "confidence": 0.95,
            "is_command": is_command,
            "command_id": command_id,
            "server_time": server_time()
        }
    
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.get("/api/voice/commands")
async def get_voice_commands():
    """
    Get supported voice commands list
    """
    return {
        "ok": True,
        "commands": VOICE_COMMANDS,
        "server_time": server_time()
    }


@app.post("/api/voice/synthesize")
async def voice_synthesize(
    text: str,
    voice_type: str = "default",
    speed: float = 1.0,
    pitch: float = 1.0
):
    """
    Voice synthesis API (TTS)
    
    Converts text to speech
    """
    # Simulate TTS (should integrate real TTS service)
    audio_url = await simulate_voice_synthesis(text, voice_type)
    
    # Estimate duration (assume 0.3s per character)
    duration_ms = int(len(text) * 300 * speed)
    
    return {
        "ok": True,
        "audio_url": audio_url,
        "duration_ms": duration_ms,
        "server_time": server_time()
    }


@app.post("/api/voice/command")
async def execute_voice_command_endpoint(pet_id: str, action: str):
    """
    Execute voice command
    """
    pet = pet_or_404(pet_id)
    
    # Execute action
    result = await execute_voice_command(pet_id, action)
    
    return {
        "ok": True,
        "pet_id": pet_id,
        "action": action,
        "result": result,
        "server_time": server_time()
    }


# Helper functions for voice processing
async def simulate_voice_recognition(audio_path: str, language: str) -> str:
    """
    Simulate voice recognition (should integrate real ASR service)
    
    Real ASR services:
    - Baidu ASR API
    - iFlytek ASR API
    - Alibaba Cloud ASR API
    - Local Whisper model
    """
    # TODO: Integrate real ASR service
    # For now, return simulated result
    return "你好"


async def simulate_voice_synthesis(text: str, voice_type: str) -> str:
    """
    Simulate voice synthesis (should integrate real TTS service)
    """
    # TODO: Integrate real TTS service
    # Return audio file URL
    return f"/static/audio/synthesized_{hash(text)}.wav"


async def execute_voice_command(pet_id: str, action: str) -> dict:
    """
    Execute voice command action
    """
    pet = pet_or_404(pet_id)
    
    # Execute action based on command
    if action == "feed":
        # Feed pet
        pet.hunger = min(100, (pet.hunger or 50) + 10)
        pet.happiness = min(100, (pet.happiness or 50) + 5)
        result = {"message": "宠物已喂食", "hunger": pet.hunger, "happiness": pet.happiness}
    
    elif action == "play":
        # Play with pet
        pet.happiness = min(100, (pet.happiness or 50) + 15)
        pet.energy = max(0, (pet.energy or 50) - 10)
        result = {"message": "与宠物玩耍", "happiness": pet.happiness, "energy": pet.energy}
    
    elif action == "sleep":
        # Pet sleep
        pet.is_sleeping = True
        result = {"message": "宠物开始睡觉"}
    
    elif action == "status":
        # Check status
        result = {
            "message": "宠物状态",
            "hunger": pet.hunger,
            "happiness": pet.happiness,
            "energy": pet.energy,
            "mood": pet.mood
        }
    
    elif action == "greet":
        # Greeting
        result = {"message": "你好！"}
    
    elif action == "settings":
        # Open settings
        result = {"message": "打开设置"}
    
    else:
        result = {"message": f"未知命令: {action}"}
    
    save_state()
    
    return result
