from __future__ import annotations
from typing import Optional, List, Dict, Tuple

from html import escape
import json
from urllib.parse import urlencode

from fastapi.responses import HTMLResponse, RedirectResponse


def status_badge_class(status: Optional[str]) -> str:
    value = (status or "unknown").lower()
    if value in {"online", "paired", "bound", "normal", "ok", "healthy"}:
        return "ok"
    if value in {"offline", "critical", "error"}:
        return "bad"
    if value in {"warning", "degraded", "unbound", "idle", "unknown"}:
        return "warn"
    return "muted"


def status_badge(label: Optional[str]) -> str:
    text = escape(label or "unknown")
    return f'<span class="badge {status_badge_class(label)}">{text}</span>'


def kv_table(rows: List[Tuple[str, object]]) -> str:
    rendered = []
    for key, value in rows:
        if isinstance(value, (dict, list)):
            value_html = f"<pre>{escape(json.dumps(value, ensure_ascii=False, indent=2))}</pre>"
        elif value is None:
            value_html = '<span class="muted">-</span>'
        else:
            value_html = escape(str(value))
        rendered.append(f"<tr><th>{escape(str(key))}</th><td>{value_html}</td></tr>")
    return '<table class="kv">' + ''.join(rendered) + '</table>'


def page_shell(title: str, body: str) -> HTMLResponse:
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(title)}</title>
  <meta http-equiv=\"refresh\" content=\"15\" />
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0b1020; color: #e8eefc; }}
    a {{ color: #7cc8ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
    .topbar {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
    .nav {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .hero {{ background: linear-gradient(135deg, #15203a, #10182d); border: 1px solid #253558; border-radius: 18px; padding: 20px; margin-bottom: 18px; box-shadow: 0 8px 24px rgba(0,0,0,.25); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .card {{ background: #10182d; border: 1px solid #253558; border-radius: 16px; padding: 16px; box-shadow: 0 8px 20px rgba(0,0,0,.18); }}
    .card h2, .card h3 {{ margin-top: 0; }}
    .meta {{ color: #9fb0d1; font-size: 14px; }}
    .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-right: 6px; }}
    .badge.ok {{ background: #183c2b; color: #7ef0b2; }}
    .badge.warn {{ background: #473717; color: #ffd27a; }}
    .badge.bad {{ background: #4d2020; color: #ff9696; }}
    .badge.muted {{ background: #2a3550; color: #c3d0ea; }}
    .list {{ display: grid; gap: 10px; }}
    .item {{ background: #0d1426; border: 1px solid #1e2c49; border-radius: 12px; padding: 12px; }}
    .item-title {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }}
    .mini {{ font-size: 13px; color: #97a9c8; }}
    .kv {{ width: 100%; border-collapse: collapse; }}
    .kv th, .kv td {{ text-align: left; vertical-align: top; padding: 8px 10px; border-top: 1px solid #22304f; }}
    .kv th {{ width: 160px; color: #9fb0d1; font-weight: 600; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; color: #d7e3fb; }}
    .muted {{ color: #8ea1c5; }}
    .statline {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }}
    .pill {{ background: #16213b; border: 1px solid #2a3b62; border-radius: 999px; padding: 6px 10px; font-size: 13px; color: #cdd9f2; }}
    .notice {{ margin: 0 0 16px 0; padding: 12px 14px; border-radius: 12px; border: 1px solid #2a3b62; background: #13203a; color: #d8e7ff; }}
    .notice.ok {{ border-color: #27573d; background: #13281e; color: #bff3d4; }}
    .notice.warn {{ border-color: #6a5520; background: #2d2410; color: #ffe2a0; }}
    .actions {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
    .btn {{ display: inline-block; border: 1px solid #355189; background: #17305d; color: #eaf2ff; border-radius: 10px; padding: 8px 12px; font-size: 14px; }}
    .btn:hover {{ text-decoration: none; background: #21407b; }}
    form.inline {{ display: inline; }}
    input, select, textarea {{ width: 100%; box-sizing: border-box; background: #0d1426; color: #e8eefc; border: 1px solid #2a3b62; border-radius: 10px; padding: 10px; margin-top: 6px; }}
    label {{ display: block; margin: 10px 0; color: #cbd9f6; font-size: 14px; }}
    button {{ background: #1e4ba3; color: white; border: none; border-radius: 10px; padding: 10px 14px; cursor: pointer; }}
    button:hover {{ background: #2860cf; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"topbar\">
      <div>
        <strong>nuonuo-pet backend UI</strong>
        <div class=\"meta\">调试后台 / 一体化内嵌页面 / 15 秒自动刷新</div>
      </div>
      <div class=\"nav\">
        <a href="/ui">总览</a>
        <a href="/ui/devices">设备管理</a>
        <a href="/ui/pets">宠物管理</a>
        <a href="/ui/system">系统状态</a>
        <a href="/ui/events">事件流</a>
        <a href="/ui/actions">快捷操作</a>
        <a href="/ui/config">配置中心</a>
        <a href="/ui/resources">资源中心</a>
        <a href="/ui/memory">记忆中心</a>
        <a href="/ui/chat">对话调试</a>
        <a href="/ui/assets">资产清单</a>
        <a href="/docs">Swagger</a>
        <a href="/redoc">ReDoc</a>
        <a href="/health">Health JSON</a>
      </div>
    </div>
    {body}
  </div>
</body>
</html>"""
    return HTMLResponse(content=html)


def notice_html(message: Optional[str], level: str = "ok") -> str:
    if not message:
        return ""
    level = level if level in {"ok", "warn"} else "ok"
    return f'<div class="notice {level}">{escape(message)}</div>'


def options_html(items: List[str], selected: Optional[str] = None) -> str:
    rendered = ['<option value="">(none)</option>']
    for item in items:
        sel = ' selected' if selected == item else ''
        rendered.append(f'<option value="{escape(item)}"{sel}>{escape(item)}</option>')
    return ''.join(rendered)


def render_rows(rows: List[Dict[str, object]], columns: List[Tuple[str, str]]) -> str:
    if not rows:
        return '<div class="muted">暂无数据</div>'
    header = ''.join(f'<th>{escape(title)}</th>' for title, _ in columns)
    body_rows: List[str] = []
    for row in rows:
        cells: List[str] = []
        for _, key in columns:
            value = row.get(key)
            if isinstance(value, (dict, list)):
                rendered = f"<pre>{escape(json.dumps(value, ensure_ascii=False, indent=2))}</pre>"
            elif value is None or value == "":
                rendered = '<span class="muted">-</span>'
            else:
                rendered = escape(str(value))
            cells.append(f'<td>{rendered}</td>')
        body_rows.append('<tr>' + ''.join(cells) + '</tr>')
    return f'<table class="kv"><thead><tr>{header}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'


def textarea_json(value: object) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def parse_json_object(text: Optional[str] = None, empty_default: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    fallback = empty_default or {}
    raw = (text or "").strip()
    if not raw:
        return dict(fallback)
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("JSON must be an object")
    return parsed


def redirect_with_message(path: str, message: str, level: str = "ok") -> RedirectResponse:
    query = urlencode({"msg": message, "level": level})
    return RedirectResponse(url=f"{path}?{query}", status_code=303)


def parse_bulk_ids(text: Optional[str]) -> List[str]:
    raw = (text or "").replace(',', '\n')
    seen: set[str] = set()
    items: List[str] = []
    for part in raw.splitlines():
        value = part.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        items.append(value)
    return items
