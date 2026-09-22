import random

import discord
from discord.ext import commands
from discord import app_commands


class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def accion(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        accion: str,
        frases: list[str]
    ):

        if usuario.id == interaction.user.id:
            texto = f"**{interaction.user.mention}** {random.choice(frases)}"
        else:
            texto = (
                f"**{interaction.user.display_name}** "
                f"{random.choice(frases)} "
                f"**{usuario.display_name}**"
            )

        embed = discord.Embed(
            description=texto,
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Dale un abrazo a alguien.")
    async def hug(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            "hug",
            [
                "le dio un abrazo enorme a",
                "abrazó a",
                "se acercó y abrazó a"
            ]
        )

    @app_commands.command(name="kiss", description="Dale un beso a alguien.")
    async def kiss(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            "kiss",
            [
                "le dio un beso a",
                "besó a",
                "le mandó un beso a"
            ]
        )

    @app_commands.command(name="slap", description="Dale una cachetada a alguien.")
    async def slap(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            "slap",
            [
                "le dio una cachetada a",
                "le pegó una cachetada a",
                "le mandó una cachetada a"
            ]
        )

    @app_commands.command(name="pat", description="Acaricia la cabeza de alguien.")
    async def pat(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            "pat",
            [
                "le acarició la cabeza a",
                "le dio unas palmaditas a",
                "mimó a"
            ]
        )

    @app_commands.command(name="ship", description="Calcula la compatibilidad entre dos usuarios.")
    async def ship(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        porcentaje = random.randint(0, 100)

        if porcentaje < 20:
            mensaje = "💔 Muy complicada la cosa."
        elif porcentaje < 50:
            mensaje = "👀 Puede haber algo."
        elif porcentaje < 80:
            mensaje = "❤️ Hay química."
        else:
            mensaje = "💜 Alta compatibilidad."

        embed = discord.Embed(
            title="💜 Ship",
            description=(
                f"{interaction.user.mention} + {usuario.mention}\n\n"
                f"**Compatibilidad:** {porcentaje}%\n"
                f"{mensaje}"
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Social(bot))