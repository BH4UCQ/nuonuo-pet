from __future__ import annotations
from typing import Optional, List, Dict, Tuple

from html import escape
import json

from .storage import ASSET_MANIFEST, DEVICE_EVENTS, DEVICES, EVENTS, MODEL_ROUTES, PETS, SPECIES_TEMPLATES, THEME_PACKS


def build_devices_page_context(
    *,
    connection_state: str,
    bound: str,
    keyword: Optional[str],
    problem: str,
    capability: str,
    owner_scope: str,
    sort_by: str,
    device_health_snapshot,
    build_device_sync_summary,
    pet_device_owner,
    render_device_management_row,
    status_badge,
    device_record_type,
) -> Dict[str, object]:
    rows: List[str] = []
    matched = 0
    online_count = 0
    offline_count = 0
    bound_count = 0
    unbound_count = 0
    conflict_count = 0
    action_needed_count = 0
    keyword_value = (keyword or "").strip().lower()
    device_entries: List[Dict[str, object]] = []
    capability_options = sorted({cap for rec in DEVICES.values() for cap in rec.capabilities})

    for device_id in sorted(DEVICES.keys()):
        rec = DEVICES[device_id]
        health = device_health_snapshot(rec)
        summary = build_device_sync_summary(device_id)
        owner_pet = pet_device_owner(device_id)
        is_bound = rec.bound
        state_value = str(health.get("connection_state") or rec.connection_state or "unknown")
        quick_owner = owner_pet.pet_id if owner_pet else ""
        has_problem = bool(
            summary.occupancy_state == "conflicted"
            or health.get("is_offline")
            or summary.recommended_action != "normal"
            or (problem == "unbound" and not is_bound)
        )

        haystack = " ".join(
            [
                device_id,
                rec.hardware_model,
                rec.firmware_version,
                rec.owner_id or "",
                owner_pet.pet_id if owner_pet else "",
                " ".join(rec.capabilities),
                summary.summary_line,
                summary.action_hint,
                summary.recommended_action,
                json.dumps(rec.state or {}, ensure_ascii=False),
            ]
        ).lower()
        if keyword_value and keyword_value not in haystack:
            continue
        if connection_state != "all" and state_value != connection_state:
            continue
        if bound == "bound" and not is_bound:
            continue
        if bound == "unbound" and is_bound:
            continue
        if capability != "all" and capability not in rec.capabilities:
            continue
        if owner_scope == "with-owner" and not rec.owner_id:
            continue
        if owner_scope == "without-owner" and rec.owner_id:
            continue
        if owner_scope == "with-pet" and not quick_owner:
            continue
        if owner_scope == "without-pet" and quick_owner:
            continue
        if problem == "problem" and not has_problem:
            continue
        if problem == "conflict" and summary.occupancy_state != "conflicted":
            continue
        if problem == "offline" and not health.get("is_offline"):
            continue
        if problem == "unbound" and is_bound:
            continue
        if problem == "action-needed" and summary.recommended_action == "normal":
            continue

        device_entries.append(
            {
                "device_id": device_id,
                "rec": rec,
                "summary": summary,
                "owner_pet": owner_pet,
                "state_value": state_value,
                "is_bound": is_bound,
            }
        )

    def _device_sort_key(item: Dict[str, object]) -> Tuple[object, ...]:
        rec = item["rec"]
        summary = item["summary"]
        state_value = str(item["state_value"])
        owner_pet = item["owner_pet"]
        rec_obj = rec if isinstance(rec, device_record_type) else None
        priority_state = 0 if state_value == "online" else 1
        priority_action = 0 if getattr(summary, "recommended_action", "normal") != "normal" else 1
        if sort_by == "state":
            return (priority_state, str(item["device_id"]))
        if sort_by == "action":
            return (priority_action, str(getattr(summary, "recommended_action", "")), str(item["device_id"]))
        if sort_by == "owner":
            return (str(rec_obj.owner_id or "zzz") if rec_obj else "zzz", str(getattr(owner_pet, "pet_id", "zzz")), str(item["device_id"]))
        if sort_by == "hardware":
            return (str(rec_obj.hardware_model) if rec_obj else "", str(item["device_id"]))
        return (str(item["device_id"]),)

    for item in sorted(device_entries, key=_device_sort_key):
        device_id = str(item["device_id"])
        rec = item["rec"]
        summary = item["summary"]
        owner_pet = item["owner_pet"]
        is_bound = bool(item["is_bound"])
        state_value = str(item["state_value"])
        matched += 1
        if state_value == "online":
            online_count += 1
        else:
            offline_count += 1
        if is_bound:
            bound_count += 1
        else:
            unbound_count += 1
        if summary.occupancy_state == "conflicted":
            conflict_count += 1
        if summary.recommended_action != "normal":
            action_needed_count += 1

        rows.append(
            render_device_management_row(
                device_id=device_id,
                hardware_model=rec.hardware_model,
                firmware_version=rec.firmware_version,
                state_value=state_value,
                is_bound=is_bound,
                owner_id=rec.owner_id,
                pet_id=owner_pet.pet_id if owner_pet else None,
                capabilities_text=', '.join(rec.capabilities) if rec.capabilities else '-',
                summary_line=summary.summary_line or '-',
                recommended_action=summary.recommended_action,
                action_hint=summary.action_hint or 'manual+attention',
                status_badge=status_badge,
            )
        )

    capability_options_html = ''.join(
        f'<option value="{escape(item)}"{" selected" if capability == item else ""}>{escape(item)}</option>'
        for item in capability_options
    )
    return {
        'rows_html': ''.join(rows),
        'matched': matched,
        'online_count': online_count,
        'offline_count': offline_count,
        'bound_count': bound_count,
        'unbound_count': unbound_count,
        'conflict_count': conflict_count,
        'action_needed_count': action_needed_count,
        'capability_options_html': capability_options_html,
    }

