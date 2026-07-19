(() => {
  const STOP = new Set([
    "من", "في", "على", "إلى", "الى", "عن", "مع", "هذا", "هذه", "ما", "ماذا",
    "كيف", "هل", "و", "أو", "او", "أن", "ان", "التي", "الذي", "أريد", "اريد",
  ]);

  let seed = { articles: [], domains: [] };
  let authed = sessionStorage.getItem("nadee_auth") === "1";

  const loginView = document.getElementById("login-view");
  const appShell = document.getElementById("app-shell");
  const page = document.getElementById("page");

  function normalize(text) {
    return text
      .trim()
      .toLowerCase()
      .replace(/[إأآا]/g, "ا")
      .replace(/ى/g, "ي")
      .replace(/ة/g, "ه")
      .replace(/[^\w\s\u0600-\u06FF]/g, " ")
      .replace(/\s+/g, " ");
  }

  function stem(token) {
    if (token.startsWith("ال") && token.length > 4) token = token.slice(2);
    const map = {
      اسجل: "تسجيل",
      مجالات: "مجال",
      مجال: "مجال",
      معايير: "معيار",
      مرفقات: "مرفق",
      نضي: "نضيء",
    };
    return map[token] || token;
  }

  function tokenize(text) {
    return new Set(
      normalize(text)
        .split(" ")
        .filter((t) => t.length > 1 && !STOP.has(t))
        .map(stem)
    );
  }

  function answerQuestion(question) {
    const q = tokenize(question);
    let best = null;
    let bestScore = 0;
    for (const article of seed.articles) {
      const hay = tokenize(
        `${article.title} ${article.content} ${article.keywords || ""}`
      );
      const overlap = [...q].filter((t) => hay.has(t));
      if (!overlap.length) continue;
      const generic = new Set(["نضيء", "منصه", "بيانات", "سدايا"]);
      const distinctive = overlap.filter((t) => !generic.has(t));
      const score =
        (overlap.length / Math.max(q.size, 1)) * 0.55 +
        distinctive.length * 0.55 +
        ([...tokenize(article.title)].filter((t) => q.has(t)).length) * 0.25 +
        ([...tokenize(article.keywords || "")].filter((t) => q.has(t)).length) *
          0.4;
      if (score > bestScore) {
        bestScore = score;
        best = article;
      }
    }
    if (!best || bestScore < 0.35) {
      return "لم أجد إجابة مباشرة. جرّب: عناصر المؤشر، مجالات نضيء، مستويات النضج، أو جودة البيانات.";
    }
    return `**${best.title}**\n\n${best.content}\n\n— المصدر: ${best.source}`;
  }

  function maturityLabel(score) {
    if (score < 1) return "غير مطبّق";
    if (score < 2) return "مبتدئ";
    if (score < 3) return "نامٍ";
    if (score < 4) return "متوسط";
    if (score < 5) return "متقدم";
    return "متميز";
  }

  function setAuth(on) {
    authed = on;
    sessionStorage.setItem("nadee_auth", on ? "1" : "0");
    loginView.classList.toggle("hidden", on);
    appShell.classList.toggle("hidden", !on);
    if (on) route();
  }

  function navActive(name) {
    document.querySelectorAll("[data-nav]").forEach((a) => {
      a.classList.toggle("active", a.dataset.nav === name);
    });
  }

  function renderHome() {
    navActive("home");
    const avg =
      seed.domains.reduce((s, d) => s + (d.maturity_score || 0), 0) /
      Math.max(seed.domains.length, 1);
    page.innerHTML = `
      <section class="hero">
        <div class="shell" style="padding-top:0;padding-bottom:0;width:min(1180px,92vw);">
          <p class="hero-brand">مساعد نضيء الذكي</p>
          <h2>المؤشر الوطني للبيانات — دورة القياس الثالثة</h2>
          <p>نسخة الاستعراض على GitHub Pages. اسأل المساعد عن المجالات والمعايير ومستويات النضج.</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="#chat">ابدأ المحادثة</a>
            <a class="btn btn-ghost" href="#analytics">تحليل نضج المجالات</a>
          </div>
        </div>
      </section>
      <div class="shell">
        <section class="section">
          <div class="section-head">
            <h2>عناصر المؤشر</h2>
            <p>ثلاثة عناصر رئيسية وفق دليل دورة القياس الثالثة.</p>
          </div>
          <div class="elements-grid">
            <article class="element-card maturity"><header>قياس نضج الممارسات</header><div class="body">14 مجالاً لإدارة البيانات.</div><footer>42 معياراً</footer></article>
            <article class="element-card compliance"><header>قياس الامتثال</header><div class="body">ضوابط ومواصفات إدارة البيانات وحماية البيانات الشخصية.</div><footer>191 مواصفة</footer></article>
            <article class="element-card ops"><header>قياس التميز التشغيلي</header><div class="body">متابعة التقدم التشغيلي المرتبط بالبيانات.</div><footer>22 معياراً</footer></article>
          </div>
        </section>
        <section class="section">
          <div class="metric-strip">
            <div class="metric"><strong>${seed.articles.length}</strong><span>مادة معرفية</span></div>
            <div class="metric"><strong>${seed.domains.length}</strong><span>مجال إدارة بيانات</span></div>
            <div class="metric"><strong>${avg.toFixed(2)}</strong><span>متوسط النضج</span></div>
          </div>
        </section>
      </div>`;
  }

  function renderChat() {
    navActive("chat");
    page.className = "shell";
    page.innerHTML = `
      <div class="chat-layout">
        <aside class="chat-side">
          <h3>أسئلة مقترحة</h3>
          <div class="chip-list" id="suggests">
            <button type="button" class="chip" data-q="ما هو المؤشر الوطني للبيانات نضيء؟">ما هو نضيء؟</button>
            <button type="button" class="chip" data-q="ما هي عناصر المؤشر الوطني للبيانات نضيء؟">عناصر المؤشر</button>
            <button type="button" class="chip" data-q="كم عدد مجالات ومعايير نضج إدارة البيانات في نضيء؟">المجالات والمعايير</button>
            <button type="button" class="chip" data-q="ما هي مستويات النضج الستة في مؤشر نضيء؟">مستويات النضج</button>
            <button type="button" class="chip" data-q="مجال جودة البيانات">جودة البيانات</button>
          </div>
        </aside>
        <section class="chat-main">
          <div class="chat-toolbar">
            <h1>المساعد الذكي</h1>
            <p>يعمل محلياً في المتصفح من قاعدة معرفة نضيء</p>
          </div>
          <div class="messages" id="messages">
            <div class="bubble assistant">مرحباً، اسألني عن نضيء: المجالات، المعايير، أو الوثائق الداعمة.</div>
          </div>
          <form class="composer" id="chat-form">
            <input class="chat-input" id="chat-input" placeholder="اكتب سؤالك..." required>
            <button class="btn btn-primary" type="submit">إرسال</button>
          </form>
        </section>
      </div>`;

    const messages = document.getElementById("messages");
    const input = document.getElementById("chat-input");
    const add = (role, text) => {
      const div = document.createElement("div");
      div.className = `bubble ${role}`;
      div.textContent = text.replace(/\*\*(.*?)\*\*/g, "$1");
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    };

    document.getElementById("chat-form").addEventListener("submit", (e) => {
      e.preventDefault();
      const q = input.value.trim();
      if (!q) return;
      add("user", q);
      input.value = "";
      add("assistant", answerQuestion(q));
    });

    document.querySelectorAll("#suggests [data-q]").forEach((btn) => {
      btn.addEventListener("click", () => {
        input.value = btn.dataset.q;
        input.focus();
      });
    });
  }

  function renderKnowledge() {
    navActive("knowledge");
    page.className = "shell";
    const rows = seed.articles
      .map(
        (a, i) => `
      <a class="article-row" href="#knowledge/${i}">
        <h3>${a.title}</h3>
        <p class="meta">${a.category} · ${a.source}</p>
      </a>`
      )
      .join("");
    page.innerHTML = `
      <section class="section">
        <div class="section-head">
          <h2>قاعدة المعرفة</h2>
          <p>محتوى مستمد من دليل المؤشر الوطني للبيانات (نضيء).</p>
        </div>
        <div class="article-list">${rows}</div>
      </section>`;
  }

  function renderKnowledgeDetail(index) {
    navActive("knowledge");
    page.className = "shell";
    const a = seed.articles[index];
    if (!a) return renderKnowledge();
    page.innerHTML = `
      <section class="section">
        <a class="meta" href="#knowledge">← العودة</a>
        <div class="panel" style="margin-top:1rem;">
          <span class="tag">${a.category}</span>
          <h1 style="font-family:var(--font-display);margin:0.7rem 0;color:var(--navy);">${a.title}</h1>
          <p class="meta">المصدر: ${a.source}</p>
          <div style="margin-top:1.2rem;line-height:1.9;white-space:pre-wrap;">${a.content}</div>
        </div>
      </section>`;
  }

  function renderAnalytics() {
    navActive("analytics");
    page.className = "shell";
    const total = seed.domains.reduce((s, d) => s + (d.criteria_count || 0), 0);
    const avg =
      seed.domains.reduce((s, d) => s + (d.maturity_score || 0), 0) /
      Math.max(seed.domains.length, 1);
    const rows = seed.domains
      .map((d, i) => {
        const pct = Math.round(((d.maturity_score || 0) / 5) * 100);
        return `<tr>
          <td>${i + 1}</td>
          <td>${d.name}</td>
          <td>${d.pillar || ""}</td>
          <td>${d.criteria_count}</td>
          <td><div style="display:flex;align-items:center;gap:0.55rem;"><span>${d.maturity_score}</span><div class="bar"><span style="width:${pct}%"></span></div></div></td>
          <td><span class="tag">${maturityLabel(d.maturity_score || 0)}</span></td>
        </tr>`;
      })
      .join("");
    page.innerHTML = `
      <section class="section">
        <div class="section-head">
          <h2>تحليل أداء إدارة البيانات — نضيء</h2>
          <p>مجالات قياس نضج الممارسات الأربعة عشر.</p>
        </div>
        <div class="metric-strip" style="margin-bottom:1.2rem;">
          <div class="metric"><strong>${avg.toFixed(2)}</strong><span>متوسط النضج</span></div>
          <div class="metric"><strong>${total}</strong><span>إجمالي المعايير</span></div>
          <div class="metric"><strong>${seed.domains.length}</strong><span>عدد المجالات</span></div>
        </div>
        <div class="panel" style="overflow-x:auto;">
          <table class="domains-table">
            <thead><tr><th>#</th><th>المجال</th><th>الركيزة</th><th>المعايير</th><th>النضج</th><th>المستوى</th></tr></thead>
            <tbody>${rows}</tbody>
            <tfoot><tr><td colspan="3">المجموع</td><td>${total}</td><td colspan="2">${avg.toFixed(2)} متوسط النضج</td></tr></tfoot>
          </table>
        </div>
      </section>`;
  }

  function renderAbout() {
    navActive("about");
    page.className = "shell";
    page.innerHTML = `
      <section class="section">
        <div class="section-head">
          <h2>عن المنصة</h2>
          <p>مساعد نضيء الذكي — نظام داخلي لمنسوبي أمانة المنطقة ضمن إدارة البيانات.</p>
        </div>
        <div class="panel">
          <p class="meta" style="line-height:1.85;">
            هذه نسخة استعراض على GitHub Pages بنفس التصميم وقاعدة معرفة نضيء.
            النسخة الكاملة بـ Django متوفرة في المستودع للتشغيل المحلي.
          </p>
        </div>
        <p class="footer-note">المؤشر الوطني للبيانات (نضيء) — دورة القياس الثالثة / سدايا</p>
      </section>`;
  }

  function route() {
    if (!authed) return;
    const hash = (location.hash || "#home").slice(1);
    page.className = "";
    if (hash.startsWith("knowledge/")) {
      renderKnowledgeDetail(Number(hash.split("/")[1]));
      return;
    }
    const map = {
      home: renderHome,
      chat: renderChat,
      knowledge: renderKnowledge,
      analytics: renderAnalytics,
      about: renderAbout,
    };
    (map[hash] || renderHome)();
  }

  document.getElementById("login-form").addEventListener("submit", (e) => {
    e.preventDefault();
    setAuth(true);
    location.hash = "#home";
  });

  document.getElementById("logout-btn").addEventListener("click", () => {
    setAuth(false);
    location.hash = "";
  });

  window.addEventListener("hashchange", route);

  fetch("./data/nadee_seed.json")
    .then((r) => r.json())
    .then((data) => {
      seed = data;
      setAuth(authed);
      if (authed) route();
    })
    .catch(() => {
      alert("تعذر تحميل بيانات نضيء.");
    });
})();
