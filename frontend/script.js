document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000';
    let global_access_token = null;
    let draggedCard = null;
    let pollingInterval = null;
    let isPollingActive = false;

    const ui = {
        auth: document.getElementById('auth-section'),
        regUser: document.getElementById('reg-username'),
        regPass: document.getElementById('reg-password'),
        loginUser: document.getElementById('login-username'),
        loginPass: document.getElementById('login-password'),
        ticket: document.getElementById('ticket-section'),
        batch: document.getElementById('batch-section'),
        andon: document.getElementById('andon-section'),
        light: document.getElementById('andon-light'),
        statusText: document.getElementById('andon-status-text'),
        pollingLabel: document.getElementById('polling-label'),
        pollingBtn: document.getElementById('polling-btn'),
        logout: document.getElementById('logoutBtn'),
        msg: document.getElementById('message'),
        logCont: document.getElementById('logListContainer'),
        fileInput: document.getElementById('jsonFileInput'),
        tickTitle: document.getElementById('ticketTitle'),
        tickDesc: document.getElementById('ticketDescription'),
        tickPrio: document.getElementById('ticketPriority')
    };

    function showMsg(t, type = 'error') {
        if (!ui.msg) return;
        ui.msg.textContent = t; ui.msg.className = `message ${type}`;
        setTimeout(() => ui.msg.className = 'message', 5000);
    }

    // CORREÇÃO 1: Adicionado 'cache: no-store' para obrigar o navegador a buscar os dados novos do Polling
    async function fetchAPI(end, opt = {}) {
        const headers = { ...opt.headers, 'Content-Type': 'application/json' };
        if (global_access_token) headers['Authorization'] = `Bearer ${global_access_token}`;
        return fetch(`${API_URL}${end}`, { ...opt, headers, cache: 'no-store' });
    }

    // --- 1. AUTENTICAÇÃO ---
    const handleLogin = async () => {
        const username = ui.loginUser.value;
        const password = ui.loginPass.value;
        if (!username || !password) return showMsg("Preencha as credenciais de login.");
        try {
            const res = await fetchAPI('/api/auth/login', { 
                method: 'POST', body: JSON.stringify({ username, password }) 
            });
            const data = await res.json();
            if (res.status === 200) {
                global_access_token = data.access_token;
                ui.auth.style.display = 'none'; ui.ticket.style.display = 'block'; 
                ui.batch.style.display = 'block'; ui.andon.style.display = 'block'; ui.logout.style.display = 'block';
                setupDragAndDrop();
                fetchData();
                showMsg("Logged in!", "success");
            } else {
                showMsg("Login falhou. Verifique usuário e senha.");
            }
        } catch (e) { showMsg("Erro de conexão."); }
    };

    const handleRegister = async () => {
        const username = ui.regUser.value;
        const password = ui.regPass.value;
        if (!username || !password) return showMsg("Preencha os campos de registro.");
        try {
            const res = await fetchAPI('/api/auth/register', { 
                method: 'POST', body: JSON.stringify({ username, password }) 
            });
            if (res.status === 201) {
                showMsg("Usuário registrado com sucesso!", "success");
                ui.regUser.value = ''; ui.regPass.value = '';
            } else if (res.status === 409) {
                showMsg("Erro: Este usuário já existe! Faça login abaixo.");
            } else {
                showMsg("Falha no registro.");
            }
        } catch (e) { showMsg("Erro no servidor."); }
    };

    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) loginBtn.addEventListener('click', handleLogin);

    const regBtn = document.getElementById('registerUserBtn');
    if (regBtn) regBtn.addEventListener('click', handleRegister);

    [ui.loginUser, ui.loginPass].forEach(el => {
        if (el) el.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleLogin(); });
    });

    [ui.regUser, ui.regPass].forEach(el => {
        if (el) el.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleRegister(); });
    });

    // --- 2. DASHBOARD E TICKETS ---
    async function fetchData() {
        try {
            const [resT, resL] = await Promise.all([fetchAPI('/api/tickets'), fetchAPI('/api/logs')]);
            const tickets = await resT.json(); const logs = await resL.json();
            const tList = tickets.data || (Array.isArray(tickets) ? tickets : []);
            const lList = logs.data || (Array.isArray(logs) ? logs : []);

            const cols = { "open": document.getElementById('column-open'), "inprogress": document.getElementById('column-inprogress'), "closed": document.getElementById('column-closed') };
            Object.values(cols).forEach(c => { if(c) c.innerHTML = ''; });
            
            let maxV = 0;
            tList.forEach(t => {
                const key = t.status.toLowerCase().replace(/\s+/g, '');
                if (cols[key]) {
                    if (t.status !== 'Closed' || cols["closed"].children.length < 5) {
                        cols[key].appendChild(createCard(t));
                    }
                }
                if (t.status !== 'Closed') {
                    const v = t.priority.toLowerCase() === 'high' ? 2 : (t.priority.toLowerCase() === 'middle' ? 1 : 0);
                    if (v > maxV) maxV = v;
                }
            });
            
            ui.light.className = `andon-light status-${maxV}`;
            ui.statusText.textContent = `Status: ${maxV === 2 ? 'CRITICAL' : (maxV === 1 ? 'WARNING' : 'STABLE')}`;
            
            // ---> AQUI ESTÁ A CORREÇÃO: ATUALIZANDO OS CONTADORES <---
            if (document.getElementById('count-open')) {
                document.getElementById('count-open').textContent = tList.filter(t => t.status.toLowerCase().replace(/\s+/g, '') === 'open').length;
            }
            if (document.getElementById('count-inprogress')) {
                document.getElementById('count-inprogress').textContent = tList.filter(t => t.status.toLowerCase().replace(/\s+/g, '') === 'inprogress').length;
            }
            if (document.getElementById('count-closed')) {
                document.getElementById('count-closed').textContent = tList.filter(t => t.status.toLowerCase().replace(/\s+/g, '') === 'closed').length;
            }
            
            // Logs
            ui.logCont.innerHTML = '';
            const sortedLogs = lList.sort((a, b) => (b.id || 0) - (a.id || 0)).slice(0, 20);
            
            sortedLogs.forEach(l => {
                const div = document.createElement('div'); 
                div.className = 'log-card';
                let timeStr = new Date().toLocaleTimeString();
                if (l.timestamp || l.created_at) {
                    const dbDate = new Date(l.timestamp || l.created_at);
                    if (!isNaN(dbDate)) timeStr = dbDate.toLocaleTimeString();
                }
                div.innerHTML = `<span>[${timeStr}] <b>${l.action}</b>: ${l.details}</span>`;
                ui.logCont.appendChild(div);
            });
        } catch (e) { console.error("Refresh Error"); }
    }

    // --- 3. IA ANALYSIS ---
    async function runAIAnalysis(item) {
        try {
            const payload = {
                device_id: item.device_id || item.id || "UNKNOWN-DEVICE",
                cpu_usage_pct: item.metrics?.cpu_usage_pct ?? item.cpu_usage_pct ?? 0,
                mem_available_gb: item.metrics?.mem_available_gb ?? item.mem_available_gb ?? 2.0,
                active_threats: item.metrics?.active_threats ?? item.active_threats ?? 0,
                untrusted_processes: item.metrics?.untrusted_processes ?? item.untrusted_processes ?? 0
            };
            const res = await fetchAPI('/api/andon/analyze', { method: 'POST', body: JSON.stringify(payload) });
            const result = await res.json();
            
            if (res.status === 201 && result.data?.andon_status >= 1) {
                await fetchAPI('/api/tickets', {
                    method: 'POST', body: JSON.stringify({ 
                        title: `[AI Alert] Failure: ${payload.device_id}`, 
                        description: `Anomaly detected (CPU: ${payload.cpu_usage_pct}%).`, 
                        priority: result.data.andon_status === 2 ? "High" : "Middle" 
                    })
                });
            }
        } catch (e) { console.error("AI Error"); }
    }

    async function executePolling() {
        const randomID = Math.floor(Math.random() * 9000) + 1000;
        await runAIAnalysis({ 
            device_id: `SRV-POLL-${randomID}`, 
            cpu_usage_pct: 99.1, 
            active_threats: 3 
        });
        await fetchData(); 
    }

    ui.pollingBtn.addEventListener('click', () => {
        if (isPollingActive) {
            clearInterval(pollingInterval); isPollingActive = false;
            ui.pollingBtn.textContent = "Enable Polling";
        } else {
            executePolling();
            pollingInterval = setInterval(executePolling, 15000); 
            isPollingActive = true;
            ui.pollingBtn.textContent = "Disable Polling";
        }
    });

    // --- 4. BATCH E MANUAL ---
    if (ui.fileInput) {
        document.getElementById('processBatchBtn').addEventListener('click', () => {
            const file = ui.fileInput.files[0];
            if (!file) return showMsg("Selecione um arquivo JSON primeiro!", "error");
            showMsg("Lendo arquivo...", "success");
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const parsedData = JSON.parse(e.target.result);
                    const list = Array.isArray(parsedData) ? parsedData : (parsedData.data || parsedData.metrics || []);
                    if (list.length === 0) return showMsg("Nenhum dado encontrado no JSON.", "error");

                    for (const item of list) {
                        await runAIAnalysis(item);
                        await new Promise(r => setTimeout(r, 50));
                    }
                    ui.fileInput.value = ''; await fetchData();
                    showMsg("Arquivo processado com sucesso!", "success");
                } catch (err) { showMsg("Erro: Arquivo JSON inválido.", "error"); }
            };
            reader.readAsText(file);
        });
    }

    document.getElementById('registerTicketBtn').addEventListener('click', async () => {
        const res = await fetchAPI('/api/tickets', {
            method: 'POST', body: JSON.stringify({ 
                title: ui.tickTitle.value, description: ui.tickDesc.value, priority: ui.tickPrio.value 
            })
        });
        if (res.status === 201) { ui.tickTitle.value=''; ui.tickDesc.value=''; fetchData(); }
    });

    function createCard(t) {
        const card = document.createElement('div');
        const prio = t.priority.charAt(0).toUpperCase() + t.priority.slice(1).toLowerCase();
        card.className = `ticket-card priority-${prio}`;
        card.id = `ticket-${t.id}`; card.draggable = true;
        card.innerHTML = `<strong>${t.title}</strong><br><small>${t.priority}</small>`;
        card.addEventListener('dragstart', () => draggedCard = card);
        return card;
    }

    function setupDragAndDrop() {
        document.querySelectorAll('.ticket-list').forEach(list => {
            list.addEventListener('dragover', (e) => e.preventDefault());
            list.addEventListener('drop', async () => {
                const tid = draggedCard.id.replace('ticket-', '');
                const map = { 'column-open': 'Open', 'column-inprogress': 'In Progress', 'column-closed': 'Closed' };
                await fetchAPI(`/api/tickets/${tid}`, { method: 'PUT', body: JSON.stringify({ status: map[list.id] }) });
                fetchData();
            });
        });
    }

    if (ui.logout) ui.logout.addEventListener('click', () => location.reload());
});