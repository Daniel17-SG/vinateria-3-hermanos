// accesibilidad.js - Sistema profesional de accesibilidad web
(function () {
  // Utilidades
  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return document.querySelectorAll(sel); }
  function save(key, val) { localStorage.setItem(key, JSON.stringify(val)); }
  function load(key, def) { try { return JSON.parse(localStorage.getItem(key)) ?? def; } catch { return def; } }

  // Estado
  const state = load('accessibility-state', {
    dark: false, grayscale: false, contrast: false, invert: false, easyread: false, dyslexia: false,
    highlightLinks: false, highlightTitles: false, largeText: false, xlargeText: false, smallText: false,
    letterspace: false, linespace: false, bigButtons: false, bigTouch: false, pauseAnimations: false
  });

  // Aplicar estado
  function applyState() {
    document.body.classList.toggle('access-dark', state.dark);
    document.body.classList.toggle('access-grayscale', state.grayscale);
    document.body.classList.toggle('access-contrast', state.contrast);
    document.body.classList.toggle('access-invert', state.invert);
    document.body.classList.toggle('access-easyread', state.easyread);
    document.body.classList.toggle('access-dyslexia', state.dyslexia);
    document.body.classList.toggle('access-highlight-links', state.highlightLinks);
    document.body.classList.toggle('access-highlight-titles', state.highlightTitles);
    document.body.classList.toggle('access-large-text', state.largeText);
    document.body.classList.toggle('access-xlarge-text', state.xlargeText);
    document.body.classList.toggle('access-small-text', state.smallText);
    document.body.classList.toggle('access-letterspace', state.letterspace);
    document.body.classList.toggle('access-linespace', state.linespace);
    document.body.classList.toggle('access-big-buttons', state.bigButtons);
    document.body.classList.toggle('access-big-touch', state.bigTouch);
    document.body.classList.toggle('access-pause-animations', state.pauseAnimations);
  }

  // Crear botón flotante
  const btn = document.createElement('button');
  btn.id = 'accessibility-btn';
  btn.title = 'Opciones de accesibilidad';
  btn.setAttribute('aria-label', 'Opciones de accesibilidad');
  btn.innerHTML = '<span aria-hidden="true">♿</span>';
  btn.tabIndex = 0;
  // Asegura que el botón esté al final del body para que el CSS controle la posición
  document.body.appendChild(btn);

  // Crear panel lateral
  const panel = document.createElement('aside');
  panel.id = 'accessibility-panel';
  panel.setAttribute('aria-label', 'Panel de accesibilidad');
  panel.innerHTML = `
    <header>
      <h2>Accesibilidad</h2>
      <button class="close" aria-label="Cerrar">&times;</button>
    </header>
    <div class="section">
      <div class="subtitle">Modos visuales</div>
      <label><input type="checkbox" id="acc-dark"> <span class="icon">🌙</span>Modo oscuro</label>
      <label><input type="checkbox" id="acc-grayscale"> <span class="icon">⬛</span>Escala de grises</label>
      <label><input type="checkbox" id="acc-contrast"> <span class="icon">🔳</span>Alto contraste</label>
      <label><input type="checkbox" id="acc-invert"> <span class="icon">🎨</span>Contraste invertido</label>
      <label><input type="checkbox" id="acc-easyread"> <span class="icon">📖</span>Modo lectura fácil</label>
      <label><input type="checkbox" id="acc-dyslexia"> <span class="icon">🔤</span>Tipografía dislexia</label>
    </div>
    <div class="section">
      <div class="subtitle">Tamaño y espaciado</div>
      <label><input type="checkbox" id="acc-large-text"> <span class="icon">A+</span>Texto grande</label>
      <label><input type="checkbox" id="acc-xlarge-text"> <span class="icon">A++</span>Texto extra grande</label>
      <label><input type="checkbox" id="acc-small-text"> <span class="icon">A-</span>Texto pequeño</label>
      <label><input type="checkbox" id="acc-letterspace"> <span class="icon">↔</span>Espaciado entre letras</label>
      <label><input type="checkbox" id="acc-linespace"> <span class="icon">↕</span>Espaciado entre líneas</label>
    </div>
    <div class="section">
      <div class="subtitle">Resaltado</div>
      <label><input type="checkbox" id="acc-highlight-links"> <span class="icon">🔗</span>Resaltar enlaces</label>
      <label><input type="checkbox" id="acc-highlight-titles"> <span class="icon">🔠</span>Resaltar títulos</label>
    </div>
    <div class="section">
      <div class="subtitle">Motriz y cognitiva</div>
      <label><input type="checkbox" id="acc-big-buttons"> <span class="icon">🖱️</span>Botones grandes</label>
      <label><input type="checkbox" id="acc-big-touch"> <span class="icon">📱</span>Área táctil grande</label>
      <label><input type="checkbox" id="acc-pause-animations"> <span class="icon">⏸️</span>Pausar animaciones</label>
    </div>
    <div class="section">
      <button id="acc-reset" style="width:100%;margin-top:1em;">Restablecer ajustes</button>
    </div>
  `;
  document.body.appendChild(panel);

  // Abrir/cerrar panel
  btn.onclick = () => { panel.classList.add('open'); panel.querySelector('.close').focus(); };
  panel.querySelector('.close').onclick = () => panel.classList.remove('open');
  btn.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { btn.click(); } };

  // Cerrar con ESC
  panel.addEventListener('keydown', e => {
    if (e.key === 'Escape') panel.classList.remove('open');
  });

  // Opciones y bindings
  const options = [
    ['dark', '#acc-dark'],
    ['grayscale', '#acc-grayscale'],
    ['contrast', '#acc-contrast'],
    ['invert', '#acc-invert'],
    ['easyread', '#acc-easyread'],
    ['dyslexia', '#acc-dyslexia'],
    ['largeText', '#acc-large-text'],
    ['xlargeText', '#acc-xlarge-text'],
    ['smallText', '#acc-small-text'],
    ['letterspace', '#acc-letterspace'],
    ['linespace', '#acc-linespace'],
    ['highlightLinks', '#acc-highlight-links'],
    ['highlightTitles', '#acc-highlight-titles'],
    ['bigButtons', '#acc-big-buttons'],
    ['bigTouch', '#acc-big-touch'],
    ['pauseAnimations', '#acc-pause-animations']
  ];
  options.forEach(([key, sel]) => {
    const el = panel.querySelector(sel);
    el.checked = !!state[key];
    el.onchange = e => {
      state[key] = el.checked;
      save('accessibility-state', state);
      applyState();
    };
  });

  // Reset
  panel.querySelector('#acc-reset').onclick = () => {
    Object.keys(state).forEach(k => state[k] = false);
    save('accessibility-state', state);
    applyState();
    options.forEach(([key, sel]) => { panel.querySelector(sel).checked = false; });
  };

  // Saltar al contenido principal
  const skip = document.createElement('a');
  skip.href = '#main-content';
  skip.textContent = 'Saltar al contenido principal';
  skip.className = 'visually-hidden-focusable';
  skip.tabIndex = 0;
  skip.style.position = 'absolute';
  skip.style.left = '0';
  skip.style.top = '0';
  skip.style.background = '#ffd600';
  skip.style.color = '#222';
  skip.style.padding = '0.5em 1em';
  skip.style.zIndex = '10002';
  skip.style.transform = 'translateY(-120%)';
  skip.style.transition = 'transform 0.2s';
  skip.onfocus = () => { skip.style.transform = 'translateY(0)'; };
  skip.onblur = () => { skip.style.transform = 'translateY(-120%)'; };
  document.body.prepend(skip);

  // Navegación por teclado: foco visible ya está en CSS

  // Lectura en voz alta (lector simple)
  window.readContent = function () {
    if ('speechSynthesis' in window) {
      const txt = document.getElementById('main-content')?.innerText || document.body.innerText;
      const utter = new SpeechSynthesisUtterance(txt);
      window.speechSynthesis.speak(utter);
    } else {
      alert('Tu navegador no soporta lectura en voz alta.');
    }
  };

  // Agregar botón de lectura en voz alta
  const readBtn = document.createElement('button');
  readBtn.innerHTML = '🔊 Leer página';
  readBtn.id = 'accessibility-read-btn';
  readBtn.style.background = '#fff';
  readBtn.style.color = '#222';
  readBtn.style.border = '2px solid #1976d2';
  readBtn.style.borderRadius = '8px';
  readBtn.style.padding = '0.5em 1.2em';
  readBtn.style.fontSize = '1.1em';
  readBtn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
  readBtn.onclick = window.readContent;
  readBtn.tabIndex = 0;
  readBtn.setAttribute('aria-label', 'Leer página en voz alta');
  document.body.appendChild(readBtn);

  // Aplicar estado al cargar
  applyState();

  // Mejoras de accesibilidad: ALT en imágenes
  $all('img').forEach(img => {
    if (!img.alt || img.alt.trim() === '') img.alt = 'Imagen decorativa';
  });

  // Etiquetas accesibles en formularios
  $all('form input, form select, form textarea').forEach(el => {
    if (el.id && !document.querySelector(`label[for="${el.id}"]`)) {
      el.setAttribute('aria-label', el.placeholder || el.name || 'Campo de formulario');
    }
  });

  // Subtítulos/transcripciones en videos (aviso)
  $all('video').forEach(video => {
    if (!video.querySelector('track[kind="subtitles"]')) {
      const msg = document.createElement('div');
      msg.textContent = 'Este video no tiene subtítulos.';
      msg.style.background = '#ffd600';
      msg.style.color = '#222';
      msg.style.padding = '0.3em 0.7em';
      msg.style.fontSize = '0.95em';
      msg.style.margin = '0.5em 0';
      video.parentNode.insertBefore(msg, video.nextSibling);
    }
  });

  // Alertas visuales además de sonido
  window.addEventListener('error', function(e) {
    const alertDiv = document.createElement('div');
    alertDiv.textContent = '⚠️ ' + (e.message || 'Error en la página');
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '16px';
    alertDiv.style.right = '16px';
    alertDiv.style.background = '#ffd600';
    alertDiv.style.color = '#222';
    alertDiv.style.padding = '0.7em 1.2em';
    alertDiv.style.zIndex = '10010';
    alertDiv.style.borderRadius = '8px';
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 6000);
  });

})();
