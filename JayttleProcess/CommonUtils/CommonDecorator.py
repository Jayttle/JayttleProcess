import functools
import time
from datetime import datetime


def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录函数调用时间
        call_time = datetime.now()
        start_time = time.time()  # 记录函数开始执行的时间

        print(f"Function '{func.__name__}' called at {call_time}")

        # 记录传入的参数
        args_str = ', '.join([str(arg) for arg in args if isinstance(arg, (int, float, str))])
        kwargs_str = ', '.join([f"{key}={value}" for key, value in kwargs.items() if isinstance(value, (int, float, str))])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        print(f"Arguments: {all_args}")

        # 调用函数并记录返回值
        result = func(*args, **kwargs)
        print(f"Returned data type: {type(result).__name__}")  # 打印返回值的数据类型
        end_time = time.time()  # 记录函数执行完毕的时间
        print(f"executed in {(end_time - start_time):.4f}s")  # 打印执行时间
        print()
        return result

    return wrapper


def cache_results(func):
    cache = {}  # 创建一个字典来存储之前的调用结果
    def wrapper(*args, **kwargs):
        # 将参数转换为可哈希的形式，以便用作字典的键
        cache_key = (args, tuple(sorted(kwargs.items())))
        if cache_key in cache:  # 如果缓存中有这个键，直接返回对应的值
            print("Returning cached result for", cache_key, "cache[cache_key]: ", cache[cache_key])
            return cache[cache_key]
        else:  # 否则，调用函数并存储结果到缓存中
            result = func(*args, **kwargs)
            cache[cache_key] = result
            return result
    return wrapper


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行函数
        end_time = time.time()  # 记录函数执行完毕的时间
        print(f"Function {func.__name__!r} executed in {(end_time - start_time):.4f}s")  # 打印执行时间
        return result
    return wrapper


def catch_exceptions(default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An exception occurred in {func.__name__}: {e}")
                return default_value
        return wrapper
    return decorator


