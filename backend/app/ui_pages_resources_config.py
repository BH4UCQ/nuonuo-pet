from __future__ import annotations

from html import escape
from typing import Any, Callable, Optional, List

from fastapi.responses import HTMLResponse

from .ui_page_common import KvTableFn, NoticeFn, PageShellFn, StatusBadgeFn


def render_resources_page(
    *,
    species_count: int,
    theme_count: int,
    resource_pack_count: int,
    assets_manifest_count: int,
    species_cards_html: str,
    theme_cards_html: str,
    resource_cards_html: str,
    compatibility_cards_html: str,
    notice_html: NoticeFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">资源中心</h1>
      <div class="meta">集中查看物种模板、主题包、资源包及其兼容性，作为后台资源配置页的第一版。</div>
      <div class="statline">
        <span class="pill">species: {species_count}</span>
        <span class="pill">themes: {theme_count}</span>
        <span class="pill">resource_packs: {resource_pack_count}</span>
        <span class="pill">assets_manifest: {assets_manifest_count}</span>
      </div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>快速导入测试资源包</h2>
        <form method="get" action="/ui/action/resource-pack-import-sample">
          <label>pack_id<input name="pack_id" value="pack-demo"></label>
          <label>name<input name="name" value="演示资源包"></label>
          <label>pack_type<input name="pack_type" value="theme-assets"></label>
          <label>version<input name="version" value="0.1.0"></label>
          <label>species_id<input name="species_id" value="cat-default"></label>
          <label>theme_id<input name="theme_id" value="cat-gold-day"></label>
          <label><input type="checkbox" name="enabled" value="1" style="width:auto;margin-right:8px;">导入后启用</label>
          <button type="submit">导入示例资源包</button>
        </form>
      </div>
      <div class="card">
        <h2>导入自定义资源包</h2>
        <form method="post" action="/ui/action/import-resource-pack">
          <label>pack_id<input name="pack_id" value="pack-custom"></label>
          <label>name<input name="name" value="自定义资源包"></label>
          <label>pack_type<input name="pack_type" value="theme-assets"></label>
          <label>version<input name="version" value="0.1.0"></label>
          <label>species_id<input name="species_id" value="cat-default"></label>
          <label>theme_id<input name="theme_id" value="cat-gold-day"></label>
          <label>description<textarea name="description" rows="3">通过后台 UI 直接导入</textarea></label>
          <label>slots_json<textarea name="slots_json" rows="8">[]</textarea></label>
          <label><input type="checkbox" name="enabled" value="1" style="width:auto;margin-right:8px;">导入后启用</label>
          <label><input type="checkbox" name="replace" value="1" style="width:auto;margin-right:8px;" checked>允许覆盖同名资源包</label>
          <button type="submit">导入自定义资源包</button>
        </form>
      </div>
      <div class="card">
        <h2>资源接口入口</h2>
        <div class="list">
          <div class="item"><a href="/api/species/templates">物种模板 JSON</a></div>
          <div class="item"><a href="/api/theme/compatibility">主题兼容性 JSON</a></div>
          <div class="item"><a href="/api/resource/packs">资源包列表 JSON</a></div>
          <div class="item"><a href="/api/assets/manifest">资产清单 JSON</a></div>
          <div class="item"><a href="/api/preview/sample">预览样例 JSON</a></div>
        </div>
      </div>
    </div>
    <div class="grid" style="margin-top:16px;">
      <div class="card"><h2>物种模板</h2><div class="list">{species_cards_html or '<div class="muted">暂无物种模板</div>'}</div></div>
      <div class="card"><h2>主题包</h2><div class="list">{theme_cards_html or '<div class="muted">暂无主题包</div>'}</div></div>
    </div>
    <div class="grid" style="margin-top:16px;">
      <div class="card"><h2>资源包</h2><div class="list">{resource_cards_html or '<div class="muted">暂无资源包</div>'}</div></div>
      <div class="card"><h2>主题兼容性</h2><div class="list">{compatibility_cards_html or '<div class="muted">暂无兼容性信息</div>'}</div></div>
    </div>
    '''
    return page_shell("Resource Center", body)

def render_config_page(
    *,
    route_ids: List[str],
    default_route_id: Optional[str],
    fallback_route_ids: List[str],
    prefer_enabled: bool,
    allow_manual_override: bool,
    routing_notes: str,
    route_cards_html: str,
    pet_cards_html: str,
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    options_html: Callable[..., str],
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">配置中心</h1>
      <div class="meta">集中查看模型路由默认配置、回退策略，以及宠物当前模型绑定情况。</div>
      <div class="statline">
        <span class="pill">default_route_id: {escape(default_route_id or '-')}</span>
        <span class="pill">fallback_count: {len(fallback_route_ids)}</span>
        <span class="pill">prefer_enabled: {escape(str(prefer_enabled))}</span>
        <span class="pill">allow_manual_override: {escape(str(allow_manual_override))}</span>
      </div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>模型路由配置</h2>
        {kv_table([
            ('default_route_id', default_route_id),
            ('fallback_route_ids', fallback_route_ids),
            ('prefer_enabled', prefer_enabled),
            ('allow_manual_override', allow_manual_override),
            ('routing_notes', routing_notes),
        ])}
      </div>
      <div class="card">
        <h2>更新默认配置</h2>
        <form method="get" action="/ui/action/model-route-config">
          <label>default_route_id
            <select name="default_route_id">{options_html(route_ids, default_route_id)}</select>
          </label>
          <label>fallback_route_ids（逗号分隔）
            <input name="fallback_route_ids" value="{escape(','.join(fallback_route_ids))}">
          </label>
          <label>prefer_enabled
            <select name="prefer_enabled">
              <option value="1"{' selected' if prefer_enabled else ''}>true</option>
              <option value="0"{' selected' if not prefer_enabled else ''}>false</option>
            </select>
          </label>
          <label>allow_manual_override
            <select name="allow_manual_override">
              <option value="1"{' selected' if allow_manual_override else ''}>true</option>
              <option value="0"{' selected' if not allow_manual_override else ''}>false</option>
            </select>
          </label>
          <label>routing_notes
            <textarea name="routing_notes" rows="4">{escape(routing_notes)}</textarea>
          </label>
          <button type="submit">保存配置</button>
        </form>
      </div>
    </div>
    <div class="grid" style="margin-top:16px;">
      <div class="card"><h2>可用模型路由</h2><div class="list">{route_cards_html or '<div class="muted">暂无模型路由</div>'}</div></div>
      <div class="card"><h2>宠物模型绑定概览</h2><div class="list">{pet_cards_html or '<div class="muted">暂无宠物</div>'}</div></div>
    </div>
    '''
    return page_shell("Config Center", body)

