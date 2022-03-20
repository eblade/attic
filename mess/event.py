import typing as t
import asyncio
import logging
import weakref


logger = logging.getLogger(__name__)


class Event:
    def __init__(self):
        self.__handlers: t.List[t.Coroutine] = []

    def __iadd__(self, handler: t.Coroutine):
        self.__handlers.append(weakref.WeakMethod(handler))
        return self

    #def __isub__(self, handler: t.Coroutine):
    #    self.__handlers.remove(handler)
    #    return self

    def fire(self, *args, **keywargs) -> t.List[asyncio.Future]:
        loop = asyncio.get_running_loop()
        logger.info(f'Loop is {id(loop)}')
        futures = []
        for handler_ref in self.__handlers:
            handler = handler_ref()
            if asyncio.iscoroutinefunction(handler):
                futures.append(asyncio.run_coroutine_threadsafe(self._check_call(handler(*args, **keywargs)), loop))
            elif asyncio.iscoroutine(handler):
                futures.append(asyncio.run_coroutine_threadsafe(self._check_call(handler), loop))
            else:
                raise TypeError("Expected Coroutine or CoroutineFunction, got %s" % type(handler))
        return futures

    @staticmethod
    async def _check_call(coro: t.Coroutine):
        try:
            await coro
        except:
            traceback.print_exc()
            logger.exception(f'(Check Call) Async call raised exception')
            raise

    def clear(self):
        self.__handlers = [h for h in self._handlers if getattr(h, 'im_self', False) != obj]
