# 阿里云 API 选型与对接方案

> 版本: v1.0  ·  2026-06-21

## 选型总览

| 用途 | 模型 / 服务 | API 端点 | 状态 |
|------|------------|---------|------|
| LLM 对话 | Qwen-Plus | DashScope OpenAI 兼容 | ✅ 可用 |
| LLM 高级 | Qwen3-Max / Qwen3.5-Plus | DashScope | ✅ 可用 |
| TTS 流式 | CosyVoice 3.5 Plus | WebSocket | ✅ 可用 |
| ASR 实时 | Fun-ASR 1.5 / Qwen3-ASR | HTTP / WebSocket | ✅ 可用 |
| 发音评估 | Qwen2-Audio-7B-Instruct | DashScope | ✅ 可用 |
| 一体化(可选) | Qwen3.5-Omni Realtime | WebSocket | ✅ 可用 |

**统一接入**: 阿里云百炼平台 → DashScope SDK (Python)
- 注册: https://dashscope.console.aliyun.com
- API Key 格式: `sk-xxxxxxxx`
- 新用户 180 天各送 100 万 token 免费额度

---

## 1. LLM 对话:Qwen-Plus / Qwen3-Max

### 用途
- NPC 角色对话生成
- 剧本上下文管理
- 教学反馈卡生成
- 语法错误识别

### 推荐
- **主对话**: Qwen-Plus(便宜,质量够用)
- **复杂场景**: Qwen3-Max(教学反馈卡需要更细致)
- 备选: Qwen3.5-Plus(2026 新发布)

### 价格
- Qwen-Plus: ¥0.0004/千 token 输入(2024 降价后)
- Qwen3-Max: 略高,质量更好

### 接入示例(Python)
```python
import dashscope
from dashscope import Generation

dashscope.api_key = "sk-xxx"

response = Generation.call(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "你是一位柏林咖啡馆的 Kellnerin..."},
        {"role": "user", "content": "Ich möchte einen Kaffee bitte."}
    ],
    result_format="message"
)
print(response.output.choices[0].message.content)
```

---

## 2. TTS: CosyVoice 3.5(流式)

### 用途
NPC 语音回复(德语,带情感)

### 推荐
- **CosyVoice 3.5 Plus**(2026-03 发布,13 种语言,首包延迟 150ms)
- 支持**音色克隆**(10-20 秒参考音频)
- 支持**情感控制**(自然语言描述:用"略带疲惫但温柔"语气)
- 流式输出(WebSocket),适合实时游戏

### 价格
- 约 ¥0.0001/字(按字数计费,需查最新)
- 5 分钟对话约 500 字 = ¥0.05

### 接入示例(WebSocket)
```python
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer

# 加载预训练音色(或自定义)
synthesizer = SpeechSynthesizer(
    model="cosyvoice-v3.5-plus",
    voice="longxiaocheng"  # 预置德语男声(或上传克隆)
)

# 流式合成
audio = synthesizer.call("Guten Tag! Was darf es sein?")
```

### 音色方案
- 方案 A: 用 CosyVoice 预置德语音色
- 方案 B: 上传 NPC 配音演员的 10-20 秒参考音频做克隆
- 方案 C: 多 NPC 用不同克隆音色区分角色

---

## 3. ASR: Fun-ASR 1.5 / Qwen3-ASR

### 用途
用户德语语音 → 文字(同时用于反馈卡)

### 推荐
- **Qwen3-ASR-Flash**(2026-01-29 开源,52 种语言,德语支持,商业 API)
- **Fun-ASR 1.5**(2026-04,30 种语言,商业 API,行业场景优化)
- 两个选一个,都支持德语

### 接入方式
- **流式(WebSocket)**: 边录音边识别,适合实时游戏
- **一句话识别**: 用户说完后一次性识别(更简单,MVP 推荐)

### 价格
- 一句话识别:约 ¥0.006/15秒
- 流式识别:按音频时长计费,类似价位

### 接入示例(一句话识别)
```python
import dashscope
from dashscope.audio.asr import Recognition

result = Recognition.call(
    model="fun-asr",
    file_urls=["https://your-audio-url.wav"],
    language_hints=["de"]
)
print(result.output["text"])
```

---

## 4. 发音评估: Qwen2-Audio-7B-Instruct

### 用途
直接吃用户音频,输出"哪里错 / 怎么改"的文字评估

