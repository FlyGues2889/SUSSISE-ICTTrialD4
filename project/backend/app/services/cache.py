"""可选缓存层。

设置了 REDIS_URL 时使用 Redis，否则自动降级为进程内字典缓存，
因此本地演示与单机部署无需安装 Redis 也能正常运行。
"""

import json
import os
import time

REDIS_URL = os.getenv("REDIS_URL", "")

_mem: dict[str, tuple[float, object]] = {}
_client = None
_resolved = False


async def _redis():
    global _client, _resolved
    if _resolved:
        return _client
    _resolved = True
    if not REDIS_URL:
        return None
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        await client.ping()
        _client = client
        print(f"[缓存] 已连接 Redis: {REDIS_URL}")
    except Exception as e:  # pragma: no cover - 依赖运行环境
        print(f"[缓存] Redis 不可用，降级为进程内缓存: {e}")
        _client = None
    return _client


async def get_json(key: str):
    client = await _redis()
    if client is not None:
        try:
            raw = await client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None

    item = _mem.get(key)
    if not item:
        return None
    expires_at, value = item
    if expires_at and expires_at < time.time():
        _mem.pop(key, None)
        return None
    return value


async def set_json(key: str, value, ttl: int = 300) -> None:
    client = await _redis()
    if client is not None:
        try:
            await client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
            return
        except Exception:
            pass
    _mem[key] = (time.time() + ttl if ttl else 0, value)


async def delete(*keys: str) -> None:
    client = await _redis()
    if client is not None:
        try:
            await client.delete(*keys)
            return
        except Exception:
            pass
    for key in keys:
        _mem.pop(key, None)