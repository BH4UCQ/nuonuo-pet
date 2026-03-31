#!/usr/bin/env python3
"""nuonuo-pet 同步冲突 / 推荐动作自检。

说明：
- 不依赖 FastAPI。
- 直接复刻同步摘要逻辑，验证冲突事件与推荐动作。
"""
from __future__ import annotations

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


storage = load_module("nuonuo_storage_sync_conflict", STORAGE_PATH)

DEVICES = storage.DEVICES
DEVICE_EVENTS = storage.DEVICE_EVENTS
PETS = storage.PETS
MEMORY = storage.MEMORY
EVENTS = storage.EVENTS
DeviceRecord = storage.DeviceRecord
PetRecord = storage.PetRecord
DeviceEventRecord = storage.DeviceEventRecord
EventRecord = storage.EventRecord


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


def record_device_conflict(device_id: str, pet_ids: list[str], note: str) -> None:
    created_at = server_time()
    payload = {
        "device_id": device_id,
        "pet_ids": list(pet_ids),
        "note": note,
        "conflict": True,
    }
    DEVICE_EVENTS.setdefault(device_id, []).append(
        DeviceEventRecord(device_id=device_id, kind="sync-conflict", message=note, created_at=created_at, meta=payload)
    )
    for pet_id in pet_ids:
        EVENTS.setdefault(pet_id, []).append(
            EventRecord(kind="sync-conflict", text=note, tags=["system", "sync", "conflict", "category:system"], created_at=created_at)
        )


def pet_device_recent_events(device_id: str, limit: int = 5) -> list[dict[str, object]]:
    items = DEVICE_EVENTS.get(device_id, [])[-max(1, min(limit, 20)) :]
    return [
        {"kind": item.kind, "message": item.message, "created_at": item.created_at, "meta": dict(item.meta)}
        for item in items
    ]


def pet_recent_events(pet_id: str, limit: int = 5) -> list[dict[str, object]]:
    items = EVENTS.get(pet_id, [])[-max(1, min(limit, 20)) :]
    return [
        {"kind": item.kind, "text": item.text, "tags": list(item.tags), "created_at": item.created_at}
        for item in items
    ]


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
    occupancy_state = "conflicted" if conflict_device_ids else "claimed" if linked_ids else "free"
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=primary_device_online,
        total_devices=len(device_items),
    )
    occupancy_state = "conflicted" if conflict_device_ids else "claimed" if linked_ids else "free"
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=primary_device_online,
        total_devices=len(device_items),
    )
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
        "recommended_action": recommended_action,
        "health_level": health_level,
        "summary_line": summary_line_for_sync(len(device_items), online_devices, offline_devices, missing_devices, len(conflict_device_ids)),
        "primary_hint": primary_hint_for_sync(pet.device_id, primary_device_online, primary_device_present, occupancy_state),
        "action_hint": action_hint_for_sync(recommended_action, pet.device_id),
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
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=[device_id] if len(linked_pet_ids) > 1 else [],
        offline_devices=1 if device.connection_state == "offline" else 0,
        missing_devices=0,
        primary_device_online=bool(pet and pet.device_id == device_id and device.connection_state != "offline"),
        total_devices=len(linked_pet_ids),
    )
    linked_device_ids = pet_linked_device_ids(pet) if pet else []
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=[device_id] if len(linked_pet_ids) > 1 else [],
        offline_devices=1 if device.connection_state == "offline" else 0,
        missing_devices=0,
        primary_device_online=bool(pet and pet.device_id == device_id and device.connection_state != "offline"),
        total_devices=len(linked_pet_ids),
    )
    return {
        "device_id": device_id,
        "server_time": server_time(),
        "pet_id": pet.pet_id if pet else None,
        "primary_device_id": pet.device_id if pet else None,
        "linked_device_ids": linked_device_ids,
        "linked_pet_ids": linked_pet_ids,
        "occupancy_state": occupancy_state,
        "conflict_notes": conflict_notes,
        "recommended_action": recommended_action,
        "health_level": health_level,
        "summary_line": summary_line_for_sync(len(linked_device_ids), 1 if device.connection_state != "offline" else 0, 1 if device.connection_state == "offline" else 0, 0, len(conflict_notes)),
        "primary_hint": primary_hint_for_sync(pet.device_id if pet else None, bool(pet and pet.device_id == device_id and device.connection_state != "offline"), bool(pet), occupancy_state),
        "action_hint": action_hint_for_sync(recommended_action, pet.device_id if pet else None),
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
    occupancy_state = "conflicted" if conflict_device_ids else "claimed" if linked_ids else "free"
    recommended_action = recommended_action_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=bool(device_items and device_items[0]["is_online"]),
        total_devices=len(device_items),
    )
    health_level = health_level_for_sync(
        occupancy_state=occupancy_state,
        conflict_device_ids=conflict_device_ids,
        offline_devices=offline_devices,
        missing_devices=missing_devices,
        primary_device_online=bool(device_items and device_items[0]["is_online"]),
        total_devices=len(device_items),
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
        "recommended_action": recommended_action,
        "health_level": health_level,
        "summary_line": summary_line_for_sync(len(device_items), online_devices, offline_devices, missing_devices, len(conflict_device_ids)),
        "primary_hint": primary_hint_for_sync(pet.device_id, bool(device_items and device_items[0]["is_online"]), bool(linked_ids), occupancy_state),
        "action_hint": action_hint_for_sync(recommended_action, pet.device_id),
        "broadcast_items": broadcast_items[-15:],
        "device_items": device_items,
        "sync_notes": sync_notes,
    }


