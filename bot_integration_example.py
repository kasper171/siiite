#!/usr/bin/env python3
"""
Exemplo de integração do Discord Backup Site com bot do Discord
Este arquivo mostra como modificar seu bot para salvar mensagens no site de backup.
"""

import discord
from discord.ext import commands
import requests
import aiohttp
import asyncio
from datetime import datetime
import os

# URL do seu site de backup (substitua pela URL real após deploy)
BACKUP_SITE_URL = "https://kaleidoscopic-gaufre-9ba204.netlify.app/"  # ou sua URL de produção http://localhost:5000

class DiscordBackupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        """Configuração inicial do bot"""
        print(f'{self.user} conectado e pronto para fazer backup!')

    async def on_ready(self):
        """Evento quando o bot fica online"""
        print(f'Bot {self.user} está online!')
        
    async def on_message(self, message):
        """Evento disparado a cada mensagem enviada"""
        # Não processar mensagens do próprio bot
        if message.author == self.user:
            return
            
        # Salvar mensagem no site de backup
        await self.save_message_to_backup(message)
        
        # Processar comandos normalmente
        await self.process_commands(message)
    
    async def save_message_to_backup(self, message):
        """Salva uma mensagem no site de backup"""
        try:
            # Primeiro, garantir que o canal existe no backup
            await self.ensure_channel_exists(message.channel, message.guild)
            
            # Preparar dados da mensagem
            message_data = {
                "discord_message_id": str(message.id),
                "user_id": str(message.author.id),
                "username": message.author.display_name,
                "avatar_url": str(message.author.avatar.url) if message.author.avatar else None,
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "channel_id": str(message.channel.id),
                "channel_name": message.channel.name,
                "server_id": str(message.guild.id),
                "server_name": message.guild.name,
                "message_type": "text",
                "is_bot": message.author.bot
            }
            
            # Processar anexos (imagens, áudios, etc.)
            if message.attachments:
                attachment = message.attachments[0]  # Pegar primeiro anexo
                
                # Determinar tipo de mídia
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    message_data["message_type"] = "image"
                elif any(attachment.filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.m4a']):
                    message_data["message_type"] = "audio"
                
                # Fazer download e upload do arquivo
                media_url = await self.upload_attachment(attachment)
                if media_url:
                    message_data["media_url"] = media_url
                    message_data["media_filename"] = attachment.filename
            
            # Enviar mensagem para o site de backup
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKUP_SITE_URL}/api/messages",
                    json=message_data
                ) as response:
                    if response.status == 201:
                        print(f"✅ Mensagem de {message.author.display_name} salva no backup")
                    else:
                        print(f"❌ Erro ao salvar mensagem: {response.status}")
                        
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
    
    async def ensure_channel_exists(self, channel, guild):
        """Garante que o canal existe no site de backup"""
        try:
            channel_data = {
                "discord_channel_id": str(channel.id),
                "name": channel.name,
                "server_id": str(guild.id),
                "server_name": guild.name
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKUP_SITE_URL}/api/channels",
                    json=channel_data
                ) as response:
                    # Status 200 = canal já existe, 201 = canal criado
                    if response.status in [200, 201]:
                        return True
                    else:
                        print(f"❌ Erro ao criar/verificar canal: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Erro ao verificar canal: {e}")
            return False
    
    async def upload_attachment(self, attachment):
        """Faz upload de um anexo para o site de backup"""
        try:
            # Fazer download do arquivo
            file_data = await attachment.read()
            
            # Preparar dados para upload
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename=attachment.filename)
            
            # Fazer upload
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKUP_SITE_URL}/api/upload",
                    data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['url']
                    else:
                        print(f"❌ Erro no upload: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"❌ Erro ao fazer upload: {e}")
            return None

    @commands.command(name='backup_stats')
    async def backup_stats(self, ctx):
        """Comando para ver estatísticas do backup"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKUP_SITE_URL}/api/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        
                        embed = discord.Embed(
                            title="📊 Estatísticas do Backup",
                            color=0x5865f2
                        )
                        embed.add_field(
                            name="Mensagens", 
                            value=f"{stats['total_messages']:,}", 
                            inline=True
                        )
                        embed.add_field(
                            name="Canais", 
                            value=f"{stats['total_channels']:,}", 
                            inline=True
                        )
                        embed.add_field(
                            name="Servidores", 
                            value=f"{stats['total_servers']:,}", 
                            inline=True
                        )
                        
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Erro ao obter estatísticas do backup")
                        
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")

    @commands.command(name='backup_channel')
    async def backup_channel_history(self, ctx, limit: int = 100):
        """Comando para fazer backup do histórico de um canal"""
        await ctx.send(f"🔄 Iniciando backup das últimas {limit} mensagens...")
        
        count = 0
        async for message in ctx.channel.history(limit=limit):
            await self.save_message_to_backup(message)
            count += 1
            
            # Atualizar progresso a cada 50 mensagens
            if count % 50 == 0:
                await ctx.send(f"📝 {count} mensagens processadas...")
        
        await ctx.send(f"✅ Backup concluído! {count} mensagens salvas.")

# Exemplo de uso
if __name__ == "__main__":
    # Substitua pelo token do seu bot
    BOT_TOKEN = "SEU_TOKEN_AQUI"
    
    bot = DiscordBackupBot()
    
    # Adicionar mais comandos se necessário
    @bot.command(name='backup_url')
    async def backup_url(ctx):
        """Comando para mostrar URL do site de backup"""
        embed = discord.Embed(
            title="🔗 Site de Backup",
            description=f"Acesse o backup em: {BACKUP_SITE_URL}",
            color=0x5865f2
        )
        await ctx.send(embed=embed)
    
    # Executar o bot
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Erro ao executar bot: {e}")

"""
INSTRUÇÕES DE USO:

1. Instale as dependências:
   pip install discord.py aiohttp

2. Configure o token do bot:
   - Substitua "SEU_TOKEN_AQUI" pelo token real do seu bot
   - Ou use variável de ambiente: os.getenv('DISCORD_BOT_TOKEN')

3. Configure a URL do backup:
   - Substitua BACKUP_SITE_URL pela URL real do seu site

4. Execute o bot:
   python bot_integration_example.py

5. Comandos disponíveis:
   - !backup_stats - Mostra estatísticas do backup
   - !backup_channel [limite] - Faz backup do histórico do canal
   - !backup_url - Mostra URL do site de backup

FUNCIONALIDADES:

✅ Backup automático de todas as mensagens
✅ Suporte a imagens e áudios
✅ Criação automática de canais
✅ Comandos para backup manual
✅ Estatísticas do backup
✅ Tratamento de erros

PERSONALIZAÇÃO:

- Adicione filtros para canais específicos
- Implemente backup agendado
- Adicione mais tipos de mídia
- Configure notificações de backup
- Adicione sistema de logs mais detalhado
"""

