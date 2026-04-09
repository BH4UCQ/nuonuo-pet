from __future__ import annotations
from typing import List, Callable

from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from .models import (
    DeviceEventRequest,
    DeviceHeartbeatRequest,
    PetDeviceLinkRequest,
    PetDevicePrimaryRequest,
    PetDeviceUnlinkRequest,
    PetEventRequest,
    PetUpdateRequest,
)
from .storage import DEVICE_EVENTS, DEVICES, PETS, DeviceEventRecord
from .ui_helpers import redirect_with_message


RedirectFn = Callable[..., RedirectResponse]
ServerTimeFn = Callable[..., object]
SaveStateFn = Callable[..., object]
DeviceHeartbeatFn = Callable[..., object]
DeviceEventFn = Callable[..., object]
PetsClaimingDeviceFn = Callable[..., object]
LinkPetDeviceFn = Callable[..., object]
UnlinkPetDeviceFn = Callable[..., object]
PetLinkedDeviceIdsFn = Callable[..., object]
SetPetPrimaryDeviceFn = Callable[..., object]
PetUpdateFn = Callable[..., object]
PetEventFn = Callable[..., object]


def handle_bulk_device_op(
    *,
    ids: List[str],
    operation: str,
    message: str,
    owner_id: str,
    pet_id: str,
    server_time: ServerTimeFn,
    save_state: SaveStateFn,
    device_heartbeat: DeviceHeartbeatFn,
    device_event: DeviceEventFn,
    pets_claiming_device: PetsClaimingDeviceFn,
    link_pet_device: LinkPetDeviceFn,
    unlink_pet_device: UnlinkPetDeviceFn,
    redirect: RedirectFn = redirect_with_message,
) -> RedirectResponse:
    if not ids:
        return redirect("/ui/devices", "未提供有效 device_id", "warn")

    owner_value = owner_id.strip() or None
    pet_value = pet_id.strip() or None
    ok_count = 0
    missing: List[str] = []
    failed: List[str] = []
    for device_id in ids:
        rec = DEVICES.get(device_id)
        if rec is None:
            missing.append(device_id)
            continue
        try:
            if operation == "heartbeat":
                device_heartbeat(DeviceHeartbeatRequest(device_id=device_id, note=message))
            elif operation == "resume-event":
                device_event(device_id, DeviceEventRequest(kind="resume", message=message, meta={"source": "ui-bulk"}))
            elif operation == "offline-event":
                device_event(device_id, DeviceEventRequest(kind="offline", message=message, meta={"source": "ui-bulk"}))
            elif operation == "attention-event":
                device_event(device_id, DeviceEventRequest(kind="attention", message=message, meta={"source": "ui-bulk"}))
            elif operation == "assign-owner":
                if not owner_value:
                    return redirect("/ui/devices", "assign-owner 需要提供 owner_id", "warn")
                rec.owner_id = owner_value
                if not rec.bound:
                    rec.bound = True
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="owner-assign",
                        message=message or f"bulk owner assigned to {owner_value}",
                        created_at=server_time(),
                        meta={"source": "ui-bulk", "owner_id": owner_value},
                    )
                )
            elif operation == "clear-owner":
                rec.owner_id = None
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="owner-clear",
                        message=message or "bulk owner cleared",
                        created_at=server_time(),
                        meta={"source": "ui-bulk"},
                    )
                )
            elif operation == "mark-bound":
                rec.bound = True
                if owner_value:
                    rec.owner_id = owner_value
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="binding-marked",
                        message=message or "bulk device marked bound",
                        created_at=server_time(),
                        meta={"source": "ui-bulk", "bound": True, "owner_id": rec.owner_id},
                    )
                )
            elif operation == "mark-unbound":
                rec.bound = False
                rec.bind_code = None
                rec.bind_expires_at = None
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="binding-marked",
                        message=message or "bulk device marked unbound",
                        created_at=server_time(),
                        meta={"source": "ui-bulk", "bound": False},
                    )
                )
            elif operation == "attach-primary-pet":
                if not pet_value:
                    return redirect("/ui/devices", "attach-primary-pet 需要提供 pet_id", "warn")
                if pet_value not in PETS:
                    failed.append(device_id)
                    continue
                link_pet_device(pet_value, PetDeviceLinkRequest(device_id=device_id, make_primary=True))
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="pet-attach",
                        message=message or f"bulk attached to pet {pet_value} as primary",
                        created_at=server_time(),
                        meta={"source": "ui-bulk", "pet_id": pet_value, "primary": True},
                    )
                )
            elif operation == "unlink-all-pets":
                owners = pets_claiming_device(device_id)
                if not owners:
                    failed.append(device_id)
                    continue
                for pet in owners:
                    unlink_pet_device(pet.pet_id, PetDeviceUnlinkRequest(device_id=device_id, remove_primary=True))
                DEVICE_EVENTS.setdefault(device_id, []).append(
                    DeviceEventRecord(
                        device_id=device_id,
                        kind="pet-detach",
                        message=message or "bulk detached from all pets",
                        created_at=server_time(),
                        meta={"source": "ui-bulk", "pet_ids": [pet.pet_id for pet in owners]},
                    )
                )
            else:
                return redirect("/ui/devices", f"不支持的设备批量操作：{operation}", "warn")
        except HTTPException:
            failed.append(device_id)
            continue
        ok_count += 1

    save_state()
    detail = f"批量设备操作完成：success={ok_count}, op={operation}"
    if missing:
        detail += f" / missing={','.join(missing)}"
    if failed:
        detail += f" / failed={','.join(failed)}"
    return redirect("/ui/devices", detail, "warn" if (missing or failed) else "ok")


