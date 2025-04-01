import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio
import uuid

from src.config import TEAM_MEMBER_CONFIGRATIONS, TEAM_MEMBERS
from src.graph import build_graph
from src.tools.browser import browser_tool
from langchain_community.adapters.openai import convert_message_to_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()

# Cache for coordinator messages
MAX_CACHE_SIZE = 3

# Global variable to track current browser tool instance
current_browser_tool: Optional[browser_tool] = None


async def initialize_workflow(
    messages: List[Dict[str, str]],
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
    team_members: Optional[List[str]] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    初始化工作流
    
    Args:
        messages: 消息列表
        debug: 是否启用调试模式
        deep_thinking_mode: 是否启用深度思考模式
        search_before_planning: 是否在规划前进行搜索
        team_members: 团队成员列表
        
    Yields:
        Dict[str, Any]: 工作流事件
    """
    if not messages:
        raise ValueError("输入消息不能为空")

    if debug:
        enable_debug_logging()

    logger.info(f"开始工作流，用户输入: {messages}")

    workflow_id = str(uuid.uuid4())
    team_members = team_members if team_members else TEAM_MEMBERS
    streaming_llm_agents = [*team_members, "planner", "coordinator"]

    # 重置协调器缓存
    global current_browser_tool
    coordinator_cache = []
    current_browser_tool = browser_tool
    is_handoff_case = False
    is_workflow_triggered = False

    try:
        async for event in graph.astream_events(
            {
                # 常量
                "TEAM_MEMBERS": team_members,
                "TEAM_MEMBER_CONFIGRATIONS": TEAM_MEMBER_CONFIGRATIONS,
                # 运行时变量
                "messages": messages,
                "deep_thinking_mode": deep_thinking_mode,
                "search_before_planning": search_before_planning,
            },
            version="v2",
        ):
            kind = event.get("event")
            data = event.get("data")
            name = event.get("name")
            metadata = event.get("metadata")
            node = (
                ""
                if (metadata.get("checkpoint_ns") is None)
                else metadata.get("checkpoint_ns").split(":")[0]
            )
            langgraph_step = (
                ""
                if (metadata.get("langgraph_step") is None)
                else str(metadata["langgraph_step"])
            )
            run_id = "" if (event.get("run_id") is None) else str(event["run_id"])

            if kind == "on_chain_start" and name in streaming_llm_agents:
                if name == "planner":
                    is_workflow_triggered = True
                    yield {
                        "event": "start_of_workflow",
                        "data": {
                            "workflow_id": workflow_id,
                            "input": messages,
                        },
                    }
                yield {
                    "event": "start_of_agent",
                    "data": {
                        "agent_name": name,
                        "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                    },
                }
            elif kind == "on_chain_end" and name in streaming_llm_agents:
                yield {
                    "event": "end_of_agent",
                    "data": {
                        "agent_name": name,
                        "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                    },
                }
            elif kind == "on_chat_model_start" and node in streaming_llm_agents:
                yield {
                    "event": "start_of_llm",
                    "data": {"agent_name": node},
                }
            elif kind == "on_chat_model_end" and node in streaming_llm_agents:
                yield {
                    "event": "end_of_llm",
                    "data": {"agent_name": node},
                }
            elif kind == "on_chat_model_stream" and node in streaming_llm_agents:
                content = data["chunk"].content
                if content is None or content == "":
                    if not data["chunk"].additional_kwargs.get("reasoning_content"):
                        continue
                    yield {
                        "event": "message",
                        "data": {
                            "message_id": data["chunk"].id,
                            "delta": {
                                "reasoning_content": (
                                    data["chunk"].additional_kwargs["reasoning_content"]
                                )
                            },
                        },
                    }
                else:
                    if node == "coordinator":
                        if len(coordinator_cache) < MAX_CACHE_SIZE:
                            coordinator_cache.append(content)
                            cached_content = "".join(coordinator_cache)
                            if cached_content.startswith("handoff"):
                                is_handoff_case = True
                                continue
                            if len(coordinator_cache) < MAX_CACHE_SIZE:
                                continue
                            yield {
                                "event": "message",
                                "data": {
                                    "message_id": data["chunk"].id,
                                    "delta": {"content": cached_content},
                                },
                            }
                        elif not is_handoff_case:
                            yield {
                                "event": "message",
                                "data": {
                                    "message_id": data["chunk"].id,
                                    "delta": {"content": content},
                                },
                            }
                    else:
                        yield {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": content},
                            },
                        }
            elif kind == "on_tool_start" and node in team_members:
                yield {
                    "event": "tool_call",
                    "data": {
                        "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                        "tool_name": name,
                        "tool_input": data.get("input"),
                    },
                }
            elif kind == "on_tool_end" and node in team_members:
                yield {
                    "event": "tool_call_result",
                    "data": {
                        "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                        "tool_name": name,
                        "tool_result": (
                            data["output"].content if data.get("output") else ""
                        ),
                    },
                }
            else:
                continue

        if is_workflow_triggered:
            yield {
                "event": "end_of_workflow",
                "data": {
                    "workflow_id": workflow_id,
                    "messages": [
                        convert_message_to_dict(msg)
                        for msg in data["output"].get("messages", [])
                    ],
                },
            }
        yield {
            "event": "final_session_state",
            "data": {
                "messages": [
                    convert_message_to_dict(msg)
                    for msg in data["output"].get("messages", [])
                ],
            },
        }
    except Exception as e:
        logger.error(f"工作流初始化过程中发生错误: {e}")
        raise


async def run_agent_workflow(
    messages: List[Dict[str, str]],
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
    team_members: Optional[List[str]] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    运行代理工作流
    
    Args:
        messages: 消息列表
        debug: 是否启用调试模式
        deep_thinking_mode: 是否启用深度思考模式
        search_before_planning: 是否在规划前进行搜索
        team_members: 团队成员列表
        
    Yields:
        Dict[str, Any]: 工作流事件
    """
    try:
        # 直接使用initialize_workflow的异步生成器
        async for event in initialize_workflow(
            messages, debug, deep_thinking_mode, search_before_planning, team_members
        ):
            yield event
            
    except asyncio.CancelledError:
        logger.info("工作流被取消，正在清理资源...")
        # 确保浏览器代理被正确清理
        if current_browser_tool:
            try:
                await current_browser_tool.cleanup()
            except Exception as e:
                logger.error(f"清理浏览器代理时发生错误: {e}")
        raise
    except Exception as e:
        logger.error(f"工作流执行过程中发生错误: {e}")
        # 确保浏览器代理被正确清理
        if current_browser_tool:
            try:
                await current_browser_tool.cleanup()
            except Exception as cleanup_error:
                logger.error(f"清理浏览器代理时发生错误: {cleanup_error}")
        yield {
            "event": "error",
            "data": {"error": str(e)}
        }
    finally:
        # 确保所有资源都被清理
        if current_browser_tool:
            try:
                await current_browser_tool.cleanup()
            except Exception as e:
                logger.error(f"清理浏览器代理资源时发生错误: {e}")