### 推荐
- **Qwen2-Audio-7B-Instruct**(开源,Apache 2.0)
- 阿里云百炼平台有 API(直接调用)
- 2026-01 arxiv 论文证明在 L2 发音零样本评估上有效

### 系统 Prompt 示例
```
你是一位耐心的德语老师。听用户的德语发音,按以下格式回复:

【你听到的内容】
<原样转写>

【语法评估】
- 错误 1:...
- 错误 2:...(如有)
- ✓ 语法正确(无误时)

【发音评估】
- 音素 1:发音准确/略有偏差/明显错误
- 音素 2:...

【给学生的建议】
<一句自然的中文反馈,鼓励性>
```

### 接入示例
```python
import dashscope
from dashscope import MultiModalConversation

messages = [
    {
        "role": "system",
        "content": [{"text": "你是一位耐心的德语老师..."}]
    },
    {
        "role": "user",
        "content": [
            {"audio": "https://user-audio.wav"},
            {"text": "请评估这段德语发音"}
        ]
    }
]

response = MultiModalConversation.call(
    model="qwen2-audio-7b-instruct",
    messages=messages
)
print(response.output.choices[0].message.content)
```

### 备选:Qwen3.5-Omni Realtime
如果想一步到位,可以用 **Qwen3.5-Omni** 的 Realtime API:
- 一个 WebSocket 连接,支持流式 ASR + LLM + TTS 全流程
- 内置 VAD(语音活动检测)、语义打断
- 113 种语种 ASR + 36 种语种 TTS
- 但教学反馈卡的逻辑需要单独加

**建议 MVP 先用组合方案(LLM + TTS + ASR + Qwen2-Audio 评估),后续 V2 再切 Omni Realtime。**

---

## 5. 备选架构: Qwen3.5-Omni 一体化

如果走 Omni Realtime 路线:

```
玩家录音(流式)
  ↓
Qwen3.5-Omni Realtime WebSocket
  ├─ ASR(德语)
  ├─ LLM(角色对话 + 教学)
  ├─ TTS(德语回复,流式)
  └─ 可选: 边对话边出教学反馈
  ↓
返回流式音频 + 文字
```

**优势**:
- 端到端延迟最低(网络一跳)
- 工程量最小(不用管 ASR/TTS/LLM 拼接)
- 语义打断原生支持

**劣势**:
- LLM 和教学逻辑耦合,改 prompt 不灵活
- 流式纠错难度大(可能丢字)
- 价格略高(按秒计费)

**判断**: V1 走组合方案,留 Omni 作为 V2 升级选项。

---

## 6. 关键注意事项

1. **WebSocket 长连接**: 流式 TTS / 流式 ASR 都需要 WebSocket,FastAPI 集成要注意
2. **音频格式**: 上传/下载统一用 16kHz, 16bit, mono PCM(浏览器录音标准)
3. **多请求并发**: 用户可能同时和多个 NPC 对话,API 调用要 async
4. **失败重试**: 云 API 偶有失败,需要重试机制
5. **速率限制**: 阿里云 API 有 QPS 限制,大规模时要考虑排队

---

## 7. 成本估算(单用户,完整 1 关)

| 项目 | 用量 | 成本 |
|------|------|------|
| LLM 对话 | 5 回合 × 500 token 输出 | ¥0.01 |
| TTS | NPC 5 句 × 20 字 | ¥0.01 |
| ASR | 5 句 × 5 秒 = 25 秒 | ¥0.01 |
| 发音评估 | 5 次 | ¥0.05 (估算) |
| **小计** | 1 关完整 | **¥0.08-0.15** |

**一个用户玩完整本 A1(15 关)**: 约 ¥1.2-2.3
**100 个种子用户**: 约 ¥120-230
**几乎可忽略**,完全可以覆盖。

---

## 8. 备选: 自建开源(如果未来想脱钩云服务)

万一阿里云涨价 / 政策变化,可以切本地:
- LLM: Qwen2.5-14B (Mac mini M4 Pro 64GB) 或 DeepSeek V4-Flash
- TTS: CosyVoice 开源版(自部署)
- ASR: Qwen3-ASR-0.6B(2GB 显存)
- 发音评估: Qwen2-Audio-7B(开源)

**好处**: 长期零边际成本
**代价**: 初次部署工作量 + 硬件升级(Mac mini 不够就要 GPU 服务器)

短期 V1 用阿里云,长期保留自建路线作为 Plan B。
