import random

import discord
from discord import app_commands
from discord.ext import commands


class Juegos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="dado",
        description="Tirá un dado."
    )
    async def dado(
        self,
        interaction: discord.Interaction
    ):

        numero = random.randint(1, 6)

        await interaction.response.send_message(
            f"🎲 Sacaste **{numero}**."
        )

    @app_commands.command(
        name="moneda",
        description="Lanzá una moneda."
    )
    async def moneda(
        self,
        interaction: discord.Interaction
    ):

        resultado = random.choice(
            ["Cara", "Cruz"]
        )

        await interaction.response.send_message(
            f"🪙 Salió **{resultado}**."
        )

    @app_commands.command(
        name="8ball",
        description="Hacé una pregunta."
    )
    @app_commands.describe(
        pregunta="Tu pregunta"
    )
    async def eightball(
        self,
        interaction: discord.Interaction,
        pregunta: str
    ):

        respuestas = [
            "Sí.",
            "No.",
            "Probablemente.",
            "No parece.",
            "Puede ser.",
            "Definitivamente.",
            "No tengo idea.",
            "Preguntame más tarde."
        ]

        respuesta = random.choice(respuestas)

        await interaction.response.send_message(
            f"🎱 **Pregunta:** {pregunta}\n"
            f"**Respuesta:** {respuesta}"
        )


async def setup(bot):
    await bot.add_cog(Juegos(bot))