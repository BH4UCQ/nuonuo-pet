from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class HealthResponse(BaseModel):
    status: str = "ok"
    server_time: Optional[str] = None


class ProtocolInfo(BaseModel):
    protocol_name: str = "nuonuo-pet"
    protocol_version: str = "0.1.0"
    server_time: Optional[str] = None


class DeviceRegisterRequest(BaseModel):
    device_id: str
    hardware_model: str = "unknown"
    firmware_version: str = "0.0.0"
    capabilities: List[str] = Field(default_factory=list)


class DeviceRegisterResponse(BaseModel):
    device_id: str
    registered: bool = True
    binding_required: bool = True
    server_time: Optional[str] = None
    next_step: str = "request_binding"


class BindRequest(BaseModel):
    device_id: str


class BindRequestResponse(BaseModel):
    device_id: str
    bind_code: str
    expires_in_seconds: int = 600
    expires_at: Optional[str] = None
    bind_hint: str = "Use the code in the companion app to confirm binding."


class BindConfirmRequest(BaseModel):
    device_id: str
    bind_code: str
    owner_id: str


class BindConfirmResponse(BaseModel):
    device_id: str
    bound: bool
    owner_id: str
    pet_id: Optional[str] = None
    server_time: Optional[str] = None


class DeviceStateRequest(BaseModel):
    device_id: str
    pet_id: Optional[str] = None
    state: Dict[str, Any] = Field(default_factory=dict)


class DeviceStateResponse(BaseModel):
    ok: bool = True
    device_id: str
    server_time: Optional[str] = None
    binding_state: str = "unknown"


class DeviceHealthResponse(BaseModel):
    device_id: str
    bound: bool = False
    connection_state: str = "unknown"
    last_seen_at: Optional[str] = None
    is_offline: bool = False
    offline_reason: Optional[str] = None
    stale_after_seconds: int = 300
    server_time: Optional[str] = None


class DeviceHeartbeatRequest(BaseModel):
    device_id: str
    note: Optional[str] = None


class DeviceHeartbeatResponse(BaseModel):
    ok: bool = True
    device_id: str
    connection_state: str = "online"
    last_seen_at: Optional[str] = None
    server_time: Optional[str] = None
    state: Dict[str, Any] = Field(default_factory=dict)
    hardware_model: str = "unknown"
    firmware_version: str = "0.0.0"
    capabilities: List[str] = Field(default_factory=list)
    bound: bool = False
    owner_id: Optional[str] = None
    bind_code: Optional[str] = None
    bind_expires_at: Optional[str] = None


class DeviceEventItem(BaseModel):
    device_id: str
    kind: str
    message: str
    created_at: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class DeviceEventRequest(BaseModel):
    kind: str
    message: str
    meta: Dict[str, Any] = Field(default_factory=dict)


class DeviceEventResponse(BaseModel):
    ok: bool = True
    device_id: str
    event_count: int = 0
    server_time: Optional[str] = None


class DeviceEventListResponse(BaseModel):
    device_id: str
    server_time: Optional[str] = None
    items: List[DeviceEventItem] = Field(default_factory=list)


class SpeciesTemplateItem(BaseModel):
    id: str
    name: str
    description: str
    default_theme_id: str
    personality_tags: List[str] = Field(default_factory=list)
    allowed_theme_ids: List[str] = Field(default_factory=list)
    growth_curve: Dict[str, int] = Field(default_factory=dict)
    ui_slots: List[str] = Field(default_factory=list)


class SpeciesTemplateResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[SpeciesTemplateItem] = Field(default_factory=list)


class ModelRouteItem(BaseModel):
    id: str
    provider: str
    model_name: str
    mode: str = "auto"
    cost_tier: str = "balanced"
    latency_tier: str = "balanced"
    enabled: bool = True


class ModelRouteResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[ModelRouteItem] = Field(default_factory=list)


class ModelRouteConfigResponse(BaseModel):
    server_time: Optional[str] = None
    default_route_id: Optional[str] = None
    fallback_route_ids: List[str] = Field(default_factory=list)
    prefer_enabled: bool = True
    allow_manual_override: bool = True
    routing_notes: str = ""


class ModelRouteConfigUpdateRequest(BaseModel):
    default_route_id: Optional[str] = None
    fallback_route_ids: Optional[List[str]] = None
    prefer_enabled: Optional[bool] = None
    allow_manual_override: Optional[bool] = None
    routing_notes: Optional[str] = None


