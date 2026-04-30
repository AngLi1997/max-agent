# 重置密码功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为用户管理新增"重置密码"能力，管理员确认后系统随机生成临时密码，被重置用户当前登录态立即失效，下次登录必须修改密码。

**Architecture:** 新增权限点 `user:reset-password` 写入种子数据；在 `SlidingRedisStrategy` 上补充用户 token 索引，支持按用户批量失效 token；新增 `POST /users/{user_id}/reset-password` 路由，调用服务层重置密码并失效 token；前端在用户管理操作菜单新增"重置密码"项，确认后展示新临时密码。

**Tech Stack:** Python/FastAPI, SQLAlchemy, Redis, pwdlib, Vue 3, Ant Design Vue, axios

---

## 文件结构

### 修改

- `backend/app/db/seed.py` — PERMISSIONS 列表新增 `user:reset-password`
- `backend/app/services/auth.py` — SlidingRedisStrategy 增加 token 索引方法
- `backend/app/services/system_users.py` — 新增 `reset_password_for_user` 辅助函数
- `backend/app/schemas/user.py` — 新增 `ResetPasswordResponse`
- `backend/app/api/routes/users.py` — 新增 reset-password 路由
- `frontend/src/api/user.ts` — 新增 `resetPasswordApi`
- `frontend/src/views/setting/user/index.vue` — 操作菜单新增"重置密码"

### 新建

- `backend/tests/test_auth_token_strategy.py` — token 索引单元测试
- `backend/tests/test_users_reset_password.py` — 重置密码路由单元测试

### 已有测试文件追加

- `backend/tests/test_seed_menu_permissions.py` — 验证新权限已入种子
- `backend/tests/test_system_users_service.py` — 验证 reset 辅助函数

---

## Task 1: 种子数据 + 响应 Schema + 服务层辅助函数

**Files:**
- Modify: `backend/app/db/seed.py`
- Modify: `backend/app/schemas/user.py`
- Modify: `backend/app/services/system_users.py`
- Test: `backend/tests/test_seed_menu_permissions.py`
- Test: `backend/tests/test_system_users_service.py`

- [ ] **Step 1: 写种子数据权限验证测试（失败）**

在 `backend/tests/test_seed_menu_permissions.py` 末尾追加：

```python
def test_reset_password_permission_is_seeded() -> None:
    permission_identifiers = {p["identifier"] for p in PERMISSIONS}
    assert "user:reset-password" in permission_identifiers
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd backend && uv run pytest tests/test_seed_menu_permissions.py::test_reset_password_permission_is_seeded -v
```

预期：FAIL，`AssertionError`

- [ ] **Step 3: 在种子数据中添加权限**

在 `backend/app/db/seed.py` 的 `PERMISSIONS` 列表末尾（`"登录日志查看"` 之后）追加：

```python
    {"name": "用户重置密码", "identifier": "user:reset-password", "type": "按钮", "status": "active"},
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd backend && uv run pytest tests/test_seed_menu_permissions.py -v
```

预期：全部 PASS

- [ ] **Step 5: 写 reset 辅助函数测试（失败）**

在 `backend/tests/test_system_users_service.py` 末尾追加：

```python
def test_reset_password_for_user_sets_new_hash_and_force_change() -> None:
    from app.services.system_users import reset_password_for_user

    user = User(
        username="editor",
        email="editor@example.com",
        hashed_password=password_hash.hash("old-pass"),
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        must_change_password=False,
    )
    old_hash = user.hashed_password
    temp_password = reset_password_for_user(user)

    assert len(temp_password) >= 12
    assert user.hashed_password != old_hash
    assert user.must_change_password is True
    assert password_hash.verify(temp_password, user.hashed_password)
```

- [ ] **Step 6: 运行测试确认失败**

```bash
cd backend && uv run pytest tests/test_system_users_service.py::test_reset_password_for_user_sets_new_hash_and_force_change -v
```

预期：FAIL，`ImportError: cannot import name 'reset_password_for_user'`

- [ ] **Step 7: 实现 reset_password_for_user**

在 `backend/app/services/system_users.py` 末尾追加：

```python
def reset_password_for_user(user) -> str:
    temp_password = create_temporary_password()
    user.hashed_password = password_hash.hash(temp_password)
    user.must_change_password = True
    return temp_password
```

- [ ] **Step 8: 新增 ResetPasswordResponse**

在 `backend/app/schemas/user.py` 末尾追加：

```python
class ResetPasswordResponse(BaseModel):
    message: str
    temporaryPassword: str
```

- [ ] **Step 9: 运行全部测试确认通过**

