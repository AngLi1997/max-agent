from secrets import choice
from string import ascii_letters, digits

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def build_current_user_payload(*, user, roles, permissions: set[str], menus: list[dict]) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "roles": roles,
        "permissions": sorted(permissions),
        "menus": menus,
        "mustChangePassword": user.must_change_password,
    }


def change_own_password(user, *, old_password: str, new_password: str) -> None:
    verified, updated_hash = password_hash.verify_and_update(old_password, user.hashed_password)
    if not verified:
        raise ValueError("旧密码错误")
    user.hashed_password = updated_hash or password_hash.hash(new_password)
    user.must_change_password = False


def create_temporary_password(length: int = 12) -> str:
    alphabet = ascii_letters + digits
    return "".join(choice(alphabet) for _ in range(length))


def delete_user_or_raise(user) -> None:
    if user.is_builtin:
        raise ValueError("内置用户不允许删除")
