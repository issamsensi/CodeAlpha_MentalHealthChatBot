const form = document.getElementById("chatForm");
const questionInput = document.getElementById("question");
const chatWindow = document.getElementById("chatWindow");
const sendBtn = document.getElementById("sendBtn");
const statusText = document.getElementById("statusText");

function appendMessage(text, sender, confidence) {
  const article = document.createElement("article");
  article.className = `message ${sender === "user" ? "message-user" : "message-bot"}`;

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.appendChild(paragraph);

  if (sender === "bot" && typeof confidence === "number") {
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `Confidence: ${confidence.toFixed(3)}`;
    article.appendChild(meta);
  }

  chatWindow.appendChild(article);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function askBot(question) {
  const response = await fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();

  if (!question) {
    return;
  }

  appendMessage(question, "user");
  questionInput.value = "";
  questionInput.focus();
  sendBtn.disabled = true;
  statusText.textContent = "MindCare is thinking...";

  try {
    const data = await askBot(question);
    appendMessage(data.answer, "bot", data.confidence);
    statusText.textContent = "";
  } catch (error) {
    appendMessage("Sorry, I could not process that. Please try again.", "bot");
    statusText.textContent = error.message;
  } finally {
    sendBtn.disabled = false;
  }
});

chatWindow.scrollTop = chatWindow.scrollHeight;
