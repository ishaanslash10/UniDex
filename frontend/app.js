/* ============================================================
   UNIDEX AI — FINAL APP.JS
   ============================================================ */

/* ── 1. DOM REFS ────────────────────────────────────────────── */

const chat        = document.getElementById('chat');

const input       = document.getElementById('input');

const inputBox    = document.getElementById('inputBox');

const logoBox     = document.getElementById('logoBox');

const loginScreen = document.getElementById('loginScreen');

const mainApp     = document.getElementById('mainApp');

/* AI LOADER */

const aiLoader    = document.getElementById('aiLoader');

const loaderText  = document.getElementById('loaderText');

/* ── 2. STATE ───────────────────────────────────────────────── */

let started = false;

let loaderInterval;

/* ── 3. AI LOADING MESSAGES ───────────────────────────────── */

const loadingMessages = {

  timetable: [

    "Checking today's classes...",
    "Searching lecture schedule...",
    "Understanding timetable query...",
    "Matching academic records...",
    "Hoping your next lecture is interesting..."

  ],

  syllabus: [

    "Opening syllabus vault...",
    "Reading subject modules...",
    "Organizing academic chaos...",
    "Decoding university language...",
    "Fetching unit details..."

  ],

  general: [

    "Thinking deeply...",
    "Connecting ideas...",
    "Consulting the AI cosmos...",
    "Generating intelligent response...",
    "Synchronizing UniDex AI..."

  ]
};

/* ── 4. INTENT DETECTION ──────────────────────────────────── */

function detectIntent(query) {

  query = query.toLowerCase();

  if (

    query.includes('class') ||

    query.includes('lecture') ||

    query.includes('schedule') ||

    query.includes('timetable')

  ) {

    return 'timetable';
  }

  if (

    query.includes('syllabus') ||

    query.includes('unit') ||

    query.includes('subject')

  ) {

    return 'syllabus';
  }

  return 'general';
}

/* ── 5. START LOADER ───────────────────────────────────────── */

function startDynamicLoader(intent = 'general') {

  const messages =
    [...loadingMessages[intent]];

  const rareMessages = [

    "Refueling with virtual coffee...",
    "Convincing database to cooperate...",
    "Avoiding existential crisis...",
    "Rearranging academic particles..."

  ];

  if (Math.random() < 0.25) {

    const randomMessage =

      rareMessages[
        Math.floor(
          Math.random() *
          rareMessages.length
        )
      ];

    messages.push(randomMessage);
  }

  const loader = document.createElement('div');

  loader.className = 'ai-loader';

  loader.id = 'aiLoader';

  loader.innerHTML = `

    <div class="loader-spinner"></div>

    <div
      class="loader-text"
      id="loaderText"
    >
      ${messages[0]}
    </div>
  `;

  setTimeout(() => {

    chat.appendChild(loader);

    chat.scrollTo({

      top: chat.scrollHeight,

      behavior: 'smooth'
    });

  }, 50);

  const loaderText =
    loader.querySelector('.loader-text');

  let index = 0;

  loaderInterval = setInterval(() => {

    index =
      (index + 1) %
      messages.length;

    loaderText.style.opacity = '0';

    setTimeout(() => {

      loaderText.textContent =
        messages[index];

      loaderText.style.opacity = '1';

    }, 300);

  }, 1800);

  chat.scrollTo({

    top: chat.scrollHeight,

    behavior: 'smooth'
  });
}

/* ── 6. STOP LOADER ────────────────────────────────────────── */

function stopDynamicLoader() {

  clearInterval(loaderInterval);

  const loader =
    document.getElementById('aiLoader');

  if (loader) {

    loader.remove();
  }
}

/* ── 7. HISTORY STORAGE ────────────────────────────────────── */

function getHistoryKey() {

  const regNo =
    sessionStorage.getItem('reg_no');

  return `recentSearches_${regNo}`;
}

function getRecentSearches() {

  return JSON.parse(

    localStorage.getItem(
      getHistoryKey()
    )

  ) || [];
}

