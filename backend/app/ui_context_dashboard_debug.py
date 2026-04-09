from __future__ import annotations
from typing import Optional, List, Dict, Tuple

from html import escape
import json

from .storage import ASSET_MANIFEST, DEVICE_EVENTS, DEVICES, EVENTS, MODEL_ROUTES, PETS, SPECIES_TEMPLATES, THEME_PACKS


def build_dashboard_context(
    *,
    dashboard_snapshot,
    device_health_snapshot,
    build_device_sync_summary,
    build_pet_sync_summary,
    render_dashboard_device_card,
    render_dashboard_pet_card,
    render_recent_event_card,
    status_badge,
) -> Dict[str, object]:
    snapshot = dashboard_snapshot()
    device_cards: List[str] = []
    for device_id in sorted(DEVICES.keys()):
        rec = DEVICES[device_id]
        health_info = device_health_snapshot(rec)
        sync = build_device_sync_summary(device_id)
        device_cards.append(
            render_dashboard_device_card(
                device_id=device_id,
                hardware_model=rec.hardware_model,
                firmware_version=rec.firmware_version,
                owner_id=rec.owner_id,
                pet_id=sync.pet_id,
                connection_state=str(health_info.get("connection_state") or "unknown"),
                bound=rec.bound,
                summary_line=sync.summary_line,
                event_count=len(DEVICE_EVENTS.get(device_id, [])),
                status_badge=status_badge,
            )
        )

    pet_cards: List[str] = []
    for pet_id in sorted(PETS.keys()):
        pet = PETS[pet_id]
        sync = build_pet_sync_summary(pet)
        pet_cards.append(
            render_dashboard_pet_card(
                pet_id=pet_id,
                pet_name=pet.name,
                species_id=pet.species_id,
                theme_id=pet.theme_id,
                health_level=sync.health_level,
                mood=pet.mood,
                level=pet.level,
                energy=pet.energy,
                hunger=pet.hunger,
                affection=pet.affection,
                summary_line=sync.summary_line,
                status_badge=status_badge,
            )
        )

    recent_events: List[str] = []
    merged: List[Tuple[str, str, str, str]] = []
    for device_id, items in DEVICE_EVENTS.items():
        for item in items[-3:]:
            merged.append((item.created_at, f"device:{device_id}", item.kind, item.message))
    for pet_id, items in EVENTS.items():
        for item in items[-3:]:
            merged.append((item.created_at, f"pet:{pet_id}", item.kind, item.text))
    for created_at, source, kind, message in sorted(merged, key=lambda x: x[0], reverse=True)[:12]:
        recent_events.append(
            render_recent_event_card(created_at=created_at, source=source, kind=kind, message=message)
        )

    return {
        "snapshot": snapshot,
        "device_cards_html": "".join(device_cards),
        "pet_cards_html": "".join(pet_cards),
        "recent_events_html": "".join(recent_events),
    }

