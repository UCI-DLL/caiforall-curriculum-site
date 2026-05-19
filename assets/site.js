(() => {
  function activateUnit(browser, targetId, updateHash) {
    const tabs = Array.from(browser.querySelectorAll(".unit-tab"));
    const panels = Array.from(browser.querySelectorAll(".unit-panel"));
    const targetPanel = panels.find((panel) => panel.id === targetId) || panels[0];

    if (!targetPanel) return;

    tabs.forEach((tab) => {
      const isActive = tab.dataset.unitTarget === targetPanel.id;
      tab.classList.toggle("active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
    });

    panels.forEach((panel) => {
      const isActive = panel === targetPanel;
      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });

    if (updateHash && history.replaceState) {
      history.replaceState(null, "", `#${targetPanel.id}`);
    }
  }

  document.querySelectorAll("[data-unit-browser]").forEach((browser) => {
    const tabs = browser.querySelectorAll(".unit-tab");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        activateUnit(browser, tab.dataset.unitTarget, true);
      });
    });

    if (location.hash) {
      const requested = location.hash.slice(1);
      const hasRequestedPanel = Array.from(browser.querySelectorAll(".unit-panel")).some((panel) => panel.id === requested);
      if (hasRequestedPanel) {
        activateUnit(browser, requested, false);
      }
    }
  });

  document.querySelectorAll("[data-google-form]").forEach((form) => {
    const status = form.querySelector(".form-status");
    form.addEventListener("submit", (event) => {
      const missingGroup = Array.from(form.querySelectorAll("[data-required-group]")).find((group) => {
        return !group.querySelector("input[type='checkbox']:checked");
      });

      if (missingGroup) {
        event.preventDefault();
        const legend = missingGroup.querySelector("legend");
        if (status) {
          status.textContent = `Please select at least one option for ${legend ? legend.textContent : "each required section"}.`;
          status.classList.add("error");
        }
        missingGroup.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }

      if (status) {
        status.textContent = form.classList.contains("contact-form")
          ? "Thank you. Your message has been submitted."
          : "Thank you. Your interest form has been submitted.";
        status.classList.remove("error");
      }
      window.setTimeout(() => form.reset(), 700);
    });
  });

  document.querySelectorAll("[data-contact-form]").forEach((form) => {
    const status = form.querySelector(".form-status");
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(form);
      const recipient = form.dataset.contactEmail || "ECforALL@uci.edu";
      const name = data.get("name") || "";
      const email = data.get("email") || "";
      const curriculum = data.get("curriculum") || "";
      const unitLesson = data.get("unitLesson") || "";
      const message = data.get("message") || "";
      const subject = `CAIforAll Website Contact: ${curriculum || "General"}`;
      const body = [
        `Name: ${name}`,
        `Email: ${email}`,
        `Related Curriculum: ${curriculum}`,
        `Unit & Lesson: ${unitLesson || "N/A"}`,
        "",
        "Message:",
        message,
      ].join("\n");

      window.location.href = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      if (status) {
        status.textContent = "Opening your email app with this message.";
        status.classList.remove("error");
      }
    });
  });
})();
