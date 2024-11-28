import { apiGet } from '../api.js';

export default async function Home() {
    let user = null;
    try {
        user = await apiGet('/auth/status');
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
                                <a href="#/game/room" data-link class="btn btn-info mb-2">Online Game</a>
                            ` : `
                                <button id="two-factor-button" class="btn btn-warning mb-2">Enable Email 2FA</button>
                            `}
                        ` : `
                            <a href="/signup" data-link class="btn btn-success mb-2">Sign Up</a>
                            <a href="/login" data-link class="btn btn-primary mb-2">Login</a>
                            <button id="oauth-button" class="btn btn-secondary mb-2">Login with 42 OAuth</button>
                        `}
                    </div>
                </div>
            </div>
        </div>
    `;

    // 이벤트 리스너 설정
    setTimeout(() => {
        const logoutButton = document.getElementById('logout-button');
        const twoFactorButton = document.getElementById('two-factor-button');
        const oauthButton = document.getElementById('oauth-button');

        if (logoutButton) {
            logoutButton.addEventListener('click', async () => {
                try {
                    await apiGet('/auth/logout');
                    window.location.reload();
                } catch (error) {
                    console.error('Logout failed:', error);
                }
            });
        }

        if (twoFactorButton) {
            twoFactorButton.addEventListener('click', async () => {
                try {
                    const response = await apiGet('/auth/request-otp');
                    if (response.status === 'success') {
                        alert('2FA verification email has been sent. Please check your email.');
                    }
                } catch (error) {
                    console.error('Failed to request OTP:', error);
                }
            });
        }

        if (oauthButton) {
            oauthButton.addEventListener('click', () => {
                window.location.href = '/auth/oauth';
            });
        }
    }, 0);

    return template;
}