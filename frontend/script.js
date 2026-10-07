document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const voiceBtn = document.getElementById('voice-btn');

  // Speech Recognition Setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      userInput.value = transcript;
      sendMessage(true);
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
    };
  }

  // Web Speech TTS Synthesis (Female Voice Selection)
  function speakFemale(text) {
    if (!('speechSynthesis' in window)) return;
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);

    const voices = synth.getVoices();
    const femaleVoice = voices.find(v => 
      v.name.includes('Zira') || 
      v.name.includes('Google US English') || 
      v.name.includes('Samantha') || 
      v.name.includes('Female')
    );

    if (femaleVoice) {
      utterance.voice = femaleVoice;
    }
    synth.speak(utterance);
  }

  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerHTML = `
      <div class="avatar">${sender === 'user' ? '👤' : '🤖'}</div>
      <div class="bubble">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  async function sendMessage(isVoice = false) {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    userInput.value = '';

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, voice_mode: isVoice })
      });
      const data = await resp.json();
      appendMessage('assistant', data.response);

      if (isVoice) {
        speakFemale(data.response);
      }
    } catch (e) {
      appendMessage('assistant', `Error connecting to assistant server: ${e.message}`);
    }
  }

  sendBtn.addEventListener('click', () => sendMessage(false));
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(false);
  });

  if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
      if (recognition) {
        recognition.start();
      } else {
        alert('Web Speech Recognition API is not supported in this browser.');
      }
    });
  }
});
