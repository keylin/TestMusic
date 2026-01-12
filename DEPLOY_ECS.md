# 阿里云 ECS (Debian) 一键部署指南

本指南将帮助您使用自动化脚本在阿里云 ECS (Debian系统) 上快速部署 MyMusic 项目。

## 1. 快速部署 (推荐)

我们为您准备了 `deploy.sh` 脚本，可以自动完成环境安装、代码拉取、构建和服务启动。

### 步骤 1: 准备脚本

1.  将 `deploy.sh` 上传到服务器，或者直接在服务器上创建该文件。
2.  使用编辑器打开脚本，修改配置区域：

    ```bash
    nano deploy.sh
    ```

    **必填修改**:
    ```bash
    # 把这个换成你自己仓库的 http/https 地址
    REPO_URL="https://github.com/keylin/MyMusic.git"
    ```

### 步骤 2: 运行脚本

给予执行权限并运行：

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

## 2. 运维管理 (manage.sh)

我们提供了一个统一的管理脚本 `manage.sh`，用于管理服务的启动、停止、重启和查看日志。

### 使用方法

1.  上传 `manage.sh` 到服务器。
2.  给予执行权限：`chmod +x manage.sh`。

### 交互模式
直接运行脚本，不带参数，将进入交互式菜单：
```bash
sudo ./manage.sh
```

### 命令行模式
您也可以直接通过参数执行命令：

- **启动**: `sudo ./manage.sh start`
- **停止**: `sudo ./manage.sh stop`
- **重启**: `sudo ./manage.sh restart`
- **状态**: `sudo ./manage.sh status`
- **日志**: `sudo ./manage.sh log`
- **诊断**: `sudo ./manage.sh debug`

## 3. 防火墙设置 (必看)

部署成功后，只能在服务器内部访问。要通过公网访问，您**必须**在阿里云控制台配置安全组。

1.  登录阿里云控制台 -> ECS -> 安全组。
2.  找到实例关联的安全组，点击 "配置规则"。
3.  添加一条 **入方向** 规则：
    *   端口范围: `8866/8866`
    *   授权对象: `0.0.0.0/0` (允许所有 IP 访问)

## 4. 访问项目

脚本运行结束后，会提示您的访问地址：
`http://<您的公网IP>:8866`
