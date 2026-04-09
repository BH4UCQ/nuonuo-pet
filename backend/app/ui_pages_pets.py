from __future__ import annotations
from typing import Optional, List, Dict, Tuple

from html import escape

from fastapi.responses import HTMLResponse

from .ui_page_common import KvTableFn, NoticeFn, PageShellFn, StatusBadgeFn


def render_pet_management_row(
    *,
    pet_id: str,
    pet_name: str,
    species_id: str,
    theme_id: str,
    growth_stage: str,
    mood: Optional[str],
    level_value: int,
    energy: int,
    hunger: int,
    affection: int,
    primary_device_id: Optional[str],
    linked_devices_text: str,
    summary_line: str,
    recommended_action: str,
    status_badge: StatusBadgeFn,
) -> str:
    return f'''
            <tr>
              <td><a href="/ui/pet/{escape(pet_id)}">{escape(pet_name)}</a><div class="mini">{escape(pet_id)}</div></td>
              <td>{escape(species_id)}</td>
              <td>{escape(theme_id)}</td>
              <td>{escape(growth_stage)}</td>
              <td>{status_badge(mood)}</td>
              <td>{level_value}</td>
              <td>{energy}</td>
              <td>{hunger}</td>
              <td>{affection}</td>
              <td>{escape(primary_device_id or '-')}</td>
              <td>{escape(linked_devices_text or '-')}</td>
              <td>{escape(summary_line or '-')}</td>
              <td>{escape(recommended_action)}</td>
              <td>
                <div class="actions">
                  <a class="btn" href="/ui/pet/{escape(pet_id)}">详情</a>
                  <a class="btn" href="/ui/memory?pet_id={escape(pet_id)}">记忆</a>
                  <a class="btn" href="/ui/chat?pet_id={escape(pet_id)}">对话</a>
                </div>
                <div class="actions">
                  <a class="btn" href="/ui/action/pet-event?pet_id={escape(pet_id)}&kind=feed&text=manual+feed+from+pets+page">喂食</a>
                  <a class="btn" href="/ui/action/pet-event?pet_id={escape(pet_id)}&kind=play&text=manual+play+from+pets+page">玩耍</a>
                  <a class="btn" href="/ui/action/pet-event?pet_id={escape(pet_id)}&kind=praise&text=manual+praise+from+pets+page">表扬</a>
                </div>
              </td>
            </tr>
            '''

