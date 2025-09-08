#!/usr/bin/env python3
"""
Script para adicionar dados de exemplo ao Discord Backup Site
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import db
from src.models.message import Message, Channel
from datetime import datetime, timedelta
import random

def add_sample_data():
    """Adiciona dados de exemplo para teste"""
    
    with app.app_context():
        # Limpar dados existentes
        Message.query.delete()
        Channel.query.delete()
        db.session.commit()
        
        # Dados de exemplo
        servers = [
            {"id": "123456789", "name": "Servidor de Teste"},
            {"id": "987654321", "name": "Comunidade Gaming"},
            {"id": "555666777", "name": "Estudo e Trabalho"}
        ]
        
        channels_data = [
            {"discord_channel_id": "111111111", "name": "geral", "server_id": "123456789", "server_name": "Servidor de Teste"},
            {"discord_channel_id": "222222222", "name": "random", "server_id": "123456789", "server_name": "Servidor de Teste"},
            {"discord_channel_id": "333333333", "name": "jogos", "server_id": "987654321", "server_name": "Comunidade Gaming"},
            {"discord_channel_id": "444444444", "name": "dúvidas", "server_id": "555666777", "server_name": "Estudo e Trabalho"},
            {"discord_channel_id": "555555555", "name": "projetos", "server_id": "555666777", "server_name": "Estudo e Trabalho"},
        ]
        
        # Criar canais
        for channel_data in channels_data:
            channel = Channel(**channel_data)
            db.session.add(channel)
        
        db.session.commit()
        print("Canais criados com sucesso!")
        
        # Usuários de exemplo
        users = [
            {"id": "user1", "name": "João Silva", "is_bot": False},
            {"id": "user2", "name": "Maria Santos", "is_bot": False},
            {"id": "user3", "name": "Pedro Costa", "is_bot": False},
            {"id": "bot1", "name": "Bot Helper", "is_bot": True},
            {"id": "user4", "name": "Ana Oliveira", "is_bot": False},
        ]
        
        # Mensagens de exemplo
        sample_messages = [
            "Olá pessoal! Como vocês estão?",
            "Alguém pode me ajudar com essa dúvida?",
            "Acabei de terminar o projeto, ficou muito bom!",
            "Vamos jogar hoje à noite?",
            "Compartilhando um link interessante: https://example.com",
            "😄 Que dia incrível!",
            "Preciso de ajuda com Python, alguém pode me dar uma dica?",
            "Obrigado pela ajuda de ontem!",
            "Novo update do jogo saiu hoje!",
            "Bom dia a todos! ☀️",
            "Alguém viu o filme que lançou ontem?",
            "Trabalhando no novo projeto, muito empolgante!",
            "Pizza ou hambúrguer para o almoço? 🍕🍔",
            "Consegui resolver o bug finalmente!",
            "Fim de semana chegando! 🎉"
        ]
        
        # Criar mensagens para cada canal
        message_id_counter = 1000000000
        
        for channel_data in channels_data:
            channel_id = channel_data["discord_channel_id"]
            
            # Criar 20-30 mensagens por canal
            num_messages = random.randint(20, 30)
            
            for i in range(num_messages):
                user = random.choice(users)
                message_content = random.choice(sample_messages)
                
                # Timestamp aleatório nos últimos 30 dias
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                timestamp = datetime.now() - timedelta(
                    days=days_ago, 
                    hours=hours_ago, 
                    minutes=minutes_ago
                )
                
                message = Message(
                    discord_message_id=str(message_id_counter),
                    user_id=user["id"],
                    username=user["name"],
                    content=message_content,
                    timestamp=timestamp,
                    channel_id=channel_id,
                    channel_name=channel_data["name"],
                    server_id=channel_data["server_id"],
                    server_name=channel_data["server_name"],
                    message_type="text",
                    is_bot=user["is_bot"]
                )
                
                db.session.add(message)
                message_id_counter += 1
        
        # Adicionar algumas mensagens com mídia (simuladas)
        media_messages = [
            {
                "content": "Olhem essa imagem incrível!",
                "message_type": "image",
                "media_filename": "exemplo.jpg"
            },
            {
                "content": "Gravei um áudio explicando o projeto",
                "message_type": "audio", 
                "media_filename": "explicacao.mp3"
            }
        ]
        
        for media_msg in media_messages:
            user = random.choice(users)
            channel_data = random.choice(channels_data)
            
            message = Message(
                discord_message_id=str(message_id_counter),
                user_id=user["id"],
                username=user["name"],
                content=media_msg["content"],
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 48)),
                channel_id=channel_data["discord_channel_id"],
                channel_name=channel_data["name"],
                server_id=channel_data["server_id"],
                server_name=channel_data["server_name"],
                message_type=media_msg["message_type"],
                media_filename=media_msg["media_filename"],
                is_bot=user["is_bot"]
            )
            
            db.session.add(message)
            message_id_counter += 1
        
        db.session.commit()
        print(f"Dados de exemplo adicionados com sucesso!")
        print(f"- {len(channels_data)} canais criados")
        print(f"- Aproximadamente {len(channels_data) * 25} mensagens criadas")
        print("- Dados de mídia simulados adicionados")

if __name__ == "__main__":
    add_sample_data()

