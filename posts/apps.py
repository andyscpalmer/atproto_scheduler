from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posts"
    verbose_name = "- Posting Tools -"

    def ready(self):
        try:
            from schedule_client import updater

            updater.start()
        except ModuleNotFoundError:
            print(
                "ModuleNotFoundError: If this is the static site, this error can be ignored."
            )
            pass
        except ImportError:
            print("ImportError: If this is the static site, this error can be ignored.")
            pass
        except Exception:
            raise
