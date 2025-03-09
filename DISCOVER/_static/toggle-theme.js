document.addEventListener('DOMContentLoaded', function () {
    const button = document.querySelector('.theme-switch-button');

    const getTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        return savedTheme === 'dark' || savedTheme === 'light' ? savedTheme : 'dark';
    };

    const setTheme = (theme) => {
        theme = theme === 'dark' ? 'dark' : 'light';
        document.documentElement.dataset.mode = theme;
        document.documentElement.dataset.theme = theme;
        localStorage.setItem('theme', theme);

        button.classList.toggle('dark-mode', theme === 'dark');
        button.classList.toggle('light-mode', theme === 'light');
    };

    button.addEventListener('click', (e) => {
        e.preventDefault();
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });

    setTheme(getTheme());
});
