import sys

from .article import Article
from .jina_client import WebClient
from .readability_extractor import ReadabilityExtractor


class Crawler:
    def crawl(self, url: str) -> Article:
        """
        爬取网页并提取文章内容
        
        Args:
            url: 要爬取的网页URL
            
        Returns:
            Article: 包含提取的文章内容的对象
        """
        # 使用WebClient获取网页内容
        web_client = WebClient()
        html = web_client.crawl(url, return_format="html")
        
        # 使用ReadabilityExtractor提取文章内容
        extractor = ReadabilityExtractor()
        article = extractor.extract_article(html)
        article.url = url
        return article


if __name__ == "__main__":
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = "https://fintel.io/zh-hant/s/br/nvdc34"
    crawler = Crawler()
    article = crawler.crawl(url)
    print(article.to_markdown())
