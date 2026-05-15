function createSmallCircle(id, label, tooltip) {
  document.getElementById(id).innerHTML = `
  <div title="${tooltip}"
       style="display:flex;flex-direction:column;align-items:center;">
       
    <div style="width:80px;height:80px;position:relative;">
      <svg width="80" height="80">
        <circle cx="40" cy="40" r="32"
          style="fill:none;stroke:#444444;stroke-width:7;" />

        <circle id="${id}Circle" cx="40" cy="40" r="32"
          style="
            fill:none;
            stroke:#7feaea;
            stroke-width:7;
            stroke-linecap:round;
            transform:rotate(-90deg);
            transform-origin:50% 50%;
            stroke-dasharray:201;
            stroke-dashoffset:201;
            transition:.4s;
          " />
      </svg>

      <div id="${id}Text"
        style="position:absolute;top:50%;left:50%;
        transform:translate(-50%,-50%);
        font-size:12px;font-weight:600;">
        0%
      </div>
    </div>

    <div style="margin-top:6px;font-size:13px;font-weight:600;">
      ${label}
    </div>
  </div>`;
}

createSmallCircle("memBox", "Memory", "Memory (RAM) Usage");
createSmallCircle("swapBox", "Swap", "Swap Memory Usage");
createSmallCircle("batBox", "Battery", "Battery Level");

function setSmall(id, value) {
  const circle = document.getElementById(id + "Circle");
  const text = document.getElementById(id + "Text");

  const r = 32;
  const c = 2 * Math.PI * r;
  circle.style.strokeDashoffset = c - (value / 100) * c;
  text.innerText = Math.round(value) + "%";

  circle.style.stroke = "#7feaea";
}

function setCPU(value) {
  const circle = document.getElementById("cpuCircle");
  const center = document.getElementById("cpuCenter");
  const bottom = document.getElementById("cpuBottom");

  const r = 32;
  const c = 2 * Math.PI * r;
  circle.style.strokeDashoffset = c - (value / 100) * c;

  circle.style.stroke = "#7feaea";

  if (value < 70) {
    center.innerText = "CPU";
    bottom.innerText = Math.round(value) + "%";
  } else {
    center.innerText = Math.round(value) + "%";
    bottom.innerText = "";
  }
}

async function getUtilityData() {
  try {
    const res = await fetch("/utility");
    const data = await res.json();
    setCPU(data.cpu);
    setSmall("memBox", data.memory);
    setSmall("swapBox", data.swap);
    setSmall("batBox", data.battery);
  } catch (e) {
    console.log("Utility data fetch error");
  }
}
setInterval(getUtilityData, 1000);
