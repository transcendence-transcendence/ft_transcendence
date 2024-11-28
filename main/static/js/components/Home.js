import { apiGet, apiPost } from '../api.js';

export default async function Home() {
    // 서버로부터 사용자 인증 상태를 가져오기
    let user = null;
    try {
        user = await apiGet('/auth/status'); // 서버에서 사용자 상태를 반환하는 API
    } catch (error) {
        console.error('Failed to fetch user status:', error);
    }

    // 인증 상태에 따른 버튼 렌더링
    const loggedIn = user?.is_authenticated;
    const isOtpVerified = user?.is_otp_verified;

    // 홈 페이지 템플릿
    const template = `
        <div class="home">
            <h1>Welcome to the Game Hub</h1>
            <p>Experience a simple SPA demo.</p>

            ${loggedIn ? `
                <button id="logout-button" class="btn btn-secondary">Logout</button>
                ${isOtpVerified ? `
                    <a href="#/tournament" data-link class="btn btn-primary">Local Go to Game</a>
                    <a href="#/game/room" data-link class="btn btn-primary">Online Go to Game</a>
                ` : `
                    <button id="two-factor-button" class="btn btn-primary">Enable Email 2FA</button>
                `}
            ` : `
                <a href="/signup" data-link class="btn btn-primary">Sign Up</a>
                <a href="/login" data-link class="btn btn-primary">Login</a>
                <button id="oauth-button" class="oauth-button">Login with 42 OAuth</button>
            `}
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
                history.pushState(null, '', '/two-factor'); // URL 변경
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
                    // console.error('Logout failed:', error);
                    alert('Logout failed. Please try again.');
                }
            });
        }
    }, 0);

    return template; // 템플릿 반환
}
