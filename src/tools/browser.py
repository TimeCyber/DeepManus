import asyncio
import logging
import json
import time
import random
from pydantic import BaseModel, Field
from typing import Optional, ClassVar, Type, Dict, Any
from langchain.tools import BaseTool
from browser_use import AgentHistoryList, Browser, BrowserConfig
from browser_use import Agent as BrowserAgent
from src.llms.llm import vl_llm
from src.tools.decorators import create_logged_tool
from src.config import (
    CHROME_INSTANCE_PATH,
    CHROME_HEADLESS,
    CHROME_PROXY_SERVER,
    CHROME_PROXY_USERNAME,
    CHROME_PROXY_PASSWORD,
    BROWSER_HISTORY_DIR,
)
import uuid
import os

# Configure logging
logger = logging.getLogger(__name__)

# 最大重试次数
MAX_BROWSER_RETRIES = 3

def get_browser_config():
    """创建浏览器配置"""
    browser_config = BrowserConfig(
        headless=CHROME_HEADLESS,
        chrome_instance_path=CHROME_INSTANCE_PATH,
    )
    
    # 确保代理配置正确
    if CHROME_PROXY_SERVER:
        proxy_config = {
            "server": CHROME_PROXY_SERVER,
        }
        if CHROME_PROXY_USERNAME:
            proxy_config["username"] = CHROME_PROXY_USERNAME
        if CHROME_PROXY_PASSWORD:
            proxy_config["password"] = CHROME_PROXY_PASSWORD
        browser_config.proxy = proxy_config
    
    return browser_config

# 移除全局浏览器实例
# expected_browser = Browser(config=browser_config)


class BrowserUseInput(BaseModel):
    """Input for WriteFileTool."""

    instruction: str = Field(..., description="The instruction to use browser")


