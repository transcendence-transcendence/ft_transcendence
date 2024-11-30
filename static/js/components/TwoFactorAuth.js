import { apiPost } from '../api.js';

export default function TwoFactorAuth() {
    return `
    <div class="two-factor-auth">
        <h2>Two-Factor Authentication</h2>
        <p>A one-time password (OTP) has been sent to your email. If you haven't received it, click below to send.</p>
        <button id="send-otp-button">Send OTP</button>
        <form id="two-factor-form">
            <label for="otp">Enter OTP:</label>
            <input type="text" id="otp" name="otp" required>
            <button type="submit">Verify</button>
        </form>
        <div id="error-messages" style="color: red; margin-top: 1rem;"></div>
        <div id="success-messages" style="color: green; margin-top: 1rem;"></div>
    </div>
    `;
}

setTimeout(() => {
    const twoFactorForm = document.getElementById('two-factor-form');
    const sendOtpButton = document.getElementById('send-otp-button');
    const errorContainer = document.getElementById('error-messages');
    const successContainer = document.getElementById('success-messages');

    if (sendOtpButton) {
        sendOtpButton.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const response = await apiPost('/two-factor/generate', {});
                successContainer.innerHTML = 'OTP sent successfully to your email.';
                errorContainer.innerHTML = '';
            } catch (error) {
                errorContainer.innerHTML = error.error || 'Failed to send OTP. Please try again.';
                successContainer.innerHTML = '';
            }
        });
    }

    if (twoFactorForm) {
        twoFactorForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(twoFactorForm);
            const otp = formData.get('otp');

            try {
                const response = await apiPost('/two-factor/verify', { otp });
                alert('2FA Verified! Redirecting to home.');
                window.location.href = '/'; // 인증 성공 시 홈으로 이동
            } catch (error) {
                console.error('2FA verification failed:', error);
                errorContainer.innerHTML = error.error || 'Invalid OTP. Please try again.';
            }
        });
    }
}, 0);