/* ── 8. STUDENT PROFILE ────────────────────────────────────── */

async function loadStudentProfile() {

  const regNo =
    sessionStorage.getItem(
      'reg_no'
    );

  const section =
    sessionStorage.getItem(
      'section'
    );

  if (!regNo || !section) return;

  try {

    const res = await fetch(

      `http://127.0.0.1:8000/student/${regNo}/${section}`,

      {
        method:'POST'
      }
    );

    const data =
      await res.json();

    /* SAVE */

    sessionStorage.setItem(
      'student_name',
      data.name
    );

    /* DOM */

    const userName =
      document.getElementById(
        'userName'
      );

    const userAvatar =
      document.getElementById(
        'userAvatar'
      );

    const userMeta =
      document.getElementById(
        'userMeta'
      );

    if (userName) {

      userName.innerText =
        data.name;
    }

    if (userAvatar) {

      userAvatar.innerText =
        data.name
          .charAt(0)
          .toUpperCase();
    }

    if (userMeta) {

      userMeta.innerText =
        `B.Tech CSE • Sem ${data.semester}`;
    }

  } catch (err) {

    console.error(
      'Profile load failed:',
      err
    );
  }
}

/* ── 9. LOGIN ─────────────────────────────────────────────── */

function login() {

  const regNo =
    document
      .getElementById('regNo')
      .value
      .trim();

  const section =
    document
      .getElementById('section')
      .value
      .trim();

  if (!regNo || !section) {

    alert('Please fill all fields');

    return;
  }

  /* SAVE SESSION */

  sessionStorage.setItem(
    'reg_no',
    regNo
  );

  sessionStorage.setItem(
    'section',
    section
  );

  /* LOGIN TRANSITION */

  loginScreen.classList.add(
    'fade-out'
  );

  setTimeout(() => {

    loginScreen.style.display =
      'none';

    mainApp.style.display =
      'flex';

    requestAnimationFrame(() => {

      mainApp.classList.add(
        'show'
      );

      renderHistory();

      loadStudentProfile();

    });

  }, 700);
}

/* ── 10. AUTO LOGIN ───────────────────────────────────────── */

window.onload = () => {

  const reg =
    sessionStorage.getItem(
      'reg_no'
    );

  const sec =
    sessionStorage.getItem(
      'section'
    );

  if (reg && sec) {

    loginScreen.style.display =
      'none';

    mainApp.style.display =
      'flex';

    mainApp.classList.add(
      'show'
    );

    renderHistory();

    loadStudentProfile();
  }
};

/* ── 11. LOGOUT ───────────────────────────────────────────── */

function logout() {

  sessionStorage.clear();

  location.reload();
}

/* ── 12. NEW CHAT ─────────────────────────────────────────── */

function newChat() {

  chat.innerHTML = '';

  started = false;

  logoBox.classList.remove(
    'move-up'
  );

  input.focus();
}

/* ── 13. HISTORY ──────────────────────────────────────────── */

function renderHistory() {

  const historyDiv =
    document.getElementById(
      'history'
    );

  historyDiv.innerHTML = '';

  const recentSearches =
    getRecentSearches();

  recentSearches
    .slice()
    .reverse()
    .forEach(item => {

      const div =
        document.createElement(
          'div'
        );

      div.className =
        'history-item';

      div.innerText = item;

      div.title = item;

      div.onclick = () => {

        input.value = item;

        input.focus();
      };

      historyDiv.appendChild(div);
    });
}

function saveSearch(text) {

  let recentSearches =
    getRecentSearches();

  if (
    recentSearches.includes(text)
  ) {
    return;
  }

  recentSearches.push(text);

  if (recentSearches.length > 10) {

    recentSearches.shift();
  }

  localStorage.setItem(

    getHistoryKey(),

    JSON.stringify(
      recentSearches
    )
  );

  renderHistory();
}

/* CLEAR HISTORY */

