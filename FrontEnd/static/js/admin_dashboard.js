/* ══════════════════════════════════════════════════════════════
   Admin Dashboard — Client-side JavaScript
   ══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── Helpers ────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const CSRF = getCookie('csrftoken');

  // ── Role from data attribute ──
  const USER_ROLE = $('.dash-content')?.dataset.role || 'data_moderator';
  const IS_ADMIN = USER_ROLE === 'admin';

  function api(url, opts = {}) {
    const headers = { 'X-CSRFToken': CSRF, ...(opts.headers || {}) };
    if (opts.body && typeof opts.body === 'object' && !(opts.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(opts.body);
    }
    return fetch(url, { ...opts, headers }).then((r) => {
      if (!r.ok) return r.json().then((j) => Promise.reject(j));
      return r.json();
    });
  }

  // ══════════════════════════════════════════════════════════
  //  Role-based UI visibility
  // ══════════════════════════════════════════════════════════

  function applyRoleRestrictions() {
    // Data moderators cannot run scripts
    const runBtn = $('#btn-run-script');
    if (runBtn && !IS_ADMIN) {
      runBtn.style.display = 'none';
    }

    // Data moderators cannot access User Control tab
    const usersTabBtn = $('#tab-btn-users');
    if (usersTabBtn && !IS_ADMIN) {
      usersTabBtn.style.display = 'none';
    }
  }
  applyRoleRestrictions();

  // ══════════════════════════════════════════════════════════
  //  Tab Switching
  // ══════════════════════════════════════════════════════════

  const tabBtns = $$('.tab-btn');
  const tabPanels = $$('.tab-panel');

  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      // Prevent data moderator from accessing users tab
      if (target === 'users' && !IS_ADMIN) return;

      tabBtns.forEach((b) => b.classList.remove('active'));
      tabPanels.forEach((p) => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = $(`#panel-${target}`);
      panel.classList.add('active');

      // Lazy-load tab data
      if (target === 'data' && !panel._loaded) {
        loadTables();
        panel._loaded = true;
      }
      if (target === 'users' && !panel._loaded) {
        loadUsers();
        panel._loaded = true;
      }
    });
  });

  // ══════════════════════════════════════════════════════════
  //  TAB 1 — Console Log
  // ══════════════════════════════════════════════════════════

  const consoleBox = $('#console-output');
  const statusDot = $('#status-dot');
  const statusText = $('#status-text');
  let consoleCleared = false;

  function classifyLine(line) {
    if (line.startsWith('───') || line.startsWith('===')) return 'separator';
    if (/error|✗|exception|traceback/i.test(line)) return 'error';
    return '';
  }

  async function fetchLogs() {
    try {
      const data = await api('/admin/api/logs/');
      if (!consoleCleared) {
        const html = data.lines
          .map((l) => {
            const cls = classifyLine(l);
            const escaped = l
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;');
            return `<span class="console-line${cls ? ' ' + cls : ''}">${escaped}</span>`;
          })
          .join('\n');
        consoleBox.innerHTML = html || '<span class="console-placeholder">No log output yet.</span>';
        consoleBox.scrollTop = consoleBox.scrollHeight;
      }

      if (data.running) {
        statusDot.classList.add('running');
        statusText.textContent = 'Script running…';
      } else {
        statusDot.classList.remove('running');
        statusText.textContent = 'Idle';
      }
    } catch (e) {
      /* ignore transient errors */
    }
  }

  // Initial fetch (no auto-polling — use "Update Log" button to refresh)
  fetchLogs();

  // Manual "Update Log" button
  const updateLogBtn = $('#btn-update-log');
  if (updateLogBtn) {
    updateLogBtn.addEventListener('click', () => {
      consoleCleared = false;
      fetchLogs();
    });
  }

  // Run script (admin only — button is hidden for data moderators)
  const runScriptBtn = $('#btn-run-script');
  if (runScriptBtn) {
    runScriptBtn.addEventListener('click', async () => {
      consoleCleared = false;
      try {
        const data = await api('/admin/api/run-script/', { method: 'POST' });
        if (data.status === 'already_running') {
          statusText.textContent = 'Already running…';
        }
      } catch (e) {
        statusText.textContent = 'Error starting script';
      }
    });
  }

  // Clear console (display only)
  $('#btn-clear-console').addEventListener('click', () => {
    consoleBox.innerHTML = '<span class="console-placeholder">Console cleared.</span>';
    consoleCleared = true;
    // Resume on next poll
    setTimeout(() => { consoleCleared = false; }, 5000);
  });

  // ══════════════════════════════════════════════════════════
  //  TAB 2 — Data Entry
  // ══════════════════════════════════════════════════════════

  const tableSelect = $('#table-select');
  const dynamicFields = $('#dynamic-fields');
  const insertBtn = $('#btn-insert');
  const insertFeedback = $('#insert-feedback');
  let currentColumns = [];

  async function loadTables() {
    try {
      const data = await api('/admin/api/tables/');
      tableSelect.innerHTML = '<option value="">— Choose a table —</option>';
      data.tables.forEach((t) => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = t;
        tableSelect.appendChild(opt);
      });
    } catch (e) {
      tableSelect.innerHTML = '<option value="">Error loading tables</option>';
    }
  }

  tableSelect.addEventListener('change', async () => {
    const table = tableSelect.value;
    dynamicFields.innerHTML = '';
    insertFeedback.textContent = '';
    insertFeedback.className = 'insert-feedback';
    currentColumns = [];
    insertBtn.disabled = true;

    if (!table) return;

    try {
      const data = await api(`/admin/api/tables/${encodeURIComponent(table)}/columns/`);
      currentColumns = data.columns;
      insertBtn.disabled = false;

      data.columns.forEach((col) => {
        const group = document.createElement('div');
        group.className = 'form-group';

        const label = document.createElement('label');
        label.setAttribute('for', `field-${col.name}`);
        label.innerHTML = `${col.name} <span class="field-type">${col.type || 'TEXT'}</span>`;

        const input = document.createElement('input');
        input.type = guessInputType(col.type);
        input.id = `field-${col.name}`;
        input.name = col.name;
        input.placeholder = col.pk ? 'Auto (PK)' : col.type || 'TEXT';
        if (col.type === 'TEXT' && col.name === 'datetime') {
          input.type = 'datetime-local';
        }

        group.appendChild(label);
        group.appendChild(input);
        dynamicFields.appendChild(group);
      });
    } catch (e) {
      dynamicFields.innerHTML = '<p style="color:var(--red)">Error loading columns</p>';
    }
  });

  function guessInputType(sqlType) {
    if (!sqlType) return 'text';
    const t = sqlType.toUpperCase();
    if (t.includes('INT') || t.includes('REAL') || t.includes('FLOAT') || t.includes('DOUBLE') || t.includes('NUMERIC')) return 'number';
    return 'text';
  }

  insertBtn.addEventListener('click', async () => {
    const table = tableSelect.value;
    if (!table) return;

    const row = {};
    currentColumns.forEach((col) => {
      const input = $(`#field-${CSS.escape(col.name)}`);
      if (input && input.value.trim() !== '') {
        let val = input.value.trim();
        // Convert number inputs to actual numbers
        if (input.type === 'number' && val !== '') {
          val = parseFloat(val);
          if (isNaN(val)) val = input.value.trim();
        }
        row[col.name] = val;
      }
    });

    if (Object.keys(row).length === 0) {
      showFeedback('Please fill in at least one field.', 'error');
      return;
    }

    insertBtn.disabled = true;
    try {
      await api('/admin/api/insert/', {
        method: 'POST',
        body: { table, data: row },
      });
      showFeedback(`✓ Row inserted into "${table}" successfully.`, 'success');
      // Clear inputs
      currentColumns.forEach((col) => {
        const input = $(`#field-${CSS.escape(col.name)}`);
        if (input) input.value = '';
      });
    } catch (e) {
      showFeedback(`✗ Error: ${e.error || 'Insert failed'}`, 'error');
    } finally {
      insertBtn.disabled = false;
    }
  });

  function showFeedback(msg, type) {
    insertFeedback.textContent = msg;
    insertFeedback.className = `insert-feedback ${type}`;
    setTimeout(() => {
      insertFeedback.textContent = '';
      insertFeedback.className = 'insert-feedback';
    }, 6000);
  }

  // ══════════════════════════════════════════════════════════
  //  TAB 3 — User Control (Admin only)
  // ══════════════════════════════════════════════════════════

  const usersTbody = $('#users-tbody');
  const userModal = $('#user-modal');
  const userForm = $('#user-form');
  const modalTitle = $('#modal-title');

  const ROLE_LABELS = {
    admin: { text: 'Admin', cls: 'badge-purple' },
    data_moderator: { text: 'Data Moderator', cls: 'badge-blue' },
    user: { text: 'User', cls: 'badge-yellow' },
  };

  async function loadUsers() {
    if (!IS_ADMIN) return;
    try {
      const data = await api('/admin/api/users/');
      renderUsersTable(data.users);
    } catch (e) {
      usersTbody.innerHTML = '<tr><td colspan="6" style="color:var(--red)">Error loading users</td></tr>';
    }
  }

  function renderUsersTable(users) {
    usersTbody.innerHTML = '';
    users.forEach((u) => {
      const tr = document.createElement('tr');
      const joined = u.date_joined ? new Date(u.date_joined).toLocaleDateString() : '—';
      const roleInfo = ROLE_LABELS[u.role] || ROLE_LABELS.user;
      tr.innerHTML = `
        <td><strong>${esc(u.username)}</strong></td>
        <td>${esc(u.email || '—')}</td>
        <td><span class="badge ${roleInfo.cls}">${roleInfo.text}</span></td>
        <td>${u.is_active ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-red">Inactive</span>'}</td>
        <td>${joined}</td>
        <td>
          <div class="action-btns">
            <button class="btn btn-ghost btn-sm" data-edit="${u.id}">Edit</button>
            <button class="btn btn-danger btn-sm" data-delete="${u.id}" data-name="${esc(u.username)}">Delete</button>
          </div>
        </td>
      `;
      usersTbody.appendChild(tr);
    });

    // Bind edit buttons
    usersTbody.querySelectorAll('[data-edit]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const uid = btn.dataset.edit;
        const u = users.find((x) => x.id == uid);
        if (u) openEditModal(u);
      });
    });

    // Bind delete buttons
    usersTbody.querySelectorAll('[data-delete]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const uid = btn.dataset.delete;
        const name = btn.dataset.name;
        if (!confirm(`Delete user "${name}"? This cannot be undone.`)) return;
        try {
          await api(`/admin/api/users/${uid}/`, { method: 'DELETE' });
          loadUsers();
        } catch (e) {
          alert(e.error || 'Delete failed');
        }
      });
    });
  }

  // ─── Modal logic ───
  function openAddModal() {
    modalTitle.textContent = 'Add User';
    $('#modal-user-id').value = '';
    $('#modal-username').value = '';
    $('#modal-username').disabled = false;
    $('#modal-email').value = '';
    $('#modal-password').value = '';
    $('#modal-password').placeholder = 'Password (required)';
    $('#modal-role').value = 'data_moderator';
    $('#modal-is-active').checked = true;
    userModal.style.display = 'flex';
  }

  function openEditModal(user) {
    modalTitle.textContent = 'Edit User';
    $('#modal-user-id').value = user.id;
    $('#modal-username').value = user.username;
    $('#modal-username').disabled = true;
    $('#modal-email').value = user.email || '';
    $('#modal-password').value = '';
    $('#modal-password').placeholder = 'Leave blank to keep current';
    $('#modal-role').value = user.role || 'data_moderator';
    $('#modal-is-active').checked = user.is_active;
    userModal.style.display = 'flex';
  }

  function closeModal() {
    userModal.style.display = 'none';
  }

  if ($('#btn-add-user')) {
    $('#btn-add-user').addEventListener('click', openAddModal);
  }
  if ($('#btn-cancel-modal')) {
    $('#btn-cancel-modal').addEventListener('click', closeModal);
  }
  if (userModal) {
    userModal.addEventListener('click', (e) => {
      if (e.target === userModal) closeModal();
    });
  }

  if (userForm) {
    userForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const userId = $('#modal-user-id').value;
      const isEdit = !!userId;

      const payload = {
        username: $('#modal-username').value.trim(),
        email: $('#modal-email').value.trim(),
        role: $('#modal-role').value,
        is_active: $('#modal-is-active').checked,
      };

      const pwd = $('#modal-password').value;
      if (pwd) payload.password = pwd;

      if (!isEdit && !pwd) {
        alert('Password is required for new users.');
        return;
      }

      try {
        if (isEdit) {
          await api(`/admin/api/users/${userId}/`, { method: 'PUT', body: payload });
        } else {
          if (!payload.password) {
            alert('Password is required.');
            return;
          }
          await api('/admin/api/users/', { method: 'POST', body: payload });
        }
        closeModal();
        loadUsers();
      } catch (e) {
        alert(e.error || 'Save failed');
      }
    });
  }

  // ─── Helpers ───
  function esc(str) {
    const d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
  }
})();
