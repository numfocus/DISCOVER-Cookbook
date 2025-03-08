document.addEventListener('DOMContentLoaded', function() {
    // override logic
    const themeButton = document.querySelector('.theme-switch-button');
    const newButton = themeButton.cloneNode(true);
    themeButton.parentNode.replaceChild(newButton, themeButton);

    const getTheme = () => {
        const saved = localStorage.getItem('theme');
        return (saved === 'dark' || saved === 'light') ? saved : 'dark'; // Default dark
    };

    const setTheme = (theme) => {
        theme = theme === 'dark' ? 'dark' : 'light';
        document.documentElement.dataset.mode = theme;
        document.documentElement.dataset.theme = theme;
        localStorage.setItem('mode', theme);
        localStorage.setItem('theme', theme);
        
        newButton.classList.toggle('dark-mode', theme === 'dark');
        newButton.classList.toggle('light-mode', theme === 'light');
    };

    newButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });

    setTheme(getTheme());
});
