import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from collections import defaultdict, deque
import re
import time
# ============================================================
# MODERACIÓN + AUTOMOD
# Compatible con el bot.py actual
# ============================================================
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ----------------------------------------------------
        # Historial de mensajes para detectar spam
        # guild_id -> user_id -> deque(timestamps)
        # ----------------------------------------------------
        self.message_history = defaultdict(
            lambda: defaultdict(
                lambda: deque(maxlen=30)
            )
        )
        # ----------------------------------------------------
        # Evita mandar demasiados avisos
        # ----------------------------------------------------
        self.last_warning = {}
        print("[MODERACION] Inicializando sistema...")
        # ----------------------------------------------------
        # Crear archivo usando el sistema de datos de bot.py
        # ----------------------------------------------------
        self.bot.create_cog_data_file(
            "moderacion",
            self.default_data()
        )
        print("[MODERACION] ✅ Sistema inicializado.")
    # ========================================================
    # DATOS
    # ========================================================
    @staticmethod
    def default_data():
        return {
            "guilds": {}
        }
    def get_data(self):
        return self.bot.load_cog_data(
            "moderacion",
            self.default_data()
        )
    def save_data(self, data):
        self.bot.save_cog_data(
            "moderacion",
            data
        )
    def get_config(self, guild_id):
        data = self.get_data()
        guild_id = str(guild_id)
        if "guilds" not in data:
            data["guilds"] = {}
        if guild_id not in data["guilds"]:
            data["guilds"][guild_id] = {
                "enabled": True,
                "anti_links": True,
                "anti_invites": True,
                "anti_words": True,
                "anti_spam": True,
                "max_messages": 5,
                "spam_seconds": 5,
                "timeout_minutes": 10,
                "log_channel": None,
                "blocked_words": []
            }
            self.save_data(data)
        config = data["guilds"][guild_id]
        # ----------------------------------------------------
        # Agregar configuraciones nuevas si faltan
        # ----------------------------------------------------
        defaults = {
            "enabled": True,
            "anti_links": True,
            "anti_invites": True,
            "anti_words": True,
            "anti_spam": True,
            "max_messages": 5,
            "spam_seconds": 5,
            "timeout_minutes": 10,
            "log_channel": None,
            "blocked_words": []
        }
        changed = False
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
                changed = True
        if changed:
            data["guilds"][guild_id] = config
            self.save_data(data)
        return config
    def update_config(self, guild_id, key, value):
        data = self.get_data()
        guild_id = str(guild_id)
        if "guilds" not in data:
            data["guilds"] = {}
        if guild_id not in data["guilds"]:
            self.get_config(int(guild_id))
            data = self.get_data()
        data["guilds"][guild_id][key] = value
        self.save_data(data)
    # ========================================================
    # PERMISOS
    # ========================================================
    def is_mod(self, member: discord.Member):
        if not member:
            return False
        permissions = member.guild_permissions
        return (
            permissions.administrator
            or permissions.manage_messages
            or permissions.moderate_members
            or permissions.manage_channels
        )
    async def check_mod(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "Este comando solamente funciona dentro de un servidor.",
                ephemeral=True
            )
            return False
        if not self.is_mod(interaction.user):
            await interaction.response.send_message(
                "No tenés permisos para usar este comando.",
                ephemeral=True
            )
            return False
        return True
    # ========================================================
    # LOGS
    # ========================================================
    async def send_log(
        self,
        guild: discord.Guild,
        title: str,
        description: str,
        color: discord.Color = discord.Color.purple()
    ):
        try:
            config = self.get_config(guild.id)
            channel_id = config.get("log_channel")
            if not channel_id:
                return
            channel = guild.get_channel(int(channel_id))
            if not channel:
                return
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=discord.utils.utcnow()
            )
            await channel.send(embed=embed)
        except Exception as e:
            print(
                f"[MODERACION] ❌ Error enviando log: "
                f"{type(e).__name__}: {e}"
            )
    # ========================================================
    # REGEX
    # ========================================================
    URL_REGEX = re.compile(
        r"(https?://|www\.)[^\s]+",
        re.IGNORECASE
    )
    DISCORD_INVITE_REGEX = re.compile(
        r"(discord\.gg/|discord(?:app)?\.com/invite/)",
        re.IGNORECASE
    )
    # ========================================================
    # AUTOMOD
    # ========================================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ----------------------------------------------------
        # Ignorar bots
        # ----------------------------------------------------
        if message.author.bot:
            return
        # ----------------------------------------------------
        # Ignorar DMs
        # ----------------------------------------------------
        if not message.guild:
            return
        guild = message.guild
        member = message.author
        # ----------------------------------------------------
        # Moderadores no son afectados por AutoMod
        # ----------------------------------------------------
        if self.is_mod(member):
            return
        config = self.get_config(guild.id)
        if not config.get("enabled", True):
            return
        content = message.content or ""
        # ====================================================
        # 1. INVITACIONES DE DISCORD
        # ====================================================
        if config.get("anti_invites", True):
            if self.DISCORD_INVITE_REGEX.search(content):
                deleted = await self.safe_delete(message)
                if deleted:
                    print(
                        f"[AUTOMOD] 🚫 Invitación eliminada: "
                        f"{member} ({member.id})"
                    )
                    await self.automod_action(
                        message,
                        "Invitación de Discord no permitida."
                    )
                    return
        # ====================================================
        # 2. LINKS
        # ====================================================
        if config.get("anti_links", True):
            if self.URL_REGEX.search(content):
                deleted = await self.safe_delete(message)
                if deleted:
                    print(
                        f"[AUTOMOD] 🔗 Link eliminado: "
                        f"{member} ({member.id})"
                    )
                    await self.automod_action(
                        message,
                        "Los links no están permitidos en este canal."
                    )
                    return
        # ====================================================
        # 3. PALABRAS BLOQUEADAS
        # ====================================================
        if config.get("anti_words", True):
            blocked_words = config.get(
                "blocked_words",
                []
            )
            content_lower = content.lower()
            detected_word = None
            for word in blocked_words:
                word = str(word).strip().lower()
                if not word:
                    continue
                if word in content_lower:
                    detected_word = word
                    break
            if detected_word:
                deleted = await self.safe_delete(message)
                if deleted:
                    print(
                        f"[AUTOMOD] 🤬 Palabra bloqueada: "
                        f"{member} -> {detected_word}"
                    )
                    await self.automod_action(
                        message,
                        "Ese mensaje contiene una palabra bloqueada."
                    )
                    return
        # ====================================================
        # 4. SPAM
        # ====================================================
        if config.get("anti_spam", True):
            now = time.monotonic()
            user_history = self.message_history[
                guild.id
            ][member.id]
            user_history.append(now)
            seconds = int(
                config.get(
                    "spam_seconds",
                    5
                )
            )
            max_messages = int(
                config.get(
                    "max_messages",
                    5
                )
            )
            # Mantener solamente mensajes de la ventana
            while (
                user_history
                and now - user_history[0] > seconds
            ):
                user_history.popleft()
            if len(user_history) >= max_messages:
                user_history.clear()
                print(
                    f"[AUTOMOD] ⚡ Spam detectado: "
                    f"{member} ({member.id})"
                )
                deleted = await self.safe_delete(message)
                if deleted:
                    await self.automod_action(
                        message,
                        (
                            f"Spam detectado. "
                            f"Timeout automático de "
                            f"{config.get('timeout_minutes', 10)} minutos."
                        ),
                        apply_timeout=True
                    )
                return
    # ========================================================
    # ELIMINAR MENSAJE
    # ========================================================
    async def safe_delete(self, message):
        try:
            await message.delete()
            return True
        except discord.NotFound:
            return False
        except discord.Forbidden:
            print(
                "[AUTOMOD] ❌ No tengo permiso para eliminar mensajes."
            )
            return False
        except discord.HTTPException as e:
            print(
                f"[AUTOMOD] ❌ Error eliminando mensaje: {e}"
            )
            return False
    # ========================================================
    # ACCIÓN AUTOMOD
    # ========================================================
    async def automod_action(
        self,
        message,
        reason,
        apply_timeout=False
    ):
        guild = message.guild
        member = message.author
        config = self.get_config(guild.id)
        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------
        if apply_timeout:
            minutes = int(
                config.get(
                    "timeout_minutes",
                    10
                )
            )
            try:
                await member.timeout(
                    timedelta(minutes=minutes),
                    reason=reason
                )
                print(
                    f"[AUTOMOD] 🔇 Timeout aplicado a "
                    f"{member} por {minutes} minutos."
                )
            except discord.Forbidden:
                print(
                    "[AUTOMOD] ❌ No tengo permisos "
                    "para aplicar timeout."
                )
            except discord.HTTPException as e:
                print(
                    f"[AUTOMOD] ❌ Error aplicando timeout: {e}"
                )
        # ----------------------------------------------------
        # Log
        # ----------------------------------------------------
        await self.send_log(
            guild,
            "🛡️ AutoMod",
            (
                f"**Usuario:** {member.mention} (`{member.id}`)\n"
                f"**Canal:** {message.channel.mention}\n"
                f"**Motivo:** {reason}"
            ),
            discord.Color.orange()
        )
        # ----------------------------------------------------
        # Aviso público
        # ----------------------------------------------------
        now = time.monotonic()
        last = self.last_warning.get(
            guild.id,
            0
        )
        # Máximo un aviso cada 3 segundos por servidor
        if now - last < 3:
            return
        self.last_warning[guild.id] = now
        try:
            warning = await message.channel.send(
                f"{member.mention} ⚠️ {reason}",
                delete_after=5
            )
        except Exception:
            pass
    # ========================================================
    # /automod
    # ========================================================
    @app_commands.command(
        name="automod",
        description="Configura el sistema de AutoMod."
    )
    @app_commands.describe(
        opcion="Configuración que querés modificar"
    )
    @app_commands.choices(
        opcion=[
            app_commands.Choice(
                name="Activar AutoMod",
                value="enable"
            ),
            app_commands.Choice(
                name="Desactivar AutoMod",
                value="disable"
            ),
            app_commands.Choice(
                name="Activar links",
                value="links_on"
            ),
            app_commands.Choice(
                name="Desactivar links",
                value="links_off"
            ),
            app_commands.Choice(
                name="Activar invitaciones",
                value="invites_on"
            ),
            app_commands.Choice(
                name="Desactivar invitaciones",
                value="invites_off"
            ),
            app_commands.Choice(
                name="Activar palabras",
                value="words_on"
            ),
            app_commands.Choice(
                name="Desactivar palabras",
                value="words_off"
            ),
            app_commands.Choice(
                name="Activar spam",
                value="spam_on"
            ),
            app_commands.Choice(
                name="Desactivar spam",
                value="spam_off"
            ),
            app_commands.Choice(
                name="Ver configuración",
                value="status"
            )
        ]
    )
    async def automod(
        self,
        interaction: discord.Interaction,
        opcion: app_commands.Choice[str]
    ):
        if not await self.check_mod(interaction):
            return
        value = opcion.value
        config = self.get_config(
            interaction.guild.id
        )
        # ----------------------------------------------------
        # Activar
        # ----------------------------------------------------
        if value == "enable":
            self.update_config(
                interaction.guild.id,
                "enabled",
                True
            )
            await interaction.response.send_message(
                "🛡️ **AutoMod activado.**",
                ephemeral=True
            )
        # ----------------------------------------------------
        # Desactivar
        # ----------------------------------------------------
        elif value == "disable":
            self.update_config(
                interaction.guild.id,
                "enabled",
                False
            )
            await interaction.response.send_message(
                "🛡️ **AutoMod desactivado.**",
                ephemeral=True
            )
        # ----------------------------------------------------
        # Links
        # ----------------------------------------------------
        elif value == "links_on":
            self.update_config(
                interaction.guild.id,
                "anti_links",
                True
            )
            await interaction.response.send_message(
                "🔗 Bloqueo de links **activado**.",
                ephemeral=True
            )
        elif value == "links_off":
            self.update_config(
                interaction.guild.id,
                "anti_links",
                False
            )
            await interaction.response.send_message(
                "🔗 Bloqueo de links **desactivado**.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # Invitaciones
        # ----------------------------------------------------
        elif value == "invites_on":
            self.update_config(
                interaction.guild.id,
                "anti_invites",
                True
            )
            await interaction.response.send_message(
                "🚫 Bloqueo de invitaciones **activado**.",
                ephemeral=True
            )
        elif value == "invites_off":
            self.update_config(
                interaction.guild.id,
                "anti_invites",
                False
            )
            await interaction.response.send_message(
                "🚫 Bloqueo de invitaciones **desactivado**.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # Palabras
        # ----------------------------------------------------
        elif value == "words_on":
            self.update_config(
                interaction.guild.id,
                "anti_words",
                True
            )
            await interaction.response.send_message(
                "🤬 Filtro de palabras **activado**.",
                ephemeral=True
            )
        elif value == "words_off":
            self.update_config(
                interaction.guild.id,
                "anti_words",
                False
            )
            await interaction.response.send_message(
                "🤬 Filtro de palabras **desactivado**.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # Spam
        # ----------------------------------------------------
        elif value == "spam_on":
            self.update_config(
                interaction.guild.id,
                "anti_spam",
                True
            )
            await interaction.response.send_message(
                "⚡ Anti-spam **activado**.",
                ephemeral=True
            )
        elif value == "spam_off":
            self.update_config(
                interaction.guild.id,
                "anti_spam",
                False
            )
            await interaction.response.send_message(
                "⚡ Anti-spam **desactivado**.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------
        elif value == "status":
            embed = discord.Embed(
                title="🛡️ Configuración de AutoMod",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="AutoMod",
                value="🟢 Activado"
                if config.get("enabled")
                else "🔴 Desactivado",
                inline=False
            )
            embed.add_field(
                name="🔗 Links",
                value="🟢 Activado"
                if config.get("anti_links")
                else "🔴 Desactivado",
                inline=True
            )
            embed.add_field(
                name="🚫 Invitaciones",
                value="🟢 Activado"
                if config.get("anti_invites")
                else "🔴 Desactivado",
                inline=True
            )
            embed.add_field(
                name="🤬 Palabras",
                value="🟢 Activado"
                if config.get("anti_words")
                else "🔴 Desactivado",
                inline=True
            )
            embed.add_field(
                name="⚡ Spam",
                value="🟢 Activado"
                if config.get("anti_spam")
                else "🔴 Desactivado",
                inline=True
            )
            embed.add_field(
                name="Spam",
                value=(
                    f"{config.get('max_messages', 5)} "
                    f"mensajes / "
                    f"{config.get('spam_seconds', 5)} segundos"
                ),
                inline=False
            )
            embed.add_field(
                name="Timeout automático",
                value=f"{config.get('timeout_minutes', 10)} minutos",
                inline=False
            )
            blocked = config.get(
                "blocked_words",
                []
            )
            embed.add_field(
                name="Palabras bloqueadas",
                value=str(len(blocked)),
                inline=False
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
    # ========================================================
    # /automodword
    # ========================================================
    @app_commands.command(
        name="automodword",
        description="Agrega o elimina una palabra del filtro."
    )
    @app_commands.describe(
        accion="Agregar o eliminar",
        palabra="Palabra"
    )
    @app_commands.choices(
        accion=[
            app_commands.Choice(
                name="Agregar",
                value="add"
            ),
            app_commands.Choice(
                name="Eliminar",
                value="remove"
            )
        ]
    )
    async def automodword(
        self,
        interaction: discord.Interaction,
        accion: app_commands.Choice[str],
        palabra: str
    ):
        if not await self.check_mod(interaction):
            return
        palabra = palabra.strip().lower()
        if not palabra:
            await interaction.response.send_message(
                "La palabra no puede estar vacía.",
                ephemeral=True
            )
            return
        config = self.get_config(
            interaction.guild.id
        )
        blocked = config.get(
            "blocked_words",
            []
        )
        if accion.value == "add":
            if palabra in blocked:
                await interaction.response.send_message(
                    "Esa palabra ya está bloqueada.",
                    ephemeral=True
                )
                return
            blocked.append(palabra)
            self.update_config(
                interaction.guild.id,
                "blocked_words",
                blocked
            )
            await interaction.response.send_message(
                f"🤬 Agregué `{palabra}` al filtro.",
                ephemeral=True
            )
        else:
            if palabra not in blocked:
                await interaction.response.send_message(
                    "Esa palabra no está en el filtro.",
                    ephemeral=True
                )
                return
            blocked.remove(palabra)
            self.update_config(
                interaction.guild.id,
                "blocked_words",
                blocked
            )
            await interaction.response.send_message(
                f"🗑️ Eliminé `{palabra}` del filtro.",
                ephemeral=True
            )
    # ========================================================
    # /automodwords
    # ========================================================
    @app_commands.command(
        name="automodwords",
        description="Muestra las palabras bloqueadas."
    )
    async def automodwords(
        self,
        interaction: discord.Interaction
    ):
        if not await self.check_mod(interaction):
            return
        config = self.get_config(
            interaction.guild.id
        )
        words = config.get(
            "blocked_words",
            []
        )
        if not words:
            text = "No hay palabras bloqueadas."
        else:
            text = "\n".join(
                f"• `{word}`"
                for word in words
            )
        embed = discord.Embed(
            title="🤬 Palabras bloqueadas",
            description=text,
            color=discord.Color.purple()
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # /setmodlogs
    # ========================================================
    @app_commands.command(
        name="setmodlogs",
        description="Configura el canal de logs de moderación."
    )
    async def setmodlogs(
        self,
        interaction: discord.Interaction
    ):
        if not await self.check_mod(interaction):
            return
        self.update_config(
            interaction.guild.id,
            "log_channel",
            interaction.channel.id
        )
        await interaction.response.send_message(
            f"📋 Los logs de moderación ahora se enviarán en "
            f"{interaction.channel.mention}.",
            ephemeral=True
        )
    # ========================================================
    # /warn
    # ========================================================
    @app_commands.command(
        name="warn",
        description="Advierte a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario",
        motivo="Motivo"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        motivo: str = "Sin motivo"
    ):
        if not await self.check_mod(interaction):
            return
        await interaction.response.send_message(
            f"⚠️ **{usuario}** recibió una advertencia.\n"
            f"**Motivo:** {motivo}"
        )
        try:
            await usuario.send(
                f"⚠️ Recibiste una advertencia en "
                f"**{interaction.guild.name}**.\n"
                f"**Motivo:** {motivo}"
            )
        except Exception:
            pass
        await self.send_log(
            interaction.guild,
            "⚠️ Advertencia",
            (
                f"**Usuario:** {usuario.mention}\n"
                f"**Moderador:** {interaction.user.mention}\n"
                f"**Motivo:** {motivo}"
            ),
            discord.Color.orange()
        )
    # ========================================================
    # /timeout
    # ========================================================
    @app_commands.command(
        name="timeout",
        description="Aplica timeout a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario",
        minutos="Duración",
        motivo="Motivo"
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        minutos: app_commands.Range[int, 1, 40320],
        motivo: str = "Sin motivo"
    ):
        if not await self.check_mod(interaction):
            return
        if usuario == interaction.user:
            await interaction.response.send_message(
                "No podés aplicarte timeout a vos mismo.",
                ephemeral=True
            )
            return
        if usuario.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "No podés moderar a alguien con un rol igual o superior al tuyo.",
                ephemeral=True
            )
            return
        try:
            await usuario.timeout(
                timedelta(minutes=minutos),
                reason=motivo
            )
            await interaction.response.send_message(
                f"🔇 **{usuario}** recibió timeout por "
                f"**{minutos} minutos**.\n"
                f"**Motivo:** {motivo}"
            )
            await self.send_log(
                interaction.guild,
                "🔇 Timeout",
                (
                    f"**Usuario:** {usuario.mention}\n"
                    f"**Moderador:** {interaction.user.mention}\n"
                    f"**Duración:** {minutos} minutos\n"
                    f"**Motivo:** {motivo}"
                ),
                discord.Color.orange()
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "No tengo permisos para aplicar timeout.",
                ephemeral=True
            )
    # ========================================================
    # /untimeout
    # ========================================================
    @app_commands.command(
        name="untimeout",
        description="Quita el timeout."
    )
    @app_commands.describe(
        usuario="Usuario"
    )
    async def untimeout(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        if not await self.check_mod(interaction):
            return
        try:
            await usuario.timeout(
                None,
                reason=f"Timeout removido por {interaction.user}"
            )
            await interaction.response.send_message(
                f"🔊 Timeout removido a **{usuario}**."
            )
            await self.send_log(
                interaction.guild,
                "🔊 Timeout removido",
                (
                    f"**Usuario:** {usuario.mention}\n"
                    f"**Moderador:** {interaction.user.mention}"
                ),
                discord.Color.green()
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "No tengo permisos para quitar el timeout.",
                ephemeral=True
            )
    # ========================================================
    # /clear
    # ========================================================
    @app_commands.command(
        name="clear",
        description="Elimina mensajes del canal."
    )
    @app_commands.describe(
        cantidad="Cantidad de mensajes"
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        cantidad: app_commands.Range[int, 1, 100]
    ):
        if not await self.check_mod(interaction):
            return
        await interaction.response.defer(
            ephemeral=True
        )
        try:
            deleted = await interaction.channel.purge(
                limit=cantidad
            )
            await interaction.followup.send(
                f"🧹 Eliminé **{len(deleted)} mensajes**.",
                ephemeral=True
            )
            await self.send_log(
                interaction.guild,
                "🧹 Mensajes eliminados",
                (
                    f"**Moderador:** {interaction.user.mention}\n"
                    f"**Canal:** {interaction.channel.mention}\n"
                    f"**Cantidad:** {len(deleted)}"
                )
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "No tengo permisos para eliminar mensajes.",
                ephemeral=True
            )
    # ========================================================
    # /lock
    # ========================================================
    @app_commands.command(
        name="lock",
        description="Bloquea el canal."
    )
    async def lock(
        self,
        interaction: discord.Interaction
    ):
        if not await self.check_mod(interaction):
            return
        channel = interaction.channel
        overwrite = channel.overwrites_for(
            interaction.guild.default_role
        )
        overwrite.send_messages = False
        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Canal bloqueado por {interaction.user}"
            )
            await interaction.response.send_message(
                "🔒 Canal bloqueado."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "No tengo permisos para bloquear este canal.",
                ephemeral=True
            )
    # ========================================================
    # /unlock
    # ========================================================
    @app_commands.command(
        name="unlock",
        description="Desbloquea el canal."
    )
    async def unlock(
        self,
        interaction: discord.Interaction
    ):
        if not await self.check_mod(interaction):
            return
        channel = interaction.channel
        overwrite = channel.overwrites_for(
            interaction.guild.default_role
        )
        overwrite.send_messages = None
        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                overwrite=overwrite,
                reason=f"Canal desbloqueado por {interaction.user}"
            )
            await interaction.response.send_message(
                "🔓 Canal desbloqueado."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "No tengo permisos para desbloquear este canal.",
                ephemeral=True
            )
# ============================================================
# SETUP DEL COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Moderacion(bot)
    )