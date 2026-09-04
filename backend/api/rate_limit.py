from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter instance. Imported by main.py (to register it on the app)
# and by individual routers (to decorate specific endpoints), avoiding a
# circular import between main.py and the routers it includes.
limiter = Limiter(key_func=get_remote_address)
