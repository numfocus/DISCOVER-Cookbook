document.addEventListener('DOMContentLoaded', () => {
    const logos = document.querySelectorAll('.logo__image');
    const isTagsFolder = window.location.pathname.includes('/_tags/');
    logos.forEach(logo => {
      if (logo.classList.contains('only-light')) {
        logo.src = isTagsFolder ? '../_static/logo-light.png' : '_static/logo-light.png';
      } else if (logo.classList.contains('only-dark')) {
        logo.src = isTagsFolder ? '../_static/logo-dark.png' : '_static/logo-dark.png'; 
      }
    });

    function updateLogo() {
      let mainLogo = document.querySelector(".bd-content img:not(.only-dark,.dark-light)"); // Select the image
      let isDarkMode = document.documentElement.getAttribute("data-theme") === "dark"; // Check theme
    
      if (mainLogo) {
          mainLogo.src = isDarkMode ? "_static/logo-dark.png" : "_static/logo-light.png"; // Change image source
      }
    }
    
    // Listen for attribute changes on <html> that is the root node of the document
    const observer = new MutationObserver(updateLogo);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    updateLogo();
});