def build_system_context(
    *,
    dashboard_snapshot,
    build_pet_sync_summary,
    device_health_snapshot,
    build_device_sync_summary,
    merged_event_stream,
    status_badge,
) -> Dict[str, object]:
    snapshot = dashboard_snapshot()
    checks = [
        ("后端服务已启动", "ok", "FastAPI / UI 已可访问"),
        ("至少存在一台设备", "ok" if snapshot["device_count"] > 0 else "warn", f"当前设备数：{snapshot['device_count']}"),
        ("至少存在一只宠物", "ok" if snapshot["pet_count"] > 0 else "warn", f"当前宠物数：{snapshot['pet_count']}"),
        ("至少有一台设备在线", "ok" if snapshot["online_device_count"] > 0 else "warn", f"在线设备：{snapshot['online_device_count']} / {snapshot['device_count']}"),
        ("至少有一台设备已绑定", "ok" if snapshot["bound_device_count"] > 0 else "warn", f"已绑定设备：{snapshot['bound_device_count']}"),
    ]

    pet_cards: List[str] = []
    healthy_pets = 0
    warning_pets = 0
    for pet_id in sorted(PETS.keys()):
        pet = PETS[pet_id]
        sync = build_pet_sync_summary(pet)
        if sync.health_level in {"normal", "ok", "healthy"}:
            healthy_pets += 1
        elif sync.health_level in {"warning", "degraded", "critical", "idle"}:
            warning_pets += 1
        pet_cards.append(
            f"""
            <div class=\"item\"> 
              <div class=\"item-title\"> 
                <div><strong><a href=\"/ui/pet/{escape(pet_id)}\">{escape(pet.name)}</a></strong> <span class=\"mini\">({escape(pet_id)})</span></div>
                <div>{status_badge(sync.health_level)}</div>
              </div>
              <div class=\"mini\">{escape(sync.summary_line)}</div>
              <div class=\"statline\"> 
                <span class=\"pill\">primary: {escape(sync.primary_device_id or '-')}</span>
                <span class=\"pill\">online: {sync.online_devices}</span>
                <span class=\"pill\">offline: {sync.offline_devices}</span>
                <span class=\"pill\">conflicts: {len(sync.conflict_device_ids)}</span>
              </div>
              <div class=\"mini\">{escape(sync.primary_hint)}</div>
              <div class=\"mini\">建议：{escape(sync.action_hint)}</div>
            </div>
            """
        )

    device_cards: List[str] = []
    online_ok_devices = 0
    offline_or_warn_devices = 0
    for device_id in sorted(DEVICES.keys()):
        rec = DEVICES[device_id]
        health = device_health_snapshot(rec)
        summary = build_device_sync_summary(device_id)
        is_ok = not health["is_offline"] and summary.occupancy_state != "conflicted"
        if is_ok:
            online_ok_devices += 1
        else:
            offline_or_warn_devices += 1
        device_cards.append(
            f"""
            <div class=\"item\"> 
              <div class=\"item-title\"> 
                <div><strong><a href=\"/ui/device/{escape(device_id)}\">{escape(device_id)}</a></strong></div>
                <div>{status_badge(health.get('connection_state'))}{status_badge(summary.health_level)}</div>
              </div>
              <div class=\"mini\">{escape(rec.hardware_model)} · FW {escape(rec.firmware_version)}</div>
              <div class=\"statline\"> 
                <span class=\"pill\">bound: {escape('yes' if rec.bound else 'no')}</span>
                <span class=\"pill\">pet: {escape(summary.pet_id or '-')}</span>
                <span class=\"pill\">events: {len(DEVICE_EVENTS.get(device_id, []))}</span>
              </div>
              <div class=\"mini\">{escape(summary.summary_line)}</div>
              <div class=\"mini\">建议：{escape(summary.action_hint)}</div>
            </div>
            """
        )

    check_cards = ''.join(
        f'<div class="item"><div class="item-title"><strong>{escape(title)}</strong><div>{status_badge(status)}</div></div><div class="mini">{escape(note)}</div></div>'
        for title, status, note in checks
    )
    recent_focus = merged_event_stream(limit=10)
    recent_cards = ''.join(
        f'<div class="item"><div class="item-title"><strong>{escape(item["kind"])}</strong><span class="mini">{escape(item["source_type"])}:{escape(item["source_id"])} · {escape(item["created_at"])} </span></div><div>{escape(item["message"])}</div></div>'
        for item in recent_focus
    ) or '<div class="muted">暂无事件</div>'

    return {
        "snapshot": snapshot,
        "warning_pets": warning_pets,
        "online_ok_devices": online_ok_devices,
        "offline_or_warn_devices": offline_or_warn_devices,
        "healthy_pets": healthy_pets,
        "check_cards_html": check_cards,
        "device_cards_html": ''.join(device_cards),
        "pet_cards_html": ''.join(pet_cards),
        "recent_cards_html": recent_cards,
    }