def build_pets_page_context(
    *,
    species_id: str,
    mood: str,
    keyword: Optional[str],
    problem: str,
    growth_stage: str,
    device_scope: str,
    sort_by: str,
    build_pet_sync_summary,
    render_pet_management_row,
    status_badge,
) -> Dict[str, object]:
    rows: List[str] = []
    matched = 0
    healthy_count = 0
    warning_count = 0
    action_needed_count = 0
    species_options = sorted({item.get("id", "") for item in SPECIES_TEMPLATES if item.get("id")})
    growth_stage_options = sorted({pet.growth_stage for pet in PETS.values() if pet.growth_stage})
    keyword_value = (keyword or "").strip().lower()
    pet_entries: List[Dict[str, object]] = []

    for pet_id in sorted(PETS.keys()):
        pet = PETS[pet_id]
        sync = build_pet_sync_summary(pet)
        if species_id != "all" and pet.species_id != species_id:
            continue
        if mood != "all" and pet.mood != mood:
            continue
        if growth_stage != "all" and pet.growth_stage != growth_stage:
            continue
        if device_scope == "with-device" and sync.total_devices <= 0:
            continue
        if device_scope == "without-device" and sync.total_devices > 0:
            continue
        if device_scope == "offline-device" and sync.offline_devices <= 0:
            continue
        if device_scope == "multi-device" and sync.total_devices < 2:
            continue
        haystack = " ".join(
            [
                pet_id,
                pet.name,
                pet.species_id,
                pet.theme_id,
                pet.owner_id or "",
                pet.device_id or "",
                sync.summary_line,
                sync.action_hint,
                sync.recommended_action,
                ' '.join(pet.linked_device_ids),
                pet.growth_stage,
                pet.mood,
            ]
        ).lower()
        if keyword_value and keyword_value not in haystack:
            continue

        has_problem = bool(
            sync.health_level not in {"normal", "healthy", "ok"}
            or sync.recommended_action != "normal"
            or sync.conflict_device_ids
            or sync.offline_devices > 0
            or sync.missing_devices > 0
            or sync.total_devices == 0
        )
        if problem == "problem" and not has_problem:
            continue
        if problem == "conflict" and not sync.conflict_device_ids:
            continue
        if problem == "offline" and sync.offline_devices <= 0:
            continue
        if problem == "missing-device" and sync.missing_devices <= 0:
            continue
        if problem == "no-device" and sync.total_devices > 0:
            continue
        if problem == "action-needed" and sync.recommended_action == "normal":
            continue
        if problem == "hungry" and pet.hunger < 70:
            continue
        if problem == "low-energy" and pet.energy > 30:
            continue

        pet_entries.append({"pet_id": pet_id, "pet": pet, "sync": sync})

    def _pet_sort_key(item: Dict[str, object]) -> Tuple[object, ...]:
        pet = item["pet"]
        sync = item["sync"]
        if sort_by == "level":
            return (-int(pet.level), str(item["pet_id"]))
        if sort_by == "energy":
            return (int(pet.energy), str(item["pet_id"]))
        if sort_by == "hunger":
            return (-int(pet.hunger), str(item["pet_id"]))
        if sort_by == "mood":
            return (str(pet.mood), str(item["pet_id"]))
        if sort_by == "action":
            return (0 if sync.recommended_action != "normal" else 1, str(sync.recommended_action), str(item["pet_id"]))
        return (str(item["pet_id"]),)

    for item in sorted(pet_entries, key=_pet_sort_key):
        pet_id = str(item["pet_id"])
        pet = item["pet"]
        sync = item["sync"]
        matched += 1
        if sync.health_level in {"normal", "healthy", "ok"}:
            healthy_count += 1
        else:
            warning_count += 1
        if sync.recommended_action != "normal":
            action_needed_count += 1

        rows.append(
            render_pet_management_row(
                pet_id=pet_id,
                pet_name=pet.name,
                species_id=pet.species_id,
                theme_id=pet.theme_id,
                growth_stage=pet.growth_stage,
                mood=pet.mood,
                level_value=pet.level,
                energy=pet.energy,
                hunger=pet.hunger,
                affection=pet.affection,
                primary_device_id=pet.device_id,
                linked_devices_text=', '.join(pet.linked_device_ids) if pet.linked_device_ids else '-',
                summary_line=sync.summary_line or '-',
                recommended_action=sync.recommended_action,
                status_badge=status_badge,
            )
        )

    species_options_html = ''.join(
        f'<option value="{escape(item)}"{" selected" if species_id == item else ""}>{escape(item)}</option>'
        for item in species_options
    )
    growth_stage_options_html = ''.join(
        f'<option value="{escape(item)}"{" selected" if growth_stage == item else ""}>{escape(item)}</option>'
        for item in growth_stage_options
    )
    return {
        'rows_html': ''.join(rows),
        'matched': matched,
        'healthy_count': healthy_count,
        'warning_count': warning_count,
        'action_needed_count': action_needed_count,
        'species_options_html': species_options_html,
        'growth_stage_options_html': growth_stage_options_html,
    }

