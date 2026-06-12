document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            // Não impedir o envio padrão — apenas validar campos localmente.
            const email = document.getElementById('emailInput').value;
            const password = document.getElementById('passwordInput').value;

            console.log(`Tentativa de login com email: ${email}`);

            // Validação simples no cliente: se estiver faltando algo, bloqueia e mostra alerta
            if (!email || !password) {
                e.preventDefault();
                alert('Informe e-mail e senha antes de entrar.');
                return;
            }
            // Caso contrário, permite o envio do formulário para o servidor processar.
        });
    }
});

// Tag input utilities (used in admin users modals)
function createChipElement(id, label, inputName) {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.dataset.value = id;

    const lbl = document.createElement('span');
    lbl.className = 'chip-label';
    lbl.textContent = label;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'chip-remove';
    btn.innerHTML = '&times;';

    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = inputName;
    hidden.value = id;

    btn.addEventListener('click', () => {
        chip.remove();
        hidden.remove();
    });

    chip.appendChild(lbl);
    chip.appendChild(btn);
    chip.appendChild(hidden);
    return chip;
}

function initTagSearch(root) {
    // root: element that contains tag-search, suggestions and chips
    const search = root.querySelector('.tag-search');
    const dropdown = root.querySelector('.suggestion-dropdown');
    const chipsArea = root.querySelector('.tag-chips');
    const inputName = root.dataset.inputName; // expected name for hidden inputs
    const listKey = root.dataset.listKey; // 'permissions' or 'groups'
    const dataList = window.ALL_PERMISSIONS || window.ALL_GROUPS || [];

    // choose correct list
    const options = window[listKey === 'groups' ? 'ALL_GROUPS' : 'ALL_PERMISSIONS'] || [];

    function showSuggestions(filter) {
        dropdown.innerHTML = '';
        const q = (filter || '').toLowerCase();
        const filtered = options.filter(o => o.name.toLowerCase().includes(q));
        filtered.slice(0, 50).forEach(opt => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = opt.name;
            item.dataset.id = opt.id;
            item.dataset.name = opt.name;
            item.addEventListener('click', () => {
                // avoid duplicates
                if ([...chipsArea.querySelectorAll('.chip')].some(c => c.dataset.value == opt.id)) return;
                const chip = createChipElement(opt.id, opt.name, inputName);
                chipsArea.appendChild(chip);
                dropdown.innerHTML = '';
                search.value = '';
            });
            dropdown.appendChild(item);
        });
        if (filtered.length === 0) {
            const no = document.createElement('div');
            no.className = 'suggestion-item';
            no.textContent = 'Nenhuma permissão encontrada';
            dropdown.appendChild(no);
        }
    }

    if (!search) return;
    search.addEventListener('input', (e) => {
        const v = e.target.value;
        if (!v) { dropdown.innerHTML = ''; return; }
        showSuggestions(v);
    });
    // click outside to close
    document.addEventListener('click', (e) => {
        if (!root.contains(e.target)) dropdown.innerHTML = '';
    });
    // attach remove handlers to any pre-rendered chips
    chipsArea.querySelectorAll('.chip').forEach(ch => {
        const btn = ch.querySelector('.chip-remove');
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                const hidden = ch.querySelector('input[type="hidden"]');
                ch.remove();
                if (hidden) hidden.remove();
            });
        }
    });
}

// Initialize tag inputs on the page
document.addEventListener('DOMContentLoaded', () => {
    const tagRoots = document.querySelectorAll('.tag-input-root');
    tagRoots.forEach(r => initTagSearch(r));
});

