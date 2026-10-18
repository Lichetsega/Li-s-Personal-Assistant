document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const micBtn = document.getElementById('micBtn');
    const chatContainer = document.getElementById('chatContainer');
    const voiceOrb = document.getElementById('voiceOrb');
    const statusText = document.getElementById('statusText');
    const pillBtns = document.querySelectorAll('.pill-btn');
    const soundToggleBtn = document.getElementById('soundToggleBtn');
    const soundIcon = document.getElementById('soundIcon');
    const soundLabel = document.getElementById('soundLabel');

    let isListening = false;
    let recognition = null;
    let availableVoices = [];

    // Sound Mute / Unmute State
    let isSoundMuted = localStorage.getItem('li_sound_muted') === 'true';

    function updateSoundUI() {
        if (!soundToggleBtn) return;
        if (isSoundMuted) {
            soundToggleBtn.classList.add('muted');
            if (soundIcon) soundIcon.className = 'fa-solid fa-volume-xmark';
            if (soundLabel) soundLabel.innerText = 'Muted';
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
            voiceOrb.classList.remove('speaking');
        } else {
            soundToggleBtn.classList.remove('muted');
            if (soundIcon) soundIcon.className = 'fa-solid fa-volume-high';
            if (soundLabel) soundLabel.innerText = 'Sound On';
        }
    }

    updateSoundUI();

    if (soundToggleBtn) {
        soundToggleBtn.addEventListener('click', () => {
            isSoundMuted = !isSoundMuted;
            localStorage.setItem('li_sound_muted', isSoundMuted.toString());
            updateSoundUI();
        });
    }

    // Pre-fetch browser speech synthesis voices
    function populateVoices() {
        if ('speechSynthesis' in window) {
            availableVoices = window.speechSynthesis.getVoices();
        }
    }

    if ('speechSynthesis' in window) {
        populateVoices();
        window.speechSynthesis.onvoiceschanged = populateVoices;
    }

    // Select preferred Female Voice
    function getFemaleVoice() {
        if (!availableVoices || availableVoices.length === 0) {
            populateVoices();
        }

        const femaleKeywords = ['zira', 'samantha', 'victoria', 'karen', 'hazel', 'eva', 'female', 'google us english'];
        for (const keyword of femaleKeywords) {
            const match = availableVoices.find(v => v.name.toLowerCase().includes(keyword));
            if (match) return match;
        }

        return availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0] || null;
    }

    // Initialize Web Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            voiceOrb.classList.add('listening');
            micBtn.classList.add('active');
            statusText.innerText = 'Listening to your voice... Speak now.';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            statusText.innerText = `Recognized: "${transcript}"`;
            sendMessage(transcript, 'voice');
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            stopListening();
            statusText.innerText = "Could not recognize speech. Please try typing.";
        };

        recognition.onend = () => {
            stopListening();
        };
    } else {
        console.warn("Web Speech Recognition is not supported in this browser.");
    }

    function toggleListening() {
        if (!recognition) {
            alert("Speech recognition is not supported in your browser. Please use text input.");
            return;
        }

        if (isListening) {
            recognition.stop();
            stopListening();
        } else {
            recognition.start();
        }
    }

    function stopListening() {
        isListening = false;
        voiceOrb.classList.remove('listening');
        micBtn.classList.remove('active');
        if (!statusText.innerText.startsWith("Recognized")) {
            statusText.innerText = 'Click microphone or start typing to speak with Li';
        }
    }

    // Audio-Reactive Web Speech Synthesis with Orb Pulse Animation
    function speakText(text) {
        if (isSoundMuted) return; // Silent mode honored
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();

            // Strip markdown, URLs, and code blocks for smooth TTS speech
            const cleanText = text
                .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
                .replace(/https?:\/\/\S+/g, '')
                .replace(/[*_#`•]/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();

            if (!cleanText) return;

            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.08;

            const femaleVoice = getFemaleVoice();
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }

            utterance.onstart = () => {
                voiceOrb.classList.add('speaking');
                statusText.innerText = "Speaking with Li's voice...";
            };

            utterance.onend = () => {
                voiceOrb.classList.remove('speaking');
                statusText.innerText = 'Click microphone or start typing to speak with Li';
            };

            utterance.onerror = () => {
                voiceOrb.classList.remove('speaking');
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    // Featured Projects Data for Rich Interactive Cards
    const FEATURED_PROJECTS = [
        {
            title: "Visit Ethiopia Agentic RAG",
            icon: "fa-solid fa-map-location-dot",
            desc: "Autonomous multi-agent system with Fused Supervisor Planner, domain expert sub-agents (Culture, Itinerary, Logistics), and live currency tools.",
            badges: ["Python", "Agentic RAG", "ChromaDB", "BM25 Fuzzy", "FastAPI/Streamlit"],
            bullets: [
                "Fused Supervisor Planner handling intent, pronoun resolution & multi-query expansion.",
                "Hybrid dense semantic (ChromaDB) + sparse keyword retrieval with fuzzy phonetic matching.",
                "Zero-API-call responses via two-tier exact & semantic query caching (similarity >= 0.82)."
            ],
            github: "https://github.com/Lichetsega/Agentic-Retrieval-Augmented-Generation-Agentic-RAG-"
        },
        {
            title: "Li's AI Voice Assistant",
            icon: "fa-solid fa-microphone-lines",
            desc: "Visitor-facing portfolio assistant with real-time audio interaction, Gemini multi-key failover, and strict security guardrails.",
            badges: ["FastAPI", "WebSockets", "Google Gemini AI", "Guardrails", "Local RAG"],
            bullets: [
                "Multi-layered confidentiality guardrails blocking prompt injection and code leakage.",
                "Automatic quota recovery via round-robin multi-key rotation and offline local RAG fallback.",
                "Interactive browser STT/TTS with audio-reactive visualizer and real-time GitHub sync."
            ],
            github: "https://github.com/Lichetsega/Li-s-Personal-Assistant"
        },
        {
            title: "Password Exposure Checker",
            icon: "fa-solid fa-shield-halved",
            desc: "Zero-knowledge security auditor checking compromised credentials against billions of breached accounts.",
            badges: ["Python", "SHA-1", "k-Anonymity", "HIBP API", "CLI"],
            bullets: [
                "Implements the k-Anonymity mathematical model to ensure plaintext passwords never cross the network.",
                "Transmits only the first 5 characters of the SHA-1 hash to query the Have I Been Pwned API.",
                "Supports batch password analysis from command-line arguments with exact breach counts."
            ],
            github: "https://github.com/Lichetsega/password_checker"
        },
        {
            title: "Hacker News Signal Filter",
            icon: "fa-solid fa-newspaper",
            desc: "High-signal Python scraper filtering noise from tech news to extract only top-tier discussions.",
            badges: ["Python", "BeautifulSoup", "Web Scraping", "Automation", "HTML Report"],
            bullets: [
                "Dynamically scrapes multiple pages filtering articles with points > 99.",
                "Sorts stories by engagement and generates a visual, styled HTML report.",
                "Respects ethical scraping principles with polite request throttling."
            ],
            github: "https://github.com/Lichetsega/hacker_news-scraper"
        }
    ];

    function createProjectCardElement(proj) {
        const card = document.createElement('div');
        card.className = 'project-card';

        const badgesHtml = proj.badges.map((b, i) => {
            const colorClass = i % 3 === 0 ? '' : (i % 3 === 1 ? 'cyan' : 'green');
            return `<span class="tech-badge ${colorClass}">${b}</span>`;
        }).join('');

        const bulletsHtml = proj.bullets.map(b => `<li>${b}</li>`).join('');

        card.innerHTML = `
            <div class="project-card-header">
                <div class="project-card-title">
                    <i class="${proj.icon}"></i> ${proj.title}
                </div>
                <a href="${proj.github}" target="_blank" rel="noopener" class="project-github-btn">
                    <i class="fa-brands fa-github"></i> View on GitHub
                </a>
            </div>
            <p class="project-card-desc">${proj.desc}</p>
            <div class="project-badges">${badgesHtml}</div>
            <ul class="project-bullets">${bulletsHtml}</ul>
        `;
        return card;
    }

    // Markdown and Link Formatter for Assistant Messages
    function formatMessageText(rawText) {
        // Escape basic HTML
        let escaped = rawText
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Format Markdown links [Text](URL) -> <a href="URL" target="_blank">Text</a>
        escaped = escaped.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/static\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

        // Format raw URLs
        escaped = escaped.replace(/(^|[^">])(https?:\/\/[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');

        // Bold **text**
        escaped = escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Inline `code`
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Line breaks
        escaped = escaped.replace(/\n/g, '<br>');

        return escaped;
    }

    function appendMessage(sender, text, isProjectShowcase = false) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'assistant-message');

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const content = document.createElement('div');
        content.classList.add('message-content');

        if (sender === 'user') {
            content.innerText = text;
        } else {
            content.innerHTML = formatMessageText(text);

            // Render rich interactive project cards when appropriate
            if (isProjectShowcase || text.toLowerCase().includes("featured project") || text.toLowerCase().includes("visit ethiopia agentic rag")) {
                const cardContainer = document.createElement('div');
                cardContainer.className = 'project-cards-container';
                FEATURED_PROJECTS.forEach(proj => {
                    cardContainer.appendChild(createProjectCardElement(proj));
                });
                content.appendChild(cardContainer);
            }
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(content);

        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage(textOverride, inputMode = 'text') {
        const query = textOverride || userInput.value.trim();
        if (!query) return;

        appendMessage('user', query);
        userInput.value = '';
        statusText.innerText = 'Thinking...';

        const isProjectQuery = /featured project|show project|code architecture|what has li built/i.test(query);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });

            const data = await response.json();
            const reply = data.response || "No response received.";

            appendMessage('assistant', reply, isProjectQuery);
            statusText.innerText = 'Click microphone or start typing to speak with Li';

            // Speak ONLY if input came from voice, or voice mode is active and unmuted
            if (inputMode === 'voice') {
                speakText(reply);
            }
        } catch (error) {
            console.error("Error communicating with server:", error);
            appendMessage('assistant', "Sorry, I lost connection to the server. Please check your network.");
            statusText.innerText = 'Connection error.';
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', () => sendMessage(null, 'text'));
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage(null, 'text');
    });

    micBtn.addEventListener('click', toggleListening);

    pillBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            sendMessage(cmd, 'text');
        });
    });
});
