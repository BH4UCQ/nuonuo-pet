#!/usr/bin/env python3
"""nuonuo-pet 端到端自检。

说明：
- 这个脚本不依赖 FastAPI。
- 它直接调用/复刻后端核心状态逻辑，用来验证：
  注册 → 绑定 → 创建宠物 → 成长事件 → 离线 → 恢复 → 查询摘要
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from pprint import pprint

ROOT = Path(__file__).resolve().parents[1]
STORAGE_PATH = ROOT / "backend" / "app" / "storage.py"
spec = spec_from_file_location("nuonuo_storage", STORAGE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load storage module from {STORAGE_PATH}")
storage = module_from_spec(spec)
import sys
sys.modules[spec.name] = storage
spec.loader.exec_module(storage)

DEVICES = storage.DEVICES
DEVICE_EVENTS = storage.DEVICE_EVENTS
PETS = storage.PETS
MEMORY = storage.MEMORY
EVENTS = storage.EVENTS
DeviceRecord = storage.DeviceRecord
PetRecord = storage.PetRecord
DeviceEventRecord = storage.DeviceEventRecord
EventRecord = storage.EventRecord
new_bind_code = storage.new_bind_code
now_iso = storage.now_iso
SPECIES_TEMPLATES = storage.SPECIES_TEMPLATES
MODEL_ROUTES = storage.MODEL_ROUTES


def reset_state() -> None:
    DEVICES.clear()
    DEVICE_EVENTS.clear()
    PETS.clear()
    MEMORY.clear()
    EVENTS.clear()


def server_time() -> str:
    return now_iso()


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


def apply_model_route_to_pet(pet: PetRecord) -> None:
    route = model_route_for(pet.model_route_id)
    if route is None:
        return
    pet.model_provider = route.get("provider")
    pet.model_name = route.get("model_name")


def device_touch(rec: DeviceRecord) -> None:
    rec.last_seen_at = server_time()
    rec.connection_state = "paired" if rec.bound else "unbound"
    rec.offline_reason = None


def device_is_offline(rec: DeviceRecord, stale_after_seconds: int = 300) -> bool:
    if rec.connection_state == "offline":
        return True
    if rec.last_seen_at is None:
        return False
    try:
        last_seen = datetime.fromisoformat(rec.last_seen_at)
    except Exception:
        return True
    age = (datetime.now(timezone.utc) - last_seen).total_seconds()
    return age > stale_after_seconds


def device_health_snapshot(rec: DeviceRecord, stale_after_seconds: int = 300) -> dict:
    offline = device_is_offline(rec, stale_after_seconds=stale_after_seconds)
    connection_state = rec.connection_state
    offline_reason = rec.offline_reason
    if offline:
        connection_state = "offline"
        if offline_reason is None and rec.last_seen_at is not None:
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


def sync_pets_with_device(rec: DeviceRecord, reason: str, state: dict | None = None) -> None:
    for pet in PETS.values():
        if pet.device_id != rec.device_id:
            continue
        EVENTS.setdefault(pet.pet_id, []).append(
            EventRecord(
                kind=reason,
                text=f"device {rec.device_id} {reason}",
                tags=["device", reason],
                created_at=server_time(),
            )
        )
        if reason == "resume":
            pet.mood = "curious" if pet.mood == "neutral" else pet.mood
            pet.energy = normalize_bounds(pet.energy + 5)
        else:
            pet.mood = "lonely"
            pet.energy = normalize_bounds(pet.energy - 5)


def register_device(device_id: str, hardware_model: str, firmware_version: str, capabilities: list[str]) -> DeviceRecord:
    rec = DeviceRecord(
        device_id=device_id,
        hardware_model=hardware_model,
        firmware_version=firmware_version,
        capabilities=list(capabilities),
    )
    DEVICES[device_id] = rec
    return rec


def request_bind_code(device_id: str) -> DeviceRecord:
    rec = DEVICES[device_id]
    rec.bind_code = new_bind_code()
    rec.bind_expires_at = datetime.now(timezone.utc).timestamp() + 600
    return rec


def confirm_binding(device_id: str, bind_code: str, owner_id: str) -> tuple[DeviceRecord, str]:
    rec = DEVICES[device_id]
    if rec.bind_code != bind_code:
        raise ValueError("invalid bind code")
    rec.bound = True
    rec.owner_id = owner_id
    rec.connection_state = "paired"
    device_touch(rec)
    record_device_event(device_id, "bind_confirm", "device binding confirmed", {"owner_id": owner_id})
    rec.bind_code = None
    rec.bind_expires_at = None
    pet_id = f"pet-{device_id}"
    if pet_id not in PETS:
        PETS[pet_id] = PetRecord(pet_id=pet_id, owner_id=owner_id, device_id=device_id)
    return rec, pet_id


def pet_create(pet_id: str, owner_id: str, device_id: str, species_id: str, theme_id: str) -> PetRecord:
    pet = PETS.get(pet_id)
    if pet is None:
        pet = PetRecord(
            pet_id=pet_id,
            owner_id=owner_id,
            device_id=device_id,
            species_id=species_id,
            theme_id=theme_id,
        )
        PETS[pet_id] = pet
    align_pet_to_species(pet)
    apply_model_route_to_pet(pet)
    device = DEVICES.get(device_id)
    if device is not None:
        snap = device_health_snapshot(device)
        pet.device_connection_state = snap["connection_state"]
        pet.device_last_seen_at = snap["last_seen_at"]
        pet.device_is_offline = snap["is_offline"]
        pet.device_offline_reason = snap["offline_reason"]
    return pet


def pet_event(pet_id: str, kind: str, text: str, tags: list[str] | None = None) -> dict:
    pet = PETS[pet_id]
    EVENTS.setdefault(pet_id, []).append(
        EventRecord(kind=kind, text=text, tags=list(tags or []), created_at=server_time())
    )
    kind_lower = kind.lower().strip()
    if kind_lower in {"play", "game", "chat"}:
        pet.energy = normalize_bounds(pet.energy - 8)
        pet.affection = normalize_bounds(pet.affection + 6)
        pet.exp += 6
        pet.mood = "happy"
    else:
        pet.exp += 2
    level_up_if_needed(pet)
    return {"ok": True, "pet_id": pet_id, "event_count": len(EVENTS[pet_id]), "server_time": server_time()}


def pet_growth_summary(pet_id: str) -> dict:
    pet = PETS[pet_id]
    species = species_template_for(pet.species_id) or {}
    return {
        "pet_id": pet.pet_id,
        "name": pet.name,
        "species_id": pet.species_id,
        "growth_stage": pet.growth_stage,
        "level": pet.level,
        "exp": pet.exp,
        "next_level_exp": pet.level * 10,
        "growth_curve": dict(species.get("growth_curve", {})),
        "recent_events": [
            {
                "kind": item.kind,
                "text": item.text,
                "tags": list(item.tags),
                "created_at": item.created_at,
            }
            for item in EVENTS.get(pet_id, [])[-5:]
        ],
        "server_time": server_time(),
    }


def device_state(device_id: str, state: dict) -> dict:
    rec = DEVICES[device_id]
    was_offline = device_is_offline(rec)
    rec.state = dict(state)
    device_touch(rec)
    rec.connection_state = "paired" if rec.bound else "unbound"
    if state.get("offline"):
        rec.connection_state = "offline"
        rec.offline_reason = str(state.get("offline_reason") or "device reported offline")
        record_device_event(device_id, "offline", rec.offline_reason, {"state": dict(state)})
        sync_pets_with_device(rec, rec.offline_reason, state)
    else:
        if rec.bound:
            record_device_event(device_id, "state", "device state updated", {"state": dict(state)})
        if was_offline:
            record_device_event(device_id, "resume", "device recovered from offline", {"state": dict(state)})
            sync_pets_with_device(rec, "resume", state)
    return {
        "ok": True,
        "device_id": device_id,
        "server_time": server_time(),
        "binding_state": "bound" if rec.bound else "unbound",
    }


def device_heartbeat(device_id: str, note: str | None = None) -> dict:
    rec = DEVICES[device_id]
    was_offline = device_is_offline(rec)
    device_touch(rec)
    rec.connection_state = "paired" if rec.bound else "unbound"
    record_device_event(device_id, "heartbeat", "device heartbeat received", {"note": note})
    if was_offline:
        record_device_event(device_id, "resume", "device recovered from offline via heartbeat", {"note": note})
        sync_pets_with_device(rec, "resume", {"note": note})
    return {
        "ok": True,
        "device_id": rec.device_id,
        "connection_state": rec.connection_state,
        "last_seen_at": rec.last_seen_at,
        "server_time": server_time(),
        "state": dict(rec.state),
        "hardware_model": rec.hardware_model,
        "firmware_version": rec.firmware_version,
        "capabilities": list(rec.capabilities),
        "bound": rec.bound,
        "owner_id": rec.owner_id,
        "bind_code": rec.bind_code,
        "bind_expires_at": rec.bind_expires_at,
    }


def device_health(device_id: str, stale_after_seconds: int = 300) -> dict:
    rec = DEVICES[device_id]
    snap = device_health_snapshot(rec, stale_after_seconds=stale_after_seconds)
    if snap["is_offline"]:
        rec.offline_reason = snap["offline_reason"]
    return snap


def device_events(device_id: str) -> list[dict]:
    return [asdict(item) for item in DEVICE_EVENTS.get(device_id, [])]


def device_pet(device_id: str) -> PetRecord:
    pet = next((item for item in PETS.values() if item.device_id == device_id), None)
    if pet is None:
        raise KeyError("pet not found for device")
    return pet


def main() -> None:
    reset_state()
    print("== nuonuo-pet e2e self-test ==")

    device_id = "demo-device-001"
    owner_id = "owner-demo"

    dev = register_device(
        device_id=device_id,
        hardware_model="esp32-s3-lcd-1.85",
        firmware_version="0.1.0",
        capabilities=["lcd", "touch", "wifi", "speaker"],
    )
    print("[1] register")
    pprint(asdict(dev))

    dev = request_bind_code(device_id)
    print("[2] request bind code")
    pprint({"device_id": dev.device_id, "bind_code": dev.bind_code, "expires_at": dev.bind_expires_at})

    rec, pet_id = confirm_binding(device_id, dev.bind_code or "", owner_id)
    print("[3] confirm binding")
    pprint({"device_id": rec.device_id, "bound": rec.bound, "owner_id": rec.owner_id, "pet_id": pet_id})

    pet = pet_create(pet_id=pet_id, owner_id=owner_id, device_id=device_id, species_id="cat-default", theme_id="cat-gold-day")
    print("[4] pet create")
    pprint(asdict(pet))

    event = pet_event(pet_id=pet_id, kind="play", text="一起玩一会儿", tags=["selftest", "growth"])
    print("[5] pet event")
    pprint(event)

    growth = pet_growth_summary(pet_id)
    print("[6] growth summary")
    pprint(growth)

    state_offline = device_state(device_id, {"offline": True, "offline_reason": "power save"})
    print("[7] device offline state")
    pprint(state_offline)

    health_offline = device_health(device_id)
    print("[8] health after offline")
    pprint(health_offline)

    heartbeat = device_heartbeat(device_id, note="reconnect after test")
    print("[9] heartbeat recovery")
    pprint(heartbeat)

    health_online = device_health(device_id)
    print("[10] health after recovery")
    pprint(health_online)

    evs = device_events(device_id)
    print("[11] device events")
    pprint(evs)

    pet_view = device_pet(device_id)
    print("[12] device pet lookup")
    pprint(asdict(pet_view))

    print("OK: e2e flow completed")


if __name__ == "__main__":
    main()
