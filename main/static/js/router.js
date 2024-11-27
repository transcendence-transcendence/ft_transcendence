const routes = {
    '/': 'Home',
    '/login': 'Login',
    '/signup': 'Signup',
    '/two-factor': 'TwoFactorAuth',
    '/tournament': 'Tournament',
    '/tournament/game': 'TournamentGame',
    '/game/room': 'OnlineGame',
};

export async function router() {
    const path = window.location.pathname;
    const componentName = routes[path] || 'Home'; // 기본 경로를 Home으로 설정

    try {
        const module = await import(`./components/${componentName}.js`);
        const template = await module.default();
        document.getElementById('app').innerHTML = template;
    } catch (err) {
        console.error('Failed to load component:', err);
        document.getElementById('app').innerHTML = '<h1>Error loading page</h1>';
    }
}

// 브라우저 내비게이션 처리
window.onpopstate = router;

document.body.addEventListener('click', (e) => {
    if (e.target.tagName === 'A' && e.target.hasAttribute('data-link')) {
        e.preventDefault();
        history.pushState(null, '', e.target.href);
        router();
    }
});
