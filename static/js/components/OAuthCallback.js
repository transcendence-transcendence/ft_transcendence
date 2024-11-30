const HOST = localStorage.getItem('host') || '127.0.0.1'; // 기본값 제공

const CLIENT_ID = 'u-s4t2ud-76b5fc7299ec7d4148ff001998639910bf355419b559c8539a7f3e20f4280725';
const REDIRECT_URI = `https://${HOST}/api/oauth/callback`;
const AUTHORIZATION_URL = 'https://api.intra.42.fr/oauth/authorize';

export function startOAuthFlow() {
    // Build the OAuth URL dynamically
    const oauthURL = `${AUTHORIZATION_URL}?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code`;
    // Redirect to the OAuth provider
    window.location.href = oauthURL;
}
