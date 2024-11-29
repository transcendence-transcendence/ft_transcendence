const routes = {
    '#/': 'Home',
    '#/login': 'Login',
    '#/signup': 'Signup',
    '#/two-factor': 'TwoFactorAuth',
    '#/tournament': 'Tournament',
    '#/tournament/game': 'TournamentGame',
    '#/room': 'Room',
    '#/online': 'OnlineGame'
};

export async function router() {
    const hash = window.location.hash;
    let componentName;

    // 동적 라우트 처리
    if (hash.startsWith('#/online/')) {
        componentName = 'OnlineGame';
    } else {
        componentName = routes[hash] || 'Home';
    }

    try {
        const module = await import(`./components/${componentName}.js`);
        const template = await module.default();
        document.getElementById('app').innerHTML = template;
    } catch (err) {
        console.error('Failed to load component:', err);
        document.getElementById('app').innerHTML = '<h1>Error loading page</h1>';
    }
}

// 해시 변경 이벤트 처리
window.addEventListener('hashchange', router);

document.body.addEventListener('click', (e) => {
    if (e.target.tagName === 'A' && e.target.hasAttribute('data-link')) {
        e.preventDefault();
        window.location.hash = e.target.getAttribute('href');
    }
});
