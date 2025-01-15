document.addEventListener('DOMContentLoaded', () => {
    const logos = document.querySelectorAll('.logo__image');
    
    logos.forEach(logo => {
      if (logo.classList.contains('only-light')) {
        logo.src = '_static/logo-light.png'; // Replacing with the light logo
      } else if (logo.classList.contains('only-dark')) {
        logo.src = '_static/logo-dark.png'; // Replacing with the dark logo
      }
    });
});