import streamlit.components.v1 as components

def voice_input(language="en", key=None):
    """Voice input component using SpeechRecognition and working in Streamlit Cloud via components.html."""
    
    uid = f"voice-{key}-{id(language)}"

    html_code = f"""
    <div>
        <button 
            id="{uid}" 
            onclick="startVoice_{uid}()" 
            style="background-color:#d63384;color:white;border:none;padding:10px 15px;border-radius:20px;cursor:pointer;">
            🎤 Speak now
        </button>
        <p id="{uid}-status" style="font-size:0.9rem;margin-top:5px;"></p>
    </div>
    <script>
        function startVoice_{uid}() {{
            const status = document.getElementById('{uid}-status');
            const button = document.getElementById('{uid}');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                status.innerText = "⚠️ Speech recognition not supported. Please use Chrome or Edge.";
                return;
            }}
            const recognition = new SpeechRecognition();
            recognition.lang = "{language}";
            recognition.onstart = () => {{
                button.innerText = "🔴 Listening...";
                status.innerText = "🎧 Listening...";
            }};
            recognition.onresult = e => {{
                const text = e.results[0][0].transcript;
                status.innerText = "✅ Heard: " + text;

                const input = document.querySelector('input[type="text"]');
                if (input) {{
                    input.value = text;
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    setTimeout(() => {{
                        const send = Array.from(document.querySelectorAll('button')).find(b => b.innerText === 'Send');
                        if (send) send.click();
                    }}, 500);
                }} else {{
                    status.innerText = "⚠️ No input box found to insert voice input.";
                }}
            }};
            recognition.onerror = e => {{
                status.innerText = "❌ Mic error: " + e.error;
                button.innerText = "🎤 Speak now";
            }};
            recognition.onend = () => {{
                button.innerText = "🎤 Speak now";
            }};
            recognition.start();
        }}
    </script>
    """

    # Inject the HTML+JS with execution capability
    components.html(html_code, height=150)
