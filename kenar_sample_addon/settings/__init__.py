from .base import *

ENV = os.environ.get("ENVIRONMENT", "local")

if ENV == "local":
    from .local import *
elif ENV == "production":
    from .production import *