def handle_bulk_pet_op(
    *,
    ids: List[str],
    event_kind: str,
    event_text: str,
    device_id: str,
    owner_id: str,
    save_state: SaveStateFn,
    link_pet_device: LinkPetDeviceFn,
    unlink_pet_device: UnlinkPetDeviceFn,
    pet_linked_device_ids: PetLinkedDeviceIdsFn,
    set_pet_primary_device: SetPetPrimaryDeviceFn,
    pet_update: PetUpdateFn,
    pet_event: PetEventFn,
    redirect: RedirectFn = redirect_with_message,
) -> RedirectResponse:
    if not ids:
        return redirect("/ui/pets", "未提供有效 pet_id", "warn")

    device_value = device_id.strip()
    owner_value = owner_id.strip() or None
    ok_count = 0
    missing: List[str] = []
    failed: List[str] = []
    for pet_id in ids:
        if pet_id not in PETS:
            missing.append(pet_id)
            continue
        try:
            if event_kind == "link-device":
                if not device_value:
                    return redirect("/ui/pets", "link-device 需要提供 device_id", "warn")
                link_pet_device(pet_id, PetDeviceLinkRequest(device_id=device_value, make_primary=False))
            elif event_kind == "link-device-primary":
                if not device_value:
                    return redirect("/ui/pets", "link-device-primary 需要提供 device_id", "warn")
                link_pet_device(pet_id, PetDeviceLinkRequest(device_id=device_value, make_primary=True))
            elif event_kind == "unlink-device":
                if not device_value:
                    return redirect("/ui/pets", "unlink-device 需要提供 device_id", "warn")
                unlink_pet_device(pet_id, PetDeviceUnlinkRequest(device_id=device_value, remove_primary=True))
            elif event_kind == "unlink-all-devices":
                pet = PETS[pet_id]
                linked_ids = list(pet_linked_device_ids(pet))
                if not linked_ids:
                    failed.append(pet_id)
                    continue
                for linked_id in linked_ids:
                    unlink_pet_device(pet_id, PetDeviceUnlinkRequest(device_id=linked_id, remove_primary=True))
            elif event_kind == "set-primary-device":
                if not device_value:
                    return redirect("/ui/pets", "set-primary-device 需要提供 device_id", "warn")
                set_pet_primary_device(pet_id, PetDevicePrimaryRequest(device_id=device_value))
            elif event_kind == "assign-owner":
                if not owner_value:
                    return redirect("/ui/pets", "assign-owner 需要提供 owner_id", "warn")
                pet_update(pet_id, PetUpdateRequest(owner_id=owner_value))
            elif event_kind == "clear-owner":
                pet = PETS[pet_id]
                pet.owner_id = None
            else:
                pet_event(pet_id, PetEventRequest(pet_id=pet_id, kind=event_kind, text=event_text, tags=["ui", "bulk"]))
        except HTTPException:
            failed.append(pet_id)
            continue
        ok_count += 1

    save_state()
    detail = f"批量宠物操作完成：success={ok_count}, op={event_kind}"
    if missing:
        detail += f" / missing={','.join(missing)}"
    if failed:
        detail += f" / failed={','.join(failed)}"
    return redirect("/ui/pets", detail, "warn" if (missing or failed) else "ok")
