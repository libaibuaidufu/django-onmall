from django.apps import AppConfig


class UserOpreationConfig(AppConfig):
    name = 'user_opreation'
    verbose_name = "用户操作管理"

    def ready(self):
        import user_opreation.singals
