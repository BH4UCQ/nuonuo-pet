#!/usr/bin/env python3
"""nuonuo-pet 广播同步自检。

验证内容：
- 设备注册 / 绑定
- 设备离线 / 恢复
- 宠物同步摘要 / 广播摘要
- 关联设备事件留痕
"""
from __future__ import annotations

from dataclasses import asdict
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from pprint import pprint
import sys

ROOT = Path(__file__).resolve().parents[1]
STORAGE_PATH = ROOT / "backend" / "app" / "storage.py"


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


storage = load_module("nuonuo_storage_sync", STORAGE_PATH)

DEVICES = storage.DEVICES
DEVICE_EVENTS = storage.DEVICE_EVENTS
PETS = storage.PETS
MEMORY = storage.MEMORY
EVENTS = storage.EVENTS
DeviceRecord = storage.DeviceRecord
PetRecord = storage.PetRecord
new_bind_code = storage.new_bind_code


def reset_state() -> None:
    DEVICES.clear()
    DEVICE_EVENTS.clear()
    PETS.clear()
    MEMORY.clear()
    EVENTS.clear()




def server_time() -> str:
    return storage.now_iso()


def device_is_offline(rec: DeviceRecord, stale_after_seconds: int = 300) -> bool:
    if rec.connection_state == "offline":
        return True
    if rec.last_seen_at is None:
        return False
    return False


def device_health_snapshot(rec: DeviceRecord) -> dict:
    offline = device_is_offline(rec)
    return {
        "device_id": rec.device_id,
        "bound": rec.bound,
        "connection_state": rec.connection_state,
        "last_seen_at": rec.last_seen_at,
        "is_offline": offline,
        "offline_reason": rec.offline_reason,
        "stale_after_seconds": 300,
        "server_time": server_time(),
    }


def pet_linked_device_ids(pet: PetRecord) -> list[str]:
    ids = list(getattr(pet, "linked_device_ids", []) or [])
    if pet.device_id:
        ids.insert(0, pet.device_id)
    deduped: list[str] = []
    for device_id in ids:
        if device_id and device_id not in deduped:
            deduped.append(device_id)
    return deduped


