import discord
from discord.ext import commands
from discord import app_commands


class HelpSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label="Economía",
                description="Dinero, trabajo, pagos y economía.",
                emoji="💰",
                value="economia"
            ),
            discord.SelectOption(
                label="Juegos",
                description="Juegos y comandos para divertirse.",
                emoji="🎮",
                value="juegos"
            ),
            discord.SelectOption(
                label="Social",
                description="Interacciones entre usuarios.",
                emoji="💜",
                value="social"
            ),
            discord.SelectOption(
                label="Moderación",
                description="Herramientas para moderar el servidor.",
                emoji="🛡️",
                value="moderacion"
            ),
            discord.SelectOption(
                label="Roles",
                description="Administración de roles.",
                emoji="🎨",
                value="roles"
            ),
            discord.SelectOption(
                label="Utilidades",
                description="Información y herramientas.",
                emoji="🛠️",
                value="utilidades"
            )
        ]

        super().__init__(
            placeholder="Seleccioná una categoría...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="argbot:help_select"
        )

    async def callback(self, interaction: discord.Interaction):

        categoria = self.values[0]

        datos = {

            "economia": (
                "💰 Economía",
                "`/balance` `/daily` `/work` `/beg`\n"
                "`/depositar` `/retirar` `/pay`"
            ),

            "juegos": (
                "🎮 Juegos",
                "`/dado` `/moneda` `/8ball`"
            ),

            "social": (
                "💜 Social",
                "`/hug` `/kiss` `/slap` `/pat` `/ship`"
            ),

            "moderacion": (
                "🛡️ Moderación",
                "`/kick` `/ban` `/clear`\n"
                "`/lockchannel` `/unlockchannel`"
            ),

            "roles": (
                "🎨 Roles",
                "`/crearrol` `/darrol` `/quitarrol`"
            ),

            "utilidades": (
                "🛠️ Utilidades",
                "`/userinfo` `/serverinfo` `/avatar`"
            )
        }

        titulo, descripcion = datos[categoria]

        embed = discord.Embed(
            title=titulo,
            description=descripcion,
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.set_footer(text="ArgBot • Usá /help para volver al menú")

        await interaction.response.edit_message(
            embed=embed,
            view=HelpView()
        )


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(HelpSelect())


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Muestra todos los comandos del bot."
    )
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="ArgBot",
            description=(
                "Bienvenido al centro de ayuda.\n\n"
                "Seleccioná una categoría para ver los comandos "
                "disponibles."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        embed.add_field(
            name="💰 Economía",
            value="Dinero y economía",
            inline=True
        )

        embed.add_field(
            name="🎮 Juegos",
            value="Juegos y diversión",
            inline=True
        )

        embed.add_field(
            name="💜 Social",
            value="Interacciones",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderación",
            value="Administración",
            inline=True
        )

        embed.add_field(
            name="🎨 Roles",
            value="Sistema de roles",
            inline=True
        )

        embed.add_field(
            name="🛠️ Utilidades",
            value="Herramientas",
            inline=True
        )

        embed.set_footer(
            text="ArgBot • Seleccioná una categoría"
        )

        await interaction.response.send_message(
            embed=embed,
            view=HelpView()
        )


async def setup(bot):
    await bot.add_cog(Help(bot))