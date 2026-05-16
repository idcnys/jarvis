
      document.addEventListener('DOMContentLoaded', function() {
        const voiceSelect = document.getElementById('voiceSelect');
        if (voiceSelect) {
          voiceSelect.addEventListener('change', function() {
            this.style.background = 'rgba(91, 159, 163, 0.1)';
          });
          voiceSelect.addEventListener('focus', function() {
            this.style.background = 'rgba(91, 159, 163, 0.1)';
            this.style.borderColor = '#5b9fa3';
            this.style.boxShadow = '0 0 10px rgba(91, 159, 163, 0.2)';
          });
          voiceSelect.addEventListener('blur', function() {
            this.style.background = 'rgba(91, 159, 163, 0.05)';
          });
        }
      });

      function clearHistory() {
        if (confirm("Are you sure you want to clear all history? This cannot be undone.")) {

          fetch("/clear_history", {
            method: "POST"
          })
            .then((response) => {
              if (response.ok) {
                alert("History cleared successfully!");
              }
            })
            .catch((error) => console.error("Error:", error));
        }
      }

      window.addEventListener('load', function() {
        const params = new URLSearchParams(window.location.search);
        const msg = params.get('msg');
        if (msg) {
          alert(decodeURIComponent(msg));
          // Clean up URL
          window.history.replaceState({}, document.title, '/settings');
        }
      });