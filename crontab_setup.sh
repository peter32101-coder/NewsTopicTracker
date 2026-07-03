#!/bin/bash

# 取得這支 .sh 檔案所在的資料夾路徑
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 組合出 daily_job.py 和 cron.log 的完整路徑
PYTHON_PATH=$(which python3)
JOB_PATH="$PROJECT_DIR/daily_job.py"
LOG_PATH="$PROJECT_DIR/cron.log"

# 要寫入 crontab 的那一行（每天早上 8:00 執行）
CRON_JOB="0 8 * * * $PYTHON_PATH $JOB_PATH >> $LOG_PATH 2>&1"

# 將新設定加入 crontab（保留既有設定）
( crontab -l 2>/dev/null; echo "$CRON_JOB" ) | crontab -

echo "cron job 設定完成："
echo "$CRON_JOB"