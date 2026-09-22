import discord
from discord.ext import commands
from discord import app_commands


class Bienvenida(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setbienvenida",
        description="Configura el canal de bienvenida."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setbienvenida(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data = self.bot.load_data("configuracion")

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id]["welcome_channel"] = canal.id

        self.bot.save_data("configuracion", data)

        await interaction.response.send_message(
            f"✅ Canal de bienvenida configurado en {canal.mention}.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        data = self.bot.load_data("configuracion")
        guild_data = data.get(str(member.guild.id), {})

        channel_id = guild_data.get("welcome_channel")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)

        if channel is None:
            return

        embed = discord.Embed(
            title="Bienvenido/a",
            description=(
                f"Bienvenido/a {member.mention} a **{member.guild.name}**.\n\n"
                f"Ahora somos **{member.guild.member_count}** miembros."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)

    @app_commands.command(
        name="setdespedida",
        description="Configura el canal de despedidas."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setdespedida(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data = self.bot.load_data("configuracion")

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id]["goodbye_channel"] = canal.id

        self.bot.save_data("configuracion", data)

        await interaction.response.send_message(
            f"✅ Canal de despedidas configurado en {canal.mention}.",
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        data = self.bot.load_data("configuracion")
        guild_data = data.get(str(member.guild.id), {})

        channel_id = guild_data.get("goodbye_channel")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)

        if channel is None:
            return

        embed = discord.Embed(
            title="Hasta luego",
            description=(
                f"**{member}** salió del servidor.\n\n"
                f"Ahora somos **{member.guild.member_count}** miembros."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bienvenida(bot))