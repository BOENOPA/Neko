import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import random
import time
from collections import defaultdict
# ============================================================
# SOCIAL / ANIME ACTIONS
# Compatible con tu bot.py actual
# ============================================================
class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ----------------------------------------------------
        # Datos persistentes
        # ----------------------------------------------------
        self.data = self.bot.load_cog_data(
            "social",
            {
                "users": {},
                "pairs": {}
            }
        )
        # ----------------------------------------------------
        # Sesión HTTP
        # ----------------------------------------------------
        self.session = None
        # ----------------------------------------------------
        # Caché de GIFs
        # Evita pedir constantemente a la API
        # ----------------------------------------------------
        self.gif_cache = {}
        # ----------------------------------------------------
        # Cooldown interno
        # ----------------------------------------------------
        self.last_action = defaultdict(float)
        print("[SOCIAL] 🎭 Sistema social iniciado.")
    # ========================================================
    # READY / HTTP SESSION
    # ========================================================
    @commands.Cog.listener()
    async def on_ready(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(
                total=10,
                connect=5
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "DiscordBot-Social/1.0"
                }
            )
        print("[SOCIAL] ✅ APIs de GIF preparadas.")
    # ========================================================
    # UNLOAD
    # ========================================================
    def cog_unload(self):
        if self.session and not self.session.closed:
            asyncio.create_task(
                self.session.close()
            )
    # ========================================================
    # CONFIGURACIÓN DE ACCIONES
    # ========================================================
    ACTIONS = {
        "kiss": {
            "name": "beso",
            "emoji": "💋",
            "nekosbest": "kiss",
            "waifu": "kiss",
            "phrases": [
                "{author} le dio un beso a {target} 💋",
                "{author} besó a {target} 💋",
                "{author} se acercó y besó a {target} 💋"
            ]
        },
        "hug": {
            "name": "abrazo",
            "emoji": "🤗",
            "nekosbest": "hug",
            "waifu": "hug",
            "phrases": [
                "{author} abrazó a {target} 🤗",
                "{author} le dio un abrazo a {target} 🤗",
                "{author} apretó fuerte a {target} 🤗"
            ]
        },
        "pat": {
            "name": "pat",
            "emoji": "🫳",
            "nekosbest": "pat",
            "waifu": "pat",
            "phrases": [
                "{author} le acarició la cabeza a {target} 🫳",
                "{author} le dio unas palmaditas a {target} 🫳",
                "{author} le hizo pat pat a {target} 🫳"
            ]
        },
        "cuddle": {
            "name": "acurrucarse",
            "emoji": "🫂",
            "nekosbest": "cuddle",
            "waifu": "cuddle",
            "phrases": [
                "{author} se acurrucó con {target} 🫂",
                "{author} abrazó tiernamente a {target} 🫂",
                "{author} se quedó acurrucado con {target} 🫂"
            ]
        },
        "highfive": {
            "name": "high five",
            "emoji": "✋",
            "nekosbest": "highfive",
            "waifu": "highfive",
            "phrases": [
                "{author} chocó los cinco con {target} ✋",
                "{author} le dio un high five a {target} ✋",
                "{author} y {target} chocaron los cinco ✋"
            ]
        },
        "wave": {
            "name": "saludo",
            "emoji": "👋",
            "nekosbest": "wave",
            "waifu": "wave",
            "phrases": [
                "{author} saludó a {target} 👋",
                "{author} le hizo una señal a {target} 👋",
                "{author} saludó alegremente a {target} 👋"
            ]
        },
        "poke": {
            "name": "poke",
            "emoji": "👉",
            "nekosbest": "poke",
            "waifu": "poke",
            "phrases": [
                "{author} le hizo poke a {target} 👉",
                "{author} tocó a {target} 👉",
                "{author} molestó un poquito a {target} 👉"
            ]
        },
        "bite": {
            "name": "mordida",
            "emoji": "🦷",
            "nekosbest": "bite",
            "waifu": "bite",
            "phrases": [
                "{author} mordió a {target} 🦷",
                "{author} le dio una mordidita a {target} 🦷",
                "{author} atacó a mordiscos a {target} 🦷"
            ]
        },
        "slap": {
            "name": "cachetada",
            "emoji": "👋",
            "nekosbest": "slap",
            "waifu": "slap",
            "phrases": [
                "{author} le dio una cachetada a {target} 👋",
                "{author} le pegó una cachetada a {target} 👋",
                "{author} abofeteó a {target} 👋"
            ]
        },
        "kick": {
            "name": "patada",
            "emoji": "🦵",
            "nekosbest": "kick",
            "waifu": "kick",
            "phrases": [
                "{author} le dio una patada a {target} 🦵",
                "{author} pateó a {target} 🦵",
                "{author} mandó una patada hacia {target} 🦵"
            ]
        },
        "punch": {
            "name": "golpe",
            "emoji": "👊",
            "nekosbest": "punch",
            "waifu": "punch",
            "phrases": [
                "{author} le dio un golpe a {target} 👊",
                "{author} le pegó un puñetazo a {target} 👊",
                "{author} atacó a {target} 👊"
            ]
        },
        "lick": {
            "name": "lamida",
            "emoji": "😛",
            "nekosbest": None,
            "waifu": "lick",
            "phrases": [
                "{author} le dio una lamida a {target} 😛",
                "{author} lamió a {target} 😛"
            ]
        },
        "bonk": {
            "name": "bonk",
            "emoji": "🔨",
            "nekosbest": "bonk",
            "waifu": "bonk",
            "phrases": [
                "{author} hizo BONK a {target} 🔨",
                "{author} le dio un bonk a {target} 🔨",
                "{author} bonkeó a {target} 🔨"
            ]
        },
        "yeet": {
            "name": "yeet",
            "emoji": "💨",
            "nekosbest": "yeet",
            "waifu": "yeet",
            "phrases": [
                "{author} mandó a volar a {target} 💨",
                "{author} hizo yeet con {target} 💨",
                "{author} lanzó a {target} 💨"
            ]
        },
        "tickle": {
            "name": "cosquillas",
            "emoji": "😂",
            "nekosbest": "tickle",
            "waifu": "tickle",
            "phrases": [
                "{author} le hizo cosquillas a {target} 😂",
                "{author} atacó con cosquillas a {target} 😂",
                "{author} no paró de hacerle cosquillas a {target} 😂"
            ]
        }
    }
    # ========================================================
    # DATOS DE USUARIO
    # ========================================================
    def ensure_user(self, user_id):
        user_id = str(user_id)
        users = self.data.setdefault(
            "users",
            {}
        )
        if user_id not in users:
            users[user_id] = {
                "given": {},
                "received": {},
                "total": 0
            }
        return users[user_id]
    # ========================================================
    # DATOS DE PAREJA
    # ========================================================
    def ensure_pair(self, user_a, user_b):
        ids = sorted([
            str(user_a),
            str(user_b)
        ])
        key = f"{ids[0]}:{ids[1]}"
        pairs = self.data.setdefault(
            "pairs",
            {}
        )
        if key not in pairs:
            pairs[key] = {
                "actions": {},
                "total": 0
            }
        return pairs[key]
    # ========================================================
    # REGISTRAR ACCIÓN
    # ========================================================
    def register_action(
        self,
        author_id,
        target_id,
        action
    ):
        author = self.ensure_user(
            author_id
        )
        target = self.ensure_user(
            target_id
        )
        pair = self.ensure_pair(
            author_id,
            target_id
        )
        # ----------------------------------------------------
        # Dado
        # ----------------------------------------------------
        author["given"][action] = (
            author["given"].get(action, 0) + 1
        )
        # ----------------------------------------------------
        # Recibido
        # ----------------------------------------------------
        target["received"][action] = (
            target["received"].get(action, 0) + 1
        )
        # ----------------------------------------------------
        # Total personal
        # ----------------------------------------------------
        author["total"] = (
            author.get("total", 0) + 1
        )
        target["total"] = (
            target.get("total", 0) + 1
        )
        # ----------------------------------------------------
        # Pareja
        # ----------------------------------------------------
        pair["actions"][action] = (
            pair["actions"].get(action, 0) + 1
        )
        pair["total"] = (
            pair.get("total", 0) + 1
        )
        # ----------------------------------------------------
        # Guardar
        # ----------------------------------------------------
        self.bot.save_cog_data(
            "social",
            self.data
        )
    # ========================================================
    # OBTENER GIF DE NEKOSBEST
    # ========================================================
    async def get_nekosbest(
        self,
        category
    ):
        if not category:
            return None
        url = (
            "https://nekos.best/api/v2/"
            + category
        )
        try:
            async with self.session.get(
                url
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                results = data.get(
                    "results",
                    []
                )
                if not results:
                    return None
                result = results[0]
                image_url = result.get(
                    "url"
                )
                anime_name = result.get(
                    "anime_name"
                )
                if not image_url:
                    return None
                return {
                    "url": image_url,
                    "anime": anime_name,
                    "source": "nekos.best"
                }
        except Exception as e:
            print(
                f"[SOCIAL] ⚠️ NekosBest error: "
                f"{type(e).__name__}: {e}"
            )
            return None
    # ========================================================
    # FALLBACK WAIFU.PICS
    # ========================================================
    async def get_waifu(
        self,
        category
    ):
        if not category:
            return None
        url = (
            "https://api.waifu.pics/"
            f"sfw/{category}"
        )
        try:
            async with self.session.get(
                url
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                image_url = data.get(
                    "url"
                )
                if not image_url:
                    return None
                return {
                    "url": image_url,
                    "anime": None,
                    "source": "waifu.pics"
                }
        except Exception as e:
            print(
                f"[SOCIAL] ⚠️ WaifuPics error: "
                f"{type(e).__name__}: {e}"
            )
            return None
    # ========================================================
    # BUSCAR GIF
    # ========================================================
    async def get_gif(
        self,
        action
    ):
        info = self.ACTIONS[action]
        # ----------------------------------------------------
        # Crear sesión si todavía no existe
        # ----------------------------------------------------
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(
                total=10,
                connect=5
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "DiscordBot-Social/1.0"
                }
            )
        # ----------------------------------------------------
        # No usar caché para que los GIF cambien
        # ----------------------------------------------------
        # ----------------------------------------------------
        # PRIMERA FUENTE
        # NekosBest
        # ----------------------------------------------------
        result = await self.get_nekosbest(
            info["nekosbest"]
        )
        if result:
            return result
        # ----------------------------------------------------
        # SEGUNDA FUENTE
        # WaifuPics
        # ----------------------------------------------------
        result = await self.get_waifu(
            info["waifu"]
        )
        if result:
            return result
        # ----------------------------------------------------
        # Reintento
        # ----------------------------------------------------
        await asyncio.sleep(0.2)
        result = await self.get_nekosbest(
            info["nekosbest"]
        )
        if result:
            return result
        result = await self.get_waifu(
            info["waifu"]
        )
        if result:
            return result
        return None
    # ========================================================
    # EJECUTAR ACCIÓN
    # ========================================================
    async def execute_action(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        action: str
    ):
        # ----------------------------------------------------
        # No bots
        # ----------------------------------------------------
        if target.bot:
            await interaction.response.send_message(
                "No podés usar esta acción con un bot.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # No uno mismo
        # ----------------------------------------------------
        if target.id == interaction.user.id:
            await interaction.response.send_message(
                "No podés usar esta acción con vos mismo.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Configuración
        # ----------------------------------------------------
        info = self.ACTIONS[action]
        # ----------------------------------------------------
        # Registrar inmediatamente
        # ----------------------------------------------------
        self.register_action(
            interaction.user.id,
            target.id,
            action
        )
        # ----------------------------------------------------
        # Buscar GIF
        # ----------------------------------------------------
        await interaction.response.defer()
        gif = await self.get_gif(
            action
        )
        # ----------------------------------------------------
        # Frase
        # ----------------------------------------------------
        phrase = random.choice(
            info["phrases"]
        ).format(
            author=interaction.user.mention,
            target=target.mention
        )
        # ----------------------------------------------------
        # Embed
        # ----------------------------------------------------
        embed = discord.Embed(
            description=phrase,
            color=discord.Color.from_rgb(
                115,
                55,
                210
            )
        )
        # ----------------------------------------------------
        # GIF encontrado
        # ----------------------------------------------------
        if gif:
            embed.set_image(
                url=gif["url"]
            )
            anime = gif.get(
                "anime"
            )
            if anime:
                embed.set_footer(
                    text=f"🎬 {anime}"
                )
            else:
                embed.set_footer(
                    text="Anime GIF"
                )
        else:
            embed.set_footer(
                text="✨ Acción registrada"
            )
        # ----------------------------------------------------
        # Responder
        # ----------------------------------------------------
        await interaction.followup.send(
            embed=embed
        )
    # ========================================================
    # COMANDOS
    # ========================================================
    async def action_command(
        self,
        interaction,
        target,
        action
    ):
        await self.execute_action(
            interaction,
            target,
            action
        )
    # ========================================================
    # KISS
    # ========================================================
    @app_commands.command(
        name="kiss",
        description="Dale un beso a alguien."
    )
    @app_commands.describe(
        usuario="Usuario al que querés besar"
    )
    async def kiss(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "kiss"
        )
    # ========================================================
    # HUG
    # ========================================================
    @app_commands.command(
        name="hug",
        description="Dale un abrazo a alguien."
    )
    @app_commands.describe(
        usuario="Usuario al que querés abrazar"
    )
    async def hug(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "hug"
        )
    # ========================================================
    # PAT
    # ========================================================
    @app_commands.command(
        name="pat",
        description="Acaricia la cabeza de alguien."
    )
    async def pat(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "pat"
        )
    # ========================================================
    # CUDDLE
    # ========================================================
    @app_commands.command(
        name="cuddle",
        description="Acurrucate con alguien."
    )
    async def cuddle(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "cuddle"
        )
    # ========================================================
    # HIGH FIVE
    # ========================================================
    @app_commands.command(
        name="highfive",
        description="Choca los cinco con alguien."
    )
    async def highfive(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "highfive"
        )
    # ========================================================
    # WAVE
    # ========================================================
    @app_commands.command(
        name="wave",
        description="Saluda a alguien."
    )
    async def wave(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "wave"
        )
    # ========================================================
    # POKE
    # ========================================================
    @app_commands.command(
        name="poke",
        description="Hazle poke a alguien."
    )
    async def poke(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "poke"
        )
    # ========================================================
    # BITE
    # ========================================================
    @app_commands.command(
        name="bite",
        description="Dale una mordida a alguien."
    )
    async def bite(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "bite"
        )
    # ========================================================
    # SLAP
    # ========================================================
    @app_commands.command(
        name="slap",
        description="Dale una cachetada a alguien."
    )
    async def slap(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "slap"
        )
    # ========================================================
    # KICK
    # ========================================================
    @app_commands.command(
        name="kick",
        description="Dale una patada a alguien."
    )
    async def kick(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "kick"
        )
    # ========================================================
    # PUNCH
    # ========================================================
    @app_commands.command(
        name="punch",
        description="Dale un golpe a alguien."
    )
    async def punch(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "punch"
        )
    # ========================================================
    # LICK
    # ========================================================
    @app_commands.command(
        name="lick",
        description="Haz una acción de lick."
    )
    async def lick(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "lick"
        )
    # ========================================================
    # BONK
    # ========================================================
    @app_commands.command(
        name="bonk",
        description="Hazle bonk a alguien."
    )
    async def bonk(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "bonk"
        )
    # ========================================================
    # YEET
    # ========================================================
    @app_commands.command(
        name="yeet",
        description="Manda a volar a alguien."
    )
    async def yeet(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "yeet"
        )
    # ========================================================
    # TICKLE
    # ========================================================
    @app_commands.command(
        name="tickle",
        description="Hazle cosquillas a alguien."
    )
    async def tickle(
        self,
        interaction,
        usuario: discord.Member
    ):
        await self.action_command(
            interaction,
            usuario,
            "tickle"
        )
    # ========================================================
    # SOCIAL
    # ========================================================
    @app_commands.command(
        name="social",
        description="Muestra tus estadísticas sociales."
    )
    @app_commands.describe(
        usuario="Usuario para ver las estadísticas entre ambos"
    )
    async def social(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):
        me = self.ensure_user(
            interaction.user.id
        )
        # ====================================================
        # ESTADÍSTICAS ENTRE DOS PERSONAS
        # ====================================================
        if usuario:
            if usuario.bot:
                await interaction.response.send_message(
                    "No hay estadísticas sociales para bots.",
                    ephemeral=True
                )
                return
            pair = self.ensure_pair(
                interaction.user.id,
                usuario.id
            )
            embed = discord.Embed(
                title="💜 Estadísticas sociales",
                description=(
                    f"{interaction.user.mention} × "
                    f"{usuario.mention}"
                ),
                color=discord.Color.from_rgb(
                    115,
                    55,
                    210
                )
            )
            actions = pair.get(
                "actions",
                {}
            )
            if actions:
                lines = []
                order = [
                    "hug",
                    "kiss",
                    "pat",
                    "cuddle",
                    "highfive",
                    "wave",
                    "poke",
                    "bite",
                    "slap",
                    "kick",
                    "punch",
                    "lick",
                    "bonk",
                    "yeet",
                    "tickle"
                ]
                for action in order:
                    amount = actions.get(
                        action,
                        0
                    )
                    if amount > 0:
                        info = self.ACTIONS[action]
                        lines.append(
                            f"{info['emoji']} "
                            f"**{info['name'].title()}:** "
                            f"{amount}"
                        )
                if lines:
                    embed.add_field(
                        name="Interacciones",
                        value="\n".join(lines),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Interacciones",
                        value="Todavía no hay interacciones.",
                        inline=False
                    )
            embed.add_field(
                name="✨ Total",
                value=str(
                    pair.get(
                        "total",
                        0
                    )
                ),
                inline=False
            )
            embed.set_thumbnail(
                url=usuario.display_avatar.url
            )
            await interaction.response.send_message(
                embed=embed
            )
            return
        # ====================================================
        # ESTADÍSTICAS PROPIAS
        # ====================================================
        embed = discord.Embed(
            title="💜 Perfil social",
            description=(
                f"Estadísticas de "
                f"{interaction.user.mention}"
            ),
            color=discord.Color.from_rgb(
                115,
                55,
                210
            )
        )
        given = me.get(
            "given",
            {}
        )
        received = me.get(
            "received",
            {}
        )
        order = [
            "hug",
            "kiss",
            "pat",
            "cuddle",
            "highfive",
            "wave",
            "poke",
            "bite",
            "slap",
            "kick",
            "punch",
            "lick",
            "bonk",
            "yeet",
            "tickle"
        ]
        given_lines = []
        received_lines = []
        for action in order:
            info = self.ACTIONS[action]
            amount_given = given.get(
                action,
                0
            )
            amount_received = received.get(
                action,
                0
            )
            if amount_given > 0:
                given_lines.append(
                    f"{info['emoji']} "
                    f"**{info['name'].title()}:** "
                    f"{amount_given}"
                )
            if amount_received > 0:
                received_lines.append(
                    f"{info['emoji']} "
                    f"**{info['name'].title()}:** "
                    f"{amount_received}"
                )
        if not given_lines:
            given_lines.append(
                "Todavía no diste ninguna interacción."
            )
        if not received_lines:
            received_lines.append(
                "Todavía no recibiste ninguna interacción."
            )
        embed.add_field(
            name="📤 Acciones dadas",
            value="\n".join(given_lines),
            inline=False
        )
        embed.add_field(
            name="📥 Acciones recibidas",
            value="\n".join(received_lines),
            inline=False
        )
        embed.add_field(
            name="✨ Total de interacciones",
            value=str(
                me.get(
                    "total",
                    0
                )
            ),
            inline=False
        )
        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Social(bot)
    )
    print(
        "[SOCIAL] ✅ Cog social cargado correctamente."
    )