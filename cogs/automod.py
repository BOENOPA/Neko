import time
import re
import discord

from collections import defaultdict, deque
from discord.ext import commands
from discord import app_commands


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.spam_messages = defaultdict(lambda: deque(maxlen=6))

        self.default_config = {
            "enabled": False,
            "anti_links": False,
            "anti_invites": True,
            "anti_spam": True,
            "filter_words": False,
            "log_channel": None,
            "bad_words": []
        }

    def get_config(self, guild_id):
        data = self.bot.load_data("configuracion")
        gid = str(guild_id)

        if gid not in data:
            data[gid] = {
                "automod": self.default_config.copy()
            }
            self.bot.save_data("configuracion", data)

        if "automod" not in data[gid]:
            data[gid]["automod"] = self.default_config.copy()

        config = data[gid]["automod"]

        for key, value in self.default_config.items():
            if key not in config:
                config[key] = value

        return data, gid, config

    def save_config(self, data, gid, config):
        data[gid]["automod"] = config
        self.bot.save_data("configuracion", data)

    async def send_log(self, guild, title, description):
        data = self.bot.load_data("configuracion")
        guild_data = data.get(str(guild.id), {})

        channel_id = guild_data.get("automod", {}).get("log_channel")

        if not channel_id:
            return

        channel = guild.get_channel(channel_id)

        if channel is None:
            return

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.from_rgb(115, 55, 210),
            timestamp=discord.utils.utcnow()
        )

        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        data, gid, config = self.get_config(message.guild.id)

        if not config["enabled"]:
            return

        content = message.content.lower()

        # Anti invitaciones
        if config["anti_invites"]:
            invite_pattern = r"(discord\.gg/|discord\.com/invite/)"

            if re.search(invite_pattern, content):
                try:
                    await message.delete()

                    await self.send_log(
                        message.guild,
                        "🛡️ AutoMod • Invitación eliminada",
                        (
                            f"Usuario: {message.author.mention}\n"
                            f"Canal: {message.channel.mention}\n"
                            f"Motivo: Invitación de Discord"
                        )
                    )

                    try:
                        await message.channel.send(
                            f"{message.author.mention}, no se permiten invitaciones de Discord.",
                            delete_after=5
                        )
                    except discord.HTTPException:
                        pass

                except discord.HTTPException:
                    pass

                return

        # Anti links
        if config["anti_links"]:
            link_pattern = r"https?://\S+|www\.\S+"

            if re.search(link_pattern, content):
                try:
                    await message.delete()

                    await self.send_log(
                        message.guild,
                        "🛡️ AutoMod • Link eliminado",
                        (
                            f"Usuario: {message.author.mention}\n"
                            f"Canal: {message.channel.mention}\n"
                            f"Motivo: Link detectado"
                        )
                    )

                except discord.HTTPException:
                    pass

                return

        # Palabras prohibidas
        if config["filter_words"]:
            bad_words = config.get("bad_words", [])

            for word in bad_words:
                if word.lower() in content:
                    try:
                        await message.delete()

                        await self.send_log(
                            message.guild,
                            "🛡️ AutoMod • Mensaje eliminado",
                            (
                                f"Usuario: {message.author.mention}\n"
                                f"Canal: {message.channel.mention}\n"
                                f"Motivo: Palabra filtrada"
                            )
                        )

                    except discord.HTTPException:
                        pass

                    return

        # Anti spam
        if config["anti_spam"]:
            now = time.time()

            messages = self.spam_messages[
                (message.guild.id, message.author.id)
            ]

            messages.append(now)

            recent = [
                timestamp
                for timestamp in messages
                if now - timestamp <= 6
            ]

            if len(recent) >= 5:

                try:
                    await message.delete()
                except discord.HTTPException:
                    pass

                await self.send_log(
                    message.guild,
                    "🛡️ AutoMod • Spam detectado",
                    (
                        f"Usuario: {message.author.mention}\n"
                        f"Canal: {message.channel.mention}\n"
                        f"Mensajes detectados: {len(recent)}"
                    )
                )

    @app_commands.command(
        name="automod",
        description="Activa o desactiva el AutoMod."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod(
        self,
        interaction: discord.Interaction,
        estado: bool
    ):

        data, gid, config = self.get_config(interaction.guild.id)

        config["enabled"] = estado

        self.save_config(data, gid, config)

        estado_texto = "activado" if estado else "desactivado"

        await interaction.response.send_message(
            f"🛡️ AutoMod **{estado_texto}** correctamente.",
            ephemeral=True
        )

    @app_commands.command(
        name="automodconfig",
        description="Configura una función específica del AutoMod."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        funcion="Función que querés configurar.",
        estado="Activar o desactivar."
    )
    @app_commands.choices(
        funcion=[
            app_commands.Choice(
                name="Links",
                value="anti_links"
            ),
            app_commands.Choice(
                name="Invitaciones",
                value="anti_invites"
            ),
            app_commands.Choice(
                name="Spam",
                value="anti_spam"
            ),
            app_commands.Choice(
                name="Palabras",
                value="filter_words"
            )
        ]
    )
    async def automodconfig(
        self,
        interaction: discord.Interaction,
        funcion: app_commands.Choice[str],
        estado: bool
    ):

        data, gid, config = self.get_config(interaction.guild.id)

        config[funcion.value] = estado

        self.save_config(data, gid, config)

        await interaction.response.send_message(
            f"🛡️ **{funcion.name}**: "
            f"{'activado' if estado else 'desactivado'}.",
            ephemeral=True
        )

    @app_commands.command(
        name="automodlogs",
        description="Configura el canal de logs del AutoMod."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automodlogs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data, gid, config = self.get_config(interaction.guild.id)

        config["log_channel"] = canal.id

        self.save_config(data, gid, config)

        await interaction.response.send_message(
            f"✅ Logs del AutoMod configurados en {canal.mention}.",
            ephemeral=True
        )

    @app_commands.command(
        name="automodpalabra",
        description="Agrega una palabra al filtro del AutoMod."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automodpalabra(
        self,
        interaction: discord.Interaction,
        palabra: str
    ):

        data, gid, config = self.get_config(interaction.guild.id)

        palabra = palabra.lower().strip()

        if not palabra:
            return await interaction.response.send_message(
                "❌ Escribí una palabra válida.",
                ephemeral=True
            )

        if palabra in config["bad_words"]:
            return await interaction.response.send_message(
                "⚠️ Esa palabra ya está en el filtro.",
                ephemeral=True
            )

        config["bad_words"].append(palabra)

        self.save_config(data, gid, config)

        await interaction.response.send_message(
            f"✅ `{palabra}` fue agregada al filtro.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(AutoMod(bot))