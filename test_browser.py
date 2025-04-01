"""
测试浏览器功能的简单脚本
"""
import asyncio
import logging
import sys

from src.playwright_manager import ensure_playwright_server, shutdown_playwright_server
from src.tools.browser import browser_tool

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_browser():
    """测试浏览器功能"""
    try:
        # 确保Playwright服务器已启动
        if not ensure_playwright_server():
            logger.error("无法启动Playwright服务器")
            return False
        
        # 执行简单的浏览器任务
        logger.info("执行浏览器任务: 访问百度")
        result = await browser_tool._arun("打开百度首页并截图")
        
        logger.info(f"浏览器任务结果: {result}")
        return True
    except Exception as e:
        logger.error(f"测试浏览器功能时发生错误: {e}")
        return False
    finally:
        # 清理资源
        await browser_tool.cleanup()
        shutdown_playwright_server()

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_browser())
    sys.exit(0 if success else 1) 