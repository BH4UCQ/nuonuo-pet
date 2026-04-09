from __future__ import annotations

from typing import Callable, Optional, List, Tuple

from fastapi.responses import HTMLResponse

StatusBadgeFn = Callable[..., str]
NoticeFn = Callable[..., str]
KvTableFn = Callable[..., str]
PageShellFn = Callable[..., HTMLResponse]
