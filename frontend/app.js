const API_BASE = (window.TELECORP_CONFIG?.apiUrl || '').replace(/\/$/, '');
const views = document.querySelectorAll('.view');
const navigationButtons = document.querySelectorAll('[data-view]');
const sidebar = document.querySelector('.sidebar');
const pageName = document.querySelector('#page-name');
const toast = document.querySelector('#toast');

const labels = {
  inicio: 'Inicio', reportar: 'Reportar problema',
  incidencias: 'Mis incidencias', soporte: 'Asistente IA'
};

function showToast(title, message, error = false) {
  document.querySelector('#toast-title').textContent = title;
  document.querySelector('#toast-message').textContent = message;
  toast.querySelector(':scope > span').textContent = error ? '!' : '✓';
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 3000);
}

async function api(path, options = {}) {
  if (!API_BASE) throw new Error('La URL de API no está configurada');
  const response = await fetch(`${API_BASE}${path}`, {
    ...options, headers: { 'content-type': 'application/json', ...(options.headers || {}) }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Error HTTP ${response.status}`);
  return data;
}

function changeView(viewId) {
  views.forEach((view) => view.classList.toggle('active', view.id === viewId));
  document.querySelectorAll('.nav-item').forEach((item) => item.classList.toggle('active', item.dataset.view === viewId));
  pageName.textContent = labels[viewId] || 'Inicio';
  sidebar.classList.remove('open');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (viewId === 'incidencias') loadUserData();
}

navigationButtons.forEach((button) => button.addEventListener('click', () => changeView(button.dataset.view)));
document.querySelector('.menu-button').addEventListener('click', () => sidebar.classList.toggle('open'));
document.querySelectorAll('.filter').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.filter').forEach((filter) => filter.classList.remove('active'));
  button.classList.add('active');
}));

const occurredAt = document.querySelector('#occurred-at');
occurredAt.value = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);

document.querySelector('#location-button').addEventListener('click', () => {
  if (!navigator.geolocation) return showToast('Ubicación no disponible', 'Usaremos la ubicación de demostración.', true);
  navigator.geolocation.getCurrentPosition(({ coords }) => {
    const button = document.querySelector('#location-button');
    button.dataset.lat = String(coords.latitude);
    button.dataset.lon = String(coords.longitude);
    document.querySelector('#location-label').textContent = `${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}`;
    showToast('Ubicación actualizada', 'La incluiremos en tu reporte.');
  }, () => showToast('Permiso no concedido', 'Usaremos la ubicación de demostración.', true));
});

document.querySelector('#report-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = document.querySelector('#location-button');
  const documentId = document.querySelector('#document-id').value.trim();
  const payload = {
    documentId,
    serviceNumber: document.querySelector('#service-number').value.trim(),
    lat: Number(button.dataset.lat), lon: Number(button.dataset.lon),
    occurredAt: new Date(document.querySelector('#occurred-at').value).toISOString(),
    problemType: document.querySelector('input[name="problem"]:checked').value,
    description: document.querySelector('#report-description').value.trim(),
    email: document.querySelector('#contact-email').value.trim(),
    phone: document.querySelector('#contact-phone').value.replace(/\s/g, '')
  };
  localStorage.setItem('telecorp-document', documentId);
  try {
    const result = await api('/reports', { method: 'POST', body: JSON.stringify(payload) });
    showToast('Reporte registrado', `Tu código es ${result.reportId}`);
    window.setTimeout(() => changeView('incidencias'), 1000);
  } catch (error) { showToast('No pudimos registrar', error.message, true); }
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[char]);
}

const statusLabel = (status) => ({
  REGISTRADA: 'REGISTRADA', EN_REVISION: 'EN REVISIÓN', EN_ATENCION: 'EN ATENCIÓN',
  ATENDIDA: 'EN ATENCIÓN', SOLUCIONADA: 'SOLUCIONADA', CERRADA: 'CERRADA'
})[status] || status;

function renderIncidents(items) {
  const list = document.querySelector('#incident-list');
  if (!items.length) {
    list.innerHTML = '<article class="incident-detail"><p class="empty-state">No encontramos incidencias para este documento.</p></article>';
    return;
  }
  list.innerHTML = items.map((item) => {
    const solved = ['SOLUCIONADA', 'CERRADA'].includes(item.status);
    return `<article class="incident-detail compact"><div class="incident-top">
      <span class="incident-symbol ${solved ? 'green' : 'amber'}">${solved ? '✓' : '⌁'}</span>
      <div><span class="incident-code">${escapeHtml(item.incidentId)}</span>
      <h2>${escapeHtml(item.problemType?.replaceAll('_', ' ') || 'Incidencia')}</h2>
      <p>${escapeHtml(item.description || `Zona ${item.zone || 'en evaluación'}`)}</p></div>
      <span class="status-badge ${solved ? 'solved' : 'progress'}">${escapeHtml(statusLabel(item.status))}</span></div>
      <div class="resolved-note"><span>${solved ? '✓' : '●'}</span><p><strong>Actualizada ${new Date(item.updatedAt || item.createdAt).toLocaleString('es-PE')}</strong>${escapeHtml(item.aiSummary || 'Seguimiento disponible en tiempo real.')}</p></div></article>`;
  }).join('');
}

function renderNotifications(items) {
  const list = document.querySelector('#notification-list');
  if (!items.length) return list.innerHTML = '<p class="empty-state">Aún no hay notificaciones.</p>';
  list.innerHTML = items.map((item) => `<div class="notification-item"><span>✓</span><p>${escapeHtml(item.message)}<small>${escapeHtml(statusLabel(item.status))} · ${new Date(item.createdAt.split('#')[0]).toLocaleString('es-PE')} · ${escapeHtml((item.channels || []).join(', '))}</small></p></div>`).join('');
}

async function loadUserData() {
  const documentId = localStorage.getItem('telecorp-document') || document.querySelector('#document-id').value || '70000001';
  try {
    const [incidents, notifications] = await Promise.all([
      api(`/users/${encodeURIComponent(documentId)}/incidents`),
      api(`/notifications/${encodeURIComponent(documentId)}`)
    ]);
    renderIncidents(incidents.items || []);
    renderNotifications(notifications.items || []);
  } catch (error) { showToast('Datos no disponibles', error.message, true); }
}

document.querySelector('#refresh-data').addEventListener('click', loadUserData);

async function loadDashboard() {
  try {
    const [antennas, analytics] = await Promise.all([api('/antennas'), api('/analytics/summary')]);
    const antennaItems = antennas.items || [];
    const healthy = antennaItems.filter((item) => ['NORMAL', 'SATURADA'].includes(item.state)).length;
    const availability = antennaItems.length ? `${((healthy / antennaItems.length) * 100).toFixed(1)}%` : '—';
    document.querySelector('#antenna-count').textContent = antennaItems.length;
    document.querySelector('#network-availability').childNodes[0].textContent = `${availability} `;
    document.querySelector('#network-quality').textContent = healthy === antennaItems.length ? 'Excelente' : 'Con alertas';
    document.querySelector('#network-update').textContent = 'Última medición: en vivo';
    document.querySelector('#metric-reports').textContent = analytics.totals?.reports ?? 0;
    document.querySelector('#metric-users').textContent = analytics.totals?.affectedUsers ?? 0;
    document.querySelector('#metric-collective').textContent = analytics.totals?.collectiveIncidents ?? 0;
    const recurrent = analytics.recurrentAntennas?.[0];
    document.querySelector('#metric-antenna').textContent = recurrent?.antennaId || '—';
    document.querySelector('#metric-antenna-detail').textContent = recurrent ? `${recurrent.failCount} fallas · ${recurrent.state}` : 'Sin fallas registradas';
  } catch (error) {
    document.querySelector('#network-quality').textContent = 'Sin conexión';
    document.querySelector('#network-update').textContent = error.message;
  }
}

const chatForm = document.querySelector('#chat-form');
const chatMessage = document.querySelector('#chat-message');
const messages = document.querySelector('#messages');
let chatSessionId = sessionStorage.getItem('telecorp-chat-session');

function addMessage(text, type) {
  const wrapper = document.createElement('div'); wrapper.className = `message ${type}`;
  const content = document.createElement('div');
  const paragraph = document.createElement('p'); paragraph.textContent = text;
  const time = document.createElement('time'); time.textContent = 'Ahora';
  content.append(paragraph, time);
  if (type === 'assistant') {
    const orb = document.createElement('span'); orb.className = 'ai-orb tiny'; orb.textContent = '✦'; wrapper.append(orb);
  }
  wrapper.append(content); messages.appendChild(wrapper); messages.scrollTop = messages.scrollHeight;
}

async function sendChat(text) {
  addMessage(text, 'user');
  try {
    const location = document.querySelector('#location-button');
    const result = await api('/chat', { method: 'POST', body: JSON.stringify({
      message: text, sessionId: chatSessionId || undefined,
      location: { lat: Number(location.dataset.lat), lon: Number(location.dataset.lon) }
    }) });
    chatSessionId = result.sessionId;
    sessionStorage.setItem('telecorp-chat-session', chatSessionId);
    addMessage(result.reply, 'assistant');
  } catch (error) { addMessage(`No pude consultar el asistente: ${error.message}`, 'assistant'); }
}

chatForm.addEventListener('submit', (event) => {
  event.preventDefault(); const text = chatMessage.value.trim(); if (!text) return;
  chatMessage.value = ''; sendChat(text);
});
document.querySelectorAll('.chat-suggestion').forEach((button) => button.addEventListener('click', () => {
  changeView('soporte'); sendChat(button.textContent);
}));

loadDashboard();
