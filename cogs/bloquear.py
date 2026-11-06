
import discord
from discord import app_commands
from discord.ext import commands


class Bloquear(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="bloquear",
        description="Bloquea el canal para todos menos para vos."
    )
    @app_commands.checks.has_permissions(
        manage_channels=True
    )
    async def bloquear(
        self,
        interaction: discord.Interaction
    ):

        canal = interaction.channel
        guild = interaction.guild
        usuario = interaction.user

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                "❌ Este comando solo funciona en canales de texto.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:
            # Bloquear a @everyone
            await canal.set_permissions(
                guild.default_role,
                view_channel=True,
                send_messages=False,
                add_reactions=False,
                send_messages_in_threads=False
            )

            # Permitir escribir al usuario que ejecutó el comando
            await canal.set_permissions(
                usuario,
                view_channel=True,
                send_messages=True,
                add_reactions=True,
                send_messages_in_threads=True
            )

            await interaction.followup.send(
                f"🔒 {canal.mention} fue bloqueado.\n"
                f"Solo {usuario.mention} puede escribir."
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos para modificar este canal."
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error: {e}"
            )

    @app_commands.command(
        name="desbloquear",
        description="Desbloquea el canal."
    )
    @app_commands.checks.has_permissions(
        manage_channels=True
    )
    async def desbloquear(
        self,
        interaction: discord.Interaction
    ):

        canal = interaction.channel
        guild = interaction.guild

        if not isinstance(
            canal,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                "❌ Este comando solo funciona en canales de texto.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:
            # Restaurar permisos de @everyone
            await canal.set_permissions(
                guild.default_role,
                overwrite=None
            )

            await interaction.followup.send(
                f"🔓 {canal.mention} fue desbloqueado."
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos para modificar este canal."
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error: {e}"
            )


async def setup(bot):
    await bot.add_cog(Bloquear(bot))
