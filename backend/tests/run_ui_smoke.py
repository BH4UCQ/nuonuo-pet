from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app

client = TestClient(app)
paths = [
    '/ui', '/ui/devices', '/ui/devices?problem=problem', '/ui/devices?owner_scope=without-pet',
    '/ui/pets', '/ui/pets?problem=problem', '/ui/pets?problem=no-device', '/ui/system',
    '/ui/events', '/ui/config', '/ui/resources', '/ui/memory', '/ui/chat', '/ui/assets'
]
for path in paths:
    r = client.get(path)
    if r.status_code != 200 or 'nuonuo-pet backend UI' not in r.text:
        raise SystemExit(f'FAILED {path} status={r.status_code}')

r1 = client.post('/ui/action/bulk-device-op', data={
    'device_ids': 'missing-device',
    'operation': 'heartbeat',
    'message': 'smoke',
}, follow_redirects=False)
if r1.status_code not in (302, 303) or '/ui/devices' not in r1.headers.get('location', ''):
    raise SystemExit(f'FAILED bulk-device redirect {r1.status_code} {r1.headers}')

r2 = client.post('/ui/action/bulk-pet-op', data={
    'pet_ids': 'missing-pet',
    'event_kind': 'feed',
    'event_text': 'smoke',
}, follow_redirects=False)
if r2.status_code not in (302, 303) or '/ui/pets' not in r2.headers.get('location', ''):
    raise SystemExit(f'FAILED bulk-pet redirect {r2.status_code} {r2.headers}')

print('UI smoke OK')
