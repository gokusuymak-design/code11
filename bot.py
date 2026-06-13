import discord
from discord.ext import commands
from discord import app_commands

from groq import Groq
from tavily import TavilyClient

# ============================
# ใส่ API Keys ของคุณ
# ============================
DISCORD_TOKEN = "MTUxNTI3NzU5NDkxMDUyMzQzMw.GTrBUy.IOqmEq1giTFy5qV3-SMh4p7tcqLnwmglvKpK54"
GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"
# ============================
# สร้าง Client
# ============================
groq = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def ask_with_web(question: str) -> str:
    # ค้นหาจากเว็บ
    search = tavily.search(
        query=question,
        search_depth="advanced",
        max_results=3,
    )

    context = ""

    for item in search["results"]:
        context += f"""
หัวข้อ: {item['title']}
URL: {item['url']}
เนื้อหา:
{item['content']}

"""

    prompt = f"""
ข้อมูลจากการค้นหาเว็บ:

{context}

โปรดตอบคำถามต่อไปนี้โดยอ้างอิงจากข้อมูลด้านบน
หากข้อมูลไม่แน่ชัดให้แจ้งตามตรง

คำถาม:
{question}
"""

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "คุณเป็นผู้ช่วย AI ภาษาไทย "
                    "อธิบายชัดเจน กระชับ และใช้ข้อมูลจากเว็บเป็นหลัก"
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)


# -----------------------
# !ask
# -----------------------
@bot.command()
async def ask(ctx, *, question):
    await ctx.reply("🔍 กำลังค้นหาข้อมูล...")

    try:
        answer = ask_with_web(question)
        await ctx.send(answer[:2000])
    except Exception as e:
        await ctx.send(f"เกิดข้อผิดพลาด: {e}")


# -----------------------
# /ask
# -----------------------
@bot.tree.command(
    name="ask",
    description="ถาม AI พร้อมค้นหาข้อมูลจากเว็บ",
)
@app_commands.describe(question="คำถามที่ต้องการถาม")
async def slash_ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    try:
        answer = ask_with_web(question)
        await interaction.followup.send(answer[:2000])
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
bot.run("MTUxNTI3NzU5NDkxMDUyMzQzMw.GTrBUy.IOqmEq1giTFy5qV3-SMh4p7tcqLnwmglvKpK54")