def build_device_detail_context(
    *,
    device_id: str,
    device_health_snapshot,
    build_device_sync_summary,
    build_device_display_profile,
    pet_device_owner,
    textarea_json,
) -> Dict[str, object]:
    rec = DEVICES.get(device_id)
    if rec is None:
        raise KeyError(device_id)

    health_info = device_health_snapshot(rec)
    summary = build_device_sync_summary(device_id)
    profile = build_device_display_profile(
        device_id=device_id,
        hardware_model=rec.hardware_model,
        firmware_version=rec.firmware_version,
        capabilities=list(rec.capabilities),
    )
    owner_pet = pet_device_owner(device_id)
    default_state_json = textarea_json(rec.state or {"battery": 85, "scene": "idle"})
    events_html = "".join(
        f'<div class="item"><div class="item-title"><strong>{escape(item.kind)}</strong><span class="mini">{escape(item.created_at)}</span></div><div>{escape(item.message)}</div></div>'
        for item in DEVICE_EVENTS.get(device_id, [])[-12:][::-1]
    ) or '<div class="muted">暂无设备事件</div>'

    return {
        "rec": rec,
        "owner_pet_id": owner_pet.pet_id if owner_pet else None,
        "basic_status_rows": [
            ("connection_state", health_info["connection_state"]),
            ("bound", rec.bound),
            ("last_seen_at", health_info["last_seen_at"]),
            ("offline_reason", health_info["offline_reason"]),
            ("owner_pet_id", owner_pet.pet_id if owner_pet else None),
            ("capabilities", rec.capabilities),
            ("state", rec.state),
        ],
        "sync_rows": [
            ("pet_id", summary.pet_id),
            ("occupancy_state", summary.occupancy_state),
            ("health_level", summary.health_level),
            ("summary_line", summary.summary_line),
            ("primary_hint", summary.primary_hint),
            ("action_hint", summary.action_hint),
            ("recent_events", summary.recent_events),
        ],
        "display_rows": [
            ("display_mode", profile.get("display_mode")),
            ("device_class", profile.get("device_class")),
            ("layout_name", profile.get("layout_name")),
            ("scene_hint", profile.get("scene_hint")),
            ("recommended_species_id", profile.get("recommended_species_id")),
            ("recommended_theme_id", profile.get("recommended_theme_id")),
            ("notes", profile.get("notes")),
        ],
        "state_json_text": textarea_json(rec.state),
        "default_state_json": default_state_json,
        "capabilities_csv": ",".join(rec.capabilities),
        "events_html": events_html,
    }

