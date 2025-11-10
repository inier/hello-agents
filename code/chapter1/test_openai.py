import os
from openai import OpenAI

# API配置
API_KEY = "sk-uxiFGtc00ygZXX6pHDwhH1wrzyubOOvBhHjPaPuYgpFg8e9r"
BASE_URL = "https://sg.uiuiapi.com"
MODEL_ID = "chatgpt-4o-latest"

def test_openai_call():
    print("初始化OpenAI客户端...")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    print(f"使用模型: {MODEL_ID}")
    
    try:
        print("发送测试请求...")
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "你是一个 helpful assistant."},
                {"role": "user", "content": "你好，这是测试消息"}
            ],
            stream=False,
            timeout=30
        )
        
        print(f"响应类型: {type(response)}")
        print(f"响应对象: {response}")
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            answer = response.choices[0].message.content
            print(f"成功收到回复: {answer}")
        else:
            print("响应格式不正确")
            
    except Exception as e:
        print(f"调用API时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_call()