Helper class and functions to rate limiting function calls with Python Decorators

### Usage
```
import time
from throttle.py import throttled

# Params:
# 1 - Seconds between calls (the rate limit to be enforced)
# 2 - Enforce the rate limit and block GIL (True), or return and never invoke the handler (False)
@throttled(2,False)
def test_fn():
    print("test_fn called" + str(time.time()))
    
while True:
    test_fn()
    time.sleep(0.1)
```
##### Using a cache key

```

class A:
    name="A"
    # Params:
    # 1 - Seconds between calls (the rate limit to be enforced)
    # 2 - Enforce the rate limit and block GIL (True), or return and never invoke the handler (False)
    @throttled(1,True,key=lambda self: self.name)
    def test_fn(self):
        print(f"{self.name}={str(time.time())}")


class X(A):
    name="X"
    pass
class Y(A):
    name="Y"
    pass
while True:
    a = A()
    x = X()

    while True:
        a.test_fn()
        x.test_fn()
        time.sleep(0.1)
```


#### Credits 
```
Authored by oPromessa, 2017
Published on https://github.com/oPromessa/flickr-uploader/
Inspired by: https://gist.github.com/gregburek/1441055
Extended by teocns, 2023
```