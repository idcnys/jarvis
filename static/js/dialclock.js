(function () {
  const wrapper = document.querySelector(".my-clock-wrapper");

  const secCircle = wrapper.querySelector(".my-sec-progress");
  const monthCircle = wrapper.querySelector(".my-month-progress");
  const timeEl = wrapper.querySelector(".my-clock-time");
  const monthYearEl = wrapper.querySelector(".my-month-year");
  const monthEl = monthYearEl.querySelector(".my-month");
  const yearEl = monthYearEl.querySelector(".my-year");

  const secRadius = 70;
  const monthRadius = 100;
  const secCircumference = 2 * Math.PI * secRadius;
  const monthCircumference = 2 * Math.PI * monthRadius;

  secCircle.style.strokeDasharray = secCircumference;
  monthCircle.style.strokeDasharray = monthCircumference;

  function updateClock() {
    const now = new Date();

    // Center HH:MM
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    timeEl.querySelector(".my-hhmm").textContent = `${hours}:${minutes}`;

    // Date and Day
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const day = days[now.getDay()];
    const date = now.getDate();
    timeEl.querySelector(".my-date").textContent = `${day} ${date}`;

    // Month / Year
    const monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    const month = now.getMonth(); // 0-11
    const year = now.getFullYear();
    monthEl.textContent = monthNames[month];
    yearEl.textContent = year;

    // Seconds Progress
    const seconds = now.getSeconds() + now.getMilliseconds() / 1000;
    const secOffset = secCircumference - (seconds / 60) * secCircumference;
    secCircle.style.strokeDashoffset = secOffset;

    // Month Progress
    const totalDays = new Date(year, month + 1, 0).getDate();
    const dayOfMonth =
      now.getDate() -
      1 +
      (hours * 3600 + now.getMinutes() * 60 + now.getSeconds()) / (24 * 3600);
    const monthOffset =
      monthCircumference - (dayOfMonth / totalDays) * monthCircumference;
    monthCircle.style.strokeDashoffset = monthOffset;

    requestAnimationFrame(updateClock);
  }

  requestAnimationFrame(updateClock);
})();
