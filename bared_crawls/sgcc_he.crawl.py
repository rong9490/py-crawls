import requests
import time

def fetch_captcha():
  url = "https://pmos.he.sgcc.com.cn/px-common-authcenter/auth/v2/secureKey/get"
  payload = "{}"
  headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'ClientTag': 'OUTNET_BROWSE',
    'Connection': 'keep-alive',
    'CurrentRoute': '/outNet',
    'Origin': 'https://pmos.he.sgcc.com.cn',
    'Referer': 'https://pmos.he.sgcc.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'X-Ticket': 'undefined',
    'X-Token': 'null',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Content-Type': 'application/json;charset=UTF-8'
  }
  response = requests.request("POST", url, headers=headers, data=payload)
  print(response.json())


if __name__ == '__main__':
  start_time = time.time()
  print('getter!!', start_time)
  fetch_captcha()
  time.sleep(5)
  end_time = time.time()
  print('End', end_time)