def render_pets_page(
    *,
    rows_html: str,
    matched: int,
    healthy_count: int,
    warning_count: int,
    action_needed_count: int,
    species_options_html: str,
    growth_stage_options_html: str,
    species_id: str,
    growth_stage: str,
    mood: str,
    device_scope: str,
    problem: str,
    sort_by: str,
    keyword: Optional[str],
    notice_html: NoticeFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    table_html = (
        '<table class="kv"><thead><tr>'
        '<th>pet</th><th>species</th><th>theme</th><th>growth_stage</th><th>mood</th><th>level</th><th>energy</th><th>hunger</th><th>affection</th><th>primary_device</th><th>linked_devices</th><th>summary</th><th>recommended_action</th><th>actions</th>'
        '</tr></thead><tbody>' + rows_html + '</tbody></table>'
        if rows_html else '<div class="muted">当前筛选条件下没有宠物</div>'
    )
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">宠物管理</h1>
      <div class="meta">集中查看宠物档案、成长状态、绑定设备与快捷运营操作，作为后台管理页的宠物主表。</div>
      <div class="statline">
        <span class="pill">matched: {matched}</span>
        <span class="pill">healthy: {healthy_count}</span>
        <span class="pill">warning/other: {warning_count}</span>
        <span class="pill">action-needed: {action_needed_count}</span>
      </div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>筛选条件</h2>
        <form method="get" action="/ui/pets">
          <label>species_id
            <select name="species_id">
              <option value="all"{' selected' if species_id == 'all' else ''}>all</option>
              {species_options_html}
            </select>
          </label>
          <label>growth_stage
            <select name="growth_stage">
              <option value="all"{' selected' if growth_stage == 'all' else ''}>all</option>
              {growth_stage_options_html}
            </select>
          </label>
          <label>mood
            <select name="mood">
              <option value="all"{' selected' if mood == 'all' else ''}>all</option>
              <option value="neutral"{' selected' if mood == 'neutral' else ''}>neutral</option>
              <option value="happy"{' selected' if mood == 'happy' else ''}>happy</option>
              <option value="excited"{' selected' if mood == 'excited' else ''}>excited</option>
              <option value="sleepy"{' selected' if mood == 'sleepy' else ''}>sleepy</option>
              <option value="hungry"{' selected' if mood == 'hungry' else ''}>hungry</option>
              <option value="sad"{' selected' if mood == 'sad' else ''}>sad</option>
            </select>
          </label>
          <label>device_scope
            <select name="device_scope">
              <option value="all"{' selected' if device_scope == 'all' else ''}>all</option>
              <option value="with-device"{' selected' if device_scope == 'with-device' else ''}>with device</option>
              <option value="without-device"{' selected' if device_scope == 'without-device' else ''}>without device</option>
              <option value="offline-device"{' selected' if device_scope == 'offline-device' else ''}>has offline device</option>
              <option value="multi-device"{' selected' if device_scope == 'multi-device' else ''}>multi-device</option>
            </select>
          </label>
          <label>problem_view
            <select name="problem">
              <option value="all"{' selected' if problem == 'all' else ''}>all</option>
              <option value="problem"{' selected' if problem == 'problem' else ''}>problem only</option>
              <option value="action-needed"{' selected' if problem == 'action-needed' else ''}>action-needed</option>
              <option value="offline"{' selected' if problem == 'offline' else ''}>offline-device only</option>
              <option value="missing-device"{' selected' if problem == 'missing-device' else ''}>missing-device only</option>
              <option value="conflict"{' selected' if problem == 'conflict' else ''}>conflict only</option>
              <option value="no-device"{' selected' if problem == 'no-device' else ''}>no-device only</option>
              <option value="hungry"{' selected' if problem == 'hungry' else ''}>hungry only</option>
              <option value="low-energy"{' selected' if problem == 'low-energy' else ''}>low-energy only</option>
            </select>
          </label>
          <label>sort_by
            <select name="sort_by">
              <option value="pet_id"{' selected' if sort_by == 'pet_id' else ''}>pet_id</option>
              <option value="level"{' selected' if sort_by == 'level' else ''}>level desc</option>
              <option value="energy"{' selected' if sort_by == 'energy' else ''}>energy asc</option>
              <option value="hunger"{' selected' if sort_by == 'hunger' else ''}>hunger desc</option>
              <option value="mood"{' selected' if sort_by == 'mood' else ''}>mood</option>
              <option value="action"{' selected' if sort_by == 'action' else ''}>recommended_action</option>
            </select>
          </label>
          <label>keyword
            <input name="keyword" value="{escape(keyword or '')}" placeholder="pet_id / name / owner / device / growth_stage">
          </label>
          <button type="submit">应用筛选</button>
        </form>
      </div>
      <div class="card">
        <h2>批量操作</h2>
        <form method="post" action="/ui/action/bulk-pet-op">
          <label>pet_ids（换行或逗号分隔）
            <textarea name="pet_ids" rows="6" placeholder="pet-001,pet-002"></textarea>
          </label>
          <label>event_kind
            <select name="event_kind">
              <option value="feed">feed</option>
              <option value="play">play</option>
              <option value="praise">praise</option>
              <option value="sleep">sleep</option>
              <option value="link-device">link-device</option>
              <option value="link-device-primary">link-device-primary</option>
              <option value="unlink-device">unlink-device</option>
              <option value="unlink-all-devices">unlink-all-devices</option>
              <option value="set-primary-device">set-primary-device</option>
              <option value="assign-owner">assign-owner</option>
              <option value="clear-owner">clear-owner</option>
            </select>
          </label>
          <label>device_id（设备类批量操作可用）
            <input name="device_id" value="" placeholder="dev-001">
          </label>
          <label>owner_id（assign-owner 可用）
            <input name="owner_id" value="owner-demo" placeholder="owner-demo">
          </label>
          <label>event_text
            <input name="event_text" value="manual bulk pet event from pets page">
          </label>
          <button type="submit">执行批量宠物操作</button>
        </form>
      </div>
      <div class="card">
        <h2>快捷操作</h2>
        <div class="list">
          <div class="item"><a href="/ui/actions">打开联调操作页</a></div>
          <div class="item"><a href="/ui/pets?mood=hungry">只看 hungry 宠物</a></div>
          <div class="item"><a href="/ui/pets?problem=problem">只看问题宠物</a></div>
          <div class="item"><a href="/ui/pets?problem=no-device">只看未绑定设备宠物</a></div>
          <div class="item"><a href="/ui/pets?problem=low-energy">只看低能量宠物</a></div>
          <div class="item"><a href="/ui/events?kind=pet&limit=100">查看宠物事件流</a></div>
          <div class="item"><a href="/ui/memory">打开记忆中心</a></div>
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <h2>宠物列表</h2>
      {table_html}
    </div>
    '''
    return page_shell("Pet Management", body)

def render_pet_detail_page(
    *,
    pet_id: str,
    pet_name: str,
    species_id: str,
    theme_id: str,
    mood: str,
    level_value: int,
    basic_rows: List[Tuple[str, object]],
    sync_rows: List[Tuple[str, object]],
    growth_rows: List[Tuple[str, object]],
    preview_rows: List[Tuple[str, object]],
    device_manage_html: str,
    events_html: str,
    device_options_html: str,
    form_defaults: Dict[str, object],
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0;\">宠物详情：{escape(pet_name)} <span class=\"meta\">({escape(pet_id)})</span></h1>
      <div class=\"statline\">
        <span class=\"pill\">species {escape(species_id)}</span>
        <span class=\"pill\">theme {escape(theme_id)}</span>
        <span class=\"pill\">mood {escape(mood)}</span>
        <span class=\"pill\">level {level_value}</span>
      </div>
      <div class=\"actions\">
        <a class=\"btn\" href=\"/ui/action/pet-event?pet_id={escape(pet_id)}&kind=play&text=manual+play+from+ui\">记play</a>
        <a class=\"btn\" href=\"/ui/action/pet-event?pet_id={escape(pet_id)}&kind=feed&text=manual+feed+from+ui\">记feed</a>
        <a class=\"btn\" href=\"/ui/action/pet-event?pet_id={escape(pet_id)}&kind=praise&text=manual+praise+from+ui\">记praise</a>
        <a class=\"btn\" href=\"/ui/memory?pet_id={escape(pet_id)}\">记忆中心</a>
        <a class=\"btn\" href=\"/ui/chat?pet_id={escape(pet_id)}\">对话调试</a>
        <a class=\"btn\" href=\"/ui/actions\">打开操作面板</a>
      </div>
    </div>
    <div class=\"grid\">
      <div class=\"card\"><h2>基础属性</h2>{kv_table(basic_rows)}</div>
      <div class=\"card\"><h2>同步状态</h2>{kv_table(sync_rows)}</div>
    </div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>成长摘要</h2>{kv_table(growth_rows)}</div>
      <div class=\"card\"><h2>预览信息</h2>{kv_table(preview_rows)}</div>
    </div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>编辑宠物</h2><form method=\"post\" action=\"/ui/action/update-pet\"><input type=\"hidden\" name=\"pet_id\" value=\"{escape(pet_id)}\"><label>name<input name=\"name\" value=\"{escape(str(form_defaults.get('name') or ''))}\"></label><label>species_id<input name=\"species_id\" value=\"{escape(str(form_defaults.get('species_id') or ''))}\"></label><label>theme_id<input name=\"theme_id\" value=\"{escape(str(form_defaults.get('theme_id') or ''))}\"></label><label>model_route_id<input name=\"model_route_id\" value=\"{escape(str(form_defaults.get('model_route_id') or ''))}\"></label><label>model_provider<input name=\"model_provider\" value=\"{escape(str(form_defaults.get('model_provider') or ''))}\"></label><label>model_name<input name=\"model_name\" value=\"{escape(str(form_defaults.get('model_name') or ''))}\"></label><label>growth_stage<input name=\"growth_stage\" value=\"{escape(str(form_defaults.get('growth_stage') or ''))}\"></label><label>mood<input name=\"mood\" value=\"{escape(str(form_defaults.get('mood') or ''))}\"></label><label>level<input name=\"level\" type=\"number\" value=\"{escape(str(form_defaults.get('level') or 0))}\"></label><label>exp<input name=\"exp\" type=\"number\" value=\"{escape(str(form_defaults.get('exp') or 0))}\"></label><label>energy<input name=\"energy\" type=\"number\" value=\"{escape(str(form_defaults.get('energy') or 0))}\"></label><label>hunger<input name=\"hunger\" type=\"number\" value=\"{escape(str(form_defaults.get('hunger') or 0))}\"></label><label>affection<input name=\"affection\" type=\"number\" value=\"{escape(str(form_defaults.get('affection') or 0))}\"></label><label>owner_id<input name=\"owner_id\" value=\"{escape(str(form_defaults.get('owner_id') or ''))}\"></label><label>device_id<input name=\"device_id\" value=\"{escape(str(form_defaults.get('device_id') or ''))}\"></label><button type=\"submit\">保存宠物配置</button></form></div>
      <div class=\"card\"><h2>快捷联动</h2><div class=\"list\"><div class=\"item\"><a href=\"/api/pet/{escape(pet_id)}\">宠物详情 JSON</a></div><div class=\"item\"><a href=\"/api/pet/{escape(pet_id)}/sync\">同步摘要 JSON</a></div><div class=\"item\"><a href=\"/api/pet/{escape(pet_id)}/growth\">成长摘要 JSON</a></div><div class=\"item\"><a href=\"/api/memory/{escape(pet_id)}\">记忆 JSON</a></div><div class=\"item\"><a href=\"/ui/memory?pet_id={escape(pet_id)}\">打开记忆中心</a></div><div class=\"item\"><a href=\"/ui/chat?pet_id={escape(pet_id)}\">打开对话调试</a></div></div></div>
    </div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>已关联设备</h2><div class=\"list\">{device_manage_html or '<div class="muted">当前没有已关联设备</div>'}</div></div>
      <div class=\"card\"><h2>快速绑定新设备</h2><form method=\"post\" action=\"/ui/action/link-device\"><input type=\"hidden\" name=\"pet_id\" value=\"{escape(pet_id)}\"><label>device_id<select name=\"device_id\">{device_options_html}</select></label><label><input type=\"checkbox\" name=\"make_primary\" value=\"1\" style=\"width:auto;margin-right:8px;\">绑定后设为主设备</label><button type=\"submit\">绑定设备</button></form></div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\"><h2>最近宠物事件</h2><div class=\"list\">{events_html or '<div class="muted">暂无宠物事件</div>'}</div></div>
    """
    return page_shell(f"Pet {pet_id}", body)

