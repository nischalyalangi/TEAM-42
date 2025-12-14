const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const personaBadge = document.getElementById('persona-badge');
const personaIntent = document.getElementById('persona-intent');

// Function to add a message to the UI
function addMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = isUser ? 'ME' : 'AI';
    
    const content = document.createElement('div');
    content.className = 'content';
    
    if (isUser) {
        content.textContent = text;
    } else {
        // Parse Markdown for AI messages
        content.innerHTML = marked.parse(text);
    }
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(content);
    
    messagesContainer.appendChild(msgDiv);
    
    // Smooth scroll to bottom
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// Function to call the backend API
async function callTutor(answer = null) {
    try {
        const response = await fetch('/api/tutor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answer: answer })
        });
        
        const data = await response.json();
        return data; // Returns the full step object
    } catch (error) {
        console.error('Error:', error);
        addMessage('Error connecting to the tutor. Is the backend running?', false);
        return null;
    }
}

// Handler for user input submission
async function handleInput(e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, true);
    userInput.value = '';

    // Disable input while loading
    userInput.disabled = true;

    // Call backend
    const stepData = await callTutor(text);
    
    if (stepData) {
        processStepData(stepData);
    }

    userInput.disabled = false;
    userInput.focus();
}

// Process the step data returned from backend
function processStepData(data) {
    // 1. Update Sidebar
    if (data.tier) {
        personaBadge.textContent = data.tier.charAt(0).toUpperCase() + data.tier.slice(1);
    } else if (data.persona) { // Fallback
        personaBadge.textContent = data.persona;
    }

    if (data.intent) {
        personaIntent.textContent = data.intent;
    }

    // 2. Construct AI Response Message
    let messageContent = "";

    // If it's the explanation phase
    if (data.explanation) {
        messageContent += `${data.explanation}\n\n`;
    }

    // If there is a question (Assessment or Checkpoint)
    if (data.question) {
        // Style the question distinctly
        // Simple trick: Use Markdown quote or bold header
        messageContent += `**Question:**\n${data.question}`;
        
        // Handle Options if they exist (Assessment phase might print them in text, 
        // strictly speaking the backend prints them to stdout, but let's see what `data.question` has.
        // The backend `tutor_step` returns just the question string "Which best describes you?" 
        // usually accompanied by options printed to stdout in the CLI version.
        // Wait, the `initial_assessment` implementation prints to stdout. 
        // The `tutor_step` logic calls `collect_answers`. 
        // THIS IS A PROBLEM for the WEB UI. 
        // `collect_answers` uses `input()`. This will hang the server.
    }
    
    addMessage(messageContent, false);
}

// Start button handler
async function startTutor() {
    // Hide the intro message container's button
    document.querySelector('.start-btn').style.display = 'none';
    
    // For the web UI to work with `collect_answers` that uses `input()`, 
    // we need to refactor `initial_assessment.py` to NOT use `input()` directly,
    // or we rely on `tutor_step` returning a state object that asks for input.
    // 
    // The current `tutor_step` calls `run_initial_assessment()`.
    // It calls `collect_answers()`. 
    // `collect_answers` loops with `input()`. 
    // This blocks the API. 
    
    // TEMPORARY FIX:
    // We assume the user wants to start.
    // Since we cannot easily rewrite the entire assessment logic right now to be async/stateful without a big refactor,
    // and the user asked for a UI "without disturbing present code", 
    // we might hit a blocker here.
    
    // However, looking at `api.py`, it calls `tutor_step(input.answer)`.
    // If `tutor_step` blocks on `input()`, the API hangs.
    
    addMessage("Starting assessment... (Note: CLI interaction might be required if not fully adapted)", false);
    
    // Attempt call
    const data = await callTutor(null);
    if(data) processStepData(data);
}

async function resetSession() {
    await fetch('/api/reset', { method: 'POST' });
    location.reload();
}
