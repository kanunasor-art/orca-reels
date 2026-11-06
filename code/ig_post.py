"""Instagram Graph API publisher.
Usage: python3 ig_post.py reel <video_url> <caption_file> [cover_ms]
       python3 ig_post.py story <image_or_video_url>
Token: ~/.orca/token, IG id: ~/.orca/igid"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

G = "https://graph.facebook.com/v21.0"
TOKEN = open(os.path.expanduser("~/.orca/token")).read().strip()
IG = open(os.path.expanduser("~/.orca/igid")).read().strip()


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{G}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API hatası: {e.read().decode()}")


def wait(cid):
    for _ in range(60):
        st = call("GET", cid, fields="status_code,status")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") == "ERROR":
            raise SystemExit(f"Medya hatası: {st}")
        time.sleep(10)
    raise SystemExit("Zaman aşımı")


def publish(cid):
    wait(cid)
    mid = call("POST", f"{IG}/media_publish", creation_id=cid)["id"]
    link = call("GET", mid, fields="permalink").get("permalink", "")
    print(json.dumps({"media_id": mid, "permalink": link}))


if __name__ == "__main__":
    kind, url = sys.argv[1], sys.argv[2]
    if kind == "reel":
        cap = open(sys.argv[3], encoding="utf-8").read().strip()
        p = dict(media_type="REELS", video_url=url, caption=cap, share_to_feed="true")
        if len(sys.argv) > 4:
            p["thumb_offset"] = sys.argv[4]
        publish(call("POST", f"{IG}/media", **p)["id"])
    elif kind == "story":
        key = "video_url" if url.lower().endswith(".mp4") else "image_url"
        publish(call("POST", f"{IG}/media", media_type="STORIES", **{key: url})["id"])
