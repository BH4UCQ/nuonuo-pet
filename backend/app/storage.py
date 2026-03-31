from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json
import secrets


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_FILE = DATA_DIR / "state.json"
MODEL_ROUTE_CONFIG: Dict[str, Any] = {
    "default_route_id": "cloud-balanced",
    "fallback_route_ids": ["local-default", "cloud-balanced"],
    "prefer_enabled": True,
    "allow_manual_override": True,
    "routing_notes": "Prefer balanced cloud, fall back to local when disabled or missing.",
}


@dataclass
class DeviceRecord:
    device_id: str
    hardware_model: str = "unknown"
    firmware_version: str = "0.0.0"
    capabilities: List[str] = field(default_factory=list)
    bound: bool = False
    owner_id: str | None = None
    bind_code: str | None = None
    bind_expires_at: float | None = None
    state: Dict[str, Any] = field(default_factory=dict)
    last_seen_at: str | None = None
    connection_state: str = "unknown"
    offline_reason: str | None = None


@dataclass
class DeviceEventRecord:
    device_id: str
    kind: str
    message: str
    created_at: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PetRecord:
    pet_id: str
    name: str = "nuonuo"
    species_id: str = "cat-default"
    theme_id: str = "cat-gold-day"
    model_route_id: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    growth_stage: str = "egg"
    level: int = 1
    exp: int = 0
    mood: str = "neutral"
    energy: int = 100
    hunger: int = 20
    affection: int = 50
    primary_device_id: str | None = None
    linked_device_ids: List[str] = field(default_factory=list)
    growth_preferences: Dict[str, int] = field(default_factory=lambda: {"play": 0, "care": 0, "rest": 0, "feed": 0, "chat": 0, "praise": 0})
    preference_notes: List[str] = field(default_factory=list)


@dataclass
class MemoryRecord:
    kind: str
    text: str
    tags: List[str]
    created_at: str


@dataclass
class EventRecord:
    kind: str
    text: str
    tags: List[str]
    created_at: str


DEVICES: Dict[str, DeviceRecord] = {}
DEVICE_EVENTS: Dict[str, List[DeviceEventRecord]] = {}
PETS: Dict[str, PetRecord] = {}
MEMORY: Dict[str, List[MemoryRecord]] = {}
RESOURCE_PACKS: Dict[str, Dict[str, Any]] = {}
RESOURCE_SLOT_RULES: Dict[str, Dict[str, Any]] = {
    "body": {"resource_type": "sprite", "max_width": 128, "max_height": 128, "formats": ["png", "webp"]},
    "eyes": {"resource_type": "sprite", "max_width": 64, "max_height": 64, "formats": ["png", "webp"]},
    "ears": {"resource_type": "sprite", "max_width": 64, "max_height": 64, "formats": ["png", "webp"]},
    "tail": {"resource_type": "sprite", "max_width": 96, "max_height": 96, "formats": ["png", "webp"]},
    "badge": {"resource_type": "overlay", "max_width": 48, "max_height": 48, "formats": ["png", "webp"]},
    "face": {"resource_type": "sprite", "max_width": 96, "max_height": 96, "formats": ["png", "webp"]},
    "hands": {"resource_type": "sprite", "max_width": 64, "max_height": 64, "formats": ["png", "webp"]},
    "prop": {"resource_type": "sprite", "max_width": 96, "max_height": 96, "formats": ["png", "webp"]},
    "crest": {"resource_type": "sprite", "max_width": 64, "max_height": 64, "formats": ["png", "webp"]},
    "accessory": {"resource_type": "overlay", "max_width": 48, "max_height": 48, "formats": ["png", "webp"]},
}

