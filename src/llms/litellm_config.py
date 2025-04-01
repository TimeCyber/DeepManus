"""
LiteLLM配置文件，提供增强的错误处理和重试机制
"""

import litellm
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

def configure_litellm():
    """配置LiteLLM的全局行为以提高稳定性"""
    # 启用请求缓存
    try:
        litellm.cache = litellm.Cache(type="local")
    except Exception as e:
        logger.warning(f"设置LiteLLM缓存失败: {e}")
    
    # 配置重试机制
    litellm.num_retries = 3  # 失败后重试3次
    litellm.request_timeout = 120  # 默认超时时间120秒
    
    # 特定模型配置
    litellm.model_config = {
        "deepseek/deepseek-chat": {
            "api_base": os.getenv("REASONING_BASE_URL", "https://api.deepseek.com"),
            "api_key": os.getenv("REASONING_API_KEY", ""),
            "timeout": 180,  # 更长的超时时间
            "max_retries": 5  # 更多重试次数
        }
    }
    
    # 配置指数退避重试
    litellm.retry_after = True
    
    # 错误处理
    try:
        # 尝试注册回调函数处理错误 (litellm 1.65.0+)
        if hasattr(litellm, 'callbacks'):
            class ErrorCallback:
                def on_retry(self, kwargs: Dict[str, Any]) -> None:
                    logger.info(f"重试LiteLLM API调用: {kwargs.get('exception', '未知错误')}")

                def on_error(self, kwargs: Dict[str, Any]) -> None:
                    logger.warning(f"LiteLLM错误: {kwargs.get('exception', '未知错误')}")
            
            litellm.callbacks.append(ErrorCallback())
            logger.info("已注册LiteLLM错误回调处理")
        
        # 尝试使用异常处理器API (如果可用)
        elif hasattr(litellm, 'set_exception_handler'):
            def _handle_error(exception, **kwargs):
                logger.warning(f"LiteLLM错误被捕获: {str(exception)} - 将尝试重试")
                return True  # 返回True表示重试请求
            
            litellm.set_exception_handler(_handle_error)
            logger.info("已设置LiteLLM异常处理器")
    except Exception as e:
        logger.warning(f"配置LiteLLM异常处理机制失败: {e}")
    
    logger.info("LiteLLM已配置，启用缓存和重试机制") 