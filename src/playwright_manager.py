"""
管理Playwright服务器启动和停止的模块
"""

import subprocess
import logging
import os
import signal
import time
import platform
import atexit
import sys
from pathlib import Path
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

class PlaywrightManager:
    """管理Playwright服务器的类"""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.is_running = False
        
    def _find_npm_executable(self) -> Optional[str]:
        """
        查找npm或npx可执行文件的路径
        
        Returns:
            Optional[str]: npm或npx可执行文件的路径，如果未找到则返回None
        """
        npm_commands = ["npm", "npm.cmd"] if platform.system() == "Windows" else ["npm"]
        npx_commands = ["npx", "npx.cmd"] if platform.system() == "Windows" else ["npx"]
        
        # 首先查找npx，因为这是我们优先使用的命令
        for cmd in npx_commands:
            try:
                result = subprocess.run(
                    ["where" if platform.system() == "Windows" else "which", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split("\n")[0]
            except Exception:
                pass
        
        # 如果没有找到npx，查找npm
        for cmd in npm_commands:
            try:
                result = subprocess.run(
                    ["where" if platform.system() == "Windows" else "which", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split("\n")[0]
            except Exception:
                pass
        
        return None
    
    def _check_playwright_installed(self) -> bool:
        """
        检查是否已安装Playwright
        
        Returns:
            bool: 如果安装了Playwright，则返回True
        """
        try:
            # 尝试查找已安装的playwright
            npm_path = self._find_npm_executable()
            if not npm_path:
                logger.warning("未找到npm或npx命令")
                return False
            
            # 确定是npx还是npm
            is_npx = os.path.basename(npm_path).startswith("npx")
            
            # 运行相应的命令来检查playwright是否已安装
            if is_npx:
                cmd = [npm_path, "playwright", "--version"]
            else:
                cmd = [npm_path, "exec", "playwright", "--", "--version"]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            
            return result.returncode == 0 and "Version" in result.stdout
        except Exception as e:
            logger.warning(f"检查Playwright安装状态时出错: {e}")
            return False
    
    def _install_playwright(self) -> bool:
        """
        安装Playwright及其依赖项
        
        Returns:
            bool: 安装成功则返回True
        """
        try:
            logger.info("正在安装Playwright...")
            
            # 首先尝试使用Python安装Playwright
            try:
                logger.info("尝试使用Python安装Playwright...")
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # 使用python -m playwright install
                result = subprocess.run(
                    [sys.executable, "-m", "playwright", "install"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                    startupinfo=startupinfo
                )
                
                if result.returncode == 0:
                    logger.info("使用Python成功安装Playwright")
                    return True
                else:
                    logger.warning(f"使用Python安装Playwright失败: {result.stderr}")
            except Exception as e:
                logger.warning(f"使用Python安装Playwright出错: {e}")
            
            # 如果Python安装失败，尝试使用npm
            npm_path = self._find_npm_executable()
            if not npm_path:
                logger.error("未找到npm或npx命令，无法安装Playwright")
                return False
            
            # 确定是npx还是npm
            is_npx = os.path.basename(npm_path).startswith("npx")
            
            # 安装playwright
            if is_npx:
                # 在Windows上，直接使用npm替代npx可能更稳定
                if platform.system() == "Windows":
                    npm_dir = os.path.dirname(npm_path)
                    npm_exe = os.path.join(npm_dir, "npm.cmd" if os.path.exists(os.path.join(npm_dir, "npm.cmd")) else "npm")
                    if os.path.exists(npm_exe):
                        install_cmd = [npm_exe, "install", "-g", "playwright"]
                    else:
                        install_cmd = [npm_path, "playwright", "install", "--with-deps"]
                else:
                    install_cmd = [npm_path, "playwright", "install", "--with-deps"]
            else:
                install_cmd = [npm_path, "install", "-g", "playwright"]
            
            logger.info(f"运行安装命令: {' '.join(install_cmd)}")
            
            # 使用subprocess启动安装程序，不显示窗口
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(
                install_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                startupinfo=startupinfo
            )
            
            if result.returncode != 0:
                logger.error(f"安装Playwright失败: {result.stderr}")
                return False
            
            # 安装浏览器
            if is_npx:
                if platform.system() == "Windows":
                    npm_dir = os.path.dirname(npm_path)
                    npx_exe = os.path.join(npm_dir, "npx.cmd" if os.path.exists(os.path.join(npm_dir, "npx.cmd")) else "npx")
                    browsers_cmd = [npx_exe, "playwright", "install"]
                else:
                    browsers_cmd = [npm_path, "playwright", "install"]
            else:
                browsers_cmd = [npm_path, "exec", "playwright", "--", "install"]
            
            result = subprocess.run(
                browsers_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                startupinfo=startupinfo
            )
            
            if result.returncode != 0:
                logger.error(f"安装Playwright浏览器失败: {result.stderr}")
                return False
            
            logger.info("Playwright安装完成")
            return True
            
        except Exception as e:
            logger.error(f"安装Playwright时发生错误: {e}")
            return False
    
    def _get_server_command(self) -> Optional[List[str]]:
        """
        获取启动Playwright服务器的命令
        
        Returns:
            Optional[List[str]]: 命令列表，如果无法确定则返回None
        """
        npm_path = self._find_npm_executable()
        if not npm_path:
            logger.error("未找到npm或npx命令")
            return None
        
        # 确定是npx还是npm
        is_npx = os.path.basename(npm_path).startswith("npx")
        
        # 返回适当的命令
        if is_npx:
            return [npm_path, "playwright", "run-server"]
        else:
            return [npm_path, "exec", "playwright", "--", "run-server"]
    
    def start_server(self) -> bool:
        """
        启动Playwright MCP服务器
        
        Returns:
            bool: 是否成功启动服务器
        """
        if self.is_running:
            logger.info("Playwright MCP服务器已在运行")
            return True
            
        try:
            # 检查是否安装了Playwright
            if not self._check_playwright_installed():
                logger.warning("未检测到Playwright安装，尝试安装...")
                if not self._install_playwright():
                    logger.error("无法安装Playwright，服务器无法启动")
                    return False
            
            # 尝试优雅地停止任何现有实例
            self._kill_existing_instances()
            
            # 尝试使用Python的playwright启动服务器
            try:
                logger.info("尝试使用Python启动Playwright服务器...")
                
                # 使用subprocess启动服务器，不显示窗口
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                self.server_process = subprocess.Popen(
                    [sys.executable, "-m", "playwright", "run-server"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo
                )
                
                # 等待服务器启动
                time.sleep(3)
                
                # 检查进程是否仍在运行
                if self.server_process.poll() is None:
                    self.is_running = True
                    logger.info("Playwright MCP服务器已使用Python启动")
                    
                    # 注册程序退出时关闭服务器
                    atexit.register(self.stop_server)
                    
                    return True
                else:
                    stdout, stderr = self.server_process.communicate()
                    logger.warning(f"使用Python启动Playwright服务器失败: {stderr.decode('utf-8', errors='ignore')}")
            except Exception as e:
                logger.warning(f"使用Python启动Playwright服务器出错: {e}")
            
            # 如果Python启动失败，尝试使用npm
            # 获取启动命令
            cmd = self._get_server_command()
            if not cmd:
                logger.error("无法确定启动Playwright服务器的命令")
                return False
            
            # 启动服务器
            logger.info(f"启动Playwright MCP服务器: {' '.join(cmd)}")
            
            # 使用subprocess启动服务器，不显示窗口
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # 创建node_modules/.bin目录（如果不存在），这可能是playwright查找的位置
            node_modules_bin = Path.cwd() / "node_modules" / ".bin"
            node_modules_bin.mkdir(parents=True, exist_ok=True)
            
            # 更新环境变量，确保PATH包含npm路径
            env = os.environ.copy()
            npm_dir = os.path.dirname(self._find_npm_executable() or "")
            if npm_dir:
                if platform.system() == "Windows":
                    env["PATH"] = f"{npm_dir};{env.get('PATH', '')}"
                else:
                    env["PATH"] = f"{npm_dir}:{env.get('PATH', '')}"
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                env=env
            )
            
            # 等待服务器启动
            time.sleep(3)
            
            # 检查进程是否仍在运行
            if self.server_process.poll() is None:
                self.is_running = True
                logger.info("Playwright MCP服务器已启动")
                
                # 注册程序退出时关闭服务器
                atexit.register(self.stop_server)
                
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                logger.error(f"启动Playwright MCP服务器失败: {stderr.decode('utf-8', errors='ignore')}")
                return False
                
        except Exception as e:
            logger.error(f"启动Playwright MCP服务器时发生错误: {str(e)}")
            return False
    
    def stop_server(self) -> bool:
        """
        停止Playwright MCP服务器
        
        Returns:
            bool: 是否成功停止服务器
        """
        if not self.is_running or self.server_process is None:
            return True
            
        try:
            logger.info("停止Playwright MCP服务器...")
            
            # Windows和POSIX系统有不同的终止进程方法
            if platform.system() == "Windows":
                self.server_process.terminate()
            else:
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                
            # 等待进程终止
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果超时，强制终止
                if platform.system() == "Windows":
                    self.server_process.kill()
                else:
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
            
            self.is_running = False
            self.server_process = None
            logger.info("Playwright MCP服务器已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止Playwright MCP服务器时发生错误: {str(e)}")
            return False
    
    def _kill_existing_instances(self):
        """尝试终止可能正在运行的现有实例"""
        try:
            if platform.system() == "Windows":
                # Windows上使用taskkill终止所有playwright进程
                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "playwright.cmd", "/T"], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo
                    )
                except Exception:
                    pass
                    
                # 也尝试终止Node进程
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/FI", "IMAGENAME eq node.exe", "/FI", "WINDOWTITLE eq *playwright*"], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo
                    )
                except Exception:
                    pass
            else:
                # Linux/Mac上使用pkill
                try:
                    subprocess.run(
                        ["pkill", "-f", "playwright"], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"尝试清理现有Playwright实例时出错: {e}")


# 创建全局管理器实例
playwright_manager = PlaywrightManager()


def ensure_playwright_server():
    """确保Playwright服务器正在运行"""
    return playwright_manager.start_server()


def shutdown_playwright_server():
    """关闭Playwright服务器"""
    return playwright_manager.stop_server() 