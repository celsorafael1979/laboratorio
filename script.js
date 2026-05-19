// Estado da aplicação
let state = {
    laboratorios: JSON.parse(localStorage.getItem('laboratorios')) || [],
    semestres: JSON.parse(localStorage.getItem('semestres')) || []
};

// Elementos do DOM
const navItems = document.querySelectorAll('.nav-item');
const sections = document.querySelectorAll('.page-section');
const formLab = document.getElementById('form-laboratorio');
const formSemestre = document.getElementById('form-semestre');
const tbodyLab = document.querySelector('#table-laboratorios tbody');
const tbodySemestre = document.querySelector('#table-semestres tbody');

// Inicialização
function init() {
    setupNavigation();
    setupForms();
    renderTables();
}

// Navegação
function setupNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Atualiza menu ativo
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Mostra seção correspondente
            const targetId = item.getAttribute('data-target');
            sections.forEach(sec => {
                sec.classList.remove('active');
                if(sec.id === targetId) {
                    sec.classList.add('active');
                }
            });
        });
    });
}

// Configuração de Formulários
function setupForms() {
    // Form Laboratório
    formLab.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const novoLab = {
            id: Date.now().toString(),
            nome: document.getElementById('lab-nome').value,
            local: document.getElementById('lab-local').value,
            responsavel: document.getElementById('lab-responsavel').value
        };
        
        state.laboratorios.push(novoLab);
        saveState();
        renderLaboratorios();
        formLab.reset();
        
        // Foco no primeiro campo
        document.getElementById('lab-nome').focus();
    });

    // Form Semestre
    formSemestre.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const dataInicio = new Date(document.getElementById('sem-data-inicio').value);
        const dataFim = new Date(document.getElementById('sem-data-fim').value);
        
        if(dataFim <= dataInicio) {
            alert('A data final deve ser posterior à data inicial.');
            return;
        }

        const novoSemestre = {
            id: Date.now().toString(),
            ano: document.getElementById('sem-ano').value,
            semestre: document.getElementById('sem-semestre').value,
            dataInicio: document.getElementById('sem-data-inicio').value,
            dataFim: document.getElementById('sem-data-fim').value
        };
        
        state.semestres.push(novoSemestre);
        saveState();
        renderSemestres();
        formSemestre.reset();
    });
}

// Funções de Renderização
function renderTables() {
    renderLaboratorios();
    renderSemestres();
}

function renderLaboratorios() {
    tbodyLab.innerHTML = '';
    
    if (state.laboratorios.length === 0) {
        tbodyLab.innerHTML = '<tr><td colspan="4" class="empty-state">Nenhum laboratório cadastrado.</td></tr>';
        return;
    }
    
    state.laboratorios.forEach(lab => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${lab.nome}</td>
            <td>${lab.local}</td>
            <td>${lab.responsavel}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteLab('${lab.id}')">Excluir</button>
            </td>
        `;
        tbodyLab.appendChild(tr);
    });
}

function renderSemestres() {
    tbodySemestre.innerHTML = '';
    
    if (state.semestres.length === 0) {
        tbodySemestre.innerHTML = '<tr><td colspan="4" class="empty-state">Nenhum semestre cadastrado.</td></tr>';
        return;
    }
    
    state.semestres.forEach(sem => {
        const tr = document.createElement('tr');
        const dtIni = new Date(sem.dataInicio).toLocaleDateString('pt-BR');
        const dtFim = new Date(sem.dataFim).toLocaleDateString('pt-BR');
        
        tr.innerHTML = `
            <td>${sem.ano} / ${sem.semestre}º</td>
            <td>${dtIni}</td>
            <td>${dtFim}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteSemestre('${sem.id}')">Excluir</button>
            </td>
        `;
        tbodySemestre.appendChild(tr);
    });
}

// Funções de Exclusão
window.deleteLab = function(id) {
    if(confirm('Tem certeza que deseja excluir este laboratório?')) {
        state.laboratorios = state.laboratorios.filter(l => l.id !== id);
        saveState();
        renderLaboratorios();
    }
}

window.deleteSemestre = function(id) {
    if(confirm('Tem certeza que deseja excluir este semestre?')) {
        state.semestres = state.semestres.filter(s => s.id !== id);
        saveState();
        renderSemestres();
    }
}

// Persistência
function saveState() {
    localStorage.setItem('laboratorios', JSON.stringify(state.laboratorios));
    localStorage.setItem('semestres', JSON.stringify(state.semestres));
}

// Inicia aplicação
init();