def build_memory_context(*, pet_id: Optional[str], kind: Optional[str], keyword: Optional[str], limit: int, read_memory, kv_table) -> Dict[str, object]:
    pet_ids = sorted(PETS.keys())
    selected_pet = pet_id or (pet_ids[0] if pet_ids else None)
    summary_html = '<div class="muted">暂无可展示数据</div>'
    memory_cards = '<div class="muted">暂无宠物，无法查看记忆。</div>'
    if selected_pet:
        mem = read_memory(selected_pet, kind=kind or None, keyword=keyword or None, limit=limit)
        summary_html = kv_table([
            ('pet_id', selected_pet),
            ('total', mem.total),
            ('short_term', mem.short_term),
            ('long_term', mem.long_term),
            ('event_count', mem.event_count),
            ('filter_kind', kind or '-'),
            ('keyword', keyword or '-'),
            ('limit', limit),
        ])
        memory_cards = ''.join(
            f'''<div class="item"><div class="item-title"><strong>{escape(item.kind)}</strong><span class="mini">{escape(item.created_at or '-')}</span></div><div>{escape(item.text)}</div><div class="mini">tags: {escape(', '.join(item.tags) if item.tags else '-')}</div></div>'''
            for item in mem.items[::-1]
        ) or '<div class="muted">暂无记忆</div>'
    pet_overview = ''.join(
        f'''<div class="item"><div class="item-title"><strong><a href="/ui/pet/{escape(pid)}">{escape(PETS[pid].name)}</a></strong><span class="mini">{escape(pid)}</span></div><div class="mini">species: {escape(PETS[pid].species_id)} · theme: {escape(PETS[pid].theme_id)}</div><div class="actions"><a class="btn" href="/ui/memory?pet_id={escape(pid)}">查看记忆</a><a class="btn" href="/ui/chat?pet_id={escape(pid)}">调试对话</a></div></div>'''
        for pid in pet_ids
    )
    return {
        "pet_ids": pet_ids,
        "selected_pet": selected_pet,
        "summary_html": summary_html,
        "memory_cards_html": memory_cards,
        "pet_overview_html": pet_overview,
    }

def build_chat_context(*, pet_id: Optional[str], read_memory) -> Dict[str, object]:
    pet_ids = sorted(PETS.keys())
    selected_pet = pet_id or (pet_ids[0] if pet_ids else None)
    pet = PETS.get(selected_pet) if selected_pet else None
    recent_memories = read_memory(selected_pet, limit=10).items[::-1] if selected_pet else []
    recent_events = EVENTS.get(selected_pet, [])[-8:][::-1] if selected_pet else []
    memory_cards = ''.join(
        f'''<div class="item"><div class="item-title"><strong>{escape(item.kind)}</strong><span class="mini">{escape(item.created_at or '-')}</span></div><div>{escape(item.text)}</div></div>'''
        for item in recent_memories
    ) or '<div class="muted">暂无近期记忆</div>'
    event_cards = ''.join(
        f'''<div class="item"><div class="item-title"><strong>{escape(item.kind)}</strong><span class="mini">{escape(item.created_at)}</span></div><div>{escape(item.text)}</div></div>'''
        for item in recent_events
    ) or '<div class="muted">暂无近期事件</div>'
    return {
        "pet_ids": pet_ids,
        "selected_pet": selected_pet,
        "device_id": pet.device_id if pet else None,
        "mood": pet.mood if pet else None,
        "pet_snapshot": [
            ('pet_id', selected_pet),
            ('name', pet.name if pet else None),
            ('species_id', pet.species_id if pet else None),
            ('theme_id', pet.theme_id if pet else None),
            ('mood', pet.mood if pet else None),
            ('energy', pet.energy if pet else None),
            ('hunger', pet.hunger if pet else None),
            ('affection', pet.affection if pet else None),
            ('model_route_id', pet.model_route_id if pet else None),
        ],
        "memory_cards_html": memory_cards,
        "event_cards_html": event_cards,
    }

