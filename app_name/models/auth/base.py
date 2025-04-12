from app_name.models.base import BaseDbModel


class AuthBaseDbModel(BaseDbModel):
    __abstract__ = True

    @classmethod
    def _get_prefix(cls):
        """StupidCAMelCase to stupid_ca_mel_case"""
        return "auth"