def main() -> None:
    reset_state()
    print("== nuonuo-pet sync conflict / action self-test ==")

    DEVICES["dev-a"] = DeviceRecord(
        device_id="dev-a",
        hardware_model="esp32-s3-lcd-1.85",
        firmware_version="0.1.0",
        capabilities=["lcd", "wifi"],
        bound=True,
        owner_id="owner-demo",
        connection_state="online",
        last_seen_at=server_time(),
    )
    DEVICES["dev-b"] = DeviceRecord(
        device_id="dev-b",
        hardware_model="esp32-s3-lcd-1.85",
        firmware_version="0.1.0",
        capabilities=["lcd", "wifi"],
        bound=True,
        owner_id="owner-demo",
        connection_state="offline",
        last_seen_at=server_time(),
        offline_reason="manual_offline",
    )

    pet_a = PetRecord(pet_id="pet-a", owner_id="owner-a", device_id="dev-a")
    pet_a.linked_device_ids = ["dev-a", "dev-b"]
    PETS[pet_a.pet_id] = pet_a

    pet_b = PetRecord(pet_id="pet-b", owner_id="owner-b", device_id="dev-a")
    pet_b.linked_device_ids = ["dev-a"]
    PETS[pet_b.pet_id] = pet_b

    record_device_conflict("dev-a", ["pet-a", "pet-b"], "device dev-a already linked to another pet")

    sync_a = build_pet_sync_summary(pet_a)
    device_sync = build_device_sync_summary("dev-a")
    broadcast_a = pet_broadcast_summary(pet_a)

    print("[1] pet-a sync")
    pprint(sync_a)
    print("[2] device sync")
    pprint(device_sync)
    print("[3] broadcast")
    pprint(broadcast_a)

    assert sync_a["recommended_action"] == "resolve_device_conflict"
    assert sync_a["health_level"] == "critical"
    assert sync_a["summary_line"] is not None
    assert sync_a["primary_hint"] is not None
    assert sync_a["action_hint"] is not None
    assert device_sync["recommended_action"] == "resolve_device_conflict"
    assert device_sync["health_level"] == "critical"
    assert device_sync["summary_line"] is not None
    assert device_sync["primary_hint"] is not None
    assert device_sync["action_hint"] is not None
    assert broadcast_a["recommended_action"] == "resolve_device_conflict"
    assert broadcast_a["health_level"] == "critical"
    assert broadcast_a["summary_line"] is not None
    assert broadcast_a["primary_hint"] is not None
    assert broadcast_a["action_hint"] is not None
    assert any(item.kind == "sync-conflict" for item in DEVICE_EVENTS["dev-a"]), "missing device conflict event"
    assert any(item.kind == "sync-conflict" for item in EVENTS["pet-a"]), "missing pet-a conflict event"
    assert any(item.kind == "sync-conflict" for item in EVENTS["pet-b"]), "missing pet-b conflict event"

    print("OK: conflict action and event trail completed")


if __name__ == "__main__":
    main()
