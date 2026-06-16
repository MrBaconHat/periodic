import asyncio


class Loop:
    def __init__(self, func, interval):
        self.func = func
        self.before_func = None
        self.after_func = None
        self.error_func = None
        
        self.interval = interval

        self.task = None
        self.running = False


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