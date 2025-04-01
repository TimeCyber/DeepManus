import logging
import os
import requests
import time
import random
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WebClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 请求限制参数
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 最小请求间隔(秒)
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 5  # 初始重试延迟(秒)
        
    def _wait_for_rate_limit(self):
        """等待请求间隔以避免触发速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed + random.uniform(0.5, 1.5)
            logger.debug(f"等待 {sleep_time:.2f} 秒以避免触发速率限制")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """获取代理配置（如果有设置）"""
        proxy_url = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
        if proxy_url:
            return {'http': proxy_url, 'https': proxy_url}
        return None
        
    def crawl(self, url: str, return_format: str = "html") -> str:
        """
        爬取网页内容，带重试机制
        
        Args:
            url: 要爬取的网页URL
            return_format: 返回格式，目前只支持"html"
            
        Returns:
            str: 网页的HTML内容
        """
        proxies = self._get_proxy()
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                # 等待以避免速率限制
                self._wait_for_rate_limit()
                
                # 添加随机延迟
                if retry_count > 0:
                    delay = self.retry_delay * (2 ** (retry_count - 1)) + random.uniform(0, 2)
                    logger.info(f"第 {retry_count} 次重试，等待 {delay:.2f} 秒...")
                    time.sleep(delay)
                
                # 发送请求
                response = self.session.get(
                    url, 
                    proxies=proxies,
                    timeout=15,
                    allow_redirects=True
                )
                
                # 检查状态码
                if response.status_code == 429:  # Too Many Requests
                    retry_after = response.headers.get('Retry-After')
                    wait_time = int(retry_after) if retry_after and retry_after.isdigit() else self.retry_delay * 2
                    logger.warning(f"收到429响应，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    retry_count += 1
                    continue
                    
                response.raise_for_status()  # 检查其他HTTP错误
                
                if return_format == "html":
                    return response.text
                else:
                    raise ValueError(f"不支持的返回格式: {return_format}")
                    
            except requests.RequestException as e:
                last_error = e
                logger.warning(f"请求失败 ({retry_count+1}/{self.max_retries+1}): {e}")
                retry_count += 1
                
                # 对于某些错误，我们可能需要更长的等待时间
                if isinstance(e, requests.exceptions.ConnectionError):
                    time.sleep(self.retry_delay * 2)
            
        # 如果所有重试都失败了
        logger.error(f"爬取网页时发生错误，重试 {self.max_retries} 次后仍然失败: {last_error}")
        raise last_error or requests.RequestException(f"爬取 {url} 失败，已重试 {self.max_retries} 次")
