"""
诊断脚本 - 显示本地 .env 中的 LINE credentials
用于对比 Railway 环境变量是否一致
"""

import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

print("=" * 70)
print("LINE Bot 凭证诊断")
print("=" * 70)

token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
secret = os.getenv('LINE_CHANNEL_SECRET', '')

print("\n🔑 LINE_CHANNEL_ACCESS_TOKEN:")
print(f"   长度: {len(token)} 字符")
if len(token) > 20:
    print(f"   前10位: {token[:10]}")
    print(f"   后10位: {token[-10:]}")
    print(f"   完整值: {token}")
else:
    print(f"   ⚠️  Token 太短或为空!")

print("\n🔐 LINE_CHANNEL_SECRET:")
print(f"   长度: {len(secret)} 字符")
if len(secret) > 0:
    print(f"   前10位: {secret[:10]}")
    print(f"   后10位: {secret[-10:]}")
    print(f"   完整值: {secret}")
else:
    print(f"   ❌ Secret 为空!")

print("\n" + "=" * 70)
print("📋 复制指引")
print("=" * 70)

print("\n请将以下内容复制到 Railway Raw Editor:")
print("\n--- 开始复制 (不包括这一行) ---")
print(f"LINE_CHANNEL_ACCESS_TOKEN={token}")
print(f"LINE_CHANNEL_SECRET={secret}")
print("--- 结束复制 (不包括这一行) ---")

print("\n⚠️  重要提示:")
print("   1. 复制时不要包含引号")
print("   2. 等号两边不要有空格")
print("   3. 直接覆盖 Railway Raw Editor 中的对应行")
print("   4. 保存后等待重新部署")

print("\n" + "=" * 70)