class ModelRouteResolveRequest(BaseModel):
    route_id: Optional[str] = None
    pet_id: Optional[str] = None
    prefer_enabled: bool = True
    allow_fallback: bool = True
    fallback_route_ids: List[str] = Field(default_factory=list)


class ModelRouteResolveResponse(BaseModel):
    server_time: Optional[str] = None
    requested_route_id: Optional[str] = None
    selected_route: ModelRouteItem
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    available_route_ids: List[str] = Field(default_factory=list)
    config_default_route_id: Optional[str] = None


class PetProfileResponse(BaseModel):
    pet_id: str
    name: str = "nuonuo"
    species_id: str = "cat-default"
    theme_id: str = "cat-gold-day"
    model_route_id: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    growth_stage: str = "egg"
    level: int = 1
    exp: int = 0
    mood: str = "neutral"
    energy: int = 100
    hunger: int = 20
    affection: int = 50
    owner_id: Optional[str] = None
    device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    device_connection_state: Optional[str] = None
    device_last_seen_at: Optional[str] = None
    device_is_offline: Optional[bool] = None
    device_offline_reason: Optional[str] = None
    growth_preferences: Dict[str, int] = Field(default_factory=dict)
    preference_notes: List[str] = Field(default_factory=list)


class PetCreateRequest(BaseModel):
    pet_id: str
    name: str = "nuonuo"
    species_id: str = "cat-default"
    theme_id: str = "cat-gold-day"
    model_route_id: Optional[str] = None
    owner_id: Optional[str] = None
    device_id: Optional[str] = None


class PetUpdateRequest(BaseModel):
    name: Optional[str] = None
    species_id: Optional[str] = None
    theme_id: Optional[str] = None
    model_route_id: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    growth_stage: Optional[str] = None
    level: Optional[int] = None
    exp: Optional[int] = None
    mood: Optional[str] = None
    energy: Optional[int] = None
    hunger: Optional[int] = None
    affection: Optional[int] = None
    owner_id: Optional[str] = None
    device_id: Optional[str] = None
    linked_device_ids: Optional[List[str]] = None


class PetEventRequest(BaseModel):
    pet_id: str
    kind: str
    text: str
    tags: List[str] = Field(default_factory=list)


class PetDeviceLinkRequest(BaseModel):
    device_id: str
    make_primary: bool = False


class PetDeviceUnlinkRequest(BaseModel):
    device_id: Optional[str] = None
    remove_primary: bool = False


class PetDevicePrimaryRequest(BaseModel):
    device_id: str


class PetDeviceLinkItem(BaseModel):
    device_id: str
    hardware_model: Optional[str] = None
    firmware_version: Optional[str] = None
    connection_state: Optional[str] = None
    last_seen_at: Optional[str] = None
    is_primary: bool = False
    is_online: bool = False


class PetDeviceLinkResponse(BaseModel):
    ok: bool = True
    pet_id: str
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None


class PetDeviceUnlinkResponse(BaseModel):
    ok: bool = True
    pet_id: str
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None


class PetDeviceListResponse(BaseModel):
    pet_id: str
    server_time: Optional[str] = None
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    total: int = 0
    items: List[PetDeviceLinkItem] = Field(default_factory=list)


class PetDevicePrimaryResponse(BaseModel):
    ok: bool = True
    pet_id: str
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None


class PetSyncDeviceItem(BaseModel):
    device_id: str
    is_primary: bool = False
    connection_state: Optional[str] = None
    last_seen_at: Optional[str] = None
    is_online: bool = False
    offline_reason: Optional[str] = None
    event_count: int = 0


class PetSyncSummaryResponse(BaseModel):
    pet_id: str
    server_time: Optional[str] = None
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    total_devices: int = 0
    online_devices: int = 0
    offline_devices: int = 0
    missing_devices: int = 0
    conflict_device_ids: List[str] = Field(default_factory=list)
    conflict_notes: List[str] = Field(default_factory=list)
    primary_device_present: bool = False
    primary_device_online: bool = False
    recommended_action: Optional[str] = None
    device_items: List[PetSyncDeviceItem] = Field(default_factory=list)
    recent_pet_events: List[Dict[str, Any]] = Field(default_factory=list)
    recent_device_events: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    sync_notes: List[str] = Field(default_factory=list)


