import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Загружает .env
# === НАСТРОЙКИ ===
# Рекомендуется использовать .env файл для токена в продакшене
TOKEN = os.getenv("DISCORD_TOKEN")
TRIGGER_CHANNEL_ID = int(os.getenv("TRIGGER_CHANNEL_ID"))

intents = discord.Intents.default()
intents.voice_states = True  # Обязательно для отслеживания голосовых каналов

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен и готов к работе!")


@bot.event
async def on_voice_state_update(member, before, after):
    # Игнорируем, если пользователь не менял канал
    if before.channel == after.channel:
        return

    # 🟢 Пользователь зашёл в канал-триггер
    if after.channel and after.channel.id == TRIGGER_CHANNEL_ID:
        try:
            # Создаём канал в той же категории, что и триггер
            category = after.channel.category
            new_channel = await category.create_voice_channel(
                name=f"Комната {member.name}"
            )
            # Перемещаем пользователя
            await member.move_to(new_channel)
            print(f"🔊 Создан канал {new_channel.name} для {member.name}")
        except discord.Forbidden:
            print("❌ Ошибка: у бота нет прав на создание или перемещение каналов.")
        except discord.HTTPException as e:
            print(f"❌ Ошибка Discord API: {e}")

    # 🔴 Удаляем канал, если он опустел (и это не канал-триггер)
    if before.channel and before.channel.id != TRIGGER_CHANNEL_ID:
        if len(before.channel.members) == 0:
            # Небольшая задержка, чтобы избежать гонки состояний
            await asyncio.sleep(0.5)
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                    print(f"🗑️ Удалён пустой канал {before.channel.name}")
                except (TypeError, ValueError) as e:
                    print(f"❌ Ошибка загрузки переменных: {e}")
                    exit(1)  # Завершаем работу при ошибке


# Запуск бота
bot.run(TOKEN)
