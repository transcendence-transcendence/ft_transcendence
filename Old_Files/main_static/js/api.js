const BASE_URL = 'https://127.0.0.1/api'; // 명시적으로 URL 스키마 추가

// export async function apiGet(endpoint) {
//     const csrfToken = document.cookie
//         .split('; ')
//         .find(row => row.startsWith('csrftoken'))
//         ?.split('=')[1] || '';

//     const accessToken = document.cookie
//         .split('; ')
//         .find(row => row.startsWith('access_token'))
//         ?.split('=')[1];

//     const sessionId = document.cookie
//         .split('; ')
//         .find(row => row.startsWith('sessionid'))
//         ?.split('=')[1]; // Session ID from cookies

//     try {
//         const response = await fetch(`${BASE_URL}/auth/status`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': csrfToken,
//             'Authorization': accessToken ? `Bearer ${accessToken}` : '',
//         },
//         credentials: 'include',
//         body: JSON.stringify({ action: 'check_status' }), // Example payload
//         });

//         // Check if response is okay
//         if (!response.ok) {
//             console.error('API error response:', response);
//             throw new Error(`HTTP error! Status: ${response.status}`);
//         }

//         // Ensure response has JSON content type
//         const contentType = response.headers.get('content-type');
//         if (!contentType || !contentType.includes('application/json')) {
//             console.error('Invalid content type:', contentType);
//             throw new Error('Response is not JSON');
//         }

//         // Parse and return the JSON response
//         const result = await response.json();
//         return result;

//     } catch (error) {
//         console.error('API POST 요청 실패:', error);
//         throw error;
//     }
// }

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
        // console.error('API POST 요청 실패:', error);
        throw error;
    }
}
