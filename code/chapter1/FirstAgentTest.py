AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动。
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""


import requests
import json

def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        # 格式化成自然语言返回
        return f"{city}当前天气：{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误：查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"



import os
from tavily import TavilyClient
from dotenv import load_dotenv
from environs import Env
load_dotenv()
# env = Env()
# env.read_env()
def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """

    # 从环境变量或主程序配置中获取API密钥
    api_key = os.environ.get("TAVILY_API_KEY") # 推荐方式
    # 或者，我们可以在主循环中传入，如此处代码所示
    print(api_key)

    if not api_key:
        return "错误：未配置TAVILY_API_KEY。"

    # 2. 初始化Tavily客户端
    tavily = TavilyClient(api_key=api_key)
    
    # 3. 构造一个精确的查询
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
    
    try:
        # 4. 调用API，include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        
        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        
        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        
        if not formatted_results:
             return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误：执行Tavily搜索时出现问题 - {e}"


# 将所有工具函数放入一个字典，方便后续调用
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

from openai import OpenAI

class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        print(f"OpenAI客户端初始化完成: model={model}, base_url={base_url}")

    def generate(self, prompt: str, system_prompt: str) -> str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            print(f"发送请求到模型: {self.model}")
            print(f"消息内容: {messages}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                timeout=30  # 添加30秒超时
            )
            print(f"收到API响应: {type(response)}")
            
            # 更安全地检查响应结构
            if response is None:
                print("API返回空响应")
                return "错误：API返回空响应"
                
            if not hasattr(response, 'choices'):
                print(f"API响应格式错误，缺少choices字段: {response}")
                return "错误：API响应格式不正确"
                
            if len(response.choices) == 0:
                print("API返回空的choices数组")
                return "错误：API未返回任何选择"
                
            if not hasattr(response.choices[0], 'message'):
                print(f"API响应格式错误，choice中缺少message字段: {response.choices[0]}")
                return "错误：API响应格式不正确"
                
            if not hasattr(response.choices[0].message, 'content'):
                print(f"API响应格式错误，message中缺少content字段: {response.choices[0].message}")
                return "错误：API响应内容为空"
                
            answer = response.choices[0].message.content
            print("模型回复:", answer)
            return answer
            
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return f"错误：调用语言模型服务时出错 - {str(e)}"


import re

# --- 1. 配置LLM客户端 ---
# 请根据您使用的服务，将这里替换成对应的凭证和地址
API_KEY = "sk-uxiFGtc00ygZXX6pHDwhH1wrzyubOOvBhHjPaPuYgpFg8e9r"
BASE_URL = "https://sg.uiuiapi.com"
MODEL_ID = "chatgpt-4o-latest"
# os.environ['TAVILY_API_KEY'] = "YOUR_TAVILY_API_KEY"

print(f"初始化LLM客户端: model={MODEL_ID}, base_url={BASE_URL}")
llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 2. 初始化 ---
user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "="*40)

# --- 3. 运行主循环 ---
for i in range(5): # 设置最大循环次数
    print(f"--- 循环 {i+1} ---\n")
    
    # 3.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)
    
    # 3.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)
    
    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        print("解析错误：模型输出中未找到 Action。")
        break
    action_str = action_match.group(1).strip()

    if action_str.startswith("finish"):
        finish_match = re.search(r'finish\(answer="((?:[^"\\]|\\.)*)"\)', action_str)
        if finish_match:
            final_answer = finish_match.group(1)
            # 处理转义字符
            final_answer = final_answer.replace('\\"', '"').replace('\\n', '\n')
            print(f"任务完成，最终答案: {final_answer}")
        else:
            print(f"无法解析finish动作: {action_str}")
        break
    
    # 更安全地提取工具名和参数
    tool_match = re.search(r"(\w+)\s*\((.*)\)", action_str)
    if not tool_match:
        print(f"无法解析工具调用: {action_str}")
        break
        
    tool_name = tool_match.group(1)
    args_str = tool_match.group(2)
    
    # 更安全地解析参数
    kwargs = {}
    # 匹配参数格式 key="value"
    args_matches = re.findall(r'(\w+)="([^"]*)"', args_str)
    for key, value in args_matches:
        kwargs[key] = value

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误：未定义的工具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)