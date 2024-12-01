import { apiPost } from '../api.js';

export default async function Home() {
    let user = null;
    try {
        user = await apiPost('/auth/status', {});
    } catch (error) {
        console.error('Failed to fetch user status:', error);
    }

    const loggedIn = user?.is_authenticated;
    const isOtpVerified = user?.is_otp_verified;

    const template = `
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8 text-center">
                    <h1 class="display-4 mb-4 crt-effect">PONG GAME</h1>
                    <div class="card bg-dark text-light border-light mb-4">
                        <div class="card-body">
                            <h5 class="card-title crt-effect">Welcome to the Game Hub</h5>
                            <p class="card-text">Experience classic Pong with a retro twist.</p>
                        </div>
                    </div>
                    <div class="btn-group-vertical">
                        ${loggedIn ? `
                            <button id="logout-button" class="btn btn-outline-danger mb-2">Logout</button>
                            ${isOtpVerified ? `
                                <a href="#/tournament" data-link class="btn btn-primary mb-2">Local Game</a>
                                <a href="#/room" data-link class="btn btn-info mb-2">Online Game</a>
                            ` : `
                                <button id="two-factor-button" class="btn btn-warning mb-2">Enable Email 2FA</button>
                            `}
                        ` : `
                            <a href="#/signup" data-link class="btn btn-success mb-2">Sign Up</a>
                            <a href="#/login" data-link class="btn btn-primary mb-2">Login</a>
                            <button id="oauth-button" class="btn btn-secondary mb-2">Login with 42 OAuth</button>
                        `}
                    </div>
                </div>
            </div>
        </div>
    `;

    // DOM 업데이트 후 이벤트 등록을 위해 반환된 템플릿을 비동기로 실행
    setTimeout(() => {
        const oauthButton = document.getElementById('oauth-button');
        const twoFactorButton = document.getElementById('two-factor-button');
        const logoutButton = document.getElementById('logout-button');

        // OAuth 버튼 이벤트 등록
        if (oauthButton) {
            oauthButton.addEventListener('click', () => {
                import('./OAuthCallback.js')
                    .then((module) => {
                        module.startOAuthFlow();
                    })
                    .catch((err) => console.error('Failed to start OAuth flow:', err));
            });
        }

        // 2FA 버튼 이벤트 등록
        if (twoFactorButton) {
            twoFactorButton.addEventListener('click', (e) => {
                e.preventDefault();
                history.pushState(null, '', '#/two-factor'); // URL 변경
                import('../router.js').then((module) => {
                    module.router(); // SPA 라우터로 두 팩터 페이지 렌더링
                });
            });
        }

        // Logout 버튼 이벤트 등록
        if (logoutButton) {
            logoutButton.addEventListener('click', async () => {
                try {
                    const response = await apiPost('/logout', {}); // 로그아웃 호출
                    if (response.message === 'Logout successful') {
                        alert('You have been logged out.');
                        window.location.reload(); // 홈 페이지로 리다이렉트하여 상태 초기화
                        console.log(response);
                    }
                } catch (error) {
                    alert('Logout failed. Please try again.');
                }
            });
        }
    }, 0);

    return template;
}