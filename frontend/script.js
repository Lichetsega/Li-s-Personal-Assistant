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
    const stopSpeechBtn = document.getElementById('stopSpeechBtn');
    const orbCore = document.querySelector('.orb-core');

    let isListening = false;
    let recognition = null;
    let availableVoices = [];

    // Real-Time STT State & Debounce
    let finalTranscript = '';
    let interimTranscript = '';
    let silenceTimeout = null;
    const SILENCE_DELAY_MS = 1400; // 1.4s of quiet auto-submits sentence

    // Spacebar Push-to-Talk State
    let spacebarHeld = false;

    // Web Audio API & Linear PCM WAV State
    let audioContext = null;
    let analyserNode = null;
    let micSourceNode = null;
    let pcmProcessorNode = null;
    let micStream = null;
    let animFrameId = null;
    let pcmChunks = [];

    // Cloud Whisper STT State (Groq Whisper-large-v3)
    let isWhisperAvailable = false;

    async function checkWhisperStatus() {
        try {
            const res = await fetch('/api/transcribe/status');
            const data = await res.json();
            isWhisperAvailable = !!data.whisper_available;
            if (isWhisperAvailable) {
                console.info("⚡ Groq Whisper-large-v3 Cloud STT engine is active!");
                const statusBadge = document.getElementById('statusBadge');
                if (statusBadge) {
                    statusBadge.innerHTML = `<span class="pulse-dot"></span> <span title="Groq Whisper-large-v3 Cloud Voice Engine Active" style="color: #38bdf8;"><i class="fa-solid fa-bolt" style="color: #f59e0b; margin-right: 3px;"></i> Whisper Ready</span>`;
                }
            }
        } catch (e) {
            isWhisperAvailable = false;
        }
    }
    checkWhisperStatus();

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

    // Standard 16,000 Hz 16-bit Mono Linear PCM WAV Encoder
    function createWavBlobFromPcm(chunks, sourceSampleRate, targetSampleRate = 16000) {
        let totalLength = 0;
        for (let i = 0; i < chunks.length; i++) {
            totalLength += chunks[i].length;
        }
        if (totalLength === 0) return null;

        const merged = new Float32Array(totalLength);
        let offset = 0;
        for (let i = 0; i < chunks.length; i++) {
            merged.set(chunks[i], offset);
            offset += chunks[i].length;
        }

        // Downsample to 16,000 Hz
        const ratio = sourceSampleRate / targetSampleRate;
        const targetLength = Math.round(totalLength / ratio);
        const result = new Float32Array(targetLength);
        for (let i = 0; i < targetLength; i++) {
            const index = Math.min(Math.round(i * ratio), totalLength - 1);
            result[i] = merged[index];
        }

        // Measure root-mean-square (RMS) acoustic energy
        let sumSquares = 0;
        for (let i = 0; i < result.length; i++) {
            sumSquares += result[i] * result[i];
        }
        const rms = Math.sqrt(sumSquares / result.length);
        if (rms < 0.003) {
            console.info("Acoustic energy below noise threshold (silence detected, RMS:", rms.toFixed(4) + ")");
            return null;
        }

        // 44-Byte Standard RIFF WAV Header
        const buffer = new ArrayBuffer(44 + result.length * 2);
        const view = new DataView(buffer);

        function writeString(off, str) {
            for (let i = 0; i < str.length; i++) view.setUint8(off + i, str.charCodeAt(i));
        }

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + result.length * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);                  // Subchunk1Size (16 for PCM)
        view.setUint16(20, 1, true);                   // AudioFormat (1 = Linear PCM)
        view.setUint16(22, 1, true);                   // NumChannels (1 = Mono)
        view.setUint32(24, targetSampleRate, true);    // SampleRate (16,000 Hz)
        view.setUint32(28, targetSampleRate * 2, true);// ByteRate (16,000 * 1 * 2)
        view.setUint16(32, 2, true);                   // BlockAlign (1 * 16/8)
        view.setUint16(34, 16, true);                  // BitsPerSample (16-bit)
        writeString(36, 'data');
        view.setUint32(40, result.length * 2, true);

        // Convert Float32 to Signed 16-bit PCM Int
        let pcmOffset = 44;
        for (let i = 0; i < result.length; i++, pcmOffset += 2) {
            const s = Math.max(-1, Math.min(1, result[i]));
            view.setInt16(pcmOffset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }

        return new Blob([buffer], { type: 'audio/wav' });
    }

    async function startAudioRecording() {
        try {
            if (!micStream || !micStream.active) {
                micStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });
            }

            if (!audioContext || audioContext.state === 'closed') {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
            }

            if (!micSourceNode) {
                micSourceNode = audioContext.createMediaStreamSource(micStream);
            }

            if (!analyserNode) {
                analyserNode = audioContext.createAnalyser();
                analyserNode.fftSize = 64;
                micSourceNode.connect(analyserNode);
            }

            // Real-time raw PCM sample accumulator
            pcmChunks = [];
            if (!pcmProcessorNode) {
                pcmProcessorNode = audioContext.createScriptProcessor(4096, 1, 1);
                pcmProcessorNode.onaudioprocess = (e) => {
                    if (!isListening) return;
                    const inputData = e.inputBuffer.getChannelData(0);
                    pcmChunks.push(new Float32Array(inputData));
                };
                micSourceNode.connect(pcmProcessorNode);
                pcmProcessorNode.connect(audioContext.destination);
            }

            startAudioMeter();
        } catch (err) {
            console.warn("Audio recording initialization notice:", err);
        }
    }

    function startAudioMeter() {
        if (!analyserNode) return;
        const dataArray = new Uint8Array(analyserNode.frequencyBinCount);

        function updateMeter() {
            if (!isListening) return;
            analyserNode.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const average = sum / dataArray.length; // 0 - 255
            const normalized = Math.min(average / 90, 1.0); // 0.0 - 1.0

            if (orbCore && isListening) {
                const scale = 1.05 + normalized * 0.35;
                const glow = 20 + normalized * 45;
                orbCore.style.transform = `scale(${scale.toFixed(2)})`;
                orbCore.style.boxShadow = `0 0 ${glow.toFixed(0)}px rgba(249, 115, 22, 0.95)`;
            }

            animFrameId = requestAnimationFrame(updateMeter);
        }

        updateMeter();
    }

    function stopAudioRecording() {
        return new Promise((resolve) => {
            // Short buffer to flush the final syllables of speech
            setTimeout(() => {
                if (!audioContext || pcmChunks.length === 0) {
                    resolve(null);
                    return;
                }
                const wavBlob = createWavBlobFromPcm(pcmChunks, audioContext.sampleRate, 16000);
                pcmChunks = [];
                resolve(wavBlob);
            }, 120);
        });
    }

    function stopAudioMeter() {
        if (animFrameId) cancelAnimationFrame(animFrameId);
        if (orbCore) {
            orbCore.style.transform = '';
            orbCore.style.boxShadow = '';
        }
    }

    // Initialize High-Fidelity Continuous Speech Recognition with Live Streaming
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;       // Don't cut off on short breaths
        recognition.interimResults = true;   // Stream words live as spoken
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;

        // Boost recognition probability for domain-specific acronyms and names
        const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList;
        if (SpeechGrammarList) {
            try {
                const domainTerms = ['INSA', 'Liche', 'Tsegaye', 'Jimma', 'Woliso', 'Agentic RAG', 'FastAPI', 'ChromaDB', 'MERN', 'Gemini', 'Python'];
                const grammar = '#JSGF V1.0; grammar portfolio; public <terms> = ' + domainTerms.join(' | ') + ' ;';
                const speechList = new SpeechGrammarList();
                speechList.addFromString(grammar, 1);
                recognition.grammars = speechList;
            } catch (err) {}
        }

        recognition.onstart = () => {
            isListening = true;
            finalTranscript = '';
            interimTranscript = '';
            voiceOrb.classList.add('listening');
            micBtn.classList.add('active');
            statusText.innerText = 'Listening to your voice... Speak now.';
            startAudioMeter();
        };

        recognition.onresult = (event) => {
            interimTranscript = '';
            let currentConfidence = null;

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const alt = event.results[i][0];
                const transcript = alt.transcript;
                if (typeof alt.confidence === 'number' && alt.confidence > 0) {
                    currentConfidence = alt.confidence;
                }
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            const currentSpeech = (finalTranscript + interimTranscript).trim();
            if (currentSpeech) {
                userInput.value = currentSpeech;

                let confidenceHtml = '';
                if (currentConfidence !== null) {
                    const percent = Math.round(currentConfidence * 100);
                    let badgeClass = 'high';
                    let icon = 'fa-circle-check';
                    let label = `${percent}% Clarity`;

                    if (percent < 60) {
                        badgeClass = 'low';
                        icon = 'fa-triangle-exclamation';
                        label = `${percent}% Low Clarity`;
                    } else if (percent < 80) {
                        badgeClass = 'med';
                        icon = 'fa-circle-info';
                        label = `${percent}% Clarity`;
                    }
                    confidenceHtml = `<span class="confidence-badge ${badgeClass}" title="Acoustic recognition confidence: ${percent}%"><i class="fa-solid ${icon}"></i> ${label}</span>`;
                }

                statusText.innerHTML = `<span style="color: #38bdf8;"><i class="fa-solid fa-wave-square"></i> Hearing:</span> "${currentSpeech}" ${confidenceHtml}`;

                // Smart silence debounce: auto-send after 1.4s of quiet
                if (silenceTimeout) clearTimeout(silenceTimeout);
                silenceTimeout = setTimeout(() => {
                    if (isListening && !spacebarHeld && currentSpeech) {
                        const finalQuery = currentSpeech;
                        stopListening();
                        finishVoiceQuery(finalQuery);
                    }
                }, SILENCE_DELAY_MS);
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            if (event.error !== 'no-speech') {
                stopListening();
                statusText.innerText = "Could not recognize speech. Please try again or type.";
            }
        };

        recognition.onend = () => {
            if (isListening) {
                // If user didn't explicitly stop, clean up
                stopListening();
            }
        };
    } else {
        console.warn("Web Speech Recognition is not supported in this browser.");
    }

    async function finishVoiceQuery(fallbackText) {
        let textToSend = (fallbackText || userInput.value).trim();

        // If Groq Whisper Cloud STT is active on backend
        if (isWhisperAvailable) {
            try {
                statusText.innerHTML = `<span style="color: #f59e0b;"><i class="fa-solid fa-bolt"></i> Refining with Whisper-large-v3...</span>`;
                const audioBlob = await stopAudioRecording();

                // Only transcribe if audio blob has real speech content (> 8000 bytes for 16kHz WAV)
                if (audioBlob && audioBlob.size > 8000) {
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'recording.wav');

                    const res = await fetch('/api/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (data.success && data.text && data.text.trim()) {
                        console.info("⚡ Whisper precision transcription:", data.text);
                        textToSend = data.text.trim();
                        userInput.value = textToSend;
                    } else {
                        console.info("Whisper returned no speech, preserving browser transcription:", textToSend);
                    }
                } else {
                    console.info("Audio was silent or below threshold, preserving browser transcription:", textToSend);
                }
            } catch (err) {
                console.warn("Whisper transcription error, using fallback text:", err);
            }
        }

        if (textToSend) {
            sendMessage(textToSend, 'voice');
        }
    }

    function startListening() {
        if (!recognition) {
            alert("Speech recognition is not supported in your browser. Please use text input.");
            return;
        }
        if (!isListening) {
            startAudioRecording();
            try {
                recognition.start();
            } catch (err) {
                console.warn("Recognition already started or initializing:", err);
            }
        }
    }

    function stopListening() {
        if (silenceTimeout) clearTimeout(silenceTimeout);
        isListening = false;
        voiceOrb.classList.remove('listening');
        micBtn.classList.remove('active');
        stopAudioMeter();

        if (recognition) {
            try {
                recognition.stop();
            } catch (err) {}
        }

        if (!statusText.innerText.startsWith("Speaking") && !statusText.innerText.startsWith("Thinking")) {
            statusText.innerText = 'Click microphone or hold Spacebar to speak with Li';
        }
    }

    function toggleListening() {
        if (isListening) {
            const query = userInput.value.trim();
            stopListening();
            if (query || audioChunks.length > 0) {
                finishVoiceQuery(query);
            }
        } else {
            startListening();
        }
    }

    // Spacebar "Hold-to-Talk" Push-to-Talk Listener
    window.addEventListener('keydown', (e) => {
        // Trigger only if Spacebar is pressed, not already held, and not inside an input field
        if (e.code === 'Space' && !spacebarHeld && document.activeElement !== userInput) {
            e.preventDefault();
            spacebarHeld = true;
            statusText.innerText = '🎙️ Holding Spacebar... Speak now!';
            startListening();
        }
    });

    window.addEventListener('keyup', (e) => {
        if (e.code === 'Space' && spacebarHeld && document.activeElement !== userInput) {
            e.preventDefault();
            spacebarHeld = false;
            // Short 300ms buffer to finalize last word before stopping
            setTimeout(() => {
                const query = userInput.value.trim();
                stopListening();
                if (query || audioChunks.length > 0) {
                    finishVoiceQuery(query);
                }
            }, 300);
        }
    });

    // Stop / Interrupt Assistant Speaking
    function stopSpeaking() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
        voiceOrb.classList.remove('speaking');
        if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
        statusText.innerText = 'Speech interrupted. Click microphone or hold Spacebar to speak with Li';
    }

    if (stopSpeechBtn) {
        stopSpeechBtn.addEventListener('click', stopSpeaking);
    }

    // Clicking the voice orb while speaking also interrupts speech immediately
    voiceOrb.addEventListener('click', () => {
        if (voiceOrb.classList.contains('speaking') || ('speechSynthesis' in window && window.speechSynthesis.speaking)) {
            stopSpeaking();
        }
    });

    // Pressing Escape key at any time interrupts speaking
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' || e.code === 'Escape') {
            if (voiceOrb.classList.contains('speaking') || ('speechSynthesis' in window && window.speechSynthesis.speaking)) {
                stopSpeaking();
            }
        }
    });

    // Audio-Reactive Web Speech Synthesis with Orb Pulse Animation & Stop Controls
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
                if (stopSpeechBtn) stopSpeechBtn.style.display = 'inline-flex';
                statusText.innerText = "Speaking with Li's voice... (Click 'Stop Talking' or press Esc)";
            };

            utterance.onend = () => {
                voiceOrb.classList.remove('speaking');
                if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
                statusText.innerText = 'Click microphone or hold Spacebar to speak with Li';
            };

            utterance.onerror = () => {
                voiceOrb.classList.remove('speaking');
                if (stopSpeechBtn) stopSpeechBtn.style.display = 'none';
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
        let query = (textOverride || userInput.value).trim();
        if (!query) return;

        // Auto-correct common acoustic speech recognition mishearings for domain terms
        query = query
            .replace(/\b(?:party\s+song|party\s+saw|in\s+saw|in\s+sa)\b/gi, 'at INSA')
            .replace(/\binternship\s+(?:inside|in\s+sight)\b/gi, 'internship at INSA')
            .replace(/\b(?:ragged|raggae)\b(?=\s*(?:agent|retrieval|project|system|chatbot|architecture))/gi, 'RAG')
            .replace(/\b(?:reach's|lisa's|lee's)\b/gi, "Li's")
            .replace(/\b(?:makes?\s+me\s+sleep\s+with|sleep\s+with)\b(?=\s*candidate)/gi, "makes Li a great");

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
            statusText.innerText = 'Click microphone or hold Spacebar to speak with Li';

            // Speak ONLY if input came from voice
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
