const tickContainer = document.getElementById("ticks");
const commandInput = document.querySelector(".command-text");
const responseField = document.getElementById("responseField");

// Generate HUD Ticks
for (let i = 0; i < 60; i++) {
  const tick = document.createElement("div");
  tick.className = "tick";
  tick.style.transform = `rotate(${i * 6}deg)`;
  tickContainer.appendChild(tick);
}

async function sendData() {
  const input = commandInput.value.trim();
  if (!input) return;

  // Start Animation
  document.querySelector(".core").classList.add("thinking");
  responseField.innerText = "Processing command...";
  commandInput.value = "";

  try {
    const response = await fetch("/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text_input: input }),
    });

    // CHECK IF RESPONSE IS OK BEFORE PARSING
    if (!response.ok) {
      const errorText = await response.text();
      responseField.innerText = "Server Error: " + response.status;
      console.error("Server sent back HTML instead of JSON:", errorText);
      return;
    }

    const result = await response.json();
    const outputText = result.output;

    // Update UI
    responseField.innerText = outputText;
  } catch (error) {
    responseField.innerText = "Error: Could not connect to core.";
    console.error(error);
  } finally {
    // Stop Animation
    document.querySelector(".core").classList.remove("thinking");
  }
}

async function reqQuote() {
  try {
    const response = await fetch("/quote");
    const data = await response.text();
  } catch (error) {
    console.error("Failed to fetch system info:", error);
  }
}

setInterval(reqQuote, 300000); // Fetch a new quote every 60 seconds
// Click listener
document.querySelector(".send-btn").addEventListener("click", sendData);

// Optional: Enter key to send (Shift+Enter for new line)
commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendData();
  }
});

window.addEventListener("dblclick", async () => {
  try {
    const response = await fetch("/ruhere");
    const data = await response.text();
  } catch (error) {
    console.error("Failed to fetch system info:", error);
  }
});

window.addEventListener("load", async () => {
  let isalready = localStorage.getItem("isalready");
  if (!isalready) {
    localStorage.setItem("isalready", "true");

    try {
      const response = await fetch("/greet");
      const data = await response.text();
    } catch (error) {
      console.error("Failed to fetch system info:", error);
    }
  }
});
