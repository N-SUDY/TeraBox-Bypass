import re
import requests
from sys import argv
from bs4 import BeautifulSoup
from humanize import naturalsize
from urllib.parse import quote, unquote


# sample_url = "https://teraboxapp.com/s/13FlMJT4cytJbA00IBUWX0w" # file with directories
# sample_url = "https://terabox.app/s/16oyv6pH-e97aYGPrLpbTTQ" # only file

terabox_url = terabox_url = input("Terabox url: ") if len(argv) < 2 else argv[1]

json_data_url = "https://www.4funbox.com/share/list?jsToken={jsToken}&shorturl={key}"
cookies = {"ndus": "YbDgQCEteHui0Bx8sPAmBS3hSB4K79edBrj6PrJq"}
jsToken = None
key = None


def process_terabox(terabox_url):
    global jsToken, key, cookies
    req = requests.get(terabox_url, cookies=cookies)
    soup = BeautifulSoup(req.content, "html.parser")
    result = soup.find_all("script")[3]
    if match := re.search(r'"([^"]+)"', unquote(result.text)):
        jsToken = match.group(1)
    key = req.url.split("=")[1]

      
def bypass_directory_logic(jsToken, key, link, cookies, depth=0):
    if depth >= 10:
        return
    
    res = requests.get(link, cookies=cookies)
    data = res.json()
    if "list" in data:
        for item in data["list"]:
            if "dlink" in item:
                path = item['path'].rsplit("/", 1)
                title = item['server_filename']
                size = item['size']
                dlink = item['dlink']
                
                print(f"Path: {path[0]}")
                print(f"Title: {title}")
                print(f"Size: {naturalsize(size)}")
                print(f"Dlink: {dlink}\n")
                
            if "path" in item:
                _path = quote(item["path"]).replace("/", "%2F")
                sub_link = f"{json_data_url.format(jsToken=jsToken, key=key)}&dir={_path}"
                bypass_directory_logic(jsToken, key, sub_link, cookies, depth + 1)


process_terabox(terabox_url)

base = json_data_url.format(jsToken=jsToken, key=key)
res = requests.get(f"{base}&root=1", cookies=cookies)
try:
    meta = res.json()["list"][0]
    title = meta['server_filename']
    size = meta['size']
    dlink = meta['dlink']
    
    print(f"Title: {title}")
    print(f"Size: {naturalsize(size)}")
    print(f"Dlink: {dlink}")
except KeyError:
    _path = quote(res.json()["list"][0]["path"]).replace("/", "%2F")
    link = f'{json_data_url.format(jsToken=jsToken, key=key)}&dir={_path}'
    bypass_directory_logic(jsToken, key, link, cookies)
