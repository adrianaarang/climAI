// app/static/js/vincular_telegram.js

document.addEventListener('DOMContentLoaded', () => {

  // ── Vincular por chat_id ──────────────────────────────────────────────
  const vincularBtn = document.getElementById('vincularBtn');
  const chatIdInput = document.getElementById('chatIdInput');
  const vincularMsg = document.getElementById('vincularMsg');

  if (vincularBtn) {
    vincularBtn.addEventListener('click', async () => {
      const chatId = chatIdInput.value.trim();

      if (!chatId || isNaN(chatId)) {
        mostrarMsg('Introduce un ID válido (solo números).', 'error');
        return;
      }

      vincularBtn.textContent = 'Vinculando...';
      vincularBtn.disabled = true;

      try {
        const resp = await fetch('/api/telegram/vincular-manual', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chat_id: chatId }),
        });
        const data = await resp.json();

        if (data.status === 'ok') {
          mostrarMsg('✅ ¡Vinculado! Recibirás un mensaje de confirmación en Telegram.', 'ok');
          setTimeout(() => window.location.reload(), 2000);
        } else {
          mostrarMsg('❌ ' + (data.message || 'Error al vincular.'), 'error');
          vincularBtn.textContent = 'Vincular';
          vincularBtn.disabled = false;
        }
      } catch {
        mostrarMsg('❌ Error de conexión.', 'error');
        vincularBtn.textContent = 'Vincular';
        vincularBtn.disabled = false;
      }
    });

    // Vincular con Enter
    chatIdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') vincularBtn.click();
    });
  }

  // ── Desvincular ───────────────────────────────────────────────────────
  const desvincularBtn = document.getElementById('desvincularBtn');
  if (desvincularBtn) {
    desvincularBtn.addEventListener('click', async () => {
      if (!confirm('¿Seguro que quieres desvincular tu Telegram?')) return;

      try {
        const resp = await fetch('/api/telegram/desvincular', { method: 'POST' });
        const data = await resp.json();
        if (data.status === 'ok') {
          window.location.reload();
        }
      } catch {
        alert('Error al desvincular.');
      }
    });
  }

  // ── Verificar estado ──────────────────────────────────────────────────
  const checkBtn = document.getElementById('checkStatusBtn');
  if (checkBtn) {
    checkBtn.addEventListener('click', async () => {
      checkBtn.textContent = 'Verificando...';
      try {
        const resp = await fetch('/api/telegram/estado');
        const data = await resp.json();
        const badge = document.getElementById('statusIndicator');
        if (data.vinculado) {
          badge.className = 'status-badge linked';
          badge.textContent = '✅ Vinculado';
        } else {
          badge.className = 'status-badge pending';
          badge.textContent = '⏳ Pendiente de vinculación';
        }
      } catch {
        alert('Error al verificar.');
      } finally {
        checkBtn.textContent = 'Verificar Conexión';
      }
    });
  }

  // ── Helper ────────────────────────────────────────────────────────────
  function mostrarMsg(texto, tipo) {
    if (!vincularMsg) return;
    vincularMsg.textContent = texto;
    vincularMsg.className = `vincular-msg ${tipo}`;
    vincularMsg.classList.remove('hidden');
  }
});