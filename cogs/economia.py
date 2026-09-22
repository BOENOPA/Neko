import random
import time

import discord
from discord import app_commands
from discord.ext import commands


class Economia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    # =====================================================
    # UTILIDADES
    # =====================================================

    def get_user(self, user_id: int):
        data = self.bot.load_data("economia.json", {})

        uid = str(user_id)

        if uid not in data:
            data[uid] = {
                "wallet": 1000,
                "bank": 0
            }
            self.bot.save_data("economia.json", data)

        return data, data[uid]

    def save(self, data):
        self.bot.save_data("economia.json", data)

    def cooldown(self, user_id, command, seconds):

        key = f"{user_id}:{command}"
        now = time.time()

        last = self.cooldowns.get(key, 0)
        remaining = seconds - (now - last)

        if remaining > 0:
            return remaining

        self.cooldowns[key] = now
        return 0

    # =====================================================
    # BALANCE
    # =====================================================

    @app_commands.command(
        name="balance",
        description="Mirá cuánto dinero tenés."
    )
    async def balance(self, interaction: discord.Interaction):

        data, user = self.get_user(interaction.user.id)

        total = user["wallet"] + user["bank"]

        embed = discord.Embed(
            title="💰 Tu economía",
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.add_field(
            name="Billetera",
            value=f"${user['wallet']:,}",
            inline=True
        )

        embed.add_field(
            name="Banco",
            value=f"${user['bank']:,}",
            inline=True
        )

        embed.add_field(
            name="Total",
            value=f"${total:,}",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    # =====================================================
    # DAILY
    # =====================================================

    @app_commands.command(
        name="daily",
        description="Reclamá tu recompensa diaria."
    )
    async def daily(self, interaction: discord.Interaction):

        remaining = self.cooldown(
            interaction.user.id,
            "daily",
            86400
        )

        if remaining:
            hours = int(remaining // 3600)

            await interaction.response.send_message(
                f"⏳ Ya reclamaste tu recompensa. "
                f"Volvé en aproximadamente **{hours}h**.",
                ephemeral=True
            )
            return

        amount = random.randint(500, 1500)

        data, user = self.get_user(interaction.user.id)

        user["wallet"] += amount

        self.save(data)

        await interaction.response.send_message(
            f"💰 Recibiste **${amount:,}** de tu recompensa diaria."
        )

    # =====================================================
    # WORK
    # =====================================================

    @app_commands.command(
        name="work",
        description="Trabajá para ganar dinero."
    )
    async def work(self, interaction: discord.Interaction):

        remaining = self.cooldown(
            interaction.user.id,
            "work",
            3600
        )

        if remaining:

            minutes = int(remaining // 60)

            await interaction.response.send_message(
                f"⏳ Todavía no podés trabajar. "
                f"Volvé en aproximadamente **{minutes} minutos**.",
                ephemeral=True
            )

            return

        amount = random.randint(100, 500)

        data, user = self.get_user(interaction.user.id)

        user["wallet"] += amount

        self.save(data)

        await interaction.response.send_message(
            f"💼 Trabajaste y ganaste **${amount:,}**."
        )

    # =====================================================
    # BEG
    # =====================================================

    @app_commands.command(
        name="beg",
        description="Pedí unas monedas."
    )
    async def beg(self, interaction: discord.Interaction):

        remaining = self.cooldown(
            interaction.user.id,
            "beg",
            1800
        )

        if remaining:

            minutes = int(remaining // 60)

            await interaction.response.send_message(
                f"⏳ Esperá **{minutes} minutos**.",
                ephemeral=True
            )

            return

        amount = random.randint(50, 250)

        data, user = self.get_user(interaction.user.id)

        user["wallet"] += amount

        self.save(data)

        await interaction.response.send_message(
            f"🪙 Te dieron **${amount:,}**."
        )

    # =====================================================
    # DEPOSITAR
    # =====================================================

    @app_commands.command(
        name="depositar",
        description="Depositá dinero en el banco."
    )
    @app_commands.describe(
        cantidad="Cantidad a depositar"
    )
    async def depositar(
        self,
        interaction: discord.Interaction,
        cantidad: int
    ):

        data, user = self.get_user(interaction.user.id)

        if cantidad <= 0:
            await interaction.response.send_message(
                "La cantidad debe ser mayor a 0.",
                ephemeral=True
            )
            return

        if cantidad > user["wallet"]:
            await interaction.response.send_message(
                "No tenés suficiente dinero.",
                ephemeral=True
            )
            return

        user["wallet"] -= cantidad
        user["bank"] += cantidad

        self.save(data)

        await interaction.response.send_message(
            f"🏦 Depositaste **${cantidad:,}**."
        )

    # =====================================================
    # RETIRAR
    # =====================================================

    @app_commands.command(
        name="retirar",
        description="Retirá dinero del banco."
    )
    @app_commands.describe(
        cantidad="Cantidad a retirar"
    )
    async def retirar(
        self,
        interaction: discord.Interaction,
        cantidad: int
    ):

        data, user = self.get_user(interaction.user.id)

        if cantidad <= 0:
            await interaction.response.send_message(
                "La cantidad debe ser mayor a 0.",
                ephemeral=True
            )
            return

        if cantidad > user["bank"]:
            await interaction.response.send_message(
                "No tenés suficiente dinero en el banco.",
                ephemeral=True
            )
            return

        user["bank"] -= cantidad
        user["wallet"] += cantidad

        self.save(data)

        await interaction.response.send_message(
            f"💵 Retiraste **${cantidad:,}**."
        )

    # =====================================================
    # PAY
    # =====================================================

    @app_commands.command(
        name="pay",
        description="Mandale dinero a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario que recibirá el dinero",
        cantidad="Cantidad a enviar"
    )
    async def pay(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):

        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "No podés pagarte a vos mismo.",
                ephemeral=True
            )
            return

        if usuario.bot:
            await interaction.response.send_message(
                "No podés enviar dinero a un bot.",
                ephemeral=True
            )
            return

        if cantidad <= 0:
            await interaction.response.send_message(
                "La cantidad debe ser mayor a 0.",
                ephemeral=True
            )
            return

        data, sender = self.get_user(interaction.user.id)

        if cantidad > sender["wallet"]:
            await interaction.response.send_message(
                "No tenés suficiente dinero.",
                ephemeral=True
            )
            return

        _, receiver = self.get_user(usuario.id)

        sender["wallet"] -= cantidad
        receiver["wallet"] += cantidad

        self.save(data)

        await interaction.response.send_message(
            f"💸 Le enviaste **${cantidad:,}** a {usuario.mention}."
        )


async def setup(bot):
    await bot.add_cog(Economia(bot))