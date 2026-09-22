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
# CONFIGURACIÓN
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

        self.cogs_loaded = False
        self.commands_synced = False


    # =====================================================
    # DATOS
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

            print(
                f"[DATA] Error leyendo {name}.json"
            )

            traceback.print_exc()

            return {}


    def save_data(self, name, data):

        path = self.data_path(name)

        try:

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

        except Exception:

            print(
                f"[DATA] Error guardando {name}.json"
            )

            traceback.print_exc()


    # =====================================================
    # READY
    # =====================================================

    async def on_ready(self):

        print("")
        print("=" * 60)
        print("                 ARGBOT")
        print("=" * 60)

        print(
            f"[BOT] Conectado como: "
            f"{self.user}"
        )

        print(
            f"[BOT] ID: "
            f"{self.user.id}"
        )

        guild = self.get_guild(
            self.guild_id
        )

        if guild is None:

            print("")
            print(
                "[ERROR] No encontré el servidor."
            )

            print(
                f"[ERROR] GUILD_ID configurado: "
                f"{self.guild_id}"
            )

            print(
                "[ERROR] Verificá que el bot esté "
                "dentro de ese servidor."
            )

            print("=" * 60)

            return


        print(
            f"[SERVER] {guild.name}"
        )

        print(
            f"[SERVER] ID: {guild.id}"
        )

        print(
            f"[SERVER] Miembros: "
            f"{guild.member_count}"
        )


        # =================================================
        # SINCRONIZACIÓN
        # =================================================

        if not self.commands_synced:

            try:

                print("")
                print(
                    "[SYNC] Preparando comandos..."
                )

                print(
                    f"[SYNC] Comandos locales: "
                    f"{len(self.tree.get_commands())}"
                )


                synced = await self.tree.sync(
                    guild=guild
                )


                self.commands_synced = True


                print(
                    f"[SYNC] OK - "
                    f"{len(synced)} comandos sincronizados."
                )


                if synced:

                    print(
                        "[SYNC] Comandos registrados:"
                    )

                    for command in synced:

                        print(
                            f"   /{command.name}"
                        )

                else:

                    print(
                        "[SYNC] ADVERTENCIA: "
                        "no se registró ningún comando."
                    )


            except Exception as error:

                print("")
                print(
                    "[SYNC] ERROR sincronizando comandos:"
                )

                print(
                    repr(error)
                )

                traceback.print_exc()


        print("")
        print("=" * 60)
        print("              BOT LISTO")
        print("=" * 60)
        print("")


    # =====================================================
    # ERRORES DE COMANDOS PREFIX
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
# CREAR BOT
# =========================================================

bot = ArgBot()


# =========================================================
# CARGAR COGS
# =========================================================

async def load_cogs():

    print("")
    print(
        "========== CARGANDO COGS =========="
    )

    loaded = 0
    failed = 0


    for file in sorted(
        COGS_DIR.glob("*.py")
    ):

        if file.name.startswith("_"):
            continue


        extension = (
            f"cogs.{file.stem}"
        )


        try:

            await bot.load_extension(
                extension
            )

            loaded += 1

            print(
                f"[COG] ✓ Cargado: "
                f"{file.stem}"
            )


        except Exception:

            failed += 1

            print(
                f"[COG] ✗ ERROR: "
                f"{file.stem}"
            )

            traceback.print_exc()


    bot.cogs_loaded = True


    print("")
    print(
        f"[COG] Cargados correctamente: "
        f"{loaded}"
    )

    print(
        f"[COG] Con errores: "
        f"{failed}"
    )

    print(
        "=================================="
    )

    print("")


# =========================================================
# INICIAR BOT
# =========================================================

async def start_bot():

    if not TOKEN:

        raise RuntimeError(
            "Falta la variable "
            "DISCORD_TOKEN en Render."
        )


    print("")
    print(
        "[START] Iniciando ArgBot..."
    )

    print(
        f"[START] GUILD_ID: "
        f"{GUILD_ID}"
    )


    # Primero cargamos TODOS los Cogs
    await load_cogs()


    # Después conectamos Discord
    await bot.start(TOKEN)


# =========================================================
# MAIN
# =========================================================

def main():

    print("")
    print(
        "=========================================="
    )

    print(
        "              INICIANDO ARGBOT"
    )

    print(
        "=========================================="
    )


    # Servidor web para Render
    web_thread = Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()


    print(
        "[WEB] Flask iniciado."
    )


    # Bot de Discord
    asyncio.run(
        start_bot()
    )


# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    main()