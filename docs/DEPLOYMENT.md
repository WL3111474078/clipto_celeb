# Celebrity应用部署指南

本文档提供了将Celebrity应用程序部署到生产环境的详细步骤。

## 基本部署

### 前提条件

1. Python 3.7+
2. 必要的Python依赖:
   ```
   flask>=2.0.0
   flask-cors>=3.0.10
   waitress>=2.0.0
   ```

### 直接部署

1. 克隆或下载代码库
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. 运行应用:
   ```bash
   python run.py
   ```
4. 访问 http://localhost:5000/celeb/

## Web服务器部署

### 使用Nginx和uWSGI

1. 安装uWSGI:
   ```bash
   pip install uwsgi
   ```

2. 创建uWSGI配置文件 `uwsgi.ini`:
   ```ini
   [uwsgi]
   module = trans_web.core.wsgi:application
   
   master = true
   processes = 4
   threads = 2
   
   socket = celebrity.sock
   chmod-socket = 660
   vacuum = true
   
   die-on-term = true
   ```

3. 创建Nginx配置:
   ```nginx
   server {
       listen 80;
       server_name example.com;
       
       location /celeb {
           include uwsgi_params;
           uwsgi_pass unix://path/to/celebrity.sock;
           uwsgi_param SCRIPT_NAME /celeb;
           uwsgi_modifier1 30;
       }
   }
   ```

4. 启动uWSGI:
   ```bash
   uwsgi --ini uwsgi.ini
   ```

5. 重启Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

### 使用Apache和mod_wsgi

1. 安装mod_wsgi

2. 配置Apache:
   ```apache
   <VirtualHost *:80>
       ServerName example.com
       
       WSGIDaemonProcess celebrity python-home=/path/to/venv
       WSGIProcessGroup celebrity
       WSGIScriptAlias /celeb /path/to/trans_web/core/wsgi.py
       
       <Directory /path/to/trans_web/core>
           Require all granted
       </Directory>
       
       SetEnv SCRIPT_NAME /celeb
   </VirtualHost>
   ```

## Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV SCRIPT_NAME=/celeb

EXPOSE 5000

CMD ["python", "run.py"]
```

构建并运行:
```bash
docker build -t celebrity-app .
docker run -p 5000:5000 celebrity-app
```

## 系统服务部署

### Linux Systemd服务

创建服务文件 `/etc/systemd/system/celebrity.service`:
```ini
[Unit]
Description=Celebrity Data Management App
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="SCRIPT_NAME=/celeb"
ExecStart=/path/to/python /path/to/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl enable celebrity
sudo systemctl start celebrity
```

### Windows服务

使用NSSM工具注册为Windows服务:
```
nssm install Celebrity "C:\path\to\python.exe" "C:\path\to\run.py"
nssm set Celebrity AppEnvironment SCRIPT_NAME=/celeb
nssm start Celebrity
```

## 备份策略

生产环境建议设置备份策略:

1. 设置备份间隔(在production.py中):
   ```python
   BACKUP_INTERVAL_HOURS = 12
   ```

2. 备份文件位置:
   ```
   trans_web/db_backup/
   ```

3. 定期将备份文件转移到外部存储或云存储 