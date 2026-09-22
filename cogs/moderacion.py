import discord
from discord import app_commands
from discord.ext import commands


class Moderacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def hierarchy_check(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        if interaction.user.id == member.id:
            await interaction.response.send_message(
                "No podés aplicar esta acción sobre vos mismo.",
                ephemeral=True
            )
            return False

        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "No podés moderar a alguien con un rol igual o superior al tuyo.",
                ephemeral=True
            )
            return False

        return True

    # =====================================================
    # KICK
    # =====================================================

    @app_commands.command(
        name="kick",
        description="Expulsa a un usuario."
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str = "Sin razón"
    ):

        if not await self.hierarchy_check(interaction, usuario):
            return

        await usuario.kick(reason=razon)

        await interaction.response.send_message(
            f"👢 {usuario.mention} fue expulsado.\n"
            f"Razón: **{razon}**"
        )

    # =====================================================
    # BAN
    # =====================================================

    @app_commands.command(
        name="ban",
        description="Banea a un usuario."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str = "Sin razón"
    ):

        if not await self.hierarchy_check(interaction, usuario):
            return

        await usuario.ban(reason=razon)

        await interaction.response.send_message(
            f"🔨 {usuario.mention} fue baneado.\n"
            f"Razón: **{razon}**"
        )

    # =====================================================
    # CLEAR
    # =====================================================

    @app_commands.command(
        name="clear",
        description="Borra mensajes del canal."
    )
    @app_commands.describe(
        cantidad="Cantidad de mensajes"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        cantidad: int
    ):

        if cantidad < 1 or cantidad > 100:
            await interaction.response.send_message(
                "Elegí una cantidad entre 1 y 100.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(
            limit=cantidad
        )

        await interaction.followup.send(
            f"🧹 Eliminé **{len(deleted)} mensajes**.",
            ephemeral=True
        )

    # =====================================================
    # LOCK
    # =====================================================

    @app_commands.command(
        name="lockchannel",
        description="Bloquea el canal."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lockchannel(
        self,
        interaction: discord.Interaction
    ):

        channel = interaction.channel

        await channel.set_permissions(
            interaction.guild.default_role,
            send_messages=False
        )

        await interaction.response.send_message(
            "🔒 Canal bloqueado."
        )

    # =====================================================
    # UNLOCK
    # =====================================================

    @app_commands.command(
        name="unlockchannel",
        description="Desbloquea el canal."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlockchannel(
        self,
        interaction: discord.Interaction
    ):

        channel = interaction.channel

        await channel.set_permissions(
            interaction.guild.default_role,
            send_messages=None
        )

        await interaction.response.send_message(
            "🔓 Canal desbloqueado."
        )

    # =====================================================
    # ERROR
    # =====================================================

    async def cog_app_command_error(
        self,
        interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.MissingPermissions
        ):

            if interaction.response.is_done():
                await interaction.followup.send(
                    "No tenés permisos para usar este comando.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "No tenés permisos para usar este comando.",
                    ephemeral=True
                )

            return

        raise error


async def setup(bot):
    await bot.add_cog(Moderacion(bot))