class BrowserTool(BaseTool):
    name: ClassVar[str] = "browser"
    args_schema: Type[BaseModel] = BrowserUseInput
    description: ClassVar[str] = (
        "Use this tool to interact with web browsers. Input should be a natural language description of what you want to do with the browser, such as 'Go to google.com and search for browser-use', or 'Navigate to Reddit and find the top post about AI'."
    )

    _agent: Optional[BrowserAgent] = None
    _browser_instance: Optional[Browser] = None

    def _generate_browser_result(
        self, result_content: str, generated_gif_path: str
    ) -> dict:
        return {
            "result_content": result_content,
            "generated_gif_path": generated_gif_path,
        }

    async def terminate(self):
        """Terminate the browser agent if it exists."""
        if self._agent and hasattr(self._agent, 'browser') and self._agent.browser:
            try:
                await self._agent.browser.close()
            except Exception as e:
                logger.error(f"Error terminating browser agent: {str(e)}")
        
        if self._browser_instance:
            try:
                await self._browser_instance.close()
            except Exception as e:
                logger.error(f"Error closing browser instance: {str(e)}")
                
        self._agent = None
        self._browser_instance = None

    async def cleanup(self):
        """清理浏览器资源"""
        try:
            await self.terminate()
        except Exception as e:
            logger.error(f"清理浏览器资源时发生错误: {str(e)}")
            
        # 确保本地实例变量被正确清理
        self._agent = None
        self._browser_instance = None

    async def _create_browser_with_retry(self):
        """创建浏览器实例，带有重试机制"""
        retry_count = 0
        last_error = None
        
        while retry_count < MAX_BROWSER_RETRIES:
            try:
                # 确保历史目录存在
                os.makedirs(BROWSER_HISTORY_DIR, exist_ok=True)
                
                # 如果存在旧实例，关闭它
                if self._browser_instance:
                    try:
                        await self._browser_instance.close()
                    except Exception:
                        pass
                
                # 创建新的浏览器实例
                self._browser_instance = Browser(config=get_browser_config())
                return self._browser_instance
            except Exception as e:
                last_error = e
                retry_count += 1
                logger.warning(f"创建浏览器实例失败 (尝试 {retry_count}/{MAX_BROWSER_RETRIES}): {e}")
                
                # 指数退避重试
                wait_time = 2 ** retry_count + random.uniform(0, 1)
                logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                await asyncio.sleep(wait_time)
        
        # 如果所有重试都失败了
        logger.error(f"创建浏览器实例失败，已重试 {MAX_BROWSER_RETRIES} 次: {last_error}")
        raise last_error or Exception("创建浏览器实例失败")

    def _run(self, instruction: str) -> str:
        """Run the browser task synchronously."""
        generated_gif_path = f"{BROWSER_HISTORY_DIR}/{uuid.uuid4()}.gif"
        browser = None
        try:
            # 使用事件循环创建浏览器
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                browser = loop.run_until_complete(self._create_browser_with_retry())
                
                self._agent = BrowserAgent(
                    task=instruction,
                    llm=vl_llm,
                    browser=browser,
                    generate_gif=generated_gif_path,
                )

                result = loop.run_until_complete(self._agent.run())
                if isinstance(result, AgentHistoryList):
                    return json.dumps(
                        self._generate_browser_result(
                            result.final_result(), generated_gif_path
                        )
                    )
                else:
                    return json.dumps(
                        self._generate_browser_result(result, generated_gif_path)
                    )
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error executing browser task: {str(e)}")
            return f"Error executing browser task: {str(e)}"
        finally:
            # 确保浏览器被关闭
            if browser:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(browser.close())
                    loop.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")

    async def _arun(self, instruction: str) -> str:
        """Run the browser task asynchronously."""
        generated_gif_path = f"{BROWSER_HISTORY_DIR}/{uuid.uuid4()}.gif"
        browser = None
        try:
            # 使用重试机制创建浏览器
            browser = await self._create_browser_with_retry()
            
            self._agent = BrowserAgent(
                task=instruction,
                llm=vl_llm,
                browser=browser,
                generate_gif=generated_gif_path,
            )
            
            # 添加超时控制
            try:
                result = await asyncio.wait_for(self._agent.run(), timeout=300)  # 5分钟超时
                if isinstance(result, AgentHistoryList):
                    return json.dumps(
                        self._generate_browser_result(
                            result.final_result(), generated_gif_path
                        )
                    )
                else:
                    return json.dumps(
                        self._generate_browser_result(result, generated_gif_path)
                    )
            except asyncio.TimeoutError:
                logger.error("浏览器任务执行超时")
                return json.dumps(
                    self._generate_browser_result(
                        "Browser task timed out after 5 minutes", generated_gif_path
                    )
                )
        except Exception as e:
            logger.error(f"Error executing browser task: {str(e)}")
            return f"Error executing browser task: {str(e)}"
        finally:
            # 确保浏览器被关闭
            if browser:
                try:
                    await browser.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")

    async def _browser_task(self, instruction: str) -> Dict[str, Any]:
        """执行浏览器任务"""
        browser = None
        try:
            # 确保浏览器历史目录存在
            os.makedirs(BROWSER_HISTORY_DIR, exist_ok=True)
            
            # 创建新的浏览器实例
            browser = await Browser.create(
                **get_browser_config()
            )
            
            # 创建新的上下文
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            # 创建新的页面
            page = await context.new_page()
            
            # 设置超时时间
            page.set_default_timeout(60000)
            
            # 创建浏览器控制器
            controller = BrowserController(page)
            
            # 创建浏览器代理
            agent = BrowserAgent(controller)
            
            # 执行任务
            result = await agent.run(instruction)
            
            # 生成GIF
            gif_path = await controller.create_gif()
            
            return {
                "result_content": result,
                "generated_gif_path": gif_path
            }
            
        except Exception as e:
            logger.error(f"Browser task error: {str(e)}")
            raise
        finally:
            if browser:
                try:
                    await browser.close()
                except Exception as e:
                    logger.error(f"Error closing browser: {str(e)}")


BrowserTool = create_logged_tool(BrowserTool)
browser_tool = BrowserTool()

if __name__ == "__main__":
    browser_tool._run(instruction="go to github.com and search DeepManus")
