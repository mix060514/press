#!/bin/bash

# Docker 建置腳本
echo "開始建置 press-scrapy Docker 映像..."
# 設定工作目錄為腳本所在的絕對路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 設定 psql 模組的絕對路徑
PSQL_DIR="$(cd "$SCRIPT_DIR/../psql" && pwd)"

# 檢查 psql 資料夾是否存在
if [ ! -d "$PSQL_DIR" ]; then
    echo "錯誤: psql 模組資料夾不存在於 $PSQL_DIR"
    exit 1
fi

# 檢查 psql 資料夾是否存在
if [ ! -d "psql" ]; then
    echo "複製 psql 資料夾..."
    cp -r "$PSQL_DIR" psql
fi

# 執行 Docker 建置
echo "執行 Docker 建置..."
docker build -t press-scrapy .

# 建置完成後清理
if [ -d "psql" ]; then
    echo "清理臨時資料夾..."
    rm -rf "$SCRIPT_DIR/psql"
fi

echo "建置完成！" 
