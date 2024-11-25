import { apiPost } from '../api.js';

export default function Signup() {
    const template = `
    <form id="signup-form">
      <h2>Signup</h2>
      <input type="text" name="username" placeholder="Username" autocomplete="username" required>
      <input type="email" name="email" placeholder="Email" autocomplete="email" required>
      <input type="password" name="password1" placeholder="Password" autocomplete="new-password" required>
      <input type="password" name="password2" placeholder="Confirm Password" autocomplete="new-password" required>
      <button type="submit">Signup</button>
    </form>
    <div id="error-messages" style="color: red; margin-top: 1rem;"></div>
    <p style="margin-top: 1rem;">
      Password requirements:
      <ul>
        <li>At least 8 characters</li>
        <li>Cannot be similar to your username or email</li>
        <li>Cannot be a commonly used password</li>
        <li>Cannot be entirely numeric</li>
      </ul>
    </p>
  `;

    setTimeout(() => {
        const signupForm = document.getElementById('signup-form');
        const errorContainer = document.getElementById('error-messages');

        if (signupForm) {
            signupForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(signupForm);

                try {
                    const response = await apiPost('/signup', Object.fromEntries(formData));
                    console.log(response);

                    if (response.message === 'Signup successful') {
                        alert('Signup successful! Please log in.');
                        window.location.href = '/login'; // 로그인 페이지로 리다이렉트
                    }
                } catch (error) {
                    console.error('Signup failed:', error);

                    // 에러 메시지 초기화
                    let errorMessages = '';

                    // 최상위 error 메시지 처리
                    if (error.error) {
                        errorMessages += `<p><strong>Error:</strong> ${error.error}</p>`;
                    }

                    // 중첩된 details 처리
                    if (error.details) {
                        let parsedDetails = error.details;

                        // JSON 문자열인지 확인하고 파싱
                        if (typeof parsedDetails === 'string') {
                            try {
                                parsedDetails = JSON.parse(parsedDetails);
                            } catch (parseError) {
                                console.error('Failed to parse error details:', parseError);
                                parsedDetails = {}; // 파싱 실패 시 빈 객체로 설정
                            }
                        }

                        // 중첩된 구조를 재귀적으로 처리
                        const renderDetails = (details) => {
                            if (typeof details === 'object') {
                                return `
                                  <ul>
                                    ${Object.entries(details)
                                      .map(([field, messages]) => {
                                        if (Array.isArray(messages)) {
                                            // 메시지가 배열인 경우
                                            return `<li><strong>${field}:</strong> ${messages.join('<br>')}</li>`;
                                        } else if (typeof messages === 'object') {
                                            // 메시지가 중첩된 객체인 경우
                                            return `<li><strong>${field}:</strong> ${renderDetails(messages)}</li>`;
                                        } else {
                                            // 메시지가 문자열인 경우
                                            return `<li><strong>${field}:</strong> ${messages}</li>`;
                                        }
                                      })
                                      .join('')}
                                  </ul>
                                `;
                            } else {
                                return `<p>${details}</p>`;
                            }
                        };

                        // details를 렌더링
                        errorMessages += renderDetails(parsedDetails);
                    }

                    // 에러 메시지를 렌더링
                    errorContainer.innerHTML = errorMessages || '<p>An unknown error occurred. Please try again.</p>';
                }
            });
        }
    }, 0);

    return template;
}
