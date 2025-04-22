from passlib.context import CryptContext

# check algo section:
# https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html?highlight=bcrypt#format-algorithm  # noqa # type: ignore

PwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
