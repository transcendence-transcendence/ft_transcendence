export default async function TournamentGame() {
    const template = `
        <div class="game-container">
            <div id="scoreBoard">플레이어 1: 0 | 플레이어 2: 0</div>
            <canvas id="gameCanvas" width="800" height="400"></canvas>
        </div>
    `;

    setTimeout(() => {
        initializeGame();
    }, 0);

    return template;
}

function initializeGame() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreBoard = document.getElementById('scoreBoard');

    const ball = {
        x: canvas.width / 2,
        y: canvas.height / 2,
        radius: 10,
        speed: 5,
        dx: 5,
        dy: 5
    };

    const paddle1 = {
        x: 0,
        y: canvas.height / 2 - 50,
        width: 10,
        height: 100,
        dy: 7,
        score: 0
    };

    const paddle2 = {
        x: canvas.width - 10,
        y: canvas.height / 2 - 50,
        width: 10,
        height: 100,
        dy: 7,
        score: 0
    };

    const powerUp = {
        x: 0,
        y: 0,
        radius: 15,
        active: false,
        type: ''
    };

    const keys = {
        w: false,
        s: false,
        ArrowUp: false,
        ArrowDown: false
    };

    document.addEventListener('keydown', (e) => {
        if (e.key in keys) {
            keys[e.key] = true;
        }
    });

    document.addEventListener('keyup', (e) => {
        if (e.key in keys) {
            keys[e.key] = false;
        }
    });

    function resetBall(player) {
        ball.x = canvas.width / 2;
        ball.y = canvas.height / 2;
        ball.speed = 5;
        ball.dx = ball.speed * (player === 1 ? 1 : -1);
        ball.dy = ball.speed * (Math.random() - 0.5);
    }

    function movePaddles() {
        if (keys.w && paddle1.y > 0) {
            paddle1.y -= paddle1.dy;
        }
        if (keys.s && paddle1.y < canvas.height - paddle1.height) {
            paddle1.y += paddle1.dy;
        }
        if (keys.ArrowUp && paddle2.y > 0) {
            paddle2.y -= paddle2.dy;
        }
        if (keys.ArrowDown && paddle2.y < canvas.height - paddle2.height) {
            paddle2.y += paddle2.dy;
        }
    }

    function detectCollision() {
        // 상하 벽과 충돌
        if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
            ball.dy = -ball.dy;
        }

        // 패들과 돌
        if (ball.dx < 0) {
            if (ball.x - ball.radius < paddle1.x + paddle1.width &&
                ball.y > paddle1.y && ball.y < paddle1.y + paddle1.height) {
                ball.dx = -ball.dx;
                createParticles(ball.x, ball.y, 10);
            }
        } else {
            if (ball.x + ball.radius > paddle2.x &&
                ball.y > paddle2.y && ball.y < paddle2.y + paddle2.height) {
                ball.dx = -ball.dx;
                createParticles(ball.x, ball.y, 10);
            }
        }

        // 점수 계산
        if (ball.x - ball.radius < 0) {
            paddle2.score++;
            updateScore();
            resetBall(2);
        } else if (ball.x + ball.radius > canvas.width) {
            paddle1.score++;
            updateScore();
            resetBall(1);
        }

        // 파워업 충돌 감지
        if (powerUp.active) {
            const dx = ball.x - powerUp.x;
            const dy = ball.y - powerUp.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < ball.radius + powerUp.radius) {
                applyPowerUp();
                createParticles(powerUp.x, powerUp.y, 20);
            }
        }
    }

    function createParticles(x, y, amount) {
        for (let i = 0; i < amount; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.width = `${Math.random() * 4 + 2}px`;
            particle.style.height = particle.style.width;
            
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 3 + 1;
            const dx = Math.cos(angle) * speed;
            const dy = Math.sin(angle) * speed;
            
            document.body.appendChild(particle);
            
            let opacity = 1;
            const animate = () => {
                if (opacity <= 0) {
                    particle.remove();
                    return;
                }
                
                opacity -= 0.02;
                particle.style.opacity = opacity;
                particle.style.left = `${parseFloat(particle.style.left) + dx}px`;
                particle.style.top = `${parseFloat(particle.style.top) + dy}px`;
                
                requestAnimationFrame(animate);
            };
            
            animate();
        }
    }

    function createPowerUp() {
        if (!powerUp.active) {
            powerUp.x = Math.random() * (canvas.width - 100) + 50;
            powerUp.y = Math.random() * (canvas.height - 100) + 50;
            powerUp.active = true;
            powerUp.type = Math.random() < 0.5 ? 'speed' : 'size';
        }
    }

    function applyPowerUp() {
        if (powerUp.type === 'speed') {
            ball.speed *= 0.8;
            const angle = Math.atan2(ball.dy, ball.dx);
            ball.dx = ball.speed * Math.cos(angle);
            ball.dy = ball.speed * Math.sin(angle);
        } else if (powerUp.type === 'size') {
            paddle1.height = Math.min(150, paddle1.height + 20);
            paddle2.height = Math.min(150, paddle2.height + 20);
        }
        powerUp.active = false;
    }

    function checkGameEnd() {
        if (paddle1.score >= 5) {
            endGame(localStorage.getItem('player1'));
            return true;
        } else if (paddle2.score >= 5) {
            endGame(localStorage.getItem('player2'));
            return true;
        }
        return false;
    }

    function endGame(winner) {
        localStorage.setItem('matchResult', 'completed');
        localStorage.setItem('winner', winner);
        window.history.pushState({}, '', '/tournament');
        window.dispatchEvent(new Event('popstate'));
    }

    function updateScore() {
        const player1Name = localStorage.getItem('player1');
        const player2Name = localStorage.getItem('player2');
        scoreBoard.textContent = `${player1Name}: ${paddle1.score} | ${player2Name}: ${paddle2.score}`;
        checkGameEnd();
    }

    function gameLoop() {
        if (checkGameEnd()) {
            return; // 게임이 끝나면 gameLoop 중단
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        movePaddles();
        
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.closePath();

        ctx.fillStyle = '#fff';
        ctx.fillRect(paddle1.x, paddle1.y, paddle1.width, paddle1.height);
        ctx.fillRect(paddle2.x, paddle2.y, paddle2.width, paddle2.height);

        if (powerUp.active) {
            ctx.beginPath();
            ctx.arc(powerUp.x, powerUp.y, powerUp.radius, 0, Math.PI * 2);
            ctx.fillStyle = powerUp.type === 'speed' ? '#00ffff' : '#ff00ff';
            ctx.fill();
            ctx.closePath();
        }

        ball.x += ball.dx;
        ball.y += ball.dy;

        detectCollision();

        if (Math.random() < 0.002) {
            createPowerUp();
        }

        requestAnimationFrame(gameLoop);
    }

    updateScore();
    resetBall(Math.random() < 0.5 ? 1 : 2);
    gameLoop();
} 