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
        frases: list[str]
    ):

        if usuario.bot:
            return await interaction.response.send_message(
                "No podés hacer esta interacción con un bot.",
                ephemeral=True
            )

        if usuario.id == interaction.user.id:
            texto = random.choice([
                f"**{interaction.user.display_name}** se dio un poco de cariño.",
                f"**{interaction.user.display_name}** está solo/a por ahora.",
                f"**{interaction.user.display_name}** hizo la acción consigo mismo/a."
            ])
        else:
            texto = random.choice(frases).format(
                autor=interaction.user.display_name,
                usuario=usuario.display_name
            )

        embed = discord.Embed(
            description=texto,
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="hug",
        description="Dale un abrazo a alguien."
    )
    async def hug(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** abrazó a **{usuario}**.",
                "**{autor}** le dio un abrazo enorme a **{usuario}**.",
                "**{autor}** fue directo a abrazar a **{usuario}**."
            ]
        )

    @app_commands.command(
        name="kiss",
        description="Dale un beso a alguien."
    )
    async def kiss(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** le dio un beso a **{usuario}**.",
                "**{autor}** besó a **{usuario}**.",
                "**{autor}** le mandó un beso a **{usuario}**."
            ]
        )

    @app_commands.command(
        name="slap",
        description="Dale una cachetada a alguien."
    )
    async def slap(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** le dio una cachetada a **{usuario}**.",
                "**{autor}** le pegó una cachetada a **{usuario}**.",
                "**{autor}** le mandó una cachetada a **{usuario}**."
            ]
        )

    @app_commands.command(
        name="pat",
        description="Acaricia a alguien."
    )
    async def pat(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** le acarició la cabeza a **{usuario}**.",
                "**{autor}** le dio unas palmaditas a **{usuario}**.",
                "**{autor}** mimó a **{usuario}**."
            ]
        )

    @app_commands.command(
        name="poke",
        description="Molesta un poquito a alguien."
    )
    async def poke(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** le hizo poke a **{usuario}**.",
                "**{autor}** molestó a **{usuario}**.",
                "**{autor}** tocó a **{usuario}** para llamar su atención."
            ]
        )

    @app_commands.command(
        name="highfive",
        description="Chocá los cinco con alguien."
    )
    async def highfive(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion(
            interaction,
            usuario,
            [
                "**{autor}** chocó los cinco con **{usuario}**.",
                "**{autor}** le dio un high five a **{usuario}**.",
                "**{autor}** levantó la mano y **{usuario}** respondió."
            ]
        )

    @app_commands.command(
        name="ship",
        description="Calcula la compatibilidad entre dos usuarios."
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        if usuario.id == interaction.user.id:
            return await interaction.response.send_message(
                "Elegí a otra persona para calcular el ship.",
                ephemeral=True
            )

        porcentaje = random.randint(0, 100)

        if porcentaje <= 20:
            mensaje = "Parece que necesitan conocerse un poco más."
        elif porcentaje <= 50:
            mensaje = "Hay algo de química."
        elif porcentaje <= 80:
            mensaje = "Hay bastante química."
        else:
            mensaje = "La compatibilidad está bastante alta."

        embed = discord.Embed(
            title="💜 Ship",
            description=(
                f"**{interaction.user.display_name}** × "
                f"**{usuario.display_name}**\n\n"
                f"Compatibilidad: **{porcentaje}%**\n\n"
                f"{mensaje}"
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)

    def get_relationships(self):
        return self.bot.load_data("configuracion")

    @app_commands.command(
        name="marry",
        description="Propone matrimonio a otro usuario."
    )
    async def marry(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        if usuario.id == interaction.user.id:
            return await interaction.response.send_message(
                "No podés casarte con vos mismo/a.",
                ephemeral=True
            )

        if usuario.bot:
            return await interaction.response.send_message(
                "No podés casarte con un bot.",
                ephemeral=True
            )

        data = self.get_relationships()
        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        relationships = data[guild_id].setdefault(
            "relationships",
            {}
        )

        user_id = str(interaction.user.id)
        target_id = str(usuario.id)

        if user_id in relationships:
            return await interaction.response.send_message(
                "Ya estás en una relación.",
                ephemeral=True
            )

        if target_id in relationships:
            return await interaction.response.send_message(
                "Esa persona ya está en una relación.",
                ephemeral=True
            )

        relationships[user_id] = {
            "partner": usuario.id
        }

        relationships[target_id] = {
            "partner": interaction.user.id
        }

        self.bot.save_data("configuracion", data)

        embed = discord.Embed(
            title="💍 Nueva pareja",
            description=(
                f"**{interaction.user.mention}** y "
                f"**{usuario.mention}** ahora están juntos."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="divorce",
        description="Termina tu relación actual."
    )
    async def divorce(
        self,
        interaction: discord.Interaction
    ):

        data = self.get_relationships()
        guild_id = str(interaction.guild.id)

        guild_data = data.get(guild_id, {})
        relationships = guild_data.get("relationships", {})

        user_id = str(interaction.user.id)

        relationship = relationships.get(user_id)

        if not relationship:
            return await interaction.response.send_message(
                "No estás en ninguna relación.",
                ephemeral=True
            )

        partner_id = str(relationship["partner"])

        relationships.pop(user_id, None)
        relationships.pop(partner_id, None)

        self.bot.save_data("configuracion", data)

        partner = interaction.guild.get_member(
            int(partner_id)
        )

        partner_name = (
            partner.display_name
            if partner
            else "tu pareja"
        )

        embed = discord.Embed(
            title="💔 Relación terminada",
            description=(
                f"**{interaction.user.display_name}** terminó "
                f"su relación con **{partner_name}**."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="relationship",
        description="Muestra tu relación actual."
    )
    async def relationship(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):

        usuario = usuario or interaction.user

        data = self.get_relationships()
        guild_id = str(interaction.guild.id)

        guild_data = data.get(guild_id, {})
        relationships = guild_data.get("relationships", {})

        relationship = relationships.get(str(usuario.id))

        if not relationship:
            return await interaction.response.send_message(
                f"**{usuario.display_name}** no está en ninguna relación.",
                ephemeral=True
            )

        partner = interaction.guild.get_member(
            int(relationship["partner"])
        )

        if partner is None:
            return await interaction.response.send_message(
                "No pude encontrar a la pareja actual.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="💜 Relación",
            description=(
                f"**{usuario.display_name}** está en una relación "
                f"con **{partner.display_name}**."
            ),
            color=discord.Color.from_rgb(115, 55, 210)
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Social(bot))