import os
import json
import asyncio
import traceback
from pathlib import Path

import discord
from discord.ext import commands
from flask import Flask
from threading import Thread


# =========================================================
# CONFIGURACIÓN
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1534290216418938891"))
PORT = int(os.getenv("PORT", "10000"))

BASE_DIR = Path(__file__).resolve().parent
COGS_DIR = BASE_DIR / "cogs"
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)
COGS_DIR.mkdir(exist_ok=True)


# =========================================================
# FLASK / RENDER
# =========================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "ArgBot online ✅"


@app.route("/health")
def health():
    return "OK", 200


def run_web():
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True
intents.presences = True
intents.voice_states = True
intents.messages = True
intents.reactions = True


class ArgBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.guild_id = GUILD_ID
        self.data_dir = DATA_DIR

    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    def data_path(self, filename: str) -> Path:
        return self.data_dir / filename

    def load_data(self, filename: str, default=None):

        path = self.data_path(filename)

        if not path.exists():
            if default is None:
                default = {}

            self.save_data(filename, default)
            return default

        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            print(f"[DATA] Error leyendo {filename}")

            if default is None:
                default = {}

            return default

    def save_data(self, filename: str, data):

        path = self.data_path(filename)

        try:
            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except OSError as error:
            print(f"[DATA] Error guardando {filename}: {error}")

    # -----------------------------------------------------
    # READY
    # -----------------------------------------------------

    async def on_ready(self):

        print("=" * 50)
        print("ARG BOT")
        print("=" * 50)
        print(f"Bot: {self.user}")
        print(f"ID: {self.user.id}")
        print(f"Guild ID: {self.guild_id}")
        print(f"Servers: {len(self.guilds)}")
        print("=" * 50)

        # Sincronización rápida para el servidor configurado
        guild = self.get_guild(self.guild_id)

        if guild:

            try:
                synced = await self.tree.sync(guild=guild)

                print(
                    f"[SLASH] {len(synced)} comandos sincronizados "
                    f"en {guild.name}"
                )

            except Exception:
                print("[SLASH] Error sincronizando comandos")
                traceback.print_exc()

        else:
            print(
                "[SLASH] No encontré el servidor configurado."
            )

    # -----------------------------------------------------
    # ERROR GENERAL
    # -----------------------------------------------------

    async def on_command_error(
        self,
        ctx,
        error
    ):

        if isinstance(error, commands.CommandNotFound):
            return

        print("[COMMAND ERROR]")
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__
        )


# =========================================================
# CREAR BOT
# =========================================================

bot = ArgBot()


# =========================================================
# CARGAR COGS
# =========================================================

async def load_cogs():

    print("[COGS] Buscando extensiones...")

    if not COGS_DIR.exists():
        print("[COGS] La carpeta cogs no existe.")
        return

    for file in sorted(COGS_DIR.glob("*.py")):

        if file.name.startswith("_"):
            continue

        extension = f"cogs.{file.stem}"

        try:

            await bot.load_extension(extension)

            print(f"[COGS] ✓ {extension}")

        except Exception:

            print(f"[COGS] ✗ {extension}")

            traceback.print_exc()


# =========================================================
# ARRANQUE
# =========================================================

async def start_bot():

    if not TOKEN:
        raise RuntimeError(
            "Falta la variable de entorno DISCORD_TOKEN"
        )

    await load_cogs()

    print("[BOT] Iniciando Discord...")

    await bot.start(TOKEN)


def main():

    web_thread = Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()

    try:
        asyncio.run(start_bot())

    except KeyboardInterrupt:
        print("[BOT] Detenido.")

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()