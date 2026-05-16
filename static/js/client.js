function addValue(newValue) {
  const key = "myDataList";
  let currentList = JSON.parse(localStorage.getItem(key)) || [];
  currentList.push(newValue);
  const updatedList = currentList.slice(-5);
  localStorage.setItem(key, JSON.stringify(updatedList));
}
function getArray() {
  const key = "myDataList";
  const data = localStorage.getItem(key);
  return data ? JSON.parse(data) : [];
}
const container = document.getElementById("statusMessages");

function getTime() {
  const now = new Date();
  return now.toLocaleTimeString();
}

function render() {
  container.innerHTML = "";
  const lastFive = getArray();

  lastFive.forEach((msg) => {
    const wrap = document.createElement("div");
    wrap.style.display = "flex";
    wrap.style.flexDirection = "column";
    wrap.style.alignItems = "flex-end";

    const bubble = document.createElement("div");
    bubble.innerText = msg.text;
    bubble.style.background = "#2563eb";
    bubble.style.color = "white";
    bubble.style.padding = "6px 10px";
    bubble.style.borderRadius = "10px";
    bubble.style.borderBottomRightRadius = "3px";
    bubble.style.fontSize = "12px";
    bubble.style.maxWidth = "80%";

    const meta = document.createElement("div");
    meta.style.display = "flex";
    meta.style.gap = "6px";
    meta.style.alignItems = "center";
    meta.style.marginTop = "3px";
    meta.style.fontSize = "10px";

    const time = document.createElement("span");
    time.innerText = msg.time;
    time.style.color = "#9ca3af";

    const status = document.createElement("span");
    status.innerText = msg.status;
    status.style.fontWeight = "500";

    status.style.color = "#22c55e";

    meta.appendChild(time);
    meta.appendChild(status);

    wrap.appendChild(bubble);
    wrap.appendChild(meta);
    container.appendChild(wrap);
  });

  container.scrollTop = container.scrollHeight;
}

const tickContainer = document.getElementById("ticks");
const commandInput = document.querySelector(".command-text");
const responseField = document.getElementById("responseField");

// Generate HUD Ticks
for (let i = 0; i < 100; i++) {
  const tick = document.createElement("div");
  tick.className = "tick";
  tick.style.transform = `rotate(${i * 6}deg)`;
  tickContainer.appendChild(tick);
}

async function sendData() {
  const input = commandInput.value.trim();
  if (!input) return;
  const msgObj = {
    text: input,
    status: "Sent",
    time: getTime(),
  };

  addValue(msgObj);
  // Start Animation
  document.querySelector(".core").classList.add("thinking");
  const statusElement = document.getElementById("speakingStatus");

  statusElement.classList.add("active");
  statusElement.querySelector(".status-text").textContent = "Thinking...";


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

      statusElement.classList.remove("active");
      statusElement.querySelector(".status-text").textContent = "Idle";
      
  }
}

setInterval(render, 100); 

async function fetchStaticSystemInfo() {
  try {
    const response = await fetch("/sys_static");
    const data = await response.text();
    const infoDiv = document.querySelector(".infos");
    infoDiv.innerHTML = `<h2>System Info:</h2><br><pre>${data}</pre>`;
  } catch (error) {
    console.error("Failed to fetch system info:", error);
  }
}

async function fetchAppInfo() {
  try {
    const response = await fetch("/appinfo");
    const data = await response.text();
    const infoDiv = document.querySelector(".infos2");
    infoDiv.innerHTML = `<h2>Application Info:</h2><br><pre>${data}</pre>`;
  } catch (error) {
    console.error("Failed to fetch application info:", error);
  }
}

// Real-time app info updates every 2 seconds
setInterval(fetchAppInfo, 2000);

async function reqQuote() {
  try {
    const response = await fetch("/quote");
    const data = await response.text();
  } catch (error) {
    console.error("Failed to fetch quote:", error);
  }
}

setInterval(reqQuote, 300000);
fetchStaticSystemInfo();
fetchAppInfo();
document.querySelector(".send-btn").addEventListener("click", sendData);

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


async function appUptime() {
  try {
    const response = await fetch("/uptime");
    const data = await response.json(); 
    const infoDiv = document.querySelector(".spinner-text");
    infoDiv.innerHTML = `${Math.floor(data["uptime_seconds"] / 60)} mins`; // Display uptime in minutes
  } catch (error) {
    console.error("Failed to fetch application uptime:", error);
  }
}

appUptime(); 
setInterval(appUptime, 10000);

async function updateDashboard() {
  try {
    const response = await fetch("/dashboard");
    const data = await response.json();
    
    // Update uptime
    const infoDiv = document.querySelector(".spinner-text");
    if (infoDiv) {
      infoDiv.innerHTML = `${Math.floor(data.uptime / 60)} mins`;
    }
    
    // Update speaking status and HUD animation
    // const statusElement = document.getElementById("speakingStatus");
    const hudElement = document.querySelector(".hud");
    const isActive = data.speaking || data.queue_size > 0;


      // if (isActive) {
      //   statusElement.classList.add("active");
      //   statusElement.querySelector(".status-text").textContent = 
      //     data.speaking ? "Speaking..." : `Queued (${data.queue_size})`;
      // } else {
      //   statusElement.classList.remove("active");
      //   statusElement.querySelector(".status-text").textContent = "Idle";
      // }
    
    
    // Toggle HUD animation based on speaking state
    if (hudElement) {
      if (isActive) {
        hudElement.classList.add("speaking");
      } else {
        hudElement.classList.remove("speaking");
      }
    }
  } catch (error) {
    console.error("Failed to fetch dashboard:", error);
  }
}

updateDashboard();
setInterval(updateDashboard, 1000); // Combined call every 1 second instead of 500ms for speaking + 10s for uptime

async function reqCompliment() {
  try {
    const response = await fetch("/compliment");
    const data = await response.text();
  } catch (error) {
    console.error("Failed to fetch system info:", error);
  }
}

setInterval(reqCompliment, 1000 * 60 * 3);