#!/usr/bin/env python3
"""nuonuo-pet 绑定流程自检。

这个脚本不依赖 FastAPI，可在轻量环境下直接验证：
1. 设备注册
2. 申请绑定码
3. 确认绑定
4. 自动生成宠物
5. 上报设备状态
"""
from __future__ import annotations

from dataclasses import asdict
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
PETS = storage.PETS
MEMORY = storage.MEMORY
EVENTS = storage.EVENTS
DeviceRecord = storage.DeviceRecord
PetRecord = storage.PetRecord
new_bind_code = storage.new_bind_code
now_iso = storage.now_iso


def reset_state() -> None:
    DEVICES.clear()
    PETS.clear()
    MEMORY.clear()
    EVENTS.clear()


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
    rec.bind_expires_at = 10 * 60.0
    return rec


def confirm_binding(device_id: str, bind_code: str, owner_id: str) -> tuple[DeviceRecord, str]:
    rec = DEVICES[device_id]
    if rec.bind_code != bind_code:
        raise ValueError("invalid bind code")
    rec.bound = True
    rec.owner_id = owner_id
    rec.bind_code = None
    rec.bind_expires_at = None

    pet_id = f"pet-{device_id}"
    pet = PETS.get(pet_id)
    if pet is None:
        pet = PetRecord(pet_id=pet_id, owner_id=owner_id, device_id=device_id)
        PETS[pet_id] = pet
    return rec, pet_id


def push_device_state(device_id: str, state: dict) -> dict:
    rec = DEVICES[device_id]
    rec.state = dict(state)
    return {
        "ok": True,
        "device_id": device_id,
        "server_time": now_iso(),
        "binding_state": "bound" if rec.bound else "unbound",
    }


def main() -> None:
    reset_state()
    print("== nuonuo-pet binding flow self-test ==")

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
    pprint({"device_id": dev.device_id, "bind_code": dev.bind_code, "expires_in_seconds": 600})

    rec, pet_id = confirm_binding(device_id, dev.bind_code or "", owner_id)
    print("[3] confirm binding")
    pprint({"device_id": rec.device_id, "bound": rec.bound, "owner_id": rec.owner_id, "pet_id": pet_id})

    state = push_device_state(device_id, {"screen": "ready", "mood": "curious", "energy": 96})
    print("[4] push state")
    pprint(state)

    print("[5] pet snapshot")
    pprint(asdict(PETS[pet_id]))

    print("OK: binding flow completed")


if __name__ == "__main__":
    main()
