from __future__ import annotations

from html import escape
from typing import Any, Callable, Optional, List, Tuple

from fastapi.responses import HTMLResponse

from .ui_page_common import KvTableFn, NoticeFn, PageShellFn, StatusBadgeFn


def render_events_page(
    *,
    cards_html: str,
    kind: str,
    keyword: Optional[str],
    limit: int,
    matched: int,
    notice_html: NoticeFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0;\">事件流 / 日志页</h1>
      <div class=\"meta\">把设备事件、宠物事件和冲突记录放到一个时间流里，方便联调时快速排查。</div>
      <div class=\"statline\">
        <span class=\"pill\">filter: {escape(kind)}</span>
        <span class=\"pill\">keyword: {escape(keyword or '-')}</span>
        <span class=\"pill\">limit: {limit}</span>
        <span class=\"pill\">matched: {matched}</span>
      </div>
    </div>
    <div class=\"grid\">
      <div class=\"card\">
        <h2>筛选</h2>
        <form method=\"get\" action=\"/ui/events\">
          <label>类型
            <select name=\"kind\">
              <option value=\"all\"{' selected' if kind == 'all' else ''}>all</option>
              <option value=\"device\"{' selected' if kind == 'device' else ''}>device</option>
              <option value=\"pet\"{' selected' if kind == 'pet' else ''}>pet</option>
              <option value=\"conflict\"{' selected' if kind == 'conflict' else ''}>conflict</option>
            </select>
          </label>
          <label>关键词<input name=\"keyword\" value=\"{escape(keyword or '')}\" placeholder=\"比如 offline / bind / pet-demo\"></label>
          <label>条数<input name=\"limit\" type=\"number\" min=\"1\" max=\"200\" value=\"{limit}\"></label>
          <button type=\"submit\">应用筛选</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>快捷过滤</h2>
        <div class=\"actions\">
          <a class=\"btn\" href=\"/ui/events?kind=all&limit=50\">全部</a>
          <a class=\"btn\" href=\"/ui/events?kind=device&limit=50\">设备事件</a>
          <a class=\"btn\" href=\"/ui/events?kind=pet&limit=50\">宠物事件</a>
          <a class=\"btn\" href=\"/ui/events?kind=conflict&limit=50\">冲突记录</a>
          <a class=\"btn\" href=\"/ui/events?kind=all&keyword=offline&limit=50\">搜 offline</a>
          <a class=\"btn\" href=\"/ui/events?kind=all&keyword=bind&limit=50\">搜 bind</a>
        </div>
      </div>
    </div>
    <div class=\"card\" style=\"margin-top:16px;\">
      <h2>时间流</h2>
      <div class=\"list\">{cards_html or '<div class="muted">当前筛选条件下没有事件</div>'}</div>
    </div>
    """
    return page_shell("Event Stream", body)

def render_actions_page(
    *,
    device_ids: List[str],
    pet_ids: List[str],
    options_html: Callable[..., str],
    notice_html: NoticeFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f"""
    {notice_html(msg, level)}
    <div class=\"hero\">
      <h1 style=\"margin:0;\">快捷操作面板</h1>
      <div class=\"meta\">这里放一些联调时常用的轻量操作，省得每次都去 Swagger 里手填。</div>
    </div>
    <div class=\"grid\">
      <div class=\"card\">
        <h2>注册/刷新设备</h2>
        <form method=\"post\" action=\"/ui/action/register-device\">
          <label>device_id<input name=\"device_id\" placeholder=\"dev-001\" required></label>
          <label>hardware_model<input name=\"hardware_model\" value=\"esp32-s3\"></label>
          <label>firmware_version<input name=\"firmware_version\" value=\"0.1.0\"></label>
          <label>capabilities（逗号分隔）<input name=\"capabilities\" value=\"lcd,touch,wifi\"></label>
          <button type=\"submit\">注册设备</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>发送设备心跳</h2>
        <form method=\"get\" action=\"/ui/action/heartbeat\">
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label>note<input name=\"note\" value=\"manual heartbeat from ui\"></label>
          <button type=\"submit\">发送心跳</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>写设备事件</h2>
        <form method=\"get\" action=\"/ui/action/device-event\">
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label>kind<input name=\"kind\" value=\"resume\"></label>
          <label>message<input name=\"message\" value=\"manual device event from ui\"></label>
          <button type=\"submit\">提交设备事件</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>创建宠物</h2>
        <form method=\"post\" action=\"/ui/action/create-pet\">
          <label>pet_id<input name=\"pet_id\" placeholder=\"pet-demo\" required></label>
          <label>name<input name=\"name\" value=\"nuonuo\"></label>
          <label>species_id<input name=\"species_id\" value=\"cat-default\"></label>
          <label>theme_id<input name=\"theme_id\" value=\"cat-gold-day\"></label>
          <label>owner_id<input name=\"owner_id\" value=\"demo-owner\"></label>
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <button type=\"submit\">创建宠物</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>写宠物事件</h2>
        <form method=\"get\" action=\"/ui/action/pet-event\">
          <label>pet_id<select name=\"pet_id\">{options_html(pet_ids, pet_ids[0] if pet_ids else None)}</select></label>
          <label>kind<input name=\"kind\" value=\"play\"></label>
          <label>text<input name=\"text\" value=\"manual pet event from ui\"></label>
          <button type=\"submit\">提交宠物事件</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>申请绑定码</h2>
        <form method=\"get\" action=\"/ui/action/bind-request\">
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <button type=\"submit\">生成绑定码</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>确认设备绑定</h2>
        <form method=\"post\" action=\"/ui/action/bind-confirm\">
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label>bind_code<input name=\"bind_code\" placeholder=\"先生成绑定码再填写\" required></label>
          <label>owner_id<input name=\"owner_id\" value=\"owner-demo\" required></label>
          <button type=\"submit\">确认绑定</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>写设备状态</h2>
        <form method=\"post\" action=\"/ui/action/device-state\">
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label>pet_id<input name=\"pet_id\" placeholder=\"可选\"></label>
          <label>state_json<textarea name=\"state_json\" rows=\"6\">{"battery": 85, "scene": "idle", "offline": false}</textarea></label>
          <button type=\"submit\">提交设备状态</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>给宠物绑定设备</h2>
        <form method=\"post\" action=\"/ui/action/link-device\">
          <label>pet_id<select name=\"pet_id\">{options_html(pet_ids, pet_ids[0] if pet_ids else None)}</select></label>
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label><input type=\"checkbox\" name=\"make_primary\" value=\"1\" style=\"width:auto;margin-right:8px;\">绑定后设为主设备</label>
          <button type=\"submit\">绑定设备</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>切换主设备</h2>
        <form method=\"post\" action=\"/ui/action/set-primary-device\">
          <label>pet_id<select name=\"pet_id\">{options_html(pet_ids, pet_ids[0] if pet_ids else None)}</select></label>
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <button type=\"submit\">设为主设备</button>
        </form>
      </div>
      <div class=\"card\">
        <h2>解绑设备</h2>
        <form method=\"post\" action=\"/ui/action/unlink-device\">
          <label>pet_id<select name=\"pet_id\">{options_html(pet_ids, pet_ids[0] if pet_ids else None)}</select></label>
          <label>device_id<select name=\"device_id\">{options_html(device_ids, device_ids[0] if device_ids else None)}</select></label>
          <label><input type=\"checkbox\" name=\"remove_primary\" value=\"1\" style=\"width:auto;margin-right:8px;\">同时移除主设备指向</label>
          <button type=\"submit\">解绑设备</button>
        </form>
      </div>
    </div>
    """
    return page_shell("UI Actions", body)

def render_chat_page(
    *,
    pet_ids: List[str],
    selected_pet: Optional[str],
    device_id: Optional[str],
    mood: Optional[str],
    pet_snapshot: List[Tuple[str, object]],
    memory_cards_html: str,
    event_cards_html: str,
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
      <h1 style="margin:0;">对话调试</h1>
      <div class="meta">通过后台直接向宠物发消息，观察回复、情绪、动作以及记忆写入情况。</div>
      <div class="statline"><span class="pill">selected_pet: {escape(selected_pet or '-')}</span><span class="pill">device_id: {escape(device_id or '-')}</span><span class="pill">mood: {escape(mood or '-')}</span></div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>发送对话</h2>
        <form method="post" action="/ui/action/chat">
          <label>pet_id<select name="pet_id">{options_html(pet_ids, selected_pet)}</select></label>
          <label>device_id<input name="device_id" value="{escape(device_id or '')}" placeholder="可选"></label>
          <label>mode<select name="mode"><option value="">default</option><option value="comfort">comfort</option><option value="play">play</option></select></label>
          <label>context_json<textarea name="context_json" rows="5">{{}}</textarea></label>
          <label>user_text<textarea name="user_text" rows="6" placeholder="输入测试消息" required></textarea></label>
          <button type="submit">发送</button>
        </form>
      </div>
      <div class="card">
        <h2>当前宠物快照</h2>
        {kv_table(pet_snapshot)}
      </div>
    </div>
    <div class="grid" style="margin-top:16px;">
      <div class="card"><h2>近期记忆</h2><div class="list">{memory_cards_html or '<div class="muted">暂无近期记忆</div>'}</div></div>
      <div class="card"><h2>近期宠物事件</h2><div class="list">{event_cards_html or '<div class="muted">暂无近期事件</div>'}</div></div>
    </div>
    '''
    return page_shell("Chat Debug", body)

def render_memory_page(
    *,
    pet_ids: List[str],
    selected_pet: Optional[str],
    kind: Optional[str],
    keyword: Optional[str],
    limit: int,
    pet_overview_html: str,
    summary_html: str,
    memory_cards_html: str,
    notice_html: NoticeFn,
    options_html: Callable[..., str],
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">记忆中心</h1>
      <div class="meta">集中查看并手动追加宠物记忆，方便调试记忆分层与成长偏好。</div>
      <div class="statline"><span class="pill">pet_count: {len(pet_ids)}</span><span class="pill">selected_pet: {escape(selected_pet or '-')}</span></div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>筛选记忆</h2>
        <form method="get" action="/ui/memory">
          <label>pet_id<select name="pet_id">{options_html(pet_ids, selected_pet)}</select></label>
          <label>kind<select name="kind"><option value=""{' selected' if not kind else ''}>all</option><option value="short"{' selected' if kind == 'short' else ''}>short</option><option value="long"{' selected' if kind == 'long' else ''}>long</option><option value="event"{' selected' if kind == 'event' else ''}>event</option></select></label>
          <label>keyword<input name="keyword" value="{escape(keyword or '')}" placeholder="搜索文本或标签"></label>
          <label>limit<input name="limit" type="number" min="1" max="100" value="{limit}"></label>
          <button type="submit">应用筛选</button>
        </form>
      </div>
      <div class="card">
        <h2>追加记忆</h2>
        <form method="post" action="/ui/action/write-memory">
          <label>pet_id<select name="pet_id">{options_html(pet_ids, selected_pet)}</select></label>
          <label>kind<select name="kind"><option value="short">short</option><option value="long">long</option><option value="event">event</option></select></label>
          <label>tags（逗号分隔）<input name="tags" value="manual,ui"></label>
          <label>text<textarea name="text" rows="5" placeholder="写入一条希望宠物记住的内容" required></textarea></label>
          <button type="submit">写入记忆</button>
        </form>
      </div>
    </div>
    <div class="grid" style="margin-top:16px;">
      <div class="card"><h2>宠物列表</h2><div class="list">{pet_overview_html or '<div class="muted">暂无宠物</div>'}</div></div>
      <div class="card"><h2>记忆概况</h2>{summary_html}</div>
    </div>
    <div class="card" style="margin-top:16px;"><h2>记忆条目</h2><div class="list">{memory_cards_html or '<div class="muted">暂无记忆</div>'}</div></div>
    '''
    return page_shell("Memory Center", body)

def render_assets_page(
    *,
    item_count: int,
    type_count: int,
    server_time_value: object,
    types: List[str],
    groups_html: str,
    notice_html: NoticeFn,
    kv_table: KvTableFn,
    page_shell: PageShellFn,
    msg: Optional[str] = None,
    level: str = "ok",
) -> HTMLResponse:
    body = f'''
    {notice_html(msg, level)}
    <div class="hero">
      <h1 style="margin:0;">资产清单</h1>
      <div class="meta">集中查看对外暴露的 assets manifest，便于后台核对物种、主题和后续资源资产。</div>
      <div class="statline"><span class="pill">item_count: {item_count}</span><span class="pill">type_count: {type_count}</span></div>
    </div>
    <div class="grid">
      <div class="card">
        <h2>统计</h2>
        {kv_table([('server_time', server_time_value), ('item_count', item_count), ('types', types)])}
      </div>
      <div class="card">
        <h2>快捷入口</h2>
        <div class="list">
          <div class="item"><a href="/api/assets/manifest">完整 JSON</a></div>
          <div class="item"><a href="/api/assets/manifest/sample">示例 JSON</a></div>
          <div class="item"><a href="/ui/resources">资源中心</a></div>
        </div>
      </div>
    </div>
    <div class="grid" style="margin-top:16px;">{groups_html or '<div class="card"><div class="muted">暂无资产清单</div></div>'}</div>
    '''
    return page_shell("Assets Manifest", body)

