
let messages = []; // To store chat history
let showBotInput = false; // To control visibility of bot input section

// Function to handle user input for testing chatbox functionality -- to be replaced with commented function below for extracting from LLM
function handleUserInput2() {
    const userInput = document.getElementById('user-input').value;
    
    if (userInput.trim() !== '') {
        // Add user message to the chat
        messages.push({ sender: 'user', text: userInput });
        document.getElementById('user-input').value = ''; // Clear input field
        displayMessages();

        // TODO -- show a bot response that "bot is thinking ..." with dots being flashed until timer runs out
        // Show bot thinking message
        const thinkingMessage = { sender: 'bot', text: 'Bot is thinking' };
        messages.push(thinkingMessage);
        displayMessages();

        // Add flashing dots to "thinking" message
        let thinkingText = 'Bot is thinking';
        let dotCount = 0;
        const thinkingInterval = setInterval(() => {
            if (dotCount < 3) {
                thinkingText += '.';
                dotCount++;
            } else {
                thinkingText = 'Bot is thinking';
                dotCount = 0;
            }
            messages[messages.length - 1].text = thinkingText; // Update last bot message with dots
            displayMessages();
        }, 500); // Update every 500ms to add a dot

        // Simulate a bot response after a delay
        setTimeout(() => {
            // Clear the thinking message and add the real bot response
            clearInterval(thinkingInterval); // Stop flashing dots
            messages.pop(); // Remove the thinking message
            const botResponse = 'This is a response from the bot'; // Placeholder response
            messages.push({ sender: 'bot', text: botResponse });
            displayMessages();

            // Show bot input field after user sends a message
            showBotInput = true;
            document.getElementById('bot-input-section').style.display = 'block'; // Display bot input
        }, 3000); // Simulate a delay of 3 seconds for bot response
    }
}

// Function to display messages in chatbox
function displayMessages() {
    const chatMessagesContainer = document.getElementById('chat-messages');
    chatMessagesContainer.innerHTML = ''; // Clear existing messages

    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', msg.sender);
        messageDiv.textContent = (msg.sender ==='user'? 'You: ' : 'Bot: ')+ msg.text;
        chatMessagesContainer.appendChild(messageDiv);
    });

    // Scroll to the bottom to see the latest messages
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

//++++++++++++++ACTUAL METHODS 

// Step 1: Handle User Input
function handleUserInput() {
    const userInput = document.getElementById('user-input').value;
    if (userInput) {
        // Add user input to chat window
        //addMessageToChat('You: ' + userInput);
        messages.push({ sender: 'user', text: userInput });

        // Add user message to the chat window and clear input field
        displayMessages();
        document.getElementById('user-input').value = '';

        // Show "Bot is thinking..." message and update chat
        messages.push({ sender: 'bot', text: 'Bot is processing...' });
        displayMessages();

        // Simulate LLM processing to detect intent
        fetchIntentFromLLM(userInput).then(intent => {
            // Once the LLM returns, remove the thinking message and add the bot response
            messages.pop(); // Remove the thinking message
            confirmIntentWithUser(intent);
        }).catch(error => {
            messages.pop(); // Remove the thinking message
            messages.push({ sender: 'bot', text: 'Error: ' + error.message });
            displayMessages();
        });      
    }
}

// Step 2: Get the intent from LLM (simulating an API call to LLM)
function fetchIntentFromLLM(input) {
    // Call your LLM here, passing the user input and getting the detected intent
    // Example API call (for OpenAI GPT)
    return fetch('http://127.0.0.1:3030/fetch-intent', {
        method: 'POST',
        body: JSON.stringify({ query: input }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        // LLM returns something like this:
        // { intent: "Show Dependency", Object: "React 1.2.3" }
        return data.intent;
    });
}

// Step 3: Confirm Intent with User (via buttons)
function confirmIntentWithUser(intent) {
    // Show a confirmation message with options to confirm
    let confirmationMessage = `Did you mean: ${intent}?`;
    //addMessageToChat(confirmationMessage);
    messages.push({sender: 'bot', text: confirmationMessage});
    displayMessages();

    // Example buttons to confirm or change intent
    addConfirmationButtons(intent);
}

function addConfirmationButtons() {
    const buttons = [
        { text: "Yes", action: () => showOutput(intent) },
        { text: "No", action: () => askForPromptAgain() }
    ];
    
    buttons.forEach(button => {
        const btn = document.createElement("button");
        btn.textContent = button.text;
        btn.onclick = button.action;
        document.getElementById("chatbox").appendChild(btn);
    });
}

//function added for testing
function showOutput(verified_intent){
    messages.push({sender: 'user', text: 'yes' });
    displayMessages();
    sparq_q = generate_sparql_query(verified_intent);
    const graphArea = document.getElementById("graph-area");
    graphArea.innerHTML = sparq_q ;
}

function generate_sparql_query(input){
    return fetch('http://127.0.0.1:3030/fetch-query', {
        method: 'POST',
        body: JSON.stringify({ query: input }),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        // LLM returns something like this:
        // { SPARQL QUERY STRING)
        return data.sparql;
    });
}

function askForPromptAgain(){
    let botMessage = "Please type what would you like to do?";
    messages.push({sender: 'bot', text: botMessage });
    displayMessages();

}

// Step 4: Generate Graph based on confirmed selection
function generateGraph(type, timeFrame) {
    // Fetch data and generate graph (this is where you'd query your backend)
    fetchDataAndRenderGraph(type, timeFrame)
        .then(graph => {
            // Display graph in designated area
            const graphArea = document.getElementById("graph-area");
            graphArea.innerHTML = `<img src="${graph}" alt="Graph">`;
        });
}

// Simulate data fetching for the graph
function fetchDataAndRenderGraph(type, timeFrame) {
    // Here you'd make an API call to fetch the data and then render it
    return new Promise(resolve => {
        setTimeout(() => {
            // Example: return a link to the appropriate graph image
            resolve(type === "sales" && timeFrame === "lastQuarter" ? "sales-graph.png" : "revenue-graph.png");
        }, 1000);
    });
}

// Function to display messages in chatbox
function displayMessages() {
    const chatMessagesContainer = document.getElementById('chat-messages');
    chatMessagesContainer.innerHTML = ''; // Clear existing messages

    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', msg.sender);
        messageDiv.textContent = (msg.sender ==='user'? 'You: ' : 'Bot: ')+ msg.text;
        chatMessagesContainer.appendChild(messageDiv);
    });

    // Scroll to the bottom to see the latest messages
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}









// Simulate adding messages to chat PLEASE NOTE THESE TWO WILL BE REPLACED BY displayMessages()
function addMessageToChat(message) {
    const chatBox = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to remove the "thinking" message from the chat
function removeThinkingMessage() {
    const chatBox = document.getElementById('chat-messages');
    const messages = chatBox.querySelectorAll('div');
    // Find and remove the last message that says "Bot is thinking..."
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.textContent === 'Bot is thinking...') {
        chatBox.removeChild(lastMessage);
    }
}
