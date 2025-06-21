const API_KEY = "YOUR_HUGGINGFACE_API";  // <-- Replace this with your Hugging Face API key
const MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1";

const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");

async function sendMessage() {
  const userMessage = inputField.value.trim();
  if (!userMessage) return;

  appendMessage("You", userMessage, "user");
  inputField.value = "";

  appendMessage("Bot", "Typing...", "bot", true);

  try {
    const response = await fetch(`https://api-inference.huggingface.co/models/${MODEL}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        inputs: `User: ${userMessage}\nBot:`,
        parameters: { max_new_tokens: 100, temperature: 0.7, return_full_text: true }
      })
    });

    const data = await response.json();

    // Remove the "Typing..." message
    const tempTyping = document.querySelector(".bot.typing");
    if (tempTyping) tempTyping.remove();

    if (data.error) {
      appendMessage("Bot", `Error: ${data.error}`, "bot");
      return;
    }

    let botReply = "Sorry, I couldn't understand that.";
    if (data.generated_text) {
      const splitText = data.generated_text.split("Bot:");
      botReply = splitText.length > 1 ? splitText[1].trim() : data.generated_text.trim();
    }

    appendMessage("Bot", botReply, "bot");
  } catch (error) {
    // Remove the "Typing..." message
    const tempTyping = document.querySelector(".bot.typing");
    if (tempTyping) tempTyping.remove();

    appendMessage("Bot", "An error occurred. Please try again.", "bot");
    console.error(error);
  }
}

function appendMessage(sender, message, className, isTyping = false) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", className);
  if (isTyping) messageDiv.classList.add("typing");
  messageDiv.innerText = message;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Also allow pressing Enter to send message
inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});
