import discord
from discord import app_commands
from discord.ext import commands


class Utilidades(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="userinfo",
        description="Muestra información de un usuario."
    )
    async def userinfo(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):
        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"Información de {usuario}",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.add_field(
            name="Usuario",
            value=usuario.mention
        )

        embed.add_field(
            name="ID",
            value=str(usuario.id)
        )

        embed.add_field(
            name="Cuenta creada",
            value=discord.utils.format_dt(
                usuario.created_at,
                style="R"
            ),
            inline=False
        )

        if usuario.joined_at:
            embed.add_field(
                name="Entró al servidor",
                value=discord.utils.format_dt(
                    usuario.joined_at,
                    style="R"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="serverinfo",
        description="Muestra información del servidor."
    )
    async def serverinfo(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "Este comando solamente puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.from_rgb(115, 55, 210)
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        embed.add_field(
            name="Miembros",
            value=str(guild.member_count)
        )

        embed.add_field(
            name="Canales",
            value=str(len(guild.channels))
        )

        embed.add_field(
            name="Roles",
            value=str(len(guild.roles))
        )

        embed.add_field(
            name="ID",
            value=str(guild.id)
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Utilidades(bot)
    )