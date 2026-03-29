(() => {
  const root = document.documentElement;
  const storedTheme = localStorage.getItem("aria-site-theme");
  if (storedTheme === "light") {
    root.setAttribute("data-theme", "light");
  }

  const menuToggle = document.getElementById("menuToggle");
  const primaryNav = document.getElementById("primaryNav");
  const themeToggle = document.getElementById("themeToggle");
  const year = document.getElementById("year");

  if (year) year.textContent = String(new Date().getFullYear());

  if (menuToggle && primaryNav) {
    menuToggle.addEventListener("click", () => {
      const isOpen = primaryNav.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const isLight = root.getAttribute("data-theme") === "light";
      if (isLight) {
        root.removeAttribute("data-theme");
        localStorage.setItem("aria-site-theme", "dark");
      } else {
        root.setAttribute("data-theme", "light");
        localStorage.setItem("aria-site-theme", "light");
      }
    });
  }

  const estimateForm = document.getElementById("estimateForm");
  const estimateResult = document.getElementById("estimateResult");
  if (estimateForm && estimateResult) {
    estimateForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const teamSize = Number(document.getElementById("teamSize")?.value || 0);
      const depth = document.getElementById("featureDepth")?.value || "growth";

      const depthMultiplier = depth === "starter" ? 1 : depth === "advanced" ? 2.2 : 1.5;
      const score = Math.max(1, Math.round(teamSize * depthMultiplier));
      const timeline = score < 8 ? "2–4 weeks" : score < 18 ? "4–8 weeks" : "8–12+ weeks";

      estimateResult.textContent = `Estimated complexity score: ${score}. Suggested initial timeline: ${timeline}.`;
    });
  }

  const contactForm = document.getElementById("contactForm");
  const formStatus = document.getElementById("formStatus");

  if (contactForm && formStatus) {
    contactForm.addEventListener("submit", (event) => {
      event.preventDefault();

      const name = String(document.getElementById("name")?.value || "").trim();
      const email = String(document.getElementById("email")?.value || "").trim();
      const message = String(document.getElementById("message")?.value || "").trim();

      if (!name || !email || !message) {
        formStatus.textContent = "Please fill out all fields before submitting.";
        return;
      }

      const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      if (!validEmail) {
        formStatus.textContent = "Please enter a valid email address.";
        return;
      }

      formStatus.textContent = "Thanks! Your message has been captured locally for demo purposes.";
      contactForm.reset();
    });
  }
})();
