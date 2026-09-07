(() => {
  'use strict';
  const year = document.getElementById('welcome-year');
  if (year) year.textContent = String(new Date().getFullYear());

  const dialog = document.getElementById('first-guides-dialog');
  const opener = document.getElementById('open-first-guides');
  const closer = document.getElementById('close-first-guides');
  const list = document.getElementById('first-five-list');
  const slot = document.getElementById('first-guides-slot');
  const fallback = document.getElementById('first-guides-fallback');
  if (!dialog || !opener || !closer || !list || !slot || !fallback || typeof dialog.showModal !== 'function') return;

  slot.appendChild(list);
  fallback.hidden = true;
  opener.hidden = false;

  opener.addEventListener('click', () => {
    if (dialog.open) return;
    dialog.showModal();
    document.body.classList.add('welcome-dialog-open');
    closer.focus({ preventScroll: true });
  });
  closer.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('welcome-dialog-open');
    opener.focus({ preventScroll: true });
  });
})();
