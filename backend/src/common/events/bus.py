"""Event bus interno (in-process pub/sub) para comunicação desacoplada entre módulos."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    event_type: str
    payload: dict[str, Any]
    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tenant_id: UUID | None = None


EventHandler = Callable[[DomainEvent], Awaitable[None]]

_handlers: dict[str, list[EventHandler]] = defaultdict(list)


def subscribe(event_type: str, handler: EventHandler) -> None:
    _handlers[event_type].append(handler)


async def publish(event: DomainEvent) -> None:
    for handler in _handlers.get(event.event_type, []):
        await handler(event)