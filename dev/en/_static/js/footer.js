document.addEventListener('DOMContentLoaded', function() {
  const existingFooter = document.querySelector('.bd-footer-content');
  
  if (existingFooter) {
    existingFooter.innerHTML = '';
    
    const footerContent = document.createElement('div');
    footerContent.className = 'bd-footer-content_inner container';
    footerContent.innerHTML = `
      <div class="footer-logo">
        <a href="https://numfocus.org" target="_blank" rel="noopener">
          <img src="_static/images/Numfocus-logo-dark.png" alt="NumFOCUS" class="numfocus-logo light-mode-only">
          <img src="_static/images/Numfocus-logo-light.png" alt="NumFOCUS" class="numfocus-logo dark-mode-only">
        </a>
      </div>

      <div class="footer-links">
        <a href="https://numfocus.org/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a>
        <a href="https://numfocus.org/code-of-conduct" target="_blank" rel="noopener">Code of Conduct</a>
        <a href="https://numfocus.org/support" target="_blank" rel="noopener">Support</a>
        <a href="https://numfocus.org/donate" target="_blank" rel="noopener">Donate</a>
        <span class="copyright">© Copyright 2023</span>
      </div>

      <div class="social-links">
        <a href="https://github.com/numfocus" target="_blank" rel="noopener" aria-label="GitHub">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.6.113.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
        </a>
        <a href="https://x.com/NumFOCUS" target="_blank" rel="noopener" aria-label="X (Twitter)">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg>
        </a>
        <a href="https://www.linkedin.com/company/numfocus/" target="_blank" rel="noopener" aria-label="LinkedIn">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
        </a>
      </div>
    `;
    
    const styleElement = document.createElement('style');
    styleElement.textContent = `
      /* Theme-specific logo visibility */
      .light-mode-only {
        display: block;
      }
      
      .dark-mode-only {
        display: none;
      }
      
      html[data-theme="dark"] .light-mode-only {
        display: none;
      }
      
      html[data-theme="dark"] .dark-mode-only {
        display: block;
      }
    `;
    document.head.appendChild(styleElement);
    
    existingFooter.appendChild(footerContent);
  }
});