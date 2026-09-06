(() => {
  'use strict';
  document.getElementById('year').textContent = String(new Date().getFullYear());

  // The original form controls, validation, consent and success flow are owned by Omnisend.
  const form = document.getElementById('omnisend-embedded-v2-67cb633ee44f1e1e39dd4822');
  const loading = document.getElementById('form-loading');
  const unavailable = document.getElementById('form-unavailable');
  let timeout;
  const ready = () => Boolean(form.querySelector('form, iframe, input, button'));
  const sync = () => {
    if (!ready()) return;
    loading.hidden = true;
    unavailable.hidden = true;
    clearTimeout(timeout);
    observer.disconnect();
  };
  const observer = new MutationObserver(sync);
  observer.observe(form, {childList: true, subtree: true});
  timeout = setTimeout(() => {
    if (!ready()) {
      loading.hidden = true;
      unavailable.hidden = false;
    }
  }, 15000);

  document.getElementById('retry-form').addEventListener('click', () => {
    window.location.hash = 'get-guides';
    window.location.reload();
  });

  window.omnisend = window.omnisend || [];
  window.omnisend.push(['brandID', '67cb56fd73be448eba677afd']);
  window.omnisend.push(['track', '$pageViewed']);
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.async = true;
  script.src = 'https://omnisnippet1.com/inshop/launcher-v2.js';
  script.addEventListener('error', () => {
    if (ready()) return;
    clearTimeout(timeout);
    loading.hidden = true;
    unavailable.hidden = false;
  });
  document.head.appendChild(script);
  sync();
})();
