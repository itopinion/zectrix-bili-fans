# Zectrix B 站粉丝数墨水屏推送

把 B 站粉丝数渲染成一张 `400x300` 的 JPG 图片，并推送到 Zectrix 墨水屏设备。这个项目主要用于 QNAP/NAS 定时任务。

脚本保留了原始稳定脚本的上传方式：

- 使用 `requests.post`
- multipart 文件字段名为 `images`
- 上传文件名固定为 `photo.jpg`
- 上传 MIME 类型为 `image/jpeg`
- 表单字段包含 `pageId` 和 `dither`

## 功能

- 从 B 站公开接口获取指定 UID 的粉丝数。
- 生成适合 PVC 牌子开窗区域的 `400x300` JPG 图片。
- 画面仅保留大号粉丝数和右下角更新时间。
- 如果同目录存在 `Arial Narrow Bold.ttf`，优先使用该字体。
- 支持一个或多个 Zectrix 设备。
- 推送失败时最多重试 3 次。
- API Key 和设备 MAC 都通过环境变量配置，不写入源码。

## 安装依赖

```bash
python3 -m pip install -r requirements.txt
```

如果 NAS 上没有 Arial Narrow 字体，可以把 `Arial Narrow Bold.ttf` 放到 `push_bili_fans.py` 同目录。

## 配置

至少需要设置下面两个环境变量：

```bash
export ZECTRIX_API_KEY="your_zectrix_api_key_here"
export ZECTRIX_MACS="AA:BB:CC:DD:EE:FF"
```

其他可选配置：

```bash
export BILI_UID="13131424"
export TARGET_PAGE="1"
export OUTPUT_DIR="/volume1/web/test"
```

如果要推送多台设备，MAC 用英文逗号分隔：

```bash
export ZECTRIX_MACS="AA:BB:CC:DD:EE:FF,11:22:33:44:55:66"
```

## 运行

```bash
python3 push_bili_fans.py
```

## QNAP 定时任务示例

```bash
cd /volume1/web/bili-fans
export ZECTRIX_API_KEY="your_zectrix_api_key_here"
export ZECTRIX_MACS="AA:BB:CC:DD:EE:FF"
export BILI_UID="13131424"
python3 push_bili_fans.py
```

## 安全说明

不要提交以下内容到 GitHub：

- Zectrix API Key
- `.env` 文件
- 真实设备 MAC
- SSH 私钥
- 生成的图片
- 字体文件
