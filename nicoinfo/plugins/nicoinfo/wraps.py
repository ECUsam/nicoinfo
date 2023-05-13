import asyncio
import time
from functools import wraps


def repeat_every_30_seconds(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            while True:
                start_time = time.time()
                result = await coro(*args, **kwargs)
                elapsed_time = time.time() - start_time
                sleep_duration = max(30 - elapsed_time, 0)
                await asyncio.sleep(sleep_duration)
        except Exception as e:
            print(f"Error in {coro.__name__}: {e}")
            return
    return wrapper

def retry_async(retries=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"Failed with {str(e)}, retrying...")
                    await asyncio.sleep(delay)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


@repeat_every_30_seconds
async def main():
    print(1111)

if __name__ == '__main__':
    asyncio.run(main())
    print(222)
