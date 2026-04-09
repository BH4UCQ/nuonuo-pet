from __future__ import annotations

from html import escape
from typing import Any, Callable, Optional, Dict

from fastapi.responses import HTMLResponse

from .ui_page_common import KvTableFn, NoticeFn, PageShellFn, StatusBadgeFn


def render_dashboard_device_card(
    *,
    device_id: str,
    hardware_model: str,
    firmware_version: str,
    owner_id: Optional[str],
    pet_id: Optional[str],
    connection_state: Optional[str],
    bound: bool,
    summary_line: str,
    event_count: int,
    status_badge: StatusBadgeFn,
) -> str:
    return f"""
            <div class=\"item\">
              <div class=\"item-title\">
                <div><strong><a href=\"/ui/device/{escape(device_id)}\">{escape(device_id)}</a></strong></div>
                <div>{status_badge(connection_state)}{status_badge('bound' if bound else 'unbound')}</div>
              </div>
              <div class=\"mini\">{escape(hardware_model)} · FW {escape(firmware_version)}</div>
              <div class=\"statline\">
                <span class=\"pill\">owner: {escape(owner_id or '-')}</span>
                <span class=\"pill\">events: {event_count}</span>
                <span class=\"pill\">pet: {escape(pet_id or '-')}</span>
              </div>
              <p class=\"mini\">{escape(summary_line)}</p>
              <div class=\"actions\">
                <a class=\"btn\" href=\"/ui/device/{escape(device_id)}\">查看详情</a>
                <a class=\"btn\" href=\"/ui/action/heartbeat?device_id={escape(device_id)}\">发心跳</a>
                <a class=\"btn\" href=\"/ui/action/device-event?device_id={escape(device_id)}&kind=resume&message=manual+resume\">记一条resume</a>
              </div>
            </div>
            """

def render_dashboard_pet_card(
    *,
    pet_id: str,
    pet_name: str,
    species_id: str,
    theme_id: str,
    health_level: Optional[str],
    mood: Optional[str],
    level: int,
    energy: int,
    hunger: int,
    affection: int,
    summary_line: str,
    status_badge: StatusBadgeFn,
) -> str:
    return f"""
            <div class=\"item\">
              <div class=\"item-title\">
                <div><strong><a href=\"/ui/pet/{escape(pet_id)}\">{escape(pet_name)}</a></strong> <span class=\"mini\">({escape(pet_id)})</span></div>
                <div>{status_badge(health_level)}{status_badge(mood)}</div>
              </div>
              <div class=\"mini\">species: {escape(species_id)} · theme: {escape(theme_id)}</div>
              <div class=\"statline\">
                <span class=\"pill\">level: {level}</span>
                <span class=\"pill\">energy: {energy}</span>
                <span class=\"pill\">hunger: {hunger}</span>
                <span class=\"pill\">affection: {affection}</span>
              </div>
              <p class=\"mini\">{escape(summary_line)}</p>
              <div class=\"actions\">
                <a class=\"btn\" href=\"/ui/pet/{escape(pet_id)}\">查看详情</a>
                <a class=\"btn\" href=\"/ui/action/pet-event?pet_id={escape(pet_id)}&kind=play&text=manual+play+from+ui\">记一次play</a>
                <a class=\"btn\" href=\"/api/pet/{escape(pet_id)}/sync\">看同步JSON</a>
              </div>
            </div>
            """

def render_recent_event_card(*, created_at: str, source: str, kind: str, message: Optional[str]) -> str:
    return (
        f'<div class="item"><div class="item-title"><strong>{escape(kind)}</strong>'
        f'<span class="mini">{escape(source)}</span></div><div class="mini">{escape(created_at)}</div>'
        f'<div>{escape(message or "")}</div></div>'
    )

