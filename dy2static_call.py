def dy2static_call(func):
    print("replaced")
    def wrapper(*args):
        print("in wrapper")
        func(*args)
    return wrapper