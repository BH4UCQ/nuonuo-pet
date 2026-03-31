#!/usr/bin/env python3
"""nuonuo-pet 设备占用冲突自检。

验证内容：
- 同一设备被两只宠物占用时，sync / broadcast / device summary 会给出冲突提示。
- 这个脚本不依赖 FastAPI，仅使用 storage 数据结构。
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


storage = load_module("nuonuo_storage_conflict", STORAGE_PATH)

DEVICES = storage.DEVICES
DEVICE_EVENTS = storage.DEVICE_EVENTS
PETS = storage.PETS
MEMORY = storage.MEMORY
EVENTS = storage.EVENTS
DeviceRecord = storage.DeviceRecord
PetRecord = storage.PetRecord


def reset_state() -> None:
    DEVICES.clear()
    DEVICE_EVENTS.clear()
    PETS.clear()
    MEMORY.clear()
    EVENTS.clear()


def server_time() -> str:
    return storage.now_iso()


def device_health_snapshot(rec: DeviceRecord) -> dict:
    offline = rec.connection_state == "offline"
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


def pets_claiming_device(device_id: str) -> list[PetRecord]:
    return [pet for pet in PETS.values() if pet.device_id == device_id or device_id in list(getattr(pet, "linked_device_ids", []) or [])]


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


def build_pet_sync_summary(pet: PetRecord) -> dict:
    linked_ids = pet_linked_device_ids(pet)
    device_items: list[dict[str, object]] = []
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
            {
                "device_id": device_id,
                "is_primary": is_primary,
                "connection_state": health["connection_state"] if health else None,
                "last_seen_at": health["last_seen_at"] if health else None,
                "is_online": bool(health and not health["is_offline"]),
                "offline_reason": health["offline_reason"] if health else None,
                "event_count": len(DEVICE_EVENTS.get(device_id, [])),
            }
        )

    recent_pet = pet_recent_events(pet.pet_id)
    if pet.device_id and pet.device_id not in linked_ids:
        sync_notes.append(f"primary device {pet.device_id} is not linked")

    return {
        "pet_id": pet.pet_id,
        "server_time": server_time(),
        "primary_device_id": pet.device_id,
        "linked_device_ids": linked_ids,
        "total_devices": len(device_items),
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "missing_devices": missing_devices,
        "conflict_device_ids": conflict_device_ids,
        "conflict_notes": conflict_notes,
        "primary_device_present": primary_device_present,
        "primary_device_online": primary_device_online,
        "device_items": device_items,
        "recent_pet_events": recent_pet,
        "recent_device_events": recent_device_events,
        "sync_notes": sync_notes,
    }


def build_device_sync_summary(device_id: str) -> dict:
    device = DEVICES.get(device_id)
    if device is None:
        raise RuntimeError("device not found")
    pets = pets_claiming_device(device_id)
    pet = next((item for item in pets if item.device_id == device_id), None)
    summary = build_pet_sync_summary(pet) if pet is not None else None
    linked_pet_ids = [item.pet_id for item in pets]
    conflict_notes = []
    if len(linked_pet_ids) > 1:
        conflict_notes.append(f"device {device_id} claimed by {', '.join(sorted(linked_pet_ids))}")
    occupancy_state = "free"
    if linked_pet_ids:
        occupancy_state = "conflicted" if len(linked_pet_ids) > 1 else "claimed"
    return {
        "device_id": device_id,
        "server_time": server_time(),
        "pet_id": pet.pet_id if pet else None,
        "primary_device_id": pet.device_id if pet else None,
        "linked_device_ids": pet_linked_device_ids(pet) if pet else [],
        "linked_pet_ids": linked_pet_ids,
        "occupancy_state": occupancy_state,
        "conflict_notes": conflict_notes,
        "device_state": dict(device.state),
        "recent_events": pet_device_recent_events(device_id),
        "pet_summary": summary,
    }


def pet_broadcast_summary(pet: PetRecord) -> dict:
    linked_ids = pet_linked_device_ids(pet)
    device_items: list[dict[str, object]] = []
    broadcast_items: list[dict[str, object]] = []
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
            {
                "device_id": device_id,
                "is_primary": idx == 0,
                "connection_state": health["connection_state"] if health else None,
                "last_seen_at": health["last_seen_at"] if health else None,
                "is_online": bool(health and not health["is_offline"]),
                "offline_reason": health["offline_reason"] if health else None,
                "event_count": len(DEVICE_EVENTS.get(device_id, [])),
            }
        )
        for item in pet_device_recent_events(device_id, limit=3):
            broadcast_items.append(
                {
                    "device_id": device_id,
                    "kind": item["kind"],
                    "message": item["message"],
                    "created_at": item["created_at"],
                    "meta": dict(item["meta"]),
                }
            )

    return {
        "pet_id": pet.pet_id,
        "server_time": server_time(),
        "total_devices": len(device_items),
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "missing_devices": missing_devices,
        "conflict_device_ids": conflict_device_ids,
        "conflict_notes": conflict_notes,
        "primary_device_id": pet.device_id,
        "linked_device_ids": linked_ids,
        "broadcast_items": broadcast_items[-15:],
        "device_items": device_items,
        "sync_notes": sync_notes,
    }


def main() -> None:
    reset_state()
    print("== nuonuo-pet device conflict self-test ==")

    device_id = "demo-device-001"
    device = DeviceRecord(
        device_id=device_id,
        hardware_model="esp32-s3-lcd-1.85",
        firmware_version="0.1.0",
        capabilities=["lcd", "wifi"],
        bound=True,
        owner_id="owner-demo",
        connection_state="online",
        last_seen_at=server_time(),
    )
    DEVICES[device_id] = device

    pet_a = PetRecord(pet_id="pet-a", owner_id="owner-a", device_id=device_id)
    pet_a.linked_device_ids = [device_id]
    PETS[pet_a.pet_id] = pet_a

    pet_b = PetRecord(pet_id="pet-b", owner_id="owner-b", device_id=device_id)
    pet_b.linked_device_ids = [device_id]
    PETS[pet_b.pet_id] = pet_b

    sync_a = build_pet_sync_summary(pet_a)
    sync_b = build_pet_sync_summary(pet_b)
    device_sync = build_device_sync_summary(device_id)
    broadcast_a = pet_broadcast_summary(pet_a)

    print("[1] pet-a sync")
    pprint(sync_a)
    print("[2] pet-b sync")
    pprint(sync_b)
    print("[3] device sync")
    pprint(device_sync)
    print("[4] broadcast")
    pprint(broadcast_a)

    assert sync_a["conflict_device_ids"], "expected conflict devices in pet-a sync"
    assert sync_b["conflict_device_ids"], "expected conflict devices in pet-b sync"
    assert device_sync["occupancy_state"] == "conflicted", "expected conflicted occupancy"
    assert device_sync["conflict_notes"], "expected conflict notes on device sync"
    assert broadcast_a["conflict_device_ids"], "expected conflict devices in broadcast summary"

    print("OK: device conflict detected")


if __name__ == "__main__":
    main()