def build_pet_detail_context(
    *,
    pet_id: str,
    pet_or_404,
    build_pet_sync_summary,
    pet_growth_summary,
    build_preview,
    pet_linked_device_ids,
    options_html,
) -> Dict[str, object]:
    pet = pet_or_404(pet_id)
    sync = build_pet_sync_summary(pet)
    growth = pet_growth_summary(pet_id)
    preview = build_preview(pet.species_id, pet.theme_id, pet)
    linked_ids = pet_linked_device_ids(pet)

    device_manage_cards: List[str] = []
    for device_id in linked_ids:
        role_label = "主设备" if pet.device_id == device_id else "已关联设备"
        device_manage_cards.append(
            f'<div class="item"><div class="item-title"><strong><a href="/ui/device/{escape(device_id)}">{escape(device_id)}</a></strong><span class="mini">{role_label}</span></div><div class="actions"><form class="inline" method="post" action="/ui/action/set-primary-device"><input type="hidden" name="pet_id" value="{escape(pet_id)}"><input type="hidden" name="device_id" value="{escape(device_id)}"><button type="submit">设为主设备</button></form><form class="inline" method="post" action="/ui/action/unlink-device"><input type="hidden" name="pet_id" value="{escape(pet_id)}"><input type="hidden" name="device_id" value="{escape(device_id)}"><button type="submit">解绑</button></form></div></div>'
        )

    events_html = "".join(
        f'<div class="item"><div class="item-title"><strong>{escape(item.kind)}</strong><span class="mini">{escape(item.created_at)}</span></div><div>{escape(item.text)}</div></div>'
        for item in EVENTS.get(pet_id, [])[-12:][::-1]
    ) or '<div class="muted">暂无宠物事件</div>'

    return {
        "pet": pet,
        "basic_rows": [
            ("growth_stage", pet.growth_stage),
            ("energy", pet.energy),
            ("hunger", pet.hunger),
            ("affection", pet.affection),
            ("device_id", pet.device_id),
            ("linked_device_ids", linked_ids),
            ("owner_id", pet.owner_id),
        ],
        "sync_rows": [
            ("health_level", sync.health_level),
            ("summary_line", sync.summary_line),
            ("primary_hint", sync.primary_hint),
            ("action_hint", sync.action_hint),
            ("device_items", [item.model_dump() if hasattr(item, "model_dump") else item.__dict__ for item in sync.device_items]),
            ("sync_notes", sync.sync_notes),
        ],
        "growth_rows": [
            ("exp", growth.exp),
            ("next_level_exp", growth.next_level_exp),
            ("growth_curve", growth.growth_curve),
            ("growth_preferences", growth.growth_preferences),
            ("preference_notes", growth.preference_notes),
        ],
        "preview_rows": [
            ("display_mode", preview.get("display_mode")),
            ("layout_name", preview.get("layout_name")),
            ("scene_hint", preview.get("scene_hint")),
            ("palette", preview.get("palette")),
            ("ui_slots", preview.get("ui_slots")),
            ("notes", preview.get("notes")),
        ],
        "device_manage_html": "".join(device_manage_cards),
        "events_html": events_html,
        "device_options_html": options_html(sorted(DEVICES.keys()), None),
        "form_defaults": {
            "name": pet.name,
            "species_id": pet.species_id,
            "theme_id": pet.theme_id,
            "model_route_id": pet.model_route_id,
            "model_provider": pet.model_provider,
            "model_name": pet.model_name,
            "growth_stage": pet.growth_stage,
            "mood": pet.mood,
            "level": pet.level,
            "exp": pet.exp,
            "energy": pet.energy,
            "hunger": pet.hunger,
            "affection": pet.affection,
            "owner_id": pet.owner_id,
            "device_id": pet.device_id,
        },
    }

