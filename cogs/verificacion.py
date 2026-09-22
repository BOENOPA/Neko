import discord

from discord.ext import commands
from discord import app_commands


class VerificationView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Verificarse",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="argbot:verify"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

        data = self.cog.bot.load_data("configuracion")

        guild_data = data.get(str(guild.id), {})

        role_id = guild_data.get("verification_role")

        if not role_id:
            return await interaction.response.send_message(
                "❌ El sistema de verificación todavía no está configurado.",
                ephemeral=True
            )

        role = guild.get_role(role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ No pude encontrar el rol de verificación.",
                ephemeral=True
            )

        member = interaction.user

        if role in member.roles:
            return await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )

        if guild.me.top_role <= role:
            return await interaction.response.send_message(
                "❌ Mi rol está por debajo del rol de verificación. "
                "Subí mi rol por encima de ese rol.",
                ephemeral=True
            )

        try:
            await member.add_roles(
                role,
                reason="Verificación mediante panel"
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para asignarte ese rol.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"✅ Te verificaste correctamente y recibiste {role.mention}.",
            ephemeral=True
        )


class Verificacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VerificationView(self))

    @app_commands.command(
        name="setverificacion",
        description="Configura el rol que recibirán los usuarios verificados."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setverificacion(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):

        if interaction.guild.me.top_role <= rol:
            return await interaction.response.send_message(
                "❌ Mi rol debe estar por encima del rol que quiero asignar.",
                ephemeral=True
            )

        data = self.bot.load_data("configuracion")

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id]["verification_role"] = rol.id

        self.bot.save_data("configuracion", data)

        await interaction.response.send_message(
            f"✅ Rol de verificación configurado: {rol.mention}",
            ephemeral=True
        )

    @app_commands.command(
        name="verificacionpanel",
        description="Crea el panel de verificación."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verificacionpanel(
        self,
        interaction: discord.Interaction
    ):

        data = self.bot.load_data("configuracion")
        guild_data = data.get(str(interaction.guild.id), {})

        role_id = guild_data.get("verification_role")

        if not role_id:
            return await interaction.response.send_message(
                "❌ Primero configurá el rol con `/setverificacion`.",
                ephemeral=True
            )

        role = interaction.guild.get_role(role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ El rol configurado ya no existe.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="Verificación",
            description=(
                "Para acceder al servidor necesitás verificarte.\n\n"
                "Presioná el botón **Verificarse** para recibir "
                f"{role.mention}."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_footer(
            text="ArgBot • Sistema de verificación"
        )

        await interaction.response.send_message(
            embed=embed,
            view=VerificationView(self)
        )


async def setup(bot):
    await bot.add_cog(Verificacion(bot))