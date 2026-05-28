import sys
import redis
from django.apps import AppConfig
from django.conf import settings


class ChatbotaiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ChatBotAi'

    def ready(self):
        if 'manage.py' in sys.argv and not any(cmd in sys.argv for cmd in ['runserver', 'daphne']):
            return

        try:
            channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
            default_layer = channel_layers.get('default', {})
            config = default_layer.get('CONFIG', {})
            hosts = config.get('hosts', [])

            if not hosts:
                print("--- Redis auto-fix skipped: no hosts found ---")
                return

            redis_host = hosts[0]

            if isinstance(redis_host, tuple):
                r = redis.Redis(host=redis_host[0], port=redis_host[1])
            else:
                r = redis.from_url(redis_host)

            r.config_set('stop-writes-on-bgsave-error', 'no')
            r.config_set('save', '')

            print("--- Redis auto-fixed successfully (PaaS settings) ---")

        except Exception as e:
            print(f"--- Could not auto-fix Redis: {e} ---")
