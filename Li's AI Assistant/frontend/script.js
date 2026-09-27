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
            sendMessage(transcript);
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

    // Text-To-Speech Output via Web Speech Synthesis (Online / High Quality Browser Engine)
    function speakText(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop any active speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
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

    async function sendMessage(text) {
        const query = text || userInput.value.trim();
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

            // Speak response using browser speech synthesis
            speakText(reply);
        } catch (error) {
            console.error("Error communicating with server:", error);
            appendMessage('assistant', "Sorry, I lost connection to the server.");
            statusText.innerText = 'Connection error.';
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', () => sendMessage());
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    micBtn.addEventListener('click', toggleListening);

    pillBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            sendMessage(cmd);
        });
    });
});
