FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 複製 psql 模組到容器中（uv 需要能找到此路徑）
# 注意：psql 在 pyproject.toml 中設為 editable=true (測試模式)
# 生產模式時需要：
# 1. 將 pyproject.toml 中的 editable 改為 false
# 2. 在安裝後刪除此資料夾：&& rm -rf /psql
COPY psql /psql

# 將依賴安裝與專案安裝分離以提升 Docker 快取效果
# 先安裝依賴
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# 複製專案代碼
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# 創建日誌目錄
RUN mkdir -p logs

# 將虛擬環境的 bin 目錄加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["scrapy"]

CMD ["list"]




