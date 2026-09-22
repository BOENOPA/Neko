import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path


class TicketView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Crear ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="argbot:create_ticket"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

        existing = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{interaction.user.id}"
        )

        if existing:
            return await interaction.response.send_message(
                f"Ya tenés un ticket abierto: {existing.mention}",
                ephemeral=True
            )

        category = discord.utils.get(guild.categories, name="TICKETS")

        if category is None:
            category = await guild.create_category("TICKETS")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True
            )
        }

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket de {interaction.user}"
        )

        embed = discord.Embed(
            title="🎫 Ticket creado",
            description=(
                f"Bienvenido {interaction.user.mention}.\n\n"
                "Contanos qué necesitás y el staff te va a ayudar.\n\n"
                "Cuando termines, utilizá el botón **Cerrar ticket**."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=CloseTicketView(self.cog)
        )

        await interaction.response.send_message(
            f"Ticket creado: {channel.mention}",
            ephemeral=True
        )


class CloseTicketView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Cerrar ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="argbot:close_ticket"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel

        if channel is None:
            return

        await interaction.response.send_message(
            "🔒 Cerrando ticket...",
            ephemeral=True
        )

        await channel.delete(reason=f"Ticket cerrado por {interaction.user}")


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketView(self))
        self.bot.add_view(CloseTicketView(self))

    @app_commands.command(
        name="ticketpanel",
        description="Crea el panel para abrir tickets."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticketpanel(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎫 Soporte",
            description=(
                "¿Necesitás ayuda?\n\n"
                "Presioná **Crear ticket** para abrir un canal privado "
                "con el staff."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_footer(text="ArgBot • Sistema de tickets")

        await interaction.response.send_message(
            embed=embed,
            view=TicketView(self)
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))