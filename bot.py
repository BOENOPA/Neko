import os
import json
import asyncio
import traceback
from pathlib import Path
from threading import Thread

import discord
from discord.ext import commands
from flask import Flask


# =========================================================
# RUTAS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
COGS_DIR = BASE_DIR / "cogs"
DATA_DIR = BASE_DIR / "data"

COGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = int(
    os.getenv(
        "GUILD_ID",
        "1534290216418938891"
    )
)

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)


# =========================================================
# WEB
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
        port=PORT
    )


# =========================================================
# BOT
# =========================================================

class ArgBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.presences = True
        intents.voice_states = True
        intents.messages = True
        intents.reactions = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.guild_id = GUILD_ID
        self.data_dir = DATA_DIR


    # =====================================================
    # DATA
    # =====================================================

    def data_path(self, name):

        return self.data_dir / f"{name}.json"


    def load_data(self, name):

        path = self.data_path(name)

        if not path.exists():
            return {}

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            traceback.print_exc()
            return {}


    def save_data(self, name, data):

        path = self.data_path(name)

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )


    # =====================================================
    # READY
    # =====================================================

    async def on_ready(self):

        print("")
        print("==========================================")
        print("             DISCORD CONECTADO")
        print("==========================================")

        print(
            f"[BOT] Usuario: {self.user}"
        )

        print(
            f"[BOT] ID: {self.user.id}"
        )

        print(
            f"[BOT] Guilds: {len(self.guilds)}"
        )


        guild = self.get_guild(
            self.guild_id
        )


        if guild is None:

            print("")
            print(
                "[ERROR] NO ENCUENTRO EL SERVIDOR"
            )

            print(
                f"[ERROR] GUILD_ID: {self.guild_id}"
            )

            print(
                "[ERROR] Servidores detectados:"
            )

            for server in self.guilds:

                print(
                    f"   - {server.name} "
                    f"({server.id})"
                )

            return


        print(
            f"[SERVER] {guild.name}"
        )

        print(
            f"[SERVER] {guild.id}"
        )


        # =================================================
        # SINCRONIZAR
        # =================================================

        print("")
        print("==========================================")
        print("              SINCRONIZANDO")
        print("==========================================")


        try:

            local_commands = self.tree.get_commands()

            print(
                f"[SYNC] Comandos locales: "
                f"{len(local_commands)}"
            )


            for command in local_commands:

                print(
                    f"[LOCAL] /{command.name}"
                )


            synced = await self.tree.sync(
                guild=guild
            )


            print("")
            print(
                f"[SYNC] REGISTRADOS: "
                f"{len(synced)}"
            )


            for command in synced:

                print(
                    f"[DISCORD] /{command.name}"
                )


            print("")
            print(
                "=========================================="
            )

            print(
                "              SYNC COMPLETADO"
            )

            print(
                "=========================================="
            )


        except Exception as error:

            print("")
            print(
                "[SYNC ERROR]"
            )

            print(
                repr(error)
            )

            traceback.print_exc()


    # =====================================================
    # ERROR
    # =====================================================

    async def on_command_error(
        self,
        ctx,
        error
    ):

        print(
            f"[COMMAND ERROR] {error}"
        )


# =========================================================
# BOT
# =========================================================

bot = ArgBot()


# =========================================================
# CARGAR COGS
# =========================================================

async def load_cogs():

    print("")
    print("==========================================")
    print("              BUSCANDO COGS")
    print("==========================================")


    print(
        f"[PATH] {COGS_DIR}"
    )


    if not COGS_DIR.exists():

        print(
            "[ERROR] La carpeta cogs NO existe."
        )

        return


    files = sorted(
        COGS_DIR.glob("*.py")
    )


    print(
        f"[COGS] Archivos encontrados: "
        f"{len(files)}"
    )


    if not files:

        print(
            "[ERROR] NO HAY ARCHIVOS .PY EN COGS."
        )

        return


    loaded = 0
    failed = 0


    for file in files:

        print(
            f"[COG] Detectado: {file.name}"
        )


        if file.name.startswith("_"):

            print(
                f"[COG] Ignorado: {file.name}"
            )

            continue


        extension = (
            f"cogs.{file.stem}"
        )


        print(
            f"[COG] Intentando cargar: "
            f"{extension}"
        )


        try:

            await asyncio.wait_for(
                bot.load_extension(
                    extension
                ),
                timeout=15
            )


            loaded += 1


            print(
                f"[COG] ✓ CARGADO: "
                f"{file.stem}"
            )


        except asyncio.TimeoutError:

            failed += 1

            print(
                f"[COG] ✗ TIMEOUT: "
                f"{file.stem}"
            )


        except Exception as error:

            failed += 1

            print(
                f"[COG] ✗ ERROR: "
                f"{file.stem}"
            )

            print(
                repr(error)
            )

            traceback.print_exc()


    print("")
    print("==========================================")
    print("             RESUMEN COGS")
    print("==========================================")

    print(
        f"[COG] Cargados: {loaded}"
    )

    print(
        f"[COG] Errores: {failed}"
    )

    print(
        f"[COG] Comandos registrados: "
        f"{len(bot.tree.get_commands())}"
    )

    print(
        "=========================================="
    )

    print("")


# =========================================================
# START
# =========================================================

async def start_bot():

    print("")
    print("==========================================")
    print("              INICIANDO BOT")
    print("==========================================")


    if not TOKEN:

        print(
            "[ERROR] DISCORD_TOKEN NO EXISTE."
        )

        raise RuntimeError(
            "Falta DISCORD_TOKEN en Render."
        )


    print(
        "[TOKEN] DISCORD_TOKEN detectado."
    )


    print(
        f"[GUILD] {GUILD_ID}"
    )


    await load_cogs()


    print(
        "[DISCORD] Conectando con Discord..."
    )


    await bot.start(TOKEN)


# =========================================================
# MAIN
# =========================================================

def main():

    print("")
    print("##########################################")
    print("#              ARGBOT START              #")
    print("##########################################")


    web_thread = Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()


    print(
        "[WEB] Flask iniciado."
    )


    asyncio.run(
        start_bot()
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()