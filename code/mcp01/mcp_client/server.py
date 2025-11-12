from mcp.server.fastmcp import FastMCP
 
# 初始化FastMCP服务器
mcp = FastMCP("filesystem")
 
@mcp.tool()
async def create_file(file_name: str, content: str) -> str:
    """
    创建文件
    :param file_name: 文件名
    :param content: 文件内容
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
        return "创建成功"
 
@mcp.tool()
async def read_file(file_name: str) -> str:
    """
    读取文件内容
    :param file_name: 文件名
    """
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read()
 
@mcp.tool()
async def write_file(file_name: str, content: str) -> str:
    """
    写入文件内容
    :param file_name: 文件名
    :param content: 文件内容
    """
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
        return "写入成功"
 
if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    print("MCP 聊天服务器已启动！")
    mcp.run(transport="stdio")
 