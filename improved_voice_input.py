import streamlit as st

def voice_input(language="en", key=None):
    """Voice input button with enhanced mic permission handling and user guidance."""
    
    unique_id = f"voice-{key}-{id(language)}"
    
    html = f"""
    <div>
        <button 
            id="{unique_id}" 
            onclick="setupSpeechRecognition_{unique_id}()"
            style="background-color: #d63384; color: white; border: none; 
                   border-radius: 20px; padding: 10px 15px; cursor: pointer;">
            🎤 Speak now
        </button>
        <div id="{unique_id}-status" style="margin-top: 5px; font-size: 0.9rem;"></div>
    </div>

    <script>
    function setupSpeechRecognition_{unique_id}() {{
        const statusDiv = document.getElementById('{unique_id}-status');
        const button = document.getElementById('{unique_id}');
        
        statusDiv.textContent = "Initializing...";

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            statusDiv.textContent = "⚠️ Speech recognition not supported in this browser. Use Chrome or Edge.";
            statusDiv.style.color = "red";
            return;
        }}

        const recognition = new SpeechRecognition();
        recognition.lang = '{language}';

        recognition.onstart = function() {{
            button.textContent = "🔴 Listening...";
            statusDiv.textContent = "Listening... 🎤";
        }};

        recognition.onaudiostart = function() {{
            statusDiv.textContent = "🎧 Audio detected, keep speaking...";
        }};

        recognition.onresult = function(event) {{
            const transcript = event.results[0][0].transcript;
            statusDiv.textContent = "✅ Got it: " + transcript;

            const inputs = document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {{
                for (let input of inputs) {{
                    if (window.getComputedStyle(input).display !== 'none') {{
                        input.value = transcript;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        setTimeout(() => {{
                            const sendBtns = Array.from(document.querySelectorAll('button')).filter(
                                btn => btn.innerText === 'Send'
                            );
                            if (sendBtns.length > 0) sendBtns[0].click();
                        }}, 500);
                        break;
                    }}
                }}
            }} else {{
                statusDiv.textContent = "⚠️ No input field found.";
                statusDiv.style.color = "red";
            }}
        }};

        recognition.onerror = function(event) {{
            statusDiv.textContent = "❌ Mic error: " + event.error + ". If blocked, click the 🔒 icon in the URL bar to allow mic access.";
            statusDiv.style.color = "red";
            button.textContent = "🎤 Speak now";
        }};

        recognition.onend = function() {{
            button.textContent = "🎤 Speak now";
        }};

        try {{
            recognition.start();
        }} catch (error) {{
            statusDiv.textContent = "❌ Failed to start: " + error.message;
            statusDiv.style.color = "red";
        }}
    }}
    </script>
    """
    
    return html
