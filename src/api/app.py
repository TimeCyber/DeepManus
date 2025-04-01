"""
FastAPI application for DeepManus.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import asyncio
from typing import AsyncGenerator, Dict, List, Any

from src.graph import build_graph
from src.config import TEAM_MEMBERS, TEAM_MEMBER_CONFIGRATIONS, BROWSER_HISTORY_DIR
from src.service.workflow_service import run_agent_workflow
from src.playwright_manager import ensure_playwright_server
from src.llms.litellm_config import configure_litellm

# 配置LiteLLM
configure_litellm()

# 确保Playwright服务器已启动
ensure_playwright_server()

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DeepManus API",
    description="API for DeepManus LangGraph-based agent workflow",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the graph
graph = build_graph()


class ContentItem(BaseModel):
    type: str = Field(..., description="The type of content (text, image, etc.)")
    text: Optional[str] = Field(None, description="The text content if type is 'text'")
    image_url: Optional[str] = Field(
        None, description="The image URL if type is 'image'"
    )


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="The role of the message sender (user or assistant)"
    )
    content: Union[str, List[ContentItem]] = Field(
        ...,
        description="The content of the message, either a string or a list of content items",
    )


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="The conversation history")
    debug: Optional[bool] = Field(False, description="Whether to enable debug logging")
    deep_thinking_mode: Optional[bool] = Field(
        False, description="Whether to enable deep thinking mode"
    )
    search_before_planning: Optional[bool] = Field(
        False, description="Whether to search before planning"
    )
    team_members: Optional[list] = Field(None, description="enabled team members")


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    处理聊天请求的流式响应
    
    Args:
        request: 聊天请求对象
        
    Returns:
        EventSourceResponse: 事件流响应
    """
    try:
        # Convert Pydantic models to dictionaries and normalize content format
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role}

            # Handle both string content and list of content items
            if isinstance(msg.content, str):
                message_dict["content"] = msg.content
            else:
                # For content as a list, convert to the format expected by the workflow
                content_items = []
                for item in msg.content:
                    if item.type == "text" and item.text:
                        content_items.append({"type": "text", "text": item.text})
                    elif item.type == "image" and item.image_url:
                        content_items.append(
                            {"type": "image", "image_url": item.image_url}
                        )

                message_dict["content"] = content_items

            messages.append(message_dict)

        async def event_generator():
            try:
                async for event in run_agent_workflow(
                    messages,
                    request.debug,
                    request.deep_thinking_mode,
                    request.search_before_planning,
                    request.team_members,
                ):
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"], ensure_ascii=False),
                    }
            except asyncio.CancelledError:
                logger.info("流处理被取消")
                raise
            except Exception as e:
                logger.error(f"工作流中发生错误: {e}")
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)}, ensure_ascii=False)
                }

        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            sep="\n",
        )
    except Exception as e:
        logger.error(f"聊天端点发生错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/browser_history/{filename}")
async def get_browser_history_file(filename: str):
    """
    Get a specific browser history GIF file.

    Args:
        filename: The filename of the GIF to retrieve

    Returns:
        The GIF file
    """
    try:
        file_path = os.path.join(BROWSER_HISTORY_DIR, filename)
        if not os.path.exists(file_path) or not filename.endswith(".gif"):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, media_type="image/gif", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving browser history file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/team_members")
async def get_team_members():
    """
    Get the configuration of all team members.

    Returns:
        dict: A dictionary containing team member configurations
    """
    try:
        return {"team_members": TEAM_MEMBER_CONFIGRATIONS}
    except Exception as e:
        logger.error(f"Error getting team members: {e}")
        raise HTTPException(status_code=500, detail=str(e))
