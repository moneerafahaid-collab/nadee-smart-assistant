(function () {
  const form = document.getElementById("chat-form");
  if (!form) return;

  const input = document.getElementById("chat-input");
  const messages = document.getElementById("messages");
  const sessionInput = document.getElementById("session-id");
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;

  function appendBubble(role, text) {
    const div = document.createElement("div");
    div.className = `bubble ${role}`;
    div.textContent = text.replace(/\*\*(.*?)\*\*/g, "$1");
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    appendBubble("user", text);
    input.value = "";
    input.disabled = true;

    try {
      const response = await fetch(form.dataset.url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf,
        },
        body: JSON.stringify({
          message: text,
          session_id: sessionInput.value || null,
        }),
      });
      const data = await response.json();
      if (!data.ok) {
        appendBubble("assistant", data.error || "حدث خطأ غير متوقع.");
      } else {
        sessionInput.value = data.session_id;
        appendBubble("assistant", data.assistant_message);
      }
    } catch (error) {
      appendBubble("assistant", "تعذر الاتصال بالخادم. حاول مرة أخرى.");
    } finally {
      input.disabled = false;
      input.focus();
    }
  });

  document.querySelectorAll("[data-suggest]").forEach((btn) => {
    btn.addEventListener("click", () => {
      input.value = btn.dataset.suggest;
      input.focus();
    });
  });
})();
