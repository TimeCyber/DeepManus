"""
Server script for running the DeepManus API.
"""

import logging
import uvicorn
import sys
import os
import signal
import atexit

from src.playwright_manager import ensure_playwright_server, shutdown_playwright_server
from src.llms.litellm_config import configure_litellm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def cleanup_resources():
    """清理所有资源，确保程序正常退出"""
    logger.info("正在关闭服务器并清理资源...")
    shutdown_playwright_server()
    logger.info("资源清理完成")

if __name__ == "__main__":
    logger.info("Starting DeepManus API server")
    
    # 配置LiteLLM
    configure_litellm()
    
    # 启动Playwright服务器
    if not ensure_playwright_server():
        logger.error("无法启动Playwright服务器，服务将无法使用浏览器功能")
    
    # 注册清理函数
    atexit.register(cleanup_resources)
    
    # 处理信号以确保优雅关闭
    for sig in [signal.SIGINT, signal.SIGTERM]:
        if hasattr(signal, str(sig)):
            signal.signal(sig, lambda sig, frame: cleanup_resources())
    
    # 启动服务器
    reload = True
    if sys.platform.startswith("win"):
        reload = False
    port = int(os.getenv("PORT", 8000))
    
    try:
        uvicorn.run(
            "src.api.app:app",
            host="0.0.0.0",
            port=port,
            reload=reload,
            log_level="info",
        )
    finally:
        cleanup_resources()
