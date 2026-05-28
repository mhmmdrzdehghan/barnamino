from django.apps import AppConfig
import threading


class ChatbotaiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ChatBotAi"


    def ready(self):
        # این ترد را اجرا می‌کنیم تا در بالا آمدن سرور اختلال ایجاد نکند
        def fix_redis():
            try:
                import redis
                from django.conf import settings
                # گرفتن آدرس ردیس از تنظیمات
                hosts = settings.CHANNEL_LAYERS['default']['config']['hosts'][0]
                r = redis.from_url(hosts)
                r.config_set('stop-writes-on-bgsave-error', 'no')
                r.config_set('save', '')
                print("--- Redis Persistence Disabled by App ---")
            except Exception as e:
                print(f"--- Could not auto-fix Redis: {e} ---")
        
        threading.Thread(target=fix_redis, daemon=True).start()