def pets_for_device(device_id: str) -> list[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


def broadcast_device_event_to_pet(pet: PetRecord, source_device_id: str, kind: str, message: str, meta: dict | None = None) -> None:
    payload = dict(meta or {})
    payload["source_device_id"] = source_device_id
    payload["broadcast"] = True
    EVENTS.setdefault(pet.pet_id, []).append(
        storage.EventRecord(
            kind=kind,
            text=message,
            tags=["device", "broadcast", "system"],
            created_at=server_time(),
        )
    )
    if source_device_id:
        DEVICE_EVENTS.setdefault(source_device_id, []).append(
            storage.DeviceEventRecord(
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
            storage.DeviceEventRecord(
                device_id=linked_device_id,
                kind=f"sync:{kind}",
                message=message,
                created_at=server_time(),
                meta=payload,
            )
        )


def sync_pets_with_device(rec: DeviceRecord, reason: str, meta: dict | None = None) -> None:
    pets = pets_for_device(rec.device_id)
    if not pets:
        return
    for pet in pets:
        if rec.connection_state == "offline":
            pet.mood = "lonely" if pet.affection < 40 else pet.mood
            broadcast_device_event_to_pet(pet, rec.device_id, "device-offline", reason, meta)
        elif reason in {"reconnect", "resume", "heartbeat"}:
            pet.energy = min(100, pet.energy + 5)
            if pet.mood == "lonely":
                pet.mood = "curious"
            broadcast_device_event_to_pet(pet, rec.device_id, "device-reconnect", reason, meta)
        elif meta:
            broadcast_device_event_to_pet(pet, rec.device_id, "device-state", reason, meta)
    storage.save_state()


def build_pet_sync_summary(pet: PetRecord):
    linked_ids = pet_linked_device_ids(pet)
    device_items = []
    recent_device_events = {}
    sync_notes = []
    for idx, device_id in enumerate(linked_ids):
        device = DEVICES.get(device_id)
        health = device_health_snapshot(device) if device is not None else None
        recent_device_events[device_id] = [
            {
                "kind": item.kind,
                "message": item.message,
                "created_at": item.created_at,
                "meta": dict(item.meta),
            } for item in DEVICE_EVENTS.get(device_id, [])[-3:]
        ]
        if health is None:
            sync_notes.append(f"device {device_id} missing")
        elif health["is_offline"]:
            sync_notes.append(f"device {device_id} offline")
        device_items.append({
            "device_id": device_id,
            "is_primary": idx == 0,
            "connection_state": health["connection_state"] if health else None,
            "last_seen_at": health["last_seen_at"] if health else None,
            "is_online": bool(health and not health["is_offline"]),
            "offline_reason": health["offline_reason"] if health else None,
            "event_count": len(DEVICE_EVENTS.get(device_id, [])),
        })
    recent_pet = [
        {"kind": item.kind, "text": item.text, "tags": list(item.tags), "created_at": item.created_at}
        for item in EVENTS.get(pet.pet_id, [])[-5:]
    ]
    return {
        "pet_id": pet.pet_id,
        "server_time": server_time(),
        "primary_device_id": pet.device_id,
        "linked_device_ids": linked_ids,
        "total_devices": len(device_items),
        "device_items": device_items,
        "recent_pet_events": recent_pet,
        "recent_device_events": recent_device_events,
        "sync_notes": sync_notes,
    }


def pet_broadcast_summary(pet_id: str):
    pet = PETS[pet_id]
    linked_ids = pet_linked_device_ids(pet)
    device_items = []
    broadcast_items = []
    sync_notes = []
    for idx, device_id in enumerate(linked_ids):
        device = DEVICES.get(device_id)
        health = device_health_snapshot(device) if device is not None else None
        if health is None:
            sync_notes.append(f"device {device_id} missing")
        elif health["is_offline"]:
            sync_notes.append(f"device {device_id} offline")
        device_items.append({
            "device_id": device_id,
            "is_primary": idx == 0,
            "connection_state": health["connection_state"] if health else None,
            "last_seen_at": health["last_seen_at"] if health else None,
            "is_online": bool(health and not health["is_offline"]),
            "offline_reason": health["offline_reason"] if health else None,
            "event_count": len(DEVICE_EVENTS.get(device_id, [])),
        })
        for item in DEVICE_EVENTS.get(device_id, [])[-3:]:
            broadcast_items.append({
                "device_id": device_id,
                "kind": item.kind,
                "message": item.message,
                "created_at": item.created_at,
                "meta": dict(item.meta),
            })
    return {
        "pet_id": pet.pet_id,
        "server_time": server_time(),
        "total_devices": len(device_items),
        "primary_device_id": pet.device_id,
        "linked_device_ids": linked_ids,
        "broadcast_items": broadcast_items[-15:],
        "device_items": device_items,
        "sync_notes": sync_notes,
    }


def build_device_sync_summary(device_id: str):
    device = DEVICES.get(device_id)
    pet = next((p for p in PETS.values() if p.device_id == device_id), None)
    return {
        "device_id": device_id,
        "server_time": server_time(),
        "pet_id": pet.pet_id if pet else None,
        "primary_device_id": pet.device_id if pet else None,
        "linked_device_ids": pet_linked_device_ids(pet) if pet else [],
        "device_state": dict(device.state) if device else {},
        "recent_events": [
            {"kind": item.kind, "message": item.message, "created_at": item.created_at, "meta": dict(item.meta)}
            for item in DEVICE_EVENTS.get(device_id, [])[-5:]
        ],
        "pet_summary": build_pet_sync_summary(pet) if pet else None,
    }
def register_and_bind(device_id: str, owner_id: str, hardware_model: str, capabilities: list[str]) -> str:
    rec = DeviceRecord(
        device_id=device_id,
        hardware_model=hardware_model,
        firmware_version="0.1.0",
        capabilities=list(capabilities),
    )
    DEVICES[device_id] = rec
    rec.bind_code = new_bind_code()
    rec.bind_expires_at = 600.0
    rec.bound = True
    rec.owner_id = owner_id
    rec.bind_code = None
    rec.bind_expires_at = None

    pet_id = f"pet-{device_id}"
    pet = PetRecord(pet_id=pet_id, owner_id=owner_id, device_id=device_id)
    PETS[pet_id] = pet
    return pet_id


def main_entry() -> None:
    reset_state()
    print("== nuonuo-pet broadcast sync self-test ==")

    pet_id = register_and_bind(
        device_id="demo-device-001",
        owner_id="owner-demo",
        hardware_model="esp32-s3-lcd-1.85",
        capabilities=["lcd", "touch", "wifi", "speaker"],
    )
    pet = PETS[pet_id]
    device = DEVICES[pet.device_id]
    print("[1] bound snapshot")
    pprint(asdict(device))
    pprint(asdict(pet))

    device.connection_state = "offline"
    device.offline_reason = "heartbeat expired"
    sync_pets_with_device(device, "offline", {"source": "selftest", "step": "offline"})
    offline_sync = build_pet_sync_summary(pet)
    broadcast_after_offline = pet_broadcast_summary(pet_id)
    print("[2] offline sync summary")
    pprint(offline_sync)
    print("[3] offline broadcast summary")
    pprint(broadcast_after_offline)

    device.connection_state = "online"
    device.offline_reason = None
    device.last_seen_at = server_time()
    sync_pets_with_device(device, "resume", {"source": "selftest", "step": "resume"})
    online_sync = build_pet_sync_summary(pet)
    broadcast_after_resume = pet_broadcast_summary(pet_id)
    device_sync = build_device_sync_summary(device.device_id)
    print("[4] resume sync summary")
    pprint(online_sync)
    print("[5] resume broadcast summary")
    pprint(broadcast_after_resume)
    print("[6] device sync summary")
    pprint(device_sync)

    assert broadcast_after_offline["broadcast_items"], "expected broadcast items after offline"
    assert broadcast_after_resume["broadcast_items"], "expected broadcast items after resume"
    assert any("broadcast" in item.kind or "sync" in item.kind for item in DEVICE_EVENTS.get(device.device_id, [])), "expected device event trace"
    assert any(event.kind in {"device-offline", "device-reconnect"} for event in EVENTS.get(pet_id, [])), "expected pet event trace"

    print("OK: broadcast sync completed")


if __name__ == "__main__":
    main_entry()
