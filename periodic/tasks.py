import asyncio
import functools


class Loop:
    def __init__(self, func, interval):
        self.func = func
        self.before_func = None
        self.after_func = None
        self.error_func = None
        
        self.interval = interval

        self.task = None
        self.running = False

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Cache a bound Loop per instance so .start()/.stop() state is per-instance
        key = f"_loop_{self.func.__name__}"
        bound = obj.__dict__.get(key)
        if bound is None:
            bound = Loop(functools.partial(self.func, obj), self.interval)
            bound.before_func = functools.partial(self.before_func, obj) if self.before_func else None
            bound.after_func  = functools.partial(self.after_func,  obj) if self.after_func  else None
            bound.error_func  = functools.partial(self.error_func,  obj) if self.error_func  else None
            obj.__dict__[key] = bound
        return bound


    async def _runner(self, *args, **kwargs):
        try:
            if self.before_func:
                await self.before_func()

            while self.running:
                await self.func(
                    *args,
                    **kwargs
                )

                await asyncio.sleep(
                    self.interval
                )

        except asyncio.CancelledError:
            pass
            
        except Exception as e:
            if self.error_func:
                await self.error_func(e)

        finally:
            if self.after_func:
                await self.after_func()


    # === CONTROL =====================
    
    def start(self, *args, **kwargs):
        if self.running:
            return

        self.running = True

        self.task = asyncio.create_task(
            self._runner(
                *args,
                **kwargs
            )
        )


    def stop(self):
        self.running = False

        if self.task:
            self.task.cancel()

            self.task = None


    def restart(self, *args, **kwargs):
        self.stop()

        self.start(
            *args,
            **kwargs
        )

    # === PROPERTIES ==================
    
    def is_running(self) -> bool:
        return self.runninh

    def get_task(self) -> asyncio.Task:
        return self.task

    def get_interval(self) -> float:
        return self.interval

    def set_interval(self, interval: float):
        self.interval = interval


    # === DECORATORS =================
    
    def before_loop(self, func):
        self.before_func = func
        return func

    def after_loop(self, func):
        self.after_func = func
        return func

    def error(self, func):
        self.error_func = func
        return func


def loop(interval):
    def decorator(func):
        return Loop(
            func,
            interval
        )
    return decorator