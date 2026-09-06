(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const all = (s, root = document) => [...root.querySelectorAll(s)];
  const read = key => { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } };
  const write = (key, value) => { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } };
  const prefsKey = 'indigenous:reader:size';
  const sizes = [1.5, 1.75, 2, 2.5, 3];
  let size = sizes.includes(read(prefsKey)) ? read(prefsKey) : sizes[0];
  function setSize(value) {
    size = value;
    document.documentElement.style.setProperty('--reading-size', `${size}rem`);
    if ($('#smaller-text')) $('#smaller-text').disabled = size === sizes[0];
    if ($('#larger-text')) $('#larger-text').disabled = size === sizes.at(-1);
    if ($('#text-size-status')) $('#text-size-status').textContent = `Text size ${Math.round(size / sizes[0] * 100)}%`;
  }
  setSize(size);
  $('#smaller-text')?.addEventListener('click', () => { setSize(sizes[Math.max(0, sizes.indexOf(size) - 1)]); write(prefsKey, size); });
  $('#larger-text')?.addEventListener('click', () => { setSize(sizes[Math.min(sizes.length - 1, sizes.indexOf(size) + 1)]); write(prefsKey, size); });
  const guide = document.body.dataset.guide;
  if (!guide) {
    all('[data-guide-link]').forEach(a => {
      const saved = read(`indigenous:${a.dataset.guideLink}:progress`);
      if (saved && Number.isInteger(saved.section) && saved.section >= 0 && saved.section < Number(a.dataset.sections)) {
        const status = $('.guide-state', a);
        status.textContent = saved.completed ? 'Completed on this device · Read again' : `Continue at section ${saved.section + 1} of ${a.dataset.sections}`;
        if (saved.completed) a.href = `/${a.dataset.guideLink}#section-1`;
      }
    });
    const last = read('indigenous:last-guide');
    const a = all('[data-guide-link]').find(a => a.dataset.guideLink === last?.guide);
    if (a && $('#resume-card')) {
      $('#resume-title').textContent = $('.guide-name', a).firstChild.textContent;
      $('#resume-link').href = a.getAttribute('href');
      $('#resume-card').hidden = false;
    }
    return;
  }
  const sections = all('.guide-section');
  if (!sections.length) return;
  const progressKey = `indigenous:${guide}:progress`;
  const notesKey = `indigenous:${guide}:notes`;
  const saved = read(progressKey);
  let current = 0;
  let completed = saved?.completed === true;
  let speechToken = 0;
  let speaking = false;
  const speechAvailable = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  const status = $('#save-status');
  function saveProgress() {
    const ok = write(progressKey, { section: current, completed });
    if (ok) write('indigenous:last-guide', { guide });
    status.textContent = ok ? 'Place saved on this device' : 'Your browser cannot save your place';
    return ok;
  }
  function stopListening() {
    speechToken++;
    if (speechAvailable) speechSynthesis.cancel();
    speaking = false;
    if ($('#listen')) { $('#listen').textContent = 'Listen'; $('#listen').setAttribute('aria-pressed', 'false'); }
  }
  function showSection(index, { focus = false, updateHash = true } = {}) {
    if (!Number.isInteger(index) || index < 0 || index >= sections.length) return;
    stopListening();
    current = index;
    sections.forEach((section, i) => { section.hidden = i !== current; });
    $('#section-label').textContent = `Section ${current + 1} of ${sections.length}`;
    $('#reading-progress').value = current + 1;
    $('#previous-section').disabled = current === 0;
    $('#continue-section').textContent = current === sections.length - 1 ? 'Finish guide' : 'Continue';
    $('#completion').hidden = !(completed && current === sections.length - 1);
    all('[data-section-link]').forEach(a => { if (Number(a.dataset.sectionLink) === current) a.setAttribute('aria-current', 'step'); else a.removeAttribute('aria-current'); });
    if (updateHash) history.replaceState(null, '', `#section-${current + 1}`);
    saveProgress();
    if (focus) {
      const heading = $('h2', sections[current]);
      heading.focus({ preventScroll: true });
      heading.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
  }
  function hashSection() {
    const match = /^#section-(\d+)$/.exec(location.hash);
    const i = match ? Number(match[1]) - 1 : -1;
    return i >= 0 && i < sections.length ? i : null;
  }
  document.body.classList.add('enhanced');
  all('.js-only').forEach(el => { el.hidden = false; });
  const start = hashSection() ?? (Number.isInteger(saved?.section) && saved.section >= 0 && saved.section < sections.length ? saved.section : 0);
  showSection(start);
  $('#fallback-contents').hidden = true;
  $('#previous-section').addEventListener('click', () => showSection(current - 1, { focus: true }));
  $('#continue-section').addEventListener('click', () => {
    if (current < sections.length - 1) showSection(current + 1, { focus: true });
    else {
      completed = true; saveProgress(); $('#completion').hidden = false;
      $('#completion').focus();
    }
  });
  window.addEventListener('hashchange', () => { const index = hashSection(); if (index !== null) showSection(index, { focus: true, updateHash: false }); });
  let dialogTrigger = null;
  all('[data-dialog]').forEach(button => button.addEventListener('click', () => {
    const dialog = document.getElementById(button.dataset.dialog);
    if (!dialog || typeof dialog.showModal !== 'function') return;
    stopListening();
    all('dialog[open]').forEach(d => d.close());
    dialogTrigger = button;
    dialog.showModal();
    $('[data-close-dialog]', dialog)?.focus();
  }));
  all('dialog').forEach(dialog => {
    $('[data-close-dialog]', dialog)?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => dialogTrigger?.focus({ preventScroll: true }));
  });
  if (typeof HTMLDialogElement === 'undefined' || typeof HTMLDialogElement.prototype.showModal !== 'function') {
    all('[data-dialog]').forEach(button => { button.hidden = true; });
    $('#fallback-contents').hidden = false;
  }
  all('[data-section-link]').forEach(a => a.addEventListener('click', event => {
    event.preventDefault();
    const dialog = a.closest('dialog');
    if (dialog?.open) { dialogTrigger = null; dialog.close(); }
    showSection(Number(a.dataset.sectionLink), { focus: true });
  }));
  all('.close-explanation').forEach(button => button.addEventListener('click', () => {
    const details = button.closest('details'); details.open = false; $('summary', details).focus();
  }));
  const notes = $('#guide-notes');
  const storedNotes = read(notesKey);
  if (typeof storedNotes === 'string') notes.value = storedNotes;
  const notesStatus = $('#notes-status');
  function saveNotes() {
    const ok = write(notesKey, notes.value);
    notesStatus.textContent = ok ? 'Notes saved on this device.' : 'Notes could not be saved. Copy them somewhere safe before leaving.';
    return ok;
  }
  if (typeof storedNotes === 'string' && storedNotes) notesStatus.textContent = 'Notes restored from this device.';
  notes.addEventListener('input', saveNotes);
  all('.bible-link').forEach(link => link.addEventListener('click', () => { saveProgress(); if (notes.value) saveNotes(); }));
  window.addEventListener('pagehide', () => { stopListening(); saveProgress(); if (notes.value) saveNotes(); });
  $('#print-guide').addEventListener('click', () => { stopListening(); window.print(); });
  window.addEventListener('beforeprint', () => {
    $('#printed-notes').textContent = notes.value ? `My notes\n\n${notes.value}` : '';
  });
  if (speechAvailable) {
    $('#listen').hidden = false;
    $('#listen').addEventListener('click', () => {
      if (speaking) { stopListening(); return; }
      speaking = true;
      $('#listen').textContent = 'Stop listening'; $('#listen').setAttribute('aria-pressed', 'true');
      const token = ++speechToken;
      const copy = sections[current].cloneNode(true);
      all('details,.external,button', copy).forEach(el => el.remove());
      const chunks = (copy.textContent || '').replace(/\s+/g, ' ').match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [];
      let i = 0;
      function next() {
        if (token !== speechToken) return;
        if (i >= chunks.length) { stopListening(); return; }
        const utterance = new SpeechSynthesisUtterance(chunks[i++]);
        utterance.lang = 'en-US'; utterance.rate = .9;
        utterance.onend = next;
        utterance.onerror = event => {
          if (token !== speechToken || event.error === 'canceled' || event.error === 'interrupted') return;
          stopListening(); $('#audio-status').textContent = 'Read aloud is unavailable right now. You can continue reading below.';
        };
        speechSynthesis.speak(utterance);
      }
      $('#audio-status').textContent = 'Read aloud uses your device’s voice.';
      next();
    });
  }
})();
