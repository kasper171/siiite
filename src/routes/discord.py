from flask import Blueprint, jsonify, request, current_app
from src.models.message import Message, Channel, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

discord_bp = Blueprint('discord', __name__)

# Configurações para upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@discord_bp.route('/channels', methods=['GET'])
def get_channels():
    """Retorna lista de canais disponíveis"""
    channels = Channel.query.all()
    return jsonify([channel.to_dict() for channel in channels])

@discord_bp.route('/channels', methods=['POST'])
def create_channel():
    """Cria um novo canal"""
    data = request.json
    
    # Verifica se o canal já existe
    existing_channel = Channel.query.filter_by(discord_channel_id=data['discord_channel_id']).first()
    if existing_channel:
        return jsonify(existing_channel.to_dict()), 200
    
    channel = Channel(
        discord_channel_id=data['discord_channel_id'],
        name=data['name'],
        server_id=data['server_id'],
        server_name=data['server_name']
    )
    db.session.add(channel)
    db.session.commit()
    return jsonify(channel.to_dict()), 201

@discord_bp.route('/messages/<channel_id>', methods=['GET'])
def get_messages(channel_id):
    """Retorna mensagens de um canal específico"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search', '')
    
    query = Message.query.filter_by(channel_id=channel_id)
    
    if search:
        query = query.filter(Message.content.contains(search))
    
    messages = query.order_by(Message.timestamp.asc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        'messages': [message.to_dict() for message in messages.items],
        'total': messages.total,
        'pages': messages.pages,
        'current_page': page,
        'has_next': messages.has_next,
        'has_prev': messages.has_prev
    })

@discord_bp.route('/messages', methods=['POST'])
def create_message():
    """Adiciona nova mensagem (para o bot do Discord)"""
    data = request.json
    
    # Verifica se a mensagem já existe
    existing_message = Message.query.filter_by(discord_message_id=data['discord_message_id']).first()
    if existing_message:
        return jsonify(existing_message.to_dict()), 200
    
    # Converte timestamp se necessário
    timestamp = data.get('timestamp')
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
    elif not timestamp:
        timestamp = datetime.utcnow()
    
    message = Message(
        discord_message_id=data['discord_message_id'],
        user_id=data['user_id'],
        username=data['username'],
        avatar_url=data.get('avatar_url'),
        content=data.get('content', ''),
        timestamp=timestamp,
        channel_id=data['channel_id'],
        channel_name=data['channel_name'],
        server_id=data['server_id'],
        server_name=data['server_name'],
        message_type=data.get('message_type', 'text'),
        media_url=data.get('media_url'),
        media_filename=data.get('media_filename'),
        is_bot=data.get('is_bot', False)
    )
    
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict()), 201

@discord_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload de arquivos de mídia"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Determina o diretório baseado no tipo de arquivo
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}:
            upload_dir = 'images'
        else:
            upload_dir = 'audio'
        
        # Cria diretório se não existir
        upload_path = os.path.join(current_app.static_folder, 'uploads', upload_dir)
        os.makedirs(upload_path, exist_ok=True)
        
        # Salva o arquivo
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Retorna URL relativa
        file_url = f'/uploads/{upload_dir}/{filename}'
        return jsonify({
            'url': file_url,
            'filename': filename,
            'type': upload_dir
        }), 200
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

@discord_bp.route('/servers', methods=['GET'])
def get_servers():
    """Retorna lista de servidores disponíveis"""
    servers = db.session.query(Channel.server_id, Channel.server_name).distinct().all()
    return jsonify([{
        'server_id': server.server_id,
        'server_name': server.server_name
    } for server in servers])

@discord_bp.route('/servers/<server_id>/channels', methods=['GET'])
def get_server_channels(server_id):
    """Retorna canais de um servidor específico"""
    channels = Channel.query.filter_by(server_id=server_id).all()
    return jsonify([channel.to_dict() for channel in channels])

@discord_bp.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas gerais"""
    total_messages = Message.query.count()
    total_channels = Channel.query.count()
    total_servers = db.session.query(Channel.server_id).distinct().count()
    
    return jsonify({
        'total_messages': total_messages,
        'total_channels': total_channels,
        'total_servers': total_servers
    })

