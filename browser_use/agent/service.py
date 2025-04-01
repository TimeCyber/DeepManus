import asyncio
from datetime import datetime
from typing import Dict, Any

class BrowserAgent:
    def __init__(self, controller: BrowserController):
        self.controller = controller
        self.history = AgentHistoryList()
        self.llm = LiteLLM(model="deepseek-chat")
        
    async def _handle_date_input(self, element_index: int, date_str: str) -> bool:
        """处理日期输入的特殊情况"""
        try:
            # 点击日期选择器
            await self.controller.click_element(element_index)
            await asyncio.sleep(1)  # 等待日期选择器打开
            
            # 解析日期
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # 选择年份
            year_element = await self.controller.page.query_selector(f"text={date_obj.year}")
            if year_element:
                await year_element.click()
                await asyncio.sleep(0.5)
            
            # 选择月份
            month_element = await self.controller.page.query_selector(f"text={date_obj.month}")
            if month_element:
                await month_element.click()
                await asyncio.sleep(0.5)
            
            # 选择日期
            day_element = await self.controller.page.query_selector(f"text={date_obj.day}")
            if day_element:
                await day_element.click()
                await asyncio.sleep(0.5)
            
            return True
        except Exception as e:
            logger.error(f"Error handling date input: {str(e)}")
            return False
            
    async def _execute_action(self, action: Dict[str, Any]) -> bool:
        """执行单个动作"""
        try:
            action_type = list(action.keys())[0]
            action_data = action[action_type]
            
            if action_type == "input_text":
                # 检查是否是日期输入
                if "date" in str(action_data.get("text", "")).lower():
                    return await self._handle_date_input(
                        action_data["index"],
                        action_data["text"]
                    )
                return await self.controller.input_text(
                    action_data["index"],
                    action_data["text"]
                )
            elif action_type == "click_element":
                return await self.controller.click_element(action_data["index"])
            elif action_type == "done":
                return True
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {str(e)}")
            return False

    async def cleanup(self):
        """
        清理浏览器代理资源
        """
        try:
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.error(f"关闭浏览器时发生错误: {e}")
                finally:
                    self.browser = None
                
            if self.context:
                try:
                    await self.context.close()
                except Exception as e:
                    logger.error(f"关闭浏览器上下文时发生错误: {e}")
                finally:
                    self.context = None
                
            if self.page:
                try:
                    await self.page.close()
                except Exception as e:
                    logger.error(f"关闭页面时发生错误: {e}")
                finally:
                    self.page = None
                
            logger.info("浏览器代理资源已清理")
        except Exception as e:
            logger.error(f"清理浏览器代理资源时发生错误: {e}")
            raise


