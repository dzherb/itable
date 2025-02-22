"""
ASGI config for itable project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import uvicorn

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_asgi_application()

if __name__ == '__main__':
    config = uvicorn.Config(
        app='asgi:application',
        host='0.0.0.0',
        port=8000,
        proxy_headers=True,
    )
    server = uvicorn.Server(config)
    server.run()
