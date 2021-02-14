"""
Observable lass
"""

from types import FunctionType
import asyncio


class Observable:
    def __init__(self, val=None):
        self._value = val
        self.listeners = []

    @property
    def value(self):
        return self._value

    async def next(self, val):
        self._value = val
        await self._dispatch_subscribe()

    async def subscribe(self, callback):
        self.listeners.append(callback)

    async def unsubscribe(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    async def _dispatch_subscribe(self):
        await asyncio.gather(
            *(
                func(self._value) for func in self.listeners
            )
        )
