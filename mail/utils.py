import settings


class System:
    @staticmethod
    def user_photo_path(instance, filename: str) -> str:
        return f'data/images/user_{instance.pk}/{filename}'
