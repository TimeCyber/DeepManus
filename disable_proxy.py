"""
禁用代理的脚本，用于处理连接问题
"""
import os

# 清除可能存在的代理环境变量
proxy_env_vars = [
    'HTTP_PROXY', 'http_proxy',
    'HTTPS_PROXY', 'https_proxy',
    'NO_PROXY', 'no_proxy'
]

# 清除这些环境变量
for var in proxy_env_vars:
    if var in os.environ:
        print(f"删除环境变量: {var}={os.environ[var]}")
        del os.environ[var]
    else:
        print(f"环境变量 {var} 不存在")

# 显示清除后的环境变量
print("\n清除后的代理环境变量:")
for var in proxy_env_vars:
    print(f"{var}={'不存在' if var not in os.environ else os.environ[var]}")

print("\n使用方法: 在启动应用前运行此脚本，或者在代码中导入它")
print("import disable_proxy  # 在主程序开头导入") 