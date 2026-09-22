import discord
from discord.ext import commands
from discord import app_commands


class Imagenes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="avatar",
        description="Muestra el avatar de un usuario."
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):

        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"Avatar de {usuario.display_name}",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_image(url=usuario.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="banner",
        description="Muestra el banner de un usuario."
    )
    async def banner(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):

        usuario = usuario or interaction.user

        user = await self.bot.fetch_user(usuario.id)

        if not user.banner:
            return await interaction.response.send_message(
                "Ese usuario no tiene banner.",
                ephemeral=True
            )

        embed = discord.Embed(
            title=f"Banner de {usuario.display_name}",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_image(url=user.banner.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="servericon",
        description="Muestra el icono del servidor."
    )
    async def servericon(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None or guild.icon is None:
            return await interaction.response.send_message(
                "El servidor no tiene icono.",
                ephemeral=True
            )

        embed = discord.Embed(
            title=f"Icono de {guild.name}",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_image(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Imagenes(bot))