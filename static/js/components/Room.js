import { apiGet } from '../api.js';

export default async function Room() {
    try {
        const user = await apiGet('/auth/status');
        if (!user?.is_authenticated || !user?.is_otp_verified) {
            history.pushState(null, '', '/');
            window.dispatchEvent(new Event('popstate'));
            return '';
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
        history.pushState(null, '', '/');
        window.dispatchEvent(new Event('popstate'));
        return '';
    }

    const template = `
        <div class="container d-flex flex-column justify-content-center align-items-center vh-100">
            <div class="room-form">
                <h2 class="text-center mb-4">Enter Room Name</h2>
                <form id="roomForm" class="mb-3">
                    <div class="form-group">
                        <input type="text" 
                               id="roomName" 
                               class="form-control form-control-lg" 
                               placeholder="Enter room name"
                               required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg btn-block">Start Game</button>
                </form>
            </div>
        </div>
    `;

    setTimeout(() => {
        const roomForm = document.getElementById('roomForm');
        if (roomForm) {
            roomForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const roomName = document.getElementById('roomName').value.trim();
                if (roomName) {
                    window.location.hash = `#/online/${encodeURIComponent(roomName)}`;
                }
            });
        }
    }, 0);

    return template;
} 