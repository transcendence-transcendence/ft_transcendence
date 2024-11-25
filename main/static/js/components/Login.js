import { apiPost } from '../api.js';

export default function Login() {
    const template = `
    <form id="login-form">
      <h2>Login</h2>
      <input type="text" name="username" placeholder="Username" autocomplete="username" required>
      <input type="password" name="password" placeholder="Password" autocomplete="current-password" required>
      <button type="submit">Login</button>
    </form>
  `;

    setTimeout(() => {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(loginForm);
                console.log(Object.fromEntries(formData));
                try {
                    const response = await apiPost('/login', Object.fromEntries(formData));
                    console.log(response);

                    if (response.message === 'Login successful') {
                        alert('Login successful!');
                        window.location.href = '/'; // 성공 시 홈으로 이동
                    }
                } catch (error) {
                    alert('Invalid credentials. Please try again.');
                }
            });
        }
    }, 0);

    return template;
}
