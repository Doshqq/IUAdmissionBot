from commands.panel import *
from commands.apply import *
from commands.admission_ranking import *
from commands.support import *
from bot import dp, bot


async def run_bot():
    print(f"Bot is running")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
