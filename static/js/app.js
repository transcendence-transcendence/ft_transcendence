import { router } from './router.js';

document.addEventListener('DOMContentLoaded', async () => {
    const savedHost = localStorage.getItem('host');
    if (!savedHost) {
        const host = prompt('Enter the server IP or domain (e.g., 127.0.0.1):', '127.0.0.1');
        if (host) {
            localStorage.setItem('host', host); // 사용자가 입력한 값을 저장
        }
    }
    router(); // 초기 경로 처리
});