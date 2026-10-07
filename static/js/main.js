(() => {
  const menuButton = document.getElementById("btnMenu");
  const menuPanel = document.getElementById("panelMenu");
  const menuBackdrop = document.getElementById("menuBackdrop");
  const mainContent = document.querySelector("main");
  const mobileBreakpoint = window.matchMedia("(max-width: 1024px)");

  function isMobile() {
    return mobileBreakpoint.matches;
  }

  function setMenuOpen(open, returnFocus = false, focusMenu = false) {
    const mobile = isMobile();
    const expanded = open;

    menuPanel.classList.toggle("abierto", expanded);
    menuPanel.classList.toggle("colapsado", !expanded);
    menuPanel.inert = !expanded;
    menuPanel.setAttribute("aria-hidden", String(!expanded));
    menuBackdrop.hidden = !mobile || !expanded;
    mainContent.inert = mobile && expanded;
    menuButton.setAttribute("aria-expanded", String(expanded));
    menuButton.setAttribute(
      "aria-label",
      expanded ? "Cerrar menú" : "Abrir menú"
    );
    document.body.classList.toggle("menu-abierto", mobile && expanded);
    document.body.classList.toggle("menu-colapsado", !expanded);

    if (expanded && focusMenu) {
      menuPanel.querySelector(".menu-brand").focus();
    } else if (returnFocus) {
      menuButton.focus();
    }
  }

  menuButton.addEventListener("click", () => {
    const currentlyOpen = menuButton.getAttribute("aria-expanded") === "true";
    setMenuOpen(!currentlyOpen, currentlyOpen, !currentlyOpen);
  });

  menuBackdrop.addEventListener("click", () => setMenuOpen(false, true));

  menuPanel.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (isMobile()) setMenuOpen(false);
    });
  });

  document.addEventListener("keydown", (event) => {
    if (menuButton.getAttribute("aria-expanded") !== "true") {
      return;
    }

    if (event.key === "Escape") {
      setMenuOpen(false, true);
      return;
    }

    if (!isMobile() || event.key !== "Tab") return;

    const focusableElements = [...menuPanel.querySelectorAll("a[href], summary")]
      .filter((element) => {
        const closedDetails = element.closest("details:not([open])");
        const isVisibleSummary =
          element.matches("summary") && element.parentElement === closedDetails;

        return (
          (!closedDetails || isVisibleSummary) &&
          getComputedStyle(element).visibility === "visible" &&
          element.getClientRects().length > 0
        );
      });
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.shiftKey && document.activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
    } else if (!event.shiftKey && document.activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  });

  mobileBreakpoint.addEventListener("change", () => setMenuOpen(!isMobile()));
  setMenuOpen(!isMobile());
})();