// Peças modal + AJAX management
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('pecaModal');
    if (!modalEl) return;
    const bsModal = new bootstrap.Modal(modalEl);
    const form = document.getElementById('pecaForm');
    const saveBtn = document.getElementById('pecaFormSave');
    const errorEl = document.getElementById('pecaFormError');

    function clearForm() {
        document.getElementById('peca_pk').value = '';
        document.getElementById('nome_peca').value = '';
        document.getElementById('descricao_peca').value = '';
        document.getElementById('custo_peca').value = '';
        document.getElementById('quant_peca').value = 0;
        document.getElementById('alerta_quant').value = 5;
        const sel = document.getElementById('fornecedores_select');
        if (sel) Array.from(sel.options).forEach(o => o.selected = false);
        if (errorEl) { errorEl.style.display = 'none'; errorEl.textContent = ''; }
    }

    function openModalForCreate() {
        clearForm();
        document.getElementById('pecaModalTitle').textContent = 'Adicionar Peça';
        bsModal.show();
    }

    function openModalForEdit(row) {
        if (!row) return;
        document.getElementById('pecaModalTitle').textContent = 'Editar Peça';
        document.getElementById('peca_pk').value = row.dataset.pk || '';
        document.getElementById('nome_peca').value = row.dataset.nome || '';
        document.getElementById('descricao_peca').value = row.dataset.descricao || '';
        document.getElementById('custo_peca').value = row.dataset.custo || '';
        document.getElementById('quant_peca').value = row.dataset.quant || 0;
        document.getElementById('alerta_quant').value = row.dataset.alerta || 5;
        const ids = (row.dataset.fornecedoresIds || '').split(',').filter(Boolean);
        const sel = document.getElementById('fornecedores_select');
        if (sel) Array.from(sel.options).forEach(o => o.selected = ids.includes(o.value));
        if (errorEl) { errorEl.style.display = 'none'; errorEl.textContent = ''; }
        bsModal.show();
    }

    function addRowForPeca(peca) {
        const tbody = document.querySelector('#pecasTable tbody');
        const tr = document.createElement('tr');
        const fornIds = (peca.fornecedores || []).map(f => f.id).join(',');
        const fornNames = (peca.fornecedores || []).map(f => f.nome).join(', ');
        tr.dataset.pk = peca.id;
        tr.dataset.nome = peca.nome_peca;
        tr.dataset.descricao = peca.descricao_peca || '';
        tr.dataset.custo = peca.custo_peca;
        tr.dataset.quant = peca.quant_peca;
        tr.dataset.alerta = peca.alerta_quant;
        tr.dataset.fornecedoresIds = fornIds;
        tr.dataset.fornecedoresNames = fornNames;

        tr.innerHTML = `
            <td class="peca-pk">${peca.id}</td>
            <td class="peca-nome">${peca.nome_peca}</td>
            <td class="peca-custo">${peca.custo_peca}</td>
            <td class="peca-quant">${peca.quant_peca}</td>
            <td class="peca-alerta">${peca.alerta_quant}</td>
            <td class="peca-fornecedores">${fornNames || '-'}</td>
            <td>
              <button type="button" class="btn btn-sm btn-outline-primary js-edit-peca">Editar</button>
              <button type="button" class="btn btn-sm btn-outline-danger js-delete-peca">Excluir</button>
            </td>
        `;
        tbody.appendChild(tr);
        bindRowButtons(tr);
    }

    function updateRowForPeca(peca) {
        const row = document.querySelector(`#pecasTable tr[data-pk='${peca.id}']`);
        if (!row) return;
        const fornNames = (peca.fornecedores || []).map(f => f.nome).join(', ');
        const fornIds = (peca.fornecedores || []).map(f => f.id).join(',');
        row.dataset.nome = peca.nome_peca;
        row.dataset.descricao = peca.descricao_peca || '';
        row.dataset.custo = peca.custo_peca;
        row.dataset.quant = peca.quant_peca;
        row.dataset.alerta = peca.alerta_quant;
        row.dataset.fornecedoresIds = fornIds;
        row.dataset.fornecedoresNames = fornNames;
        row.querySelector('.peca-nome').textContent = peca.nome_peca;
        row.querySelector('.peca-custo').textContent = peca.custo_peca;
        row.querySelector('.peca-quant').textContent = peca.quant_peca;
        row.querySelector('.peca-alerta').textContent = peca.alerta_quant;
        row.querySelector('.peca-fornecedores').textContent = fornNames || '-';
    }

    function bindRowButtons(row) {
        const editBtn = row.querySelector('.js-edit-peca');
        const delBtn = row.querySelector('.js-delete-peca');
        if (editBtn) editBtn.addEventListener('click', (e) => openModalForEdit(row));
        if (delBtn) delBtn.addEventListener('click', (e) => {
            if (!confirm('Excluir peça?')) return;
            const pk = row.dataset.pk;
            const url = `/admin/pecas/${pk}/deletar/`;
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin'
            }).then(r => r.json()).then(json => {
                if (json && json.success) {
                    row.remove();
                } else {
                    alert((json && json.message) || 'Erro ao excluir.');
                }
            }).catch(err => alert('Erro ao excluir peça.'));
        });
    }

    // bind existing rows
    document.querySelectorAll('#pecasTable tbody tr').forEach(r => bindRowButtons(r));

    document.getElementById('btnOpenPecaModal').addEventListener('click', (e) => openModalForCreate());

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const pk = document.getElementById('peca_pk').value;
        const url = pk ? `/admin/pecas/${pk}/editar/` : '/admin/pecas/novo/';
        const formData = new FormData(form);
        // ensure fornecedores selected values are collected
        const sel = document.getElementById('fornecedores_select');
        if (sel) {
            const selected = Array.from(sel.selectedOptions).map(o => o.value);
            // remove previous keys and set the correct ones
            formData.delete('fornecedores');
            selected.forEach(v => formData.append('fornecedores', v));
        }

        saveBtn.disabled = true;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData,
            credentials: 'same-origin'
        }).then(r => r.json()).then(json => {
            saveBtn.disabled = false;
            if (!json) { showError('Resposta inesperada do servidor.'); return; }
            if (json.success) {
                if (json.peca) {
                    if (pk) updateRowForPeca(json.peca);
                    else addRowForPeca(json.peca);
                }
                bsModal.hide();
                clearForm();
            } else {
                const msg = json.message || 'Erro ao salvar peça.';
                if (errorEl) { errorEl.style.display = 'block'; errorEl.textContent = msg; }
            }
        }).catch(err => {
            saveBtn.disabled = false;
            if (errorEl) { errorEl.style.display = 'block'; errorEl.textContent = 'Erro ao comunicar com o servidor.'; }
        });
    });

    function showError(msg) {
        if (errorEl) { errorEl.style.display = 'block'; errorEl.textContent = msg; }
    }
});