THEME_PACKS: List[Dict[str, Any]] = [
    {
        "theme_id": "cat-gold-day",
        "name": "金渐层白天",
        "species_id": "cat-default",
        "version": "0.1.0",
        "compatible_slot_ids": ["body", "eyes", "ears", "tail", "badge"],
        "min_firmware_version": "0.1.0",
        "max_firmware_version": None,
        "slot_map": {
            "body": "sprites/cat-gold/body.png",
            "eyes": "sprites/cat-gold/eyes.png",
            "ears": "sprites/cat-gold/ears.png",
            "tail": "sprites/cat-gold/tail.png",
            "badge": "overlays/gold-badge.png",
        },
        "palette": {"primary": "#d7b46a", "secondary": "#fff6e3", "accent": "#7d5a28"},
        "preview_asset": "previews/cat-gold-day.png",
    },
    {
        "theme_id": "cat-silver-night",
        "name": "银渐层夜晚",
        "species_id": "cat-default",
        "version": "0.1.0",
        "compatible_slot_ids": ["body", "eyes", "ears", "tail", "badge"],
        "min_firmware_version": "0.1.0",
        "max_firmware_version": None,
        "slot_map": {
            "body": "sprites/cat-silver/body.png",
            "eyes": "sprites/cat-silver/eyes.png",
            "ears": "sprites/cat-silver/ears.png",
            "tail": "sprites/cat-silver/tail.png",
            "badge": "overlays/silver-badge.png",
        },
        "palette": {"primary": "#b7c1cc", "secondary": "#ebeff5", "accent": "#4c5a67"},
        "preview_asset": "previews/cat-silver-night.png",
    },
    {
        "theme_id": "monkey-sun",
        "name": "猴子阳光",
        "species_id": "monkey-default",
        "version": "0.1.0",
        "slot_map": {"body": "sprites/monkey/body.png", "face": "sprites/monkey/face.png", "prop": "sprites/monkey/prop.png"},
        "palette": {"primary": "#f2a65a", "secondary": "#fff1d6", "accent": "#86562f"},
        "preview_asset": "previews/monkey-sun.png",
    },
    {
        "theme_id": "dino-green",
        "name": "恐龙绿色",
        "species_id": "dino-default",
        "version": "0.1.0",
        "slot_map": {"body": "sprites/dino/body.png", "crest": "sprites/dino/crest.png", "accessory": "overlays/dino-badge.png"},
        "palette": {"primary": "#76c96f", "secondary": "#dcf4d8", "accent": "#2f6b2d"},
        "preview_asset": "previews/dino-green.png",
    },
]

SPECIES_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "cat-default",
        "name": "猫咪模板",
        "description": "温柔、亲近、适合高频互动的默认模板。",
        "default_theme_id": "cat-gold-day",
        "personality_tags": ["gentle", "curious", "affectionate"],
        "allowed_theme_ids": ["cat-gold-day", "cat-silver-night"],
        "growth_curve": {"egg": 0, "baby": 2, "juvenile": 4, "teen": 7, "adult": 12},
        "ui_slots": ["body", "eyes", "ears", "tail", "badge"],
    },
    {
        "id": "monkey-default",
        "name": "猴子模板",
        "description": "活泼、好奇、动作更丰富的模板。",
        "default_theme_id": "monkey-sun",
        "personality_tags": ["playful", "mischievous", "energetic"],
        "allowed_theme_ids": ["monkey-sun", "monkey-forest"],
        "growth_curve": {"egg": 0, "baby": 2, "juvenile": 5, "teen": 8, "adult": 13},
        "ui_slots": ["body", "face", "hands", "tail", "prop"],
    },
    {
        "id": "dino-default",
        "name": "恐龙模板",
        "description": "更有存在感、适合夸张表情与成长感的模板。",
        "default_theme_id": "dino-green",
        "personality_tags": ["bold", "protective", "ancient"],
        "allowed_theme_ids": ["dino-green", "dino-night"],
        "growth_curve": {"egg": 0, "baby": 3, "juvenile": 6, "teen": 10, "adult": 15},
        "ui_slots": ["body", "crest", "eyes", "tail", "accessory"],
    },
]