class PetBroadcastItem(BaseModel):
    device_id: Optional[str] = None
    kind: str
    message: str
    created_at: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class PetBroadcastSummaryResponse(BaseModel):
    pet_id: str
    server_time: Optional[str] = None
    total_devices: int = 0
    online_devices: int = 0
    offline_devices: int = 0
    missing_devices: int = 0
    conflict_device_ids: List[str] = Field(default_factory=list)
    conflict_notes: List[str] = Field(default_factory=list)
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    broadcast_items: List[PetBroadcastItem] = Field(default_factory=list)
    device_items: List[PetSyncDeviceItem] = Field(default_factory=list)
    sync_notes: List[str] = Field(default_factory=list)


class DeviceSyncSummaryResponse(BaseModel):
    device_id: str
    server_time: Optional[str] = None
    pet_id: Optional[str] = None
    primary_device_id: Optional[str] = None
    linked_device_ids: List[str] = Field(default_factory=list)
    linked_pet_ids: List[str] = Field(default_factory=list)
    occupancy_state: str = "free"
    conflict_notes: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    device_state: Dict[str, Any] = Field(default_factory=dict)
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)
    pet_summary: Optional[PetSyncSummaryResponse] = None


class PetEventResponse(BaseModel):
    ok: bool = True
    pet_id: str
    event_count: int = 0
    recent_kind: Optional[str] = None
    server_time: Optional[str] = None


class PetEventSummaryItem(BaseModel):
    kind: str
    count: int = 0
    last_text: Optional[str] = None
    last_created_at: Optional[str] = None


class PetEventSummaryResponse(BaseModel):
    pet_id: str
    server_time: Optional[str] = None
    total: int = 0
    recent_event_count: int = 0
    categories: Dict[str, int] = Field(default_factory=dict)
    recent_items: List[Dict[str, Any]] = Field(default_factory=list)
    items: List[PetEventSummaryItem] = Field(default_factory=list)


class PetGrowthSummaryResponse(BaseModel):
    pet_id: str
    name: str = "nuonuo"
    species_id: str = "cat-default"
    growth_stage: str = "egg"
    level: int = 1
    exp: int = 0
    next_level_exp: int = 10
    growth_curve: Dict[str, int] = Field(default_factory=dict)
    growth_preferences: Dict[str, int] = Field(default_factory=dict)
    preference_notes: List[str] = Field(default_factory=list)
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)
    server_time: Optional[str] = None


class ChatRequest(BaseModel):
    pet_id: str
    device_id: Optional[str] = None
    user_text: str
    context: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply_text: str
    emotion: str = "neutral"
    actions: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None


class MemoryItem(BaseModel):
    kind: str
    text: str
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None


class MemoryWriteRequest(BaseModel):
    item: MemoryItem


class MemoryListResponse(BaseModel):
    pet_id: str
    server_time: Optional[str] = None
    total: int = 0
    short_term: int = 0
    long_term: int = 0
    event_count: int = 0
    items: List[MemoryItem] = Field(default_factory=list)


class MemorySummaryResponse(BaseModel):
    pet_id: str
    short_term: int = 0
    long_term: int = 0
    event_count: int = 0
    server_time: Optional[str] = None


class ResourceSlotItem(BaseModel):
    slot_id: str
    resource_type: str
    path: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    notes: Optional[str] = None


class ResourcePackManifest(BaseModel):
    pack_id: str
    pack_type: str
    version: str
    species_id: Optional[str] = None
    theme_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    slots: List[ResourceSlotItem] = Field(default_factory=list)
    checksum: Optional[str] = None


class ResourcePackValidateRequest(BaseModel):
    manifest: ResourcePackManifest


class ResourcePackRecordItem(BaseModel):
    pack_id: str
    pack_type: str
    version: str
    species_id: Optional[str] = None
    theme_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    enabled: bool = False
    active_version: Optional[str] = None
    imported_at: Optional[str] = None
    updated_at: Optional[str] = None
    previous_versions: List[str] = Field(default_factory=list)
    manifest: ResourcePackManifest


class ResourcePackListResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[ResourcePackRecordItem] = Field(default_factory=list)


class ResourcePackDetailResponse(BaseModel):
    server_time: Optional[str] = None
    item: ResourcePackRecordItem


class ResourcePackImportRequest(BaseModel):
    manifest: ResourcePackManifest
    enabled: bool = False
    replace: bool = True


class ResourcePackImportResponse(BaseModel):
    ok: bool = True
    pack_id: str
    imported: bool = True
    enabled: bool = False
    active_version: Optional[str] = None
    server_time: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class ResourcePackEnableRequest(BaseModel):
    enabled: bool = True


class ResourcePackActionResponse(BaseModel):
    ok: bool = True
    pack_id: str
    enabled: bool = True
    active_version: Optional[str] = None
    previous_versions: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None
    note: Optional[str] = None


class ResourcePackListResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[ResourcePackRecordItem] = Field(default_factory=list)


class ResourcePackDetailResponse(BaseModel):
    server_time: Optional[str] = None
    item: ResourcePackRecordItem


class ResourcePackImportRequest(BaseModel):
    manifest: ResourcePackManifest
    enabled: bool = False
    replace: bool = True


class ResourcePackImportResponse(BaseModel):
    ok: bool = True
    pack_id: str
    imported: bool = True
    enabled: bool = False
    active_version: Optional[str] = None
    server_time: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class ResourcePackEnableRequest(BaseModel):
    enabled: bool = True


class ResourcePackActionResponse(BaseModel):
    ok: bool = True
    pack_id: str
    enabled: bool = True
    active_version: Optional[str] = None
    previous_versions: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None
    note: Optional[str] = None


class ThemePackItem(BaseModel):
    theme_id: str
    name: str
    species_id: str
    version: str = "0.1.0"
    compatible_slot_ids: List[str] = Field(default_factory=list)
    min_firmware_version: Optional[str] = None
    max_firmware_version: Optional[str] = None
    slot_map: Dict[str, str] = Field(default_factory=dict)
    palette: Dict[str, str] = Field(default_factory=dict)
    preview_asset: Optional[str] = None


class ThemePackCompatibilityItem(BaseModel):
    theme_id: str
    species_id: str
    version: str = "0.1.0"
    compatible: bool = True
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ThemePackCompatibilityResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[ThemePackCompatibilityItem] = Field(default_factory=list)


class ThemePackResponse(BaseModel):
    server_time: Optional[str] = None
    items: List[ThemePackItem] = Field(default_factory=list)


class ThemePackValidateRequest(BaseModel):
    theme: ThemePackItem


class ThemePackValidateResponse(BaseModel):
    ok: bool = True
    valid: bool = True
    theme_id: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    server_time: Optional[str] = None


class PreviewLayerItem(BaseModel):
    slot_id: str
    resource_path: Optional[str] = None
    resource_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    notes: Optional[str] = None


class PetPreviewResponse(BaseModel):
    server_time: Optional[str] = None
    species_id: str
    theme_id: str
    pet_id: Optional[str] = None
    name: Optional[str] = None
    growth_stage: Optional[str] = None
    palette: Dict[str, str] = Field(default_factory=dict)
    ui_slots: List[str] = Field(default_factory=list)
    layers: List[PreviewLayerItem] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    display_mode: Optional[str] = None
    display_hint: Optional[str] = None


class TemplateSelectionResponse(BaseModel):
    server_time: Optional[str] = None
    hardware_model: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    species_id: str
    theme_id: str
    reason: str = "default"
    matched_signals: List[str] = Field(default_factory=list)


class DeviceCapabilitySummaryResponse(BaseModel):
    server_time: Optional[str] = None
    hardware_model: Optional[str] = None
    firmware_version: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    device_class: str = "unknown"
    display_mode: str = "unknown"
    display_hint: str = ""
    confidence: str = "low"
    recommended_species_id: Optional[str] = None
    recommended_theme_id: Optional[str] = None
    recommended_theme_version: Optional[str] = None
    recommended_theme_name: Optional[str] = None
    recommended_preview_asset: Optional[str] = None
    ui_slot_count: int = 0
    compatible_theme_count: int = 0
    compatible_resource_pack_count: int = 0
    notes: List[str] = Field(default_factory=list)


class DeviceCapabilitySummaryRequest(BaseModel):
    hardware_model: Optional[str] = None
    firmware_version: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)


class DeviceCapabilitySummaryBatchResponse(BaseModel):
    server_time: Optional[str] = None
    item: DeviceCapabilitySummaryResponse


