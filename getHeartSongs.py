import argparse
import getpass
import requests
import os
import json

doubanSession = requests.Session()
downloadPath = ""

def getArg():
    parser = argparse.ArgumentParser(description="DoubanFMExport Tool", usage="python getHeartSongs.py -Du \"doubanFMUserName\"")
    parser.add_argument('-Du', type=str, help='DoubanFM username')
    parser.add_argument('-od', type=str, help='Output directory')
    args = parser.parse_args()
    if args.od is not None:
        setDownloadPath(args.od)
        exit(0)
    if args.Du is None:
        parser.print_help()
        exit(1)
    password = getpass.getpass("DoubanFM password:")
    dic = {
        "name": args.Du,
        "password": password
    }
    return dic

def setDownloadPath(path):
    with open("config/config.json", "r") as f:
        configJson = json.loads(f.read())
    with open("config/config.json", "w") as f:
        configJson["downloadPath"] = path
        f.write(json.dumps(configJson))

def loginDoubanFM(name, password):
    loginUrl = "https://accounts.douban.com/j/popup/login/basic"
    checkLoginUrl = "https://douban.fm/j/check_loggedin?san=0"
    loginDic = {
        "source": "fm",
        "referer": "https://douban.fm/mine/hearts",
        "name": name,
        "password": password,
        "capcha_solution": "",
        "captcha_id": ""
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = doubanSession.post(loginUrl, data=loginDic, headers=headers)
    if r.json()["status"] == "success":
        r = doubanSession.get(checkLoginUrl)
        return 0
    else:
        raise RuntimeError("[ERROR] Login Douban failed: %s (from douban server)" % r.json()["description"])

def getHeart():
    getIdUrl = "https://douban.fm/j/v2/redheart/basic" + "?updated_time=2015-01-01+00%3A00%3A00"
    getSongUrl = "https://douban.fm/j/v2/redheart/songs"
    songIds = []
    r = doubanSession.get(getIdUrl)
    rJson = r.json()
    if rJson["creator"]["id"] != "":
        # if user is login
        songIds = rJson["songs"]
    idLen = len(songIds)
    songIter = iter(songIds)
    while idLen > 0:
        sids = []
        i = 0
        for item in songIter:
            if i == 30:
                break
            sids.append(item["sid"])
            i += 1
        requestDic = {}
        requestDic["sids"] = "|".join(sids)
        requestDic["kbps"] = "128"
        requestDic["ck"] = doubanSession.cookies.get_dict()["ck"]
        songs = doubanSession.post(getSongUrl, data=requestDic).json()
        global downloadPath
        if downloadPath == "":
            useDownloadPath = "download"
        else:
            useDownloadPath = downloadPath
        for song in songs:
            with open(os.path.join(useDownloadPath, song["title"]+"."+song["file_ext"]), "wb") as f:
                rSong = doubanSession.get(song["url"])
                for chunk in rSong.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("[INFO] download \"%s\" done" % song["title"])
        idLen -= 30

def portal():
    argDic = getArg()
    loginDoubanFM(argDic["name"], argDic["password"])
    getHeart()
    print("[INFO] done")

if __name__ == "__main__":
    with open("config/config.json", "r") as f:
        downloadPath = json.loads(f.read())["downloadPath"]
    portal()