```bash
cd backend && uv run pytest tests/test_system_users_service.py tests/test_seed_menu_permissions.py -v
```

预期：全部 PASS

- [ ] **Step 10: 提交**

```bash
git add backend/app/db/seed.py backend/app/schemas/user.py backend/app/services/system_users.py backend/tests/test_seed_menu_permissions.py backend/tests/test_system_users_service.py
git commit -m "feat: add reset-password permission seed, response schema, and service helper"
```

---

## Task 2: SlidingRedisStrategy token 索引

**Files:**
- Modify: `backend/app/services/auth.py`
- Create: `backend/tests/test_auth_token_strategy.py`

- [ ] **Step 1: 写 token 索引测试（失败）**

创建 `backend/tests/test_auth_token_strategy.py`：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.auth import SlidingRedisStrategy


class FakeRedis:
    """最小化 Redis mock，只实现 token 索引需要的方法。"""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self._store[key] = value

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def delete(self, *keys: str) -> None:
        for k in keys:
            self._store.pop(k, None)
            self._sets.pop(k, None)

    async def sadd(self, key: str, *values: str) -> None:
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key: str, *values: str) -> None:
        if key in self._sets:
            self._sets[key] -= set(values)

    async def smembers(self, key: str) -> set[str]:
        return self._sets.get(key, set())

    async def scard(self, key: str) -> int:
        return len(self._sets.get(key, set()))

    async def expire(self, key: str, seconds: int) -> None:
        pass  # TTL 不影响单元测试逻辑


def _make_strategy(redis: FakeRedis) -> SlidingRedisStrategy:
    return SlidingRedisStrategy(
        redis,  # type: ignore[arg-type]
        lifetime_seconds=3600,
        key_prefix="max_agent_token:",
    )


def _make_user(user_id: int = 1) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    return user


@pytest.mark.asyncio
async def test_write_token_adds_to_user_set() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    token = await strategy.write_token(user)

    assert token in await redis.smembers("max_agent_user_tokens:42")


@pytest.mark.asyncio
async def test_destroy_token_removes_from_user_set() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    token = await strategy.write_token(user)
    await strategy.destroy_token(token, user)

    assert token not in await redis.smembers("max_agent_user_tokens:42")


@pytest.mark.asyncio
async def test_destroy_user_tokens_clears_all() -> None:
    redis = FakeRedis()
    strategy = _make_strategy(redis)
    user = _make_user(42)

    t1 = await strategy.write_token(user)
    t2 = await strategy.write_token(user)

    await strategy.destroy_user_tokens(42)

    assert await redis.smembers("max_agent_user_tokens:42") == set()
    assert await redis.get(f"max_agent_token:{t1}") is None
    assert await redis.get(f"max_agent_token:{t2}") is None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd backend && uv run pytest tests/test_auth_token_strategy.py -v
```

预期：FAIL，`AttributeError: 'SlidingRedisStrategy' object has no attribute 'destroy_user_tokens'`

- [ ] **Step 3: 实现 token 索引方法**

修改 `backend/app/services/auth.py` 中的 `SlidingRedisStrategy` 类：

```python
class SlidingRedisStrategy(RedisStrategy[User, int]):

    def _user_tokens_key(self, user_id: int) -> str:
        return f"max_agent_user_tokens:{user_id}"

    async def write_token(self, user: User) -> str:
        token = await super().write_token(user)
        user_key = self._user_tokens_key(user.id)
        await self.redis.sadd(user_key, token)
        if self.lifetime_seconds is not None:
            await self.redis.expire(user_key, self.lifetime_seconds)
        return token

    async def read_token(self, token: str | None, user_manager: BaseUserManager[User, int]) -> User | None:
        user = await super().read_token(token, user_manager)
        if user is not None and token is not None and self.lifetime_seconds is not None:
            await self.redis.expire(f"{self.key_prefix}{token}", self.lifetime_seconds)
        return user

    async def destroy_token(self, token: str, user: User) -> None:
        await super().destroy_token(token, user)
        user_key = self._user_tokens_key(user.id)
        await self.redis.srem(user_key, token)
        remaining = await self.redis.scard(user_key)
        if remaining == 0:
            await self.redis.delete(user_key)
        elif self.lifetime_seconds is not None:
            await self.redis.expire(user_key, self.lifetime_seconds)

    async def destroy_user_tokens(self, user_id: int) -> None:
        user_key = self._user_tokens_key(user_id)
        tokens = await self.redis.smembers(user_key)
        if tokens:
            token_keys = [
                f"{self.key_prefix}{t.decode() if isinstance(t, bytes) else t}"
                for t in tokens
            ]
            await self.redis.delete(*token_keys)
        await self.redis.delete(user_key)
```

注意：这会替换掉原来只有 `read_token` 的类定义。

- [ ] **Step 4: 运行测试确认通过**

```bash
cd backend && uv run pytest tests/test_auth_token_strategy.py -v
```

预期：全部 PASS

- [ ] **Step 5: 运行全量后端测试确认无回归**

```bash
cd backend && uv run pytest -v
```

预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/services/auth.py backend/tests/test_auth_token_strategy.py
git commit -m "feat: add user token index to SlidingRedisStrategy for bulk invalidation"
```

---

## Task 3: 重置密码路由

**Files:**
- Modify: `backend/app/api/routes/users.py`
- Create: `backend/tests/test_users_reset_password.py`

- [ ] **Step 1: 写路由单元测试（失败）**

创建 `backend/tests/test_users_reset_password.py`：

```python
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.routes import users as users_routes
from app.models.user import User


def _make_target(user_id: int = 10, is_builtin: bool = False) -> User:
    user = User(
        id=user_id,
        username="editor",
        email="editor@example.com",
        hashed_password="old_hash",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        avatar="",
        status="active",
        is_builtin=is_builtin,
        must_change_password=False,
    )
    return user


def _make_actor() -> SimpleNamespace:
    return SimpleNamespace(id=1, username="admin", is_superuser=True)


def _make_session(target: User | None) -> MagicMock:
    session = MagicMock()
    session.get = AsyncMock(return_value=target)
    session.merge = AsyncMock()
    session.commit = AsyncMock()
    return session


def _make_strategy() -> MagicMock:
    strategy = MagicMock()
    strategy.destroy_user_tokens = AsyncMock()
    return strategy


@pytest.mark.asyncio
async def test_reset_password_success(monkeypatch: pytest.MonkeyPatch) -> None:
    target = _make_target()
    session = _make_session(target)
    strategy = _make_strategy()
    monkeypatch.setattr(users_routes, "write_operation_log", AsyncMock())

    result = await users_routes.reset_user_password(
        user_id=10,
        request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
        session=session,
        user=_make_actor(),
        strategy=strategy,
    )

    assert "temporaryPassword" in result
    assert result["message"] == "密码重置成功"
    assert target.must_change_password is True
    strategy.destroy_user_tokens.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_reset_password_user_not_found() -> None:
    session = _make_session(None)
    strategy = _make_strategy()

    with pytest.raises(HTTPException) as exc:
        await users_routes.reset_user_password(
            user_id=999,
            request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1")),
            session=session,
            user=_make_actor(),
            strategy=strategy,
        )

    assert exc.value.status_code == 404
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd backend && uv run pytest tests/test_users_reset_password.py -v
```

预期：FAIL，`AttributeError: module 'app.api.routes.users' has no attribute 'reset_user_password'`

- [ ] **Step 3: 实现路由**

在 `backend/app/api/routes/users.py` 顶部 import 区域追加：

```python
from app.schemas.user import ResetPasswordResponse
from app.services.auth import SlidingRedisStrategy, get_redis_strategy
from app.services.system_users import reset_password_for_user
```

在文件末尾追加路由：

```python
@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(require_permission("user:reset-password")),
    strategy: SlidingRedisStrategy = Depends(get_redis_strategy),
) -> dict:
    target = await session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    temporary_password = reset_password_for_user(target)
    session.add(target)
    await session.flush()

    await strategy.destroy_user_tokens(target.id)

    await write_operation_log(
        session,
        operator_id=user.id,
        operator_name=user.username,
        module="用户管理",
        action="重置用户密码",
        method="POST",
        result="成功",
        detail=f"重置用户 {target.username} 的密码",
        ip=request.client.host if request.client else "",
    )
    await session.commit()
    return {"message": "密码重置成功", "temporaryPassword": temporary_password}
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd backend && uv run pytest tests/test_users_reset_password.py -v
```

预期：全部 PASS

- [ ] **Step 5: 运行全量后端测试确认无回归**

```bash
cd backend && uv run pytest -v
```

预期：全部 PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/api/routes/users.py backend/app/schemas/user.py backend/tests/test_users_reset_password.py
git commit -m "feat: add POST /users/{id}/reset-password route with token invalidation"
```

---

## Task 4: 前端 API + 用户管理页交互

**Files:**
- Modify: `frontend/src/api/user.ts`
- Modify: `frontend/src/views/setting/user/index.vue`

- [ ] **Step 1: 新增前端 API 函数**

在 `frontend/src/api/user.ts` 末尾追加：

```typescript
export interface ResetPasswordResponse {
  message: string
  temporaryPassword: string
}

