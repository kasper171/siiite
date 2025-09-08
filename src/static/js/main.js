// Configurações globais
const API_BASE = '/api';
let currentChannelId = null;
let currentPage = 1;
let isLoading = false;
let searchQuery = '';

// Elementos DOM
const elements = {
    serverList: document.getElementById('serverList'),
    channelsList: document.getElementById('textChannels'),
    messagesList: document.getElementById('messagesList'),
    currentChannelName: document.getElementById('currentChannelName'),
    serverName: document.getElementById('serverName'),
    searchBtn: document.getElementById('searchBtn'),
    searchBar: document.getElementById('searchBar'),
    searchInput: document.getElementById('searchInput'),
    searchSubmit: document.getElementById('searchSubmit'),
    refreshBtn: document.getElementById('refreshBtn'),
    loading: document.getElementById('loading'),
    mediaModal: document.getElementById('mediaModal'),
    modalBody: document.getElementById('modalBody'),
    closeModal: document.getElementById('closeModal')
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Configurar event listeners
function setupEventListeners() {
    // Botão de busca
    elements.searchBtn.addEventListener('click', toggleSearch);
    
    // Busca
    elements.searchSubmit.addEventListener('click', performSearch);
    elements.searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Refresh
    elements.refreshBtn.addEventListener('click', function() {
        if (currentChannelId) {
            loadMessages(currentChannelId, 1, true);
        }
    });
    
    // Modal
    elements.closeModal.addEventListener('click', closeMediaModal);
    elements.mediaModal.addEventListener('click', function(e) {
        if (e.target === elements.mediaModal) {
            closeMediaModal();
        }
    });
    
    // Scroll infinito
    elements.messagesList.addEventListener('scroll', handleScroll);
}

// Inicializar aplicação
async function initializeApp() {
    try {
        await loadServers();
        await loadChannels();
    } catch (error) {
        console.error('Erro ao inicializar aplicação:', error);
        showError('Erro ao carregar dados iniciais');
    }
}

// Carregar servidores
async function loadServers() {
    try {
        const response = await fetch(`${API_BASE}/servers`);
        const servers = await response.json();
        
        // Limpar lista atual (manter o item "home")
        const homeItem = elements.serverList.querySelector('.server-item[data-server-id="all"]');
        elements.serverList.innerHTML = '';
        elements.serverList.appendChild(homeItem);
        
        // Adicionar servidores
        servers.forEach(server => {
            const serverItem = createServerItem(server);
            elements.serverList.appendChild(serverItem);
        });
        
    } catch (error) {
        console.error('Erro ao carregar servidores:', error);
    }
}

// Criar item de servidor
function createServerItem(server) {
    const serverItem = document.createElement('div');
    serverItem.className = 'server-item';
    serverItem.setAttribute('data-server-id', server.server_id);
    serverItem.title = server.server_name;
    
    // Usar primeira letra do nome do servidor
    const firstLetter = server.server_name.charAt(0).toUpperCase();
    serverItem.textContent = firstLetter;
    
    serverItem.addEventListener('click', function() {
        selectServer(server.server_id, server.server_name);
    });
    
    return serverItem;
}

// Selecionar servidor
async function selectServer(serverId, serverName) {
    // Atualizar UI
    document.querySelectorAll('.server-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const selectedItem = document.querySelector(`[data-server-id="${serverId}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    elements.serverName.textContent = serverName || 'Discord Backup';
    
    // Carregar canais do servidor
    if (serverId === 'all') {
        await loadChannels();
    } else {
        await loadServerChannels(serverId);
    }
}

// Carregar todos os canais
async function loadChannels() {
    try {
        const response = await fetch(`${API_BASE}/channels`);
        const channels = await response.json();
        
        displayChannels(channels);
    } catch (error) {
        console.error('Erro ao carregar canais:', error);
    }
}

// Carregar canais de um servidor específico
async function loadServerChannels(serverId) {
    try {
        const response = await fetch(`${API_BASE}/servers/${serverId}/channels`);
        const channels = await response.json();
        
        displayChannels(channels);
    } catch (error) {
        console.error('Erro ao carregar canais do servidor:', error);
    }
}

// Exibir canais
function displayChannels(channels) {
    elements.channelsList.innerHTML = '';
    
    if (channels.length === 0) {
        elements.channelsList.innerHTML = '<div style="padding: 8px; color: #72767d; font-size: 14px;">Nenhum canal encontrado</div>';
        return;
    }
    
    channels.forEach(channel => {
        const channelItem = createChannelItem(channel);
        elements.channelsList.appendChild(channelItem);
    });
}

// Criar item de canal
function createChannelItem(channel) {
    const channelItem = document.createElement('div');
    channelItem.className = 'channel-item';
    channelItem.setAttribute('data-channel-id', channel.discord_channel_id);
    
    channelItem.innerHTML = `
        <i class="fas fa-hashtag"></i>
        <span>${channel.name}</span>
    `;
    
    channelItem.addEventListener('click', function() {
        selectChannel(channel.discord_channel_id, channel.name);
    });
    
    return channelItem;
}

// Selecionar canal
function selectChannel(channelId, channelName) {
    // Atualizar UI
    document.querySelectorAll('.channel-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const selectedItem = document.querySelector(`[data-channel-id="${channelId}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    elements.currentChannelName.textContent = channelName;
    currentChannelId = channelId;
    currentPage = 1;
    
    // Carregar mensagens
    loadMessages(channelId, 1, true);
}

// Carregar mensagens
async function loadMessages(channelId, page = 1, clearMessages = false) {
    if (isLoading) return;
    
    isLoading = true;
    elements.loading.style.display = 'flex';
    
    try {
        const url = new URL(`${window.location.origin}${API_BASE}/messages/${channelId}`);
        url.searchParams.append('page', page);
        url.searchParams.append('limit', 50);
        
        if (searchQuery) {
            url.searchParams.append('search', searchQuery);
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (clearMessages) {
            elements.messagesList.innerHTML = '';
        }
        
        if (data.messages.length === 0 && page === 1) {
            elements.messagesList.innerHTML = `
                <div class="welcome-message">
                    <i class="fas fa-inbox"></i>
                    <h2>Nenhuma mensagem encontrada</h2>
                    <p>Este canal não possui mensagens ou não corresponde à sua busca.</p>
                </div>
            `;
        } else {
            data.messages.forEach(message => {
                const messageElement = createMessageElement(message);
                elements.messagesList.appendChild(messageElement);
            });
            
            // Scroll para o final se for a primeira página
            if (page === 1) {
                elements.messagesList.scrollTop = elements.messagesList.scrollHeight;
            }
        }
        
        currentPage = page;
        
    } catch (error) {
        console.error('Erro ao carregar mensagens:', error);
        showError('Erro ao carregar mensagens');
    } finally {
        isLoading = false;
        elements.loading.style.display = 'none';
    }
}

// Criar elemento de mensagem
function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    // Determinar se é mensagem própria (você pode ajustar esta lógica)
    const isOwnMessage = message.is_bot || message.username === 'Backup Viewer';
    if (isOwnMessage) {
        messageDiv.classList.add('own-message');
    }
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (message.avatar_url) {
        avatar.innerHTML = `<img src="${message.avatar_url}" alt="${message.username}">`;
    } else {
        avatar.innerHTML = `<i class="fas fa-user"></i>`;
    }
    
    // Conteúdo da mensagem
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Header da mensagem
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const username = document.createElement('span');
    username.className = 'message-username';
    username.textContent = message.username;
    
    const timestamp = document.createElement('span');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = formatTimestamp(message.timestamp);
    
    header.appendChild(username);
    header.appendChild(timestamp);
    
    // Texto da mensagem
    const text = document.createElement('div');
    text.className = 'message-text';
    text.textContent = message.content || '';
    
    content.appendChild(header);
    content.appendChild(text);
    
    // Mídia
    if (message.media_url) {
        const media = createMediaElement(message);
        content.appendChild(media);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    return messageDiv;
}

// Criar elemento de mídia
function createMediaElement(message) {
    const mediaDiv = document.createElement('div');
    mediaDiv.className = 'message-media';
    
    if (message.message_type === 'image') {
        const img = document.createElement('img');
        img.className = 'message-image';
        img.src = message.media_url;
        img.alt = message.media_filename || 'Imagem';
        img.addEventListener('click', () => openMediaModal(message.media_url, 'image'));
        mediaDiv.appendChild(img);
    } else if (message.message_type === 'audio') {
        const audioContainer = document.createElement('div');
        audioContainer.className = 'message-audio';
        
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = message.media_url;
        
        audioContainer.appendChild(audio);
        mediaDiv.appendChild(audioContainer);
    }
    
    return mediaDiv;
}

// Formatar timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    const timeString = date.toLocaleTimeString('pt-BR', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (messageDate.getTime() === today.getTime()) {
        return `Hoje às ${timeString}`;
    } else if (messageDate.getTime() === today.getTime() - 86400000) {
        return `Ontem às ${timeString}`;
    } else {
        return date.toLocaleDateString('pt-BR') + ' às ' + timeString;
    }
}

// Toggle busca
function toggleSearch() {
    const isVisible = elements.searchBar.style.display !== 'none';
    elements.searchBar.style.display = isVisible ? 'none' : 'block';
    
    if (!isVisible) {
        elements.searchInput.focus();
    } else {
        elements.searchInput.value = '';
        searchQuery = '';
        if (currentChannelId) {
            loadMessages(currentChannelId, 1, true);
        }
    }
}

// Realizar busca
function performSearch() {
    searchQuery = elements.searchInput.value.trim();
    if (currentChannelId) {
        currentPage = 1;
        loadMessages(currentChannelId, 1, true);
    }
}

// Handle scroll para paginação
function handleScroll() {
    const container = elements.messagesList;
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
        if (currentChannelId && !isLoading) {
            loadMessages(currentChannelId, currentPage + 1, false);
        }
    }
}

// Abrir modal de mídia
function openMediaModal(mediaUrl, mediaType) {
    elements.modalBody.innerHTML = '';
    
    if (mediaType === 'image') {
        const img = document.createElement('img');
        img.src = mediaUrl;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '80vh';
        elements.modalBody.appendChild(img);
    }
    
    elements.mediaModal.style.display = 'flex';
}

// Fechar modal de mídia
function closeMediaModal() {
    elements.mediaModal.style.display = 'none';
    elements.modalBody.innerHTML = '';
}

// Mostrar erro
function showError(message) {
    // Você pode implementar um sistema de notificações mais sofisticado aqui
    console.error(message);
    alert(message);
}

// Utilitários para desenvolvimento/teste
window.DiscordBackup = {
    // Função para adicionar mensagens de teste
    addTestMessage: async function(channelId, messageData) {
        try {
            const response = await fetch(`${API_BASE}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(messageData)
            });
            
            if (response.ok) {
                console.log('Mensagem de teste adicionada com sucesso');
                if (currentChannelId === channelId) {
                    loadMessages(channelId, 1, true);
                }
            }
        } catch (error) {
            console.error('Erro ao adicionar mensagem de teste:', error);
        }
    },
    
    // Função para adicionar canal de teste
    addTestChannel: async function(channelData) {
        try {
            const response = await fetch(`${API_BASE}/channels`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(channelData)
            });
            
            if (response.ok) {
                console.log('Canal de teste adicionado com sucesso');
                await loadChannels();
            }
        } catch (error) {
            console.error('Erro ao adicionar canal de teste:', error);
        }
    }
};