def render_dashboard_page(
    *,
    snapshot: Dict[str, Any],
    device_cards_html: str,
    pet_cards_html: str,
    recent_events_html: str,
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0 0 8px 0;\">后端调试总览</h1>
      <div class=\"meta\">用来直观看设备、宠物、事件和当前后端状态。</div>
      <div class=\"statline\">
        <span class=\"pill\">version: {escape(str(snapshot['protocol_version']))}</span>
        <span class=\"pill\">time: {escape(str(snapshot['server_time']))}</span>
        <span class=\"pill\">devices: {snapshot['device_count']}</span>
        <span class=\"pill\">pets: {snapshot['pet_count']}</span>
        <span class=\"pill\">online: {snapshot['online_device_count']}</span>
        <span class=\"pill\">offline: {snapshot['offline_device_count']}</span>
      </div>
      <div class=\"actions\">
        <a class=\"btn\" href=\"/ui/actions\">打开快捷操作面板</a>
        <a class=\"btn\" href=\"/ui/events\">查看事件流</a>
        <a class=\"btn\" href=\"/ui\">手动刷新</a>
      </div>
    </div>
    <div class=\"grid\">
      <div class=\"card\">
        <h2>服务状态</h2>
        {kv_table([
            ('status', 'ok'),
            ('server_time', snapshot['server_time']),
            ('protocol_version', snapshot['protocol_version']),
            ('device_count', snapshot['device_count']),
            ('pet_count', snapshot['pet_count']),
            ('bound_device_count', snapshot['bound_device_count']),
            ('device_event_count', snapshot['device_event_count']),
            ('pet_event_count', snapshot['pet_event_count']),
            ('memory_count', snapshot['memory_count']),
            ('resource_pack_count', snapshot['resource_pack_count']),
        ])}
      </div>
      <div class=\"card\">
        <h2>快捷入口</h2>
        <div class=\"list\">
          <div class=\"item\"><a href=\"/ui/actions\">联调操作页</a></div>
          <div class=\"item\"><a href=\"/ui/system\">系统状态 / 联调验收页</a></div>
          <div class=\"item\"><a href=\"/ui/events\">事件流 / 日志页</a></div>
          <div class=\"item\"><a href=\"/docs\">Swagger API 文档</a></div>
          <div class=\"item\"><a href=\"/api/species/templates\">物种模板 JSON</a></div>
          <div class=\"item\"><a href=\"/api/theme/compatibility\">主题兼容性 JSON</a></div>
          <div class=\"item\"><a href=\"/api/resource/packs\">资源包 JSON</a></div>
          <div class=\"item\"><a href=\"/api/assets/manifest\">资产清单 JSON</a></div>
        </div>
      </div>
    </div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>设备列表</h2><div class=\"list\">{device_cards_html or '<div class="muted">暂无设备</div>'}</div></div>
      <div class=\"card\"><h2>宠物列表</h2><div class=\"list\">{pet_cards_html or '<div class="muted">暂无宠物</div>'}</div></div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\">
      <h2>最近事件</h2>
      <div class=\"actions\"><a class=\"btn\" href=\"/ui/events\">打开完整事件流</a></div>
      <div class=\"list\">{recent_events_html or '<div class="muted">暂无事件</div>'}</div>
    </div>
    """
    return page_shell("nuonuo-pet backend UI", body)

def render_system_page(
    *,
    snapshot: Dict[str, Any],
    warning_pets: int,
    online_ok_devices: int,
    offline_or_warn_devices: int,
    healthy_pets: int,
    check_cards_html: str,
    device_cards_html: str,
    pet_cards_html: str,
    recent_cards_html: str,
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0 0 8px 0;\">系统状态 / 联调验收页</h1>
      <div class=\"meta\">把当前是否“接近完成”最关键的联调信息集中到一页里，方便快速判断还差哪一环。</div>
      <div class=\"statline\">
        <span class=\"pill\">devices: {snapshot['device_count']}</span>
        <span class=\"pill\">pets: {snapshot['pet_count']}</span>
        <span class=\"pill\">online devices: {snapshot['online_device_count']}</span>
        <span class=\"pill\">bound devices: {snapshot['bound_device_count']}</span>
        <span class=\"pill\">pet warnings: {warning_pets}</span>
        <span class=\"pill\">time: {escape(str(snapshot['server_time']))}</span>
      </div>
      <div class=\"actions\">
        <a class=\"btn\" href=\"/ui/actions\">去做联调操作</a>
        <a class=\"btn\" href=\"/ui/events\">查看事件流</a>
        <a class=\"btn\" href=\"/ui/system\">刷新本页</a>
      </div>
    </div>
    <div class=\"grid\">
      <div class=\"card\">
        <h2>完成度检查</h2>
        <div class=\"list\">{check_cards_html}</div>
      </div>
      <div class=\"card\">
        <h2>当前概况</h2>
        {kv_table([
            ('server_time', snapshot['server_time']),
            ('device_count', snapshot['device_count']),
            ('pet_count', snapshot['pet_count']),
            ('online_device_count', snapshot['online_device_count']),
            ('offline_device_count', snapshot['offline_device_count']),
            ('bound_device_count', snapshot['bound_device_count']),
            ('device_event_count', snapshot['device_event_count']),
            ('pet_event_count', snapshot['pet_event_count']),
            ('memory_count', snapshot['memory_count']),
            ('theme_pack_count', snapshot['theme_pack_count']),
            ('species_template_count', snapshot['species_template_count']),
        ])}
      </div>
    </div>
    <div class=\"grid\" style=\"margin-top:16px;\">
      <div class=\"card\"><h2>设备联调状态</h2><div class=\"mini\" style=\"margin-bottom:10px;\">状态较健康设备：{online_ok_devices}；需关注设备：{offline_or_warn_devices}</div><div class=\"list\">{device_cards_html or '<div class="muted">暂无设备</div>'}</div></div>
      <div class=\"card\"><h2>宠物同步状态</h2><div class=\"mini\" style=\"margin-bottom:10px;\">健康宠物：{healthy_pets}；需关注宠物：{warning_pets}</div><div class=\"list\">{pet_cards_html or '<div class="muted">暂无宠物</div>'}</div></div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\">
      <h2>最近重点事件</h2>
      <div class=\"actions\"><a class=\"btn\" href=\"/ui/events\">打开完整事件流</a></div>
      <div class=\"list\">{recent_cards_html or '<div class="muted">暂无事件</div>'}</div>
    </div>
    """
    return page_shell("System Status", body)

