document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const micBtn = document.getElementById('micBtn');
    const chatContainer = document.getElementById('chatContainer');
    const voiceOrb = document.getElementById('voiceOrb');
    const statusText = document.getElementById('statusText');
    const pillBtns = document.querySelectorAll('.pill-btn');

    let isListening = false;
    let recognition = null;
    let availableVoices = [];

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

        // Priority list of female voice keywords
        const femaleKeywords = ['zira', 'samantha', 'victoria', 'karen', 'hazel', 'eva', 'female', 'google us english'];
        
        for (const keyword of femaleKeywords) {
            const match = availableVoices.find(v => v.name.toLowerCase().includes(keyword));
            if (match) return match;
        }

        // Fallback: pick any English voice
        return availableVoices.find(v => v.lang.startsWith('en')) || availableVoices[0] || null;
    }

    // Initialize Web Speech Recognition if available
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
            // Trigger message with inputMode = 'voice'
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
            statusText.innerText = 'Click microphone or start typing to speak with Gemini AI';
        }
    }

    // Mode-aware Text-To-Speech Output via Web Speech Synthesis with Female Voice
    function speakText(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop any active speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.1; // Slightly higher pitch for natural female tone

            const femaleVoice = getFemaleVoice();
            if (femaleVoice) {
                utterance.voice = femaleVoice;
                console.log("Speaking using female voice:", femaleVoice.name);
            }

            window.speechSynthesis.speak(utterance);
        }
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'assistant-message');

        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        avatar.innerHTML = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const content = document.createElement('div');
        content.classList.add('message-content');
        content.innerText = text;

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

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query })
            });

            const data = await response.json();
            const reply = data.response || "No response received.";

            appendMessage('assistant', reply);
            statusText.innerText = 'Click microphone or start typing to speak with Gemini AI';

            // Speak ONLY if input came from voice! Keep typed input silent.
            if (inputMode === 'voice') {
                speakText(reply);
            }
        } catch (error) {
            console.error("Error communicating with server:", error);
            appendMessage('assistant', "Sorry, I lost connection to the server.");
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
