FROM python:3.9.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY . .

# 确保前端页面存在
RUN mkdir -p frontend/pages frontend/css frontend/js templates/auth templates/game static/css static/js

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]
