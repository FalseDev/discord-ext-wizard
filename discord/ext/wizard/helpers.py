import inspect


def combine_checks(*checks):
    def func(*args):
        for check in checks:
            check(*args)
    return func

async def maybe_async(func, *args, **kwargs):
    res = func(*args, **kwargs)
    if inspect.iscoroutine(res):
        return await res
    return res