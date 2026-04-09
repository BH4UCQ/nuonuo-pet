from __future__ import annotations
from typing import List, Dict

from html import escape
import json

from .storage import ASSET_MANIFEST, DEVICE_EVENTS, DEVICES, EVENTS, MODEL_ROUTES, PETS, SPECIES_TEMPLATES, THEME_PACKS


def build_config_context(*, model_routes_config, status_badge) -> Dict[str, object]:
    routes = sorted(MODEL_ROUTES, key=lambda item: item.get("id", ""))
    config = model_routes_config()
    pet_cards: List[str] = []
    for pet_id in sorted(PETS.keys()):
        pet = PETS[pet_id]
        route_label = pet.model_route_id or config.default_route_id or "-"
        pet_cards.append(
            f'''
            <div class="item">
              <div class="item-title">
                <div><strong><a href="/ui/pet/{escape(pet_id)}">{escape(pet.name)}</a></strong> <span class="mini">({escape(pet_id)})</span></div>
                <div>{status_badge(route_label)}</div>
              </div>
              <div class="mini">species: {escape(pet.species_id)} · theme: {escape(pet.theme_id)}</div>
              <div class="statline">
                <span class="pill">model_route_id: {escape(pet.model_route_id or '-')}</span>
                <span class="pill">provider: {escape(pet.model_provider or '-')}</span>
                <span class="pill">model: {escape(pet.model_name or '-')}</span>
              </div>
              <div class="actions">
                <a class="btn" href="/api/pet/{escape(pet_id)}">宠物 JSON</a>
                <a class="btn" href="/api/model/routes/apply/{escape(pet_id)}">应用接口</a>
              </div>
            </div>
            '''
        )
    route_cards = ''.join(
        f'''
        <div class="item">
          <div class="item-title">
            <div><strong>{escape(item['id'])}</strong></div>
            <div>{status_badge('enabled' if item.get('enabled') else 'disabled')}{status_badge(item.get('provider'))}</div>
          </div>
          <div class="mini">model: {escape(item.get('model_name', '-'))}</div>
          <div class="statline">
            <span class="pill">mode: {escape(item.get('mode', '-'))}</span>
            <span class="pill">cost: {escape(item.get('cost_tier', '-'))}</span>
            <span class="pill">latency: {escape(item.get('latency_tier', '-'))}</span>
          </div>
        </div>
        '''
        for item in routes
    )
    return {
        "route_ids": [item['id'] for item in routes],
        "default_route_id": config.default_route_id,
        "fallback_route_ids": config.fallback_route_ids,
        "prefer_enabled": config.prefer_enabled,
        "allow_manual_override": config.allow_manual_override,
        "routing_notes": config.routing_notes,
        "route_cards_html": route_cards,
        "pet_cards_html": ''.join(pet_cards),
    }

def build_resources_context(*, theme_compatibility, resource_packs, status_badge) -> Dict[str, object]:
    compatibility = theme_compatibility().items
    resource_items = resource_packs().items
    species_cards = ''.join(
        f'''
        <div class="item">
          <div class="item-title"><strong>{escape(item['name'])}</strong><span class="mini">{escape(item['id'])}</span></div>
          <div class="mini">default_theme: {escape(item.get('default_theme_id', '-'))}</div>
          <div class="statline">
            <span class="pill">themes: {len(item.get('allowed_theme_ids', []))}</span>
            <span class="pill">ui_slots: {len(item.get('ui_slots', []))}</span>
          </div>
          <div class="mini">{escape(item.get('description', ''))}</div>
        </div>
        '''
        for item in SPECIES_TEMPLATES
    )
    theme_cards = ''.join(
        f'''
        <div class="item">
          <div class="item-title">
            <div><strong>{escape(item.get('name', '-'))}</strong> <span class="mini">{escape(item.get('theme_id', '-'))}</span></div>
            <div>{status_badge('compatible' if any(c.theme_id == item.get('theme_id') and c.compatible for c in compatibility) else 'warning')}</div>
          </div>
          <div class="mini">species: {escape(item.get('species_id', '-'))} · version: {escape(item.get('version', '-'))}</div>
          <div class="statline">
            <span class="pill">slots: {len(item.get('slot_map', {}))}</span>
            <span class="pill">preview: {escape(item.get('preview_asset') or '-')}</span>
          </div>
        </div>
        '''
        for item in THEME_PACKS
    )
    resource_cards: List[str] = []
    for item in resource_items:
        previous_versions = item.previous_versions if hasattr(item, 'previous_versions') else []
        resource_cards.append(
            f'''
            <div class="item">
              <div class="item-title">
                <div><strong>{escape(item.name)}</strong> <span class="mini">{escape(item.pack_id)}</span></div>
                <div>{status_badge('enabled' if item.enabled else 'disabled')}</div>
              </div>
              <div class="mini">type: {escape(item.pack_type)} · version: {escape(item.version)}</div>
              <div class="statline">
                <span class="pill">active_version: {escape(item.active_version or '-')}</span>
                <span class="pill">previous_versions: {len(previous_versions)}</span>
                <span class="pill">species: {escape(item.species_id or '-')}</span>
              </div>
              <div class="actions">
                <a class="btn" href="/api/resource/packs/{escape(item.pack_id)}">详情 JSON</a>
                <a class="btn" href="/ui/action/resource-pack-enable?pack_id={escape(item.pack_id)}&enabled={'0' if item.enabled else '1'}">{'禁用' if item.enabled else '启用'}</a>
                <a class="btn" href="/ui/action/resource-pack-rollback?pack_id={escape(item.pack_id)}">回滚</a>
              </div>
            </div>
            '''
        )
    compatibility_cards = ''.join(
        f'''
        <div class="item">
          <div class="item-title"><strong>{escape(item.theme_id)}</strong><div>{status_badge('ok' if item.compatible else 'warn')}</div></div>
          <div class="mini">species: {escape(item.species_id)} · version: {escape(item.version)}</div>
          <div class="mini">reasons: {escape(', '.join(item.reasons) if item.reasons else '-')}</div>
          <div class="mini">warnings: {escape(', '.join(item.warnings) if item.warnings else '-')}</div>
        </div>
        '''
        for item in compatibility
    )
    return {
        "species_count": len(SPECIES_TEMPLATES),
        "theme_count": len(THEME_PACKS),
        "resource_pack_count": len(resource_items),
        "assets_manifest_count": len(ASSET_MANIFEST),
        "species_cards_html": species_cards,
        "theme_cards_html": theme_cards,
        "resource_cards_html": ''.join(resource_cards),
        "compatibility_cards_html": compatibility_cards,
    }

