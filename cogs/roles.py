import discord
from discord import app_commands
from discord.ext import commands


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="crearrol",
        description="Crea un rol nuevo."
    )
    @app_commands.describe(
        nombre="Nombre del rol"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def crearrol(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):

        role = await interaction.guild.create_role(
            name=nombre,
            reason=f"Creado por {interaction.user}"
        )

        await interaction.response.send_message(
            f"🎭 Rol creado: {role.mention}"
        )

    @app_commands.command(
        name="darrol",
        description="Dale un rol a un usuario."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def darrol(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        rol: discord.Role
    ):

        if rol >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "No puedo administrar ese rol.",
                ephemeral=True
            )
            return

        await usuario.add_roles(rol)

        await interaction.response.send_message(
            f"🎭 {rol.mention} fue agregado a {usuario.mention}."
        )

    @app_commands.command(
        name="quitarrol",
        description="Quitale un rol a un usuario."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def quitarrol(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        rol: discord.Role
    ):

        await usuario.remove_roles(rol)

        await interaction.response.send_message(
            f"🎭 {rol.mention} fue removido de {usuario.mention}."
        )


async def setup(bot):
    await bot.add_cog(Roles(bot))