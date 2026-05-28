# Zectrix Bilibili Fans Display

Push a Bilibili follower count image to a Zectrix e-paper device.

This project is designed for a QNAP/NAS scheduled task. It keeps the same stable upload behavior as the original working script:

- `requests.post`
- multipart field name: `images`
- upload filename: `photo.jpg`
- upload MIME type: `image/jpeg`
- form fields: `pageId` and `dither`

## Features

- Fetches follower count from Bilibili UID `13131424` by default.
- Generates a `400x300` JPG for a PVC-framed display area.
- Uses large `Arial Narrow Bold`-style digits when the font is available.
- Pushes to one Zectrix device by default: `AC:A7:04:EA:62:30`.
- Retries the Zectrix upload up to 3 times.
- Keeps secrets out of source code.

## Install

```bash
python3 -m pip install -r requirements.txt
```

Optional: copy `Arial Narrow Bold.ttf` into the same folder as `push_bili_fans.py` if your NAS does not already have Arial Narrow installed.

## Configure

Set your Zectrix API key as an environment variable:

```bash
export ZECTRIX_API_KEY="your_zectrix_api_key_here"
```

Optional environment variables:

```bash
export BILI_UID="13131424"
export ZECTRIX_MACS="AC:A7:04:EA:62:30"
export TARGET_PAGE="1"
export OUTPUT_DIR="/volume1/web/test"
```

Multiple devices can be comma-separated:

```bash
export ZECTRIX_MACS="AC:A7:04:EA:62:30,9C:13:9E:B5:79:C8"
```

## Run

```bash
python3 push_bili_fans.py
```

## QNAP Scheduled Task Example

Use an absolute path for the script and export the API key before running it:

```bash
cd /volume1/web/bili-fans
export ZECTRIX_API_KEY="your_zectrix_api_key_here"
python3 push_bili_fans.py
```

## Security

Do not commit API keys, `.env` files, SSH private keys, generated images, or font files.
