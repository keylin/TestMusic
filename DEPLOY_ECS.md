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
    REPO_URL="https://github.com/your-username/MyMusic.git"
    ```

### 步骤 2: 运行脚本

给予执行权限并运行：

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

脚本将会：
1.  自动安装 Python3, pip, Git, Node.js, npm。
2.  克隆/更新代码到 `/root/MyMusic`。
3.  创建虚拟环境并安装 Python 依赖。
4.  编译 Vue 前端项目。
5.  自动配置并启动 Systemd 后台服务。

## 2. 防火墙设置 (必看)

部署成功后，只能在服务器内部访问。要通过公网访问，您**必须**在阿里云控制台配置安全组。

1.  登录阿里云控制台 -> ECS -> 安全组。
2.  找到实例关联的安全组，点击 "配置规则"。
3.  添加一条 **入方向** 规则：
    *   端口范围: `8888/8888`
    *   授权对象: `0.0.0.0/0` (允许所有 IP 访问)

## 3. 访问项目

脚本运行结束后，会提示您的访问地址：
`http://<您的公网IP>:8888`

---

## 常用运维命令

- **查看服务状态**: `sudo systemctl status mymusic`
- **重启服务**: `sudo systemctl restart mymusic`
- **查看日志**: `sudo journalctl -u mymusic -f`
- **停止服务**: `sudo systemctl stop mymusic`
