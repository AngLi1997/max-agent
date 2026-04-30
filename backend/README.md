## 系统设置联调启动

执行顺序：
1. `docker compose up -d`
2. `cd backend`
3. `uv sync --group dev`
4. `uv run alembic upgrade head`
5. `uv run python app/db/seed.py`
6. `uv run uvicorn main:app --reload`

默认管理员：`admin / admin123`
