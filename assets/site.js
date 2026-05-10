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
})();
