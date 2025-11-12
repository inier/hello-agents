import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv
from contextlib import AsyncExitStack
 
# 加载 .env 文件
load_dotenv()
 
class MCPClient:
 
    def __init__(self):
        """初始化 MCP 客户端"""
        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("LLM_API_KEY")  # 读取 OpenAI API Key
        self.base_url = os.getenv("LLM_BASE_URL")  # 读取 BASE URL
        self.model = os.getenv("LLM_MODEL_ID")  # 读取 model
 
        if not self.openai_api_key:
            raise ValueError("未找到 API KEY. 请在.env文件中配置API_KEY")
 
        self.client = OpenAI(api_key=self.openai_api_key,
                             base_url=self.base_url)
 
    async def process_query(self, query: str) -> str:
        """调用 OpenAI API 处理用户问题"""
        messages = [{
            "role": "system",
            "content": "你是一个智能助手，帮助用户回答问题。"
        }, {
            "role": "user",
            "content": query
        }]
 
        try:
            # 调用 大模型API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(model=self.model,
                                                            messages=messages))
            return response.choices[0].message.content
        except Exception as e:
            return f"调用模型API时出错: {str(e)}"
 
    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("MCP 客户端已启动！输入 'exit' 退出")
 
        while True:
            try:
                query = input("问: ").strip()
                if query.lower() == 'exit':
                    break
 
                response = await self.process_query(query)
                print(f"AI回复: {response}")
 
            except Exception as e:
                print(f"发生错误: {str(e)}")
 
    async def clean(self):
        """清理资源"""
        await self.exit_stack.aclose()
 
 
async def main():
    client = MCPClient()
    print("MCP 聊天客户端已启动！")
    try:
        await client.chat_loop()
    finally:
        await client.clean()

 
if __name__ == "__main__":
    asyncio.run(main())
 