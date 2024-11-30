const BASE_URL = `https://${window.location.hostname}/api`; // 동적으로 BASE_URL 생성

export async function apiPost(endpoint, data) {
    const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1] || '';

    const accessToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('access_token'))
        ?.split('=')[1];

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': accessToken ? `Bearer ${accessToken}` : '',
                'X-CSRFToken': csrfToken, // CSRF 토큰 포함
            },
            body: JSON.stringify(data),
            credentials: 'include' // 쿠키를 포함
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(JSON.stringify(result));
        }

        return result;
    } catch (error) {
        throw error;
    }
}