export function resetPasswordApi(id: number) {
  return request.post(`/users/${id}/reset-password`) as Promise<ResetPasswordResponse>
}
```

- [ ] **Step 2: 用户管理页新增权限计算属性**

在 `frontend/src/views/setting/user/index.vue` 的 `<script setup>` 中，在现有 `canStatus` 之后追加：

```typescript
const canResetPassword = computed(() => userStore.hasPermission('user:reset-password'))
```

同时在 import 区域追加导入：

```typescript
import { KeyOutlined } from '@ant-design/icons-vue'
import { resetPasswordApi } from '@/api/user'
```

注意：`resetPasswordApi` 需要加到已有的 `import { ... } from '@/api/user'` 中，不要重复 import。

- [ ] **Step 3: 操作菜单新增"重置密码"项**

在模板中 `<a-menu>` 内，`<a-menu-item v-if="canDelete ...>` 之后追加：

```html
<a-menu-item v-if="canResetPassword" key="resetPassword"><KeyOutlined /> 重置密码</a-menu-item>
```

- [ ] **Step 4: 实现 handleResetPassword 函数**

在 `<script setup>` 中追加：

```typescript
function handleResetPassword(record: UserListItem) {
  Modal.confirm({
    title: '确认重置密码',
    content: `确定要重置用户「${record.username}」的密码吗？重置后该用户当前登录态将立即失效。`,
    okType: 'danger',
    okText: '重置',
    cancelText: '取消',
    async onOk() {
      const res = await resetPasswordApi(record.id)
      Modal.success({
        title: '密码重置成功',
        content: `新临时密码：${res.temporaryPassword}\n请妥善保存，该用户下次登录后需要立即修改密码。`,
      })
      fetchData()
    },
  })
}
```

- [ ] **Step 5: 在 handleMenuClick 中添加 case**

修改 `handleMenuClick` 函数，在 `case 'delete':` 之后追加：

```typescript
    case 'resetPassword': handleResetPassword(record); break
```

- [ ] **Step 6: TypeScript 构建验证**

```bash
cd frontend && pnpm build
```

预期：构建成功，无类型错误

- [ ] **Step 7: 提交**

```bash
git add frontend/src/api/user.ts frontend/src/views/setting/user/index.vue
git commit -m "feat: add reset-password button to user management page"
```

---

## Task 5: 手工验证

- [ ] **Step 1: 启动后端并执行种子数据**

```bash
cd backend && uv run python -m app.db.seed
cd backend && uv run uvicorn main:app --reload
```

确认 `user:reset-password` 权限已写入数据库，超级管理员角色自动拥有该权限。

- [ ] **Step 2: 启动前端开发服务器**

```bash
cd frontend && pnpm dev
```

- [ ] **Step 3: 验证操作菜单**

以超级管理员登录，进入用户管理页面，确认操作下拉菜单中出现"重置密码"选项。

- [ ] **Step 4: 验证重置流程**

1. 点击某个非当前用户的"重置密码"
2. 确认弹出确认框，文案包含用户名和"登录态将立即失效"
3. 点击"重置"
4. 确认弹出成功框，展示新临时密码
5. 关闭成功框后列表自动刷新

- [ ] **Step 5: 验证 token 立即失效**

1. 用另一个浏览器或无痕窗口登录被重置用户
2. 管理员执行重置密码
3. 被重置用户刷新页面，确认被 401 拦回登录页

- [ ] **Step 6: 验证强制改密**

1. 用新临时密码登录被重置用户
2. 确认登录后立即弹出"修改密码"弹窗
3. 修改密码后弹窗关闭，可正常使用系统

- [ ] **Step 7: 验证无权限用户**

1. 以没有 `user:reset-password` 权限的角色登录
2. 确认用户管理操作菜单中不显示"重置密码"

---

## 规格覆盖检查

| 规格要求 | 对应 Task |
|---------|----------|
| 新增 `user:reset-password` 权限 | Task 1 Step 3 |
| 默认分配给超级管理员 | Task 1 Step 3（seed 自动绑定全部权限） |
| 系统随机生成临时密码 | Task 1 Step 7 |
| 被重置用户 token 立即失效 | Task 2 + Task 3 Step 3 |
| 被重置用户下次登录强制改密 | Task 1 Step 7 + Task 5 Step 6 |
| 只要有权限就可以重置任意用户 | Task 3 Step 3（无内置用户限制） |
| 前端操作菜单"重置密码" | Task 4 Step 3 |
| 确认框 + 结果框交互 | Task 4 Step 4 |
| 操作日志记录 | Task 3 Step 3 |
