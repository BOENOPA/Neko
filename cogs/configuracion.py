import discord
from discord.ext import commands
from discord import app_commands


class Configuracion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="config",
        description="Muestra la configuración del servidor."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):

        data = self.bot.load_data("configuracion")
        guild_data = data.get(str(interaction.guild.id), {})

        welcome = guild_data.get("welcome_channel")
        goodbye = guild_data.get("goodbye_channel")

        welcome_text = (
            f"<#{welcome}>"
            if welcome else
            "No configurado"
        )

        goodbye_text = (
            f"<#{goodbye}>"
            if goodbye else
            "No configurado"
        )

        embed = discord.Embed(
            title="⚙️ Configuración",
            description="Configuración actual del servidor.",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.add_field(
            name="Bienvenidas",
            value=welcome_text,
            inline=False
        )

        embed.add_field(
            name="Despedidas",
            value=goodbye_text,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(
        name="setlogs",
        description="Configura el canal de logs."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlogs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data = self.bot.load_data("configuracion")

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id]["logs_channel"] = canal.id

        self.bot.save_data("configuracion", data)

        await interaction.response.send_message(
            f"✅ Canal de logs configurado: {canal.mention}",
            ephemeral=True
        )

    @app_commands.command(
        name="setstaff",
        description="Configura el rol principal del staff."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setstaff(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):

        data = self.bot.load_data("configuracion")

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id]["staff_role"] = rol.id

        self.bot.save_data("configuracion", data)

        await interaction.response.send_message(
            f"✅ Rol de staff configurado: {rol.mention}",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Configuracion(bot))