function clearHistory() {

  localStorage.removeItem(
    getHistoryKey()
  );

  renderHistory();
}

/* TOGGLE HISTORY */

function toggleHistory() {

  const wrapper =
    document.getElementById(
      'historyWrapper'
    );

  wrapper.classList.toggle(
    'collapsed'
  );
}

/* ── 14. RESPONSE FORMATTING ─────────────────────────────── */

function formatResponse(text) {

  return text

    .replace(
      /\n\n/g,
      '<br><br>'
    )

    .replace(
      /\n/g,
      '<br>'
    )

    .replace(
      /(Unit \d+:)/g,

      '<br><br><b>$1</b><br>'
    );
}

/* ── 15. MESSAGE RENDERING ───────────────────────────────── */

function addMsg(text, type) {

  const div =
    document.createElement(
      'div'
    );

  div.className =
    'msg ' + type;

  if (type === 'bot') {

    div.innerHTML =
      formatResponse(text);

  } else {

    div.innerText = text;
  }

  chat.appendChild(div);

  chat.scrollTo({

    top:chat.scrollHeight,

    behavior:'smooth'
  });
}

/* ── 16. BACKEND REQUEST ─────────────────────────────────── */

async function getBackendReply(userText) {

  try {

    const res = await fetch(

      'http://127.0.0.1:8000/ask',

      {

        method: 'POST',

        headers: {

          'Content-Type':
            'application/json',
        },

        body: JSON.stringify({

          query: userText,

          reg_no:
            sessionStorage.getItem(
              'reg_no'
            ),

          section:
            sessionStorage.getItem(
              'section'
            ),
        }),
      }
    );

    const data =
      await res.json();

    return (

      data.response ||

      'No response from server.'
    );

  } catch (err) {

    return (
      'Backend error: ' +
      err.message
    );
  }
}

/* ── 17. SEND MESSAGE ─────────────────────────────────────── */

async function send() {

  const text =
    input.value.trim();

  if (!text) return;

  /* USER MESSAGE */

  addMsg(text, 'user');

  input.value = '';

  /* SAVE FIRST MESSAGE */

  if (!started) {

    saveSearch(text);

    started = true;

    logoBox.classList.add(
      'move-up'
    );
  }

  /* DETECT INTENT */

  const intent =
    detectIntent(text);

  /* START AI LOADER */

  startDynamicLoader(intent);

  /* BACKEND */

  const reply =
    await getBackendReply(text);

  /* STOP LOADER */

  stopDynamicLoader();

  /* BOT RESPONSE */

  addMsg(reply, 'bot');
}

/* ── 18. ENTER KEY ────────────────────────────────────────── */

input.addEventListener(

  'keypress',

  e => {

    if (e.key === 'Enter') {

      send();
    }
  }
);

/* ── 19. VOICE INPUT ─────────────────────────────────────── */

function startVoice() {

  const SpeechRecognition =

    window.SpeechRecognition ||

    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {

    alert(
      'Voice input is not supported in this browser.'
    );

    return;
  }

  const rec =
    new SpeechRecognition();

  rec.onresult = e => {

    input.value =
      e.results[0][0].transcript;
  };

  rec.onerror = e => {

    console.warn(
      'Speech error:',
      e.error
    );
  };

  rec.start();
}

/* ── 20. FILE UPLOAD ─────────────────────────────────────── */

function uploadFile() {

  document
    .getElementById(
      'fileInput'
    )
    .click();
}

function handleFile(e) {

  const file =
    e.target.files[0];

  if (file) {

    addMsg(
      '📁 ' + file.name,
      'user'
    );
  }
}

/* ── 21. PARTICLES ────────────────────────────────────────── */

tsParticles.load(

  'particles',

  {

    particles: {

      number: {

        value: 80,
      },

      size: {

        value: 2,
      },

      move: {

        speed: 1,
      },

      opacity: {

        value: 0.5,
      },

      links: {

        enable: true,

        color: '#888',

        opacity: 0.4,
      },
    },
  }
);