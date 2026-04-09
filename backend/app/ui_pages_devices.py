from __future__ import annotations
from typing import Optional, List, Tuple

from html import escape

from fastapi.responses import HTMLResponse

from .ui_page_common import KvTableFn, NoticeFn, PageShellFn, StatusBadgeFn


def render_bind_request_page(
    *,
    device_id: str,
    bind_code: str,
    expires_at: object,
    expires_in_seconds: object,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
) -> HTMLResponse:
    body = f"""
    <div class=\"hero\">
      <h1 style=\"margin:0;\">绑定码已生成</h1>
      <div class=\"meta\">可以直接拿去联调绑定流程。</div>
    </div>
    <div class=\"card\">
      {kv_table([('device_id', device_id), ('bind_code', bind_code), ('expires_at', expires_at), ('expires_in_seconds', expires_in_seconds)])}
      <div class=\"actions\">
        <a class=\"btn\" href=\"/ui/device/{escape(device_id)}\">返回设备详情</a>
        <a class=\"btn\" href=\"/ui/actions\">返回操作页</a>
      </div>
    </div>
    """
    return page_shell(f"Bind Code {device_id}", body)

def render_device_management_row(
    *,
    device_id: str,
    hardware_model: str,
    firmware_version: str,
    state_value: str,
    is_bound: bool,
    owner_id: Optional[str],
    pet_id: Optional[str],
    capabilities_text: str,
    summary_line: str,
    recommended_action: str,
    action_hint: str,
    status_badge: StatusBadgeFn,
) -> str:
    unlink_form = (
        f'''<form method="post" action="/ui/action/unlink-device"><input type="hidden" name="pet_id" value="{escape(pet_id or '')}"><input type="hidden" name="device_id" value="{escape(device_id)}"><button type="submit">从宠物解绑</button></form>'''
        if pet_id
        else ''
    )
    return f'''
            <tr>
              <td><a href="/ui/device/{escape(device_id)}">{escape(device_id)}</a></td>
              <td>{escape(hardware_model)}</td>
              <td>{escape(firmware_version)}</td>
              <td>{status_badge(state_value)}</td>
              <td>{status_badge('bound' if is_bound else 'unbound')}</td>
              <td>{escape(owner_id or '-')}</td>
              <td>{escape(pet_id or '-')}</td>
              <td>{escape(capabilities_text or '-')}</td>
              <td>{escape(summary_line or '-')}</td>
              <td>{escape(recommended_action)}</td>
              <td>
                <div class="actions">
                  <a class="btn" href="/ui/device/{escape(device_id)}">详情</a>
                  <a class="btn" href="/ui/action/heartbeat?device_id={escape(device_id)}">心跳</a>
                  <a class="btn" href="/ui/action/bind-request?device_id={escape(device_id)}">绑定码</a>
                  <a class="btn" href="/ui/action/device-event?device_id={escape(device_id)}&kind=resume&message=manual+resume+from+devices+page">恢复</a>
                </div>
                <div class="actions">
                  <a class="btn" href="/ui/action/device-event?device_id={escape(device_id)}&kind=offline&message=manual+offline+from+devices+page">置离线</a>
                  <a class="btn" href="/ui/action/device-event?device_id={escape(device_id)}&kind=attention&message={escape(action_hint or 'manual+attention')}" title="写入一条需要处理的设备事件">标记待处理</a>
                </div>
                {unlink_form}
              </td>
            </tr>
            '''