PREVIEW_HINTS: Dict[str, Dict[str, Any]] = {
    "cat-default": {
        "headline": "柔软、亲近、轻微摆尾",
        "idle_pose": "sit",
        "idle_motion": "slow_breathe",
        "accent_slot": "badge",
    },
    "monkey-default": {
        "headline": "灵活、好动、擅长抓取",
        "idle_pose": "stand",
        "idle_motion": "sway",
        "accent_slot": "prop",
    },
    "dino-default": {
        "headline": "厚重、稳健、存在感更强",
        "idle_pose": "stand",
        "idle_motion": "breath_pulse",
        "accent_slot": "accessory",
    },
}
DEFAULT_PREVIEW_SELECTION: Dict[str, Dict[str, Any]] = {
    "lcd": {"species_id": "cat-default", "theme_id": "cat-gold-day", "reason": "prefer lcd-friendly cat preview", "signals": ["lcd"], "display_mode": "color-lcd"},
    "oled": {"species_id": "cat-default", "theme_id": "cat-silver-night", "reason": "prefer high-contrast oled preview", "signals": ["oled"], "display_mode": "oled-high-contrast"},
    "voice": {"species_id": "monkey-default", "theme_id": "monkey-sun", "reason": "voice-only friendly lively preview", "signals": ["voice"], "display_mode": "voice-only"},
    "rich": {"species_id": "dino-default", "theme_id": "dino-green", "reason": "rich-display friendly bold preview", "signals": ["touch", "color"], "display_mode": "rich-lcd"},
    "default": {"species_id": "cat-default", "theme_id": "cat-gold-day", "reason": "fallback default preview", "signals": [], "display_mode": "generic"},
}
MODEL_ROUTES: List[Dict[str, Any]] = [
    {
        "id": "local-default",
        "provider": "local",
        "model_name": "tiny-llm",
        "mode": "auto",
        "cost_tier": "low",
        "latency_tier": "low",
        "enabled": True,
    },
    {
        "id": "cloud-balanced",
        "provider": "cloud",
        "model_name": "general-chat",
        "mode": "auto",
        "cost_tier": "balanced",
        "latency_tier": "balanced",
        "enabled": True,
    },
    {
        "id": "cloud-premium",
        "provider": "cloud",
        "model_name": "rich-dialogue",
        "mode": "manual",
        "cost_tier": "high",
        "latency_tier": "balanced",
        "enabled": True,
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_bind_code() -> str:
    return secrets.token_hex(4).upper()


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_records(items):
    if items is None:
        return []
    result = []
    for item in items:
        if hasattr(item, "__dataclass_fields__"):
            result.append(asdict(item))
        else:
            result.append(item)
    return result


def save_state() -> None:
    _ensure_data_dir()
    payload = {
        "devices": _serialize_records(DEVICES.values()),
        "device_events": {device_id: _serialize_records(items) for device_id, items in DEVICE_EVENTS.items()},
        "pets": _serialize_records(PETS.values()),
        "memory": {pet_id: _serialize_records(items) for pet_id, items in MEMORY.items()},
        "events": {pet_id: _serialize_records(items) for pet_id, items in EVENTS.items()},
        "model_route_config": dict(MODEL_ROUTE_CONFIG),
        "resource_packs": RESOURCE_PACKS,
    }
    STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_state() -> None:
    if not STATE_FILE.exists():
        return
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    DEVICES.clear()
    DEVICE_EVENTS.clear()
    PETS.clear()
    MEMORY.clear()
    EVENTS.clear()

    for item in data.get("devices", []):
        rec = DeviceRecord(**item)
        DEVICES[rec.device_id] = rec
    for device_id, items in data.get("device_events", {}).items():
        DEVICE_EVENTS[device_id] = [DeviceEventRecord(**item) for item in items]
    for item in data.get("pets", []):
        rec = PetRecord(**item)
        PETS[rec.pet_id] = rec
    for pet_id, items in data.get("memory", {}).items():
        MEMORY[pet_id] = [MemoryRecord(**item) for item in items]
    for pet_id, items in data.get("events", {}).items():
        EVENTS[pet_id] = [EventRecord(**item) for item in items]
    RESOURCE_PACKS.clear()
    RESOURCE_PACKS.update(data.get("resource_packs", {}))
    if "default_route_id" not in MODEL_ROUTE_CONFIG:
        MODEL_ROUTE_CONFIG["default_route_id"] = "cloud-balanced"
    if "fallback_route_ids" not in MODEL_ROUTE_CONFIG:
        MODEL_ROUTE_CONFIG["fallback_route_ids"] = ["local-default", "cloud-balanced"]
    if "prefer_enabled" not in MODEL_ROUTE_CONFIG:
        MODEL_ROUTE_CONFIG["prefer_enabled"] = True
    if "allow_manual_override" not in MODEL_ROUTE_CONFIG:
        MODEL_ROUTE_CONFIG["allow_manual_override"] = True
    if "routing_notes" not in MODEL_ROUTE_CONFIG:
        MODEL_ROUTE_CONFIG["routing_notes"] = "Prefer balanced cloud, fall back to local when disabled or missing."
