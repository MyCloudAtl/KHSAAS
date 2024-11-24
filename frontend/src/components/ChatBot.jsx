import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css'; // Import the CSS file for styling

//TODs:
//1. fix auto-scroll down effect. Not working currently when messages are exchanged


// Simulate LLM intent fetching
const fetchIntentFromLLM = async (input) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/get_intent', {
        method: 'POST',
        body: JSON.stringify({ query: input }),
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      return data.intent;  // Return the intent
    } catch (error) {
      console.error('Error fetching intent:', error);
      throw error;  // Re-throw or handle the error as needed
    }
  };

// Async function to process user query and fetch sparql query
const processUserQuery = async (input) => {
  try {
    console.log('Sending query to server:', input); // Log the input query

    const response = await fetch('http://127.0.0.1:5000/process_query', {
        method: 'POST',
        body: JSON.stringify({ query: input }),
        headers: { 'Content-Type': 'application/json' },
    });

    console.log('Received raw response:', response); // Log the raw fetch response object

    if (!response.ok) {
        // Log error details if the response isn't successful
        console.error('Server responded with an error:', response.status, response.statusText);
        throw new Error(`Server Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json(); // Parse JSON
    console.log('Parsed JSON data:', data); // Log the parsed JSON data
    return data; // Return the SPARQL query results

} catch (error) {
    console.error('Error processing user query:', error); // Log any errors that occur
    throw error; // Re-throw or handle the error as needed
}
};

const ChatBot = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([
    { sender: 'Bot', text: "Welcome, what would you like to know?", type: 'text' },
  ]);
  const [graphData, setGraphData] = useState(null);
  const [visibleResults, setVisibleResults] = useState(10); // Default to show 10 results
  const [visibleVulnerabilities, setVisibleVulnerabilities] = useState(10); // Default to show 10 vulnerabilities

  // Note text
  const noteText = "Note: Currently I'm only programmed to answer dependencies and vulnerabilities for softwares given software name and version.";

  const handleGoHomepage = () => {
    window.location.href = '/'; // Redirect to homepage
  };

  // Handle user input change
  const handleUserInput = (event) => {
    setUserInput(event.target.value);
  };


  // Send message function
  const handleSendMessage = () => {
    if (userInput.trim()) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'You', text: userInput, type: 'text' },
      ]);

      setUserInput('');

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'Bot', text: 'Bot is processing...', type: 'text' },
      ]);

      fetchIntentFromLLM(userInput)
        .then((intent) => {
          setMessages((prevMessages) => prevMessages.slice(0, -1));
          confirmIntentWithUser(intent);
        })
        .catch((error) => {
          setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'Bot', text: `Error: ${error.message}`, type: 'text' },
          ]);
        });
    }
  };

  // Confirm intent with user
  const confirmIntentWithUser = (intent) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'Bot', text: `${intent}`, type: 'text' },
      { sender: 'Bot', type: 'buttons', intent },
    ]);
  };

  // Handle confirmation for Yes or No
  const handleConfirmation = (response, intent = null) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'You', text: response, type: 'text' },
    ]);
    // Remove the buttons message
  setMessages((prevMessages) =>
    prevMessages.filter((msg) => msg.type !== 'buttons')
  );
    if (response === 'Yes' && intent) {
      showOutput(intent);
    } else if (response === 'No') {
      askForPromptAgain();
    }
  };

  // Show output after confirmation
  const showOutput = (verifiedIntent) => {
    processUserQuery(verifiedIntent)
      .then((results) => {
        setGraphData(results);
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'Bot', text: 'See the results displayed in Right Window', type: 'text' },
        ]);
      })
      .catch((error) => {
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'Bot', text: `Error: ${error.message}`, type: 'text' },
        ]);
      });
  };

  // Ask user to type more clearly
  const askForPromptAgain = () => {
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        sender: 'Bot',
        text: "I couldn't understand your request. Please type more clearly.",
        type: 'text',
      },
    ]);
  };

  // Render the chat messages
  const renderMessages = () => {
    return messages.map((message, index) => {
      if (message.type === 'buttons') {
        return (
          <div key={index} className="message bot">
            <button
              className="chat-button"
              onClick={() => handleConfirmation('Yes', message.intent)}
            >
              Yes
            </button>
            <button
              className="chat-button"
              onClick={() => handleConfirmation('No')}
            >
              No
            </button>
          </div>
        );
      }
      return (
        <div key={index} className={`message ${message.sender.toLowerCase()}`}>
          {message.sender}: {message.text}
        </div>
      );
    });
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="main-container">
      
    {/* Note container positioned above the chat container */}
    <div className="note-container">
    <button className="go-homepage-btn" onClick={handleGoHomepage}>
        Go Back To Homepage
      </button> 
      <p>{noteText}</p>
    </div>
    <div className="container">
   
      <div className="chatbox">
      
        <div className="chat-messages">{renderMessages()}</div>
        <div className="user-input-section">
          <textarea
            value={userInput}
            onChange={handleUserInput}
            onKeyDown={handleKeyPress}
            placeholder="Type your response here..."
            rows="3"
          ></textarea>
          <button onClick={handleSendMessage}>Send</button>
        </div>
        </div>
      
     
        <div className="graph-area">
  {graphData ? (
    <div>
      {/* Display results title */}
      {graphData.results_title && <h3>{graphData.results_title}</h3>}

      {/* Render the response dynamically */}
      {graphData.sparql_result ? (
        <pre>{JSON.stringify(graphData.sparql_result, null, 2)}</pre> // Pretty-print the raw data
      ) : (
        <p>No results available.</p>
      )}
    </div>
  ) : (
    <p>No results available.</p>
  )}
</div>

    </div>
    </div>
  );
};

export default ChatBot;