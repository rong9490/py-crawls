import requests
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, TypedDict, NotRequired

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# 类型定义
class SecureKeyData(TypedDict):
    """安全密钥数据"""
    secureCode: str
    pubKey: str


class APIResponse(TypedDict):
    """API 响应数据结构"""
    status: int
    message: str
    data: SecureKeyData
    success: bool


class CrawlResult(TypedDict):
    """爬虫结果数据结构"""
    timestamp: str
    success: bool
    data: NotRequired[APIResponse]
    error: NotRequired[str | None]


class CacheItem(CrawlResult):
    """缓存项（继承自 CrawlResult）"""
    pass


class CacheManager:
    """管理缓存文件的读写"""

    def __init__(self, cache_file: str) -> None:
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[CacheItem]:
        """加载已有缓存数据"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"缓存文件 {self.cache_file} 格式错误，将创建新文件")
                return []
        return []

    def save(self, data: List[CacheItem]) -> None:
        """保存数据到缓存文件"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到 {self.cache_file}")

    def append(self, item: CrawlResult) -> None:
        """追加数据到缓存文件"""
        data: List[CacheItem] = self.load()
        data.append(item)  # type: ignore
        self.save(data)


class SGCC_PublicKey_Crawler:
    """
        国家电网: publicKey
        {
            "status": 0,
            "message": "Success",
            "data": {
                "secureCode": "0b20f38e205349e8b850660bc61e0f23",
                "pubKey": "0402dd60574dc653acab92f476192e68afb6c4c84235cac0a07b09db4297d603b819a154f972614fa38b33ced4197a2ccbe621ba39f78f9d2eb1da36ff902ee8c8"
            },
            "success": true
        }
    """


    def __init__(self, delay: float = 2.0, timeout: int = 10):
        self.delay = delay
        self.timeout = timeout
        self.url = "https://pmos.he.sgcc.com.cn/px-common-authcenter/auth/v2/secureKey/get"
        self.headers = {
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

    def fetch_captcha(self) -> CrawlResult:
        """发送单次请求，返回爬虫结果"""
        timestamp = datetime.now().isoformat()
        result: CrawlResult = {
            'timestamp': timestamp,
            'success': False,
            'error': None
        }

        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                data="{}",
                timeout=self.timeout
            )

            if response.status_code == 200:
                try:
                    api_response: APIResponse = response.json()
                    result['data'] = api_response
                    result['success'] = True
                    logger.info("请求成功")
                except json.JSONDecodeError as e:
                    result['error'] = f"JSON 解析失败: {str(e)}"
                    logger.error(result['error'])
            else:
                result['error'] = f"HTTP 错误: {response.status_code}"
                logger.error(result['error'])

        except requests.exceptions.Timeout:
            result['error'] = "请求超时"
            logger.error(result['error'])
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"连接错误: {str(e)}"
            logger.error(result['error'])
        except Exception as e:
            result['error'] = f"未知错误: {str(e)}"
            logger.error(result['error'])

        return result

    def run(self, count: int, cache_manager: CacheManager) -> Dict[str, int]:
        """执行爬取任务，返回统计信息"""
        logger.info(f"开始爬取，共 {count} 个请求，间隔 {self.delay} 秒")

        success_count = 0
        fail_count = 0

        for i in range(1, count + 1):
            logger.info(f"正在请求 {i}/{count}...")

            result: CrawlResult = self.fetch_captcha()
            cache_manager.append(result)

            if result['success']:
                success_count += 1
            else:
                fail_count += 1

            # 最后一次请求不延迟
            if i < count:
                time.sleep(self.delay)

        return {
            'total': count,
            'success': success_count,
            'failed': fail_count
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='国家电网')
    parser.add_argument('--count', type=int, default=1, help='请求个数（默认: 1）')
    parser.add_argument('--delay', type=float, default=4.0, help='请求间隔秒数（默认: 4.0）')
    parser.add_argument('--output', type=str, default='cache/sgcc_he_publicKey.json', help='输出文件路径（默认: cache/sgcc_he_publicKey.json）')
    args = parser.parse_args()

    # 初始化
    cache_manager = CacheManager(args.output)
    crawler = SGCC_PublicKey_Crawler(delay=args.delay)

    # 执行爬取
    start_time = time.time()
    stats = crawler.run(args.count, cache_manager)
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 输出统计
    logger.info("=" * 50)
    logger.info("爬取完成！")
    logger.info(f"总请求数: {stats['total']}")
    logger.info(f"成功: {stats['success']}")
    logger.info(f"失败: {stats['failed']}")
    logger.info(f"耗时: {elapsed_time:.2f} 秒")
    logger.info(f"缓存文件: {args.output}")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()