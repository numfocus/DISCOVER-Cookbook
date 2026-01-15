document.addEventListener('DOMContentLoaded', () => {
  const logos = document.querySelectorAll('.logo__image');
  const isTagsFolder = window.location.pathname.includes('/_tags/');

  logos.forEach(logo => {
    if (logo.classList.contains('only-light')) {
      logo.src = isTagsFolder
        ? '../_static/images/logo-light.png'
        : '_static/images/logo-light.png';
    } else if (logo.classList.contains('only-dark')) {
      logo.src = isTagsFolder
        ? '../_static/images/logo-dark.png'
        : '_static/images/logo-dark.png';
    }
  });

  function updateLogo() {
    let mainLogo = document.querySelector(
      ".bd-content img:not(.only-dark,.dark-light)"
    );
    let isDarkMode =
      document.documentElement.getAttribute("data-theme") === "dark";

    if (mainLogo) {
      mainLogo.src = isDarkMode
        ? "_static/images/logo-dark.png"
        : "_static/images/logo-light.png";
    }

    // ✅ ADD TOOLTIP + ARIA-LABEL FOR THEME SWITCHER
    const themeSwitcher = document.querySelector(".dark-light");
    if (themeSwitcher) {
      if (isDarkMode) {
        themeSwitcher.setAttribute("title", "Switch to light mode");
        themeSwitcher.setAttribute("aria-label", "Switch to light mode");
      } else {
        themeSwitcher.setAttribute("title", "Switch to dark mode");
        themeSwitcher.setAttribute("aria-label", "Switch to dark mode");
      }
    }
  }

  // Listen for attribute changes on <html>
  const observer = new MutationObserver(updateLogo);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  updateLogo();
});