def render_devices_page(
    *,
    rows_html: str,
    matched: int,
    online_count: int,
    offline_count: int,
    bound_count: int,
    unbound_count: int,
    conflict_count: int,
    action_needed_count: int,
    capability_options_html: str,
    connection_state: str,
    bound: str,
    capability: str,
    owner_scope: str,
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
        '<th>device_id</th><th>hardware</th><th>firmware</th><th>connection</th><th>binding</th><th>owner</th><th>pet</th><th>capabilities</th><th>summary</th><th>recommended_action</th><th>actions</th>'
        '</tr></thead><tbody>' + rows_html + '</tbody></table>'
        if rows_html else '<div class="muted">当前筛选条件下没有设备</div>'
    )
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">设备管理</h1>
      <div class="meta">集中查看设备状态、绑定情况、能力标签与快捷操作，作为后台管理页的设备主表。</div>
      <div class="statline">
        <span class="pill">matched: {matched}</span>
        <span class="pill">online: {online_count}</span>
        <span class="pill">offline/other: {offline_count}</span>
        <span class="pill">bound: {bound_count}</span>
        <span class="pill">unbound: {unbound_count}</span>
        <span class="pill">conflicted: {conflict_count}</span>
        <span class="pill">action-needed: {action_needed_count}</span>
      </div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>筛选条件</h2>
        <form method="get" action="/ui/devices">
          <label>connection_state
            <select name="connection_state">
              <option value="all"{' selected' if connection_state == 'all' else ''}>all</option>
              <option value="online"{' selected' if connection_state == 'online' else ''}>online</option>
              <option value="offline"{' selected' if connection_state == 'offline' else ''}>offline</option>
              <option value="unknown"{' selected' if connection_state == 'unknown' else ''}>unknown</option>
            </select>
          </label>
          <label>bound
            <select name="bound">
              <option value="all"{' selected' if bound == 'all' else ''}>all</option>
              <option value="bound"{' selected' if bound == 'bound' else ''}>bound</option>
              <option value="unbound"{' selected' if bound == 'unbound' else ''}>unbound</option>
            </select>
          </label>
          <label>capability
            <select name="capability">
              <option value="all"{' selected' if capability == 'all' else ''}>all</option>
              {capability_options_html}
            </select>
          </label>
          <label>owner_scope
            <select name="owner_scope">
              <option value="all"{' selected' if owner_scope == 'all' else ''}>all</option>
              <option value="with-owner"{' selected' if owner_scope == 'with-owner' else ''}>with owner</option>
              <option value="without-owner"{' selected' if owner_scope == 'without-owner' else ''}>without owner</option>
              <option value="with-pet"{' selected' if owner_scope == 'with-pet' else ''}>with pet</option>
              <option value="without-pet"{' selected' if owner_scope == 'without-pet' else ''}>without pet</option>
            </select>
          </label>
          <label>problem_view
            <select name="problem">
              <option value="all"{' selected' if problem == 'all' else ''}>all</option>
              <option value="problem"{' selected' if problem == 'problem' else ''}>problem only</option>
              <option value="action-needed"{' selected' if problem == 'action-needed' else ''}>action-needed</option>
              <option value="offline"{' selected' if problem == 'offline' else ''}>offline only</option>
              <option value="conflict"{' selected' if problem == 'conflict' else ''}>conflict only</option>
              <option value="unbound"{' selected' if problem == 'unbound' else ''}>unbound only</option>
            </select>
          </label>
          <label>sort_by
            <select name="sort_by">
              <option value="device_id"{' selected' if sort_by == 'device_id' else ''}>device_id</option>
              <option value="state"{' selected' if sort_by == 'state' else ''}>state</option>
              <option value="action"{' selected' if sort_by == 'action' else ''}>recommended_action</option>
              <option value="owner"{' selected' if sort_by == 'owner' else ''}>owner</option>
              <option value="hardware"{' selected' if sort_by == 'hardware' else ''}>hardware</option>
            </select>
          </label>
          <label>keyword
            <input name="keyword" value="{escape(keyword or '')}" placeholder="device_id / owner / capability / pet_id / state_json">
          </label>
          <button type="submit">应用筛选</button>
        </form>
      </div>
      <div class="card">
        <h2>批量操作</h2>
        <form method="post" action="/ui/action/bulk-device-op">
          <label>device_ids（换行或逗号分隔）
            <textarea name="device_ids" rows="6" placeholder="dev-001,dev-002"></textarea>
          </label>
          <label>operation
            <select name="operation">
              <option value="heartbeat">heartbeat</option>
              <option value="resume-event">resume-event</option>
              <option value="offline-event">offline-event</option>
              <option value="attention-event">attention-event</option>
              <option value="assign-owner">assign-owner</option>
              <option value="clear-owner">clear-owner</option>
              <option value="mark-bound">mark-bound</option>
              <option value="mark-unbound">mark-unbound</option>
              <option value="attach-primary-pet">attach-primary-pet</option>
              <option value="unlink-all-pets">unlink-all-pets</option>
            </select>
          </label>
          <label>owner_id（assign-owner / mark-bound 可用）
            <input name="owner_id" value="owner-demo" placeholder="owner-demo">
          </label>
          <label>pet_id（attach-primary-pet 可用）
            <input name="pet_id" value="" placeholder="pet-001">
          </label>
          <label>message / note
            <input name="message" value="manual bulk operation from devices page">
          </label>
          <button type="submit">执行批量设备操作</button>
        </form>
      </div>
      <div class="card">
        <h2>快捷操作</h2>
        <div class="list">
          <div class="item"><a href="/ui/actions">打开联调操作页</a></div>
          <div class="item"><a href="/ui/devices?connection_state=online">只看在线设备</a></div>
          <div class="item"><a href="/ui/devices?bound=unbound">只看未绑定设备</a></div>
          <div class="item"><a href="/ui/devices?problem=problem">只看问题设备</a></div>
          <div class="item"><a href="/ui/devices?problem=action-needed">只看需要处理设备</a></div>
          <div class="item"><a href="/ui/events?kind=device&limit=100">查看设备事件流</a></div>
        </div>
      </div>
    </div>
    <div class="card" style="margin-top:16px;">
      <h2>设备列表</h2>
      {table_html}
    </div>
    '''
    return page_shell("Device Management", body)

def render_device_detail_page(
    *,
    device_id: str,
    hardware_model: str,
    firmware_version: str,
    owner_id: Optional[str],
    owner_pet_id: Optional[str],
    basic_status_rows: List[Tuple[str, object]],
    sync_rows: List[Tuple[str, object]],
    display_rows: List[Tuple[str, object]],
    state_json_text: str,
    default_state_json: str,
    capabilities_csv: str,
    connection_state: str,
    offline_reason: Optional[str],
    bound: bool,
    bind_code: Optional[str],
    events_html: str,
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    owner_pet_link = f'<a class="btn" href="/ui/pet/{escape(owner_pet_id)}">查看所属宠物</a>' if owner_pet_id else ''
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0;\">设备详情：{escape(device_id)}</h1>
      <div class=\"statline\">
        <span class=\"pill\">{escape(hardware_model)}</span>
        <span class=\"pill\">FW {escape(firmware_version)}</span>
        <span class=\"pill\">owner {escape(owner_id or '-')}</span>
      </div>
      <div class=\"actions\">
        <a class=\"btn\" href=\"/ui/action/heartbeat?device_id={escape(device_id)}\">发心跳</a>
        <a class=\"btn\" href=\"/ui/action/device-event?device_id={escape(device_id)}&kind=resume&message=manual+resume\">记resume</a>
        <a class=\"btn\" href=\"/ui/action/device-event?device_id={escape(device_id)}&kind=offline&message=manual+offline\">记offline</a>
        <a class=\"btn\" href=\"/ui/action/bind-request?device_id={escape(device_id)}\">生成绑定码</a>
        {owner_pet_link}
      </div>
    </div>
    <div class=\"grid\">
      <div class=\"card\"><h2>基础状态</h2>{kv_table(basic_status_rows)}</div>
      <div class=\"card\"><h2>同步摘要</h2>{kv_table(sync_rows)}</div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\"><h2>显示配置</h2>{kv_table(display_rows)}</div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>编辑设备</h2><form method=\"post\" action=\"/ui/action/update-device\"><input type=\"hidden\" name=\"device_id\" value=\"{escape(device_id)}\"><label>hardware_model<input name=\"hardware_model\" value=\"{escape(hardware_model)}\"></label><label>firmware_version<input name=\"firmware_version\" value=\"{escape(firmware_version)}\"></label><label>capabilities（逗号分隔）<input name=\"capabilities\" value=\"{escape(capabilities_csv)}\"></label><label>owner_id<input name=\"owner_id\" value=\"{escape(owner_id or '')}\"></label><label>connection_state<input name=\"connection_state\" value=\"{escape(connection_state)}\"></label><label>offline_reason<input name=\"offline_reason\" value=\"{escape(offline_reason or '')}\"></label><label><input type=\"checkbox\" name=\"bound\" value=\"1\" style=\"width:auto;margin-right:8px;\"{' checked' if bound else ''}>已绑定</label><label>state_json<textarea name=\"state_json\" rows=\"8\">{escape(state_json_text)}</textarea></label><button type=\"submit\">保存设备配置</button></form></div>
      <div class=\"card\"><h2>绑定与状态操作</h2><form method=\"post\" action=\"/ui/action/bind-confirm\"><input type=\"hidden\" name=\"device_id\" value=\"{escape(device_id)}\"><label>bind_code<input name=\"bind_code\" value=\"{escape(bind_code or '')}\" placeholder=\"若为空请先生成绑定码\" required></label><label>owner_id<input name=\"owner_id\" value=\"{escape(owner_id or 'owner-demo')}\" required></label><button type=\"submit\">确认绑定</button></form><form method=\"post\" action=\"/ui/action/device-state\" style=\"margin-top:16px;\"><input type=\"hidden\" name=\"device_id\" value=\"{escape(device_id)}\"><label>pet_id<input name=\"pet_id\" value=\"{escape(owner_pet_id or '')}\"></label><label>state_json<textarea name=\"state_json\" rows=\"8\">{escape(default_state_json)}</textarea></label><button type=\"submit\">提交设备状态</button></form></div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\"><h2>最近设备事件</h2><div class=\"list\">{events_html or '<div class="muted">暂无设备事件</div>'}</div></div>
    """
    return page_shell(f"Device {device_id}", body)

