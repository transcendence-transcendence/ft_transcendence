import { apiGet } from '../api.js';

export default async function TournamentGame() {
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
        <div class="game-container">
            <div id="scoreBoard">플레이어 1: 0 | 플레이어 2: 0</div>
            <div id="gameCanvas"></div>
        </div>
    `;

    setTimeout(() => {
        initializeGame();
    }, 0);

    return template;
}

function initializeGame() {
    // Three.js 초기 설정
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x1a1a1a);
    document.getElementById('gameCanvas').appendChild(renderer.domElement);

    localStorage.removeItem('matchResult');
    localStorage.removeItem('winner');

    // 게임 상태 변수
    const scoreBoard = document.getElementById('scoreBoard');
    
    let player1Score = 0;
    let player2Score = 0;

    // 게임 필드 크기 상수
    const TABLE_WIDTH = 20;
    const TABLE_DEPTH = 10;
    const PADDLE_LIMIT = TABLE_DEPTH / 2 - 1;

    // Canvas 크기 (서버와 동일하게 설정)
    const CANVAS_WIDTH = 800;
    const CANVAS_HEIGHT = 400;

    // 서버의 패들 및 공 크기
    const PADDLE_WIDTH_SERVER = 10;
    const PADDLE_HEIGHT_SERVER = 100;
    const BALL_RADIUS_SERVER = 10;

    // 좌표 및 크기 매핑 함수
    function mapX(x) {
        return ((x - CANVAS_WIDTH / 2) / (CANVAS_WIDTH / 2)) * (TABLE_WIDTH / 2);
    }

    function mapZ(y) {
        return ((y - CANVAS_HEIGHT / 2) / (CANVAS_HEIGHT / 2)) * (TABLE_DEPTH / 2);
    }

    function mapWidth(width) {
        return (width / CANVAS_WIDTH) * TABLE_WIDTH;
    }

    function mapDepth(height) {
        return (height / CANVAS_HEIGHT) * TABLE_DEPTH;
    }

    // 3D 오브젝트 생성
    // 탁구대
    const tableGeometry = new THREE.BoxGeometry(TABLE_WIDTH, 0.5, TABLE_DEPTH);
    const tableMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x004400,
        shininess: 60
    });
    const table = new THREE.Mesh(tableGeometry, tableMaterial);
    scene.add(table);

    // 테이블 경계선
    const borderMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
    const borderGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-TABLE_WIDTH/2, 0.26, -TABLE_DEPTH/2),
        new THREE.Vector3(TABLE_WIDTH/2, 0.26, -TABLE_DEPTH/2),
        new THREE.Vector3(TABLE_WIDTH/2, 0.26, TABLE_DEPTH/2),
        new THREE.Vector3(-TABLE_WIDTH/2, 0.26, TABLE_DEPTH/2),
        new THREE.Vector3(-TABLE_WIDTH/2, 0.26, -TABLE_DEPTH/2)
    ]);
    const borderLine = new THREE.Line(borderGeometry, borderMaterial);
    scene.add(borderLine);

    // 패들
    const paddleWidth = mapWidth(PADDLE_WIDTH_SERVER);
    const paddleHeight = 1.5;
    const paddleDepth = mapDepth(PADDLE_HEIGHT_SERVER);
    const paddleGeometry = new THREE.BoxGeometry(paddleWidth, paddleHeight, paddleDepth);
    
    const paddle1 = new THREE.Mesh(paddleGeometry, new THREE.MeshPhongMaterial({ 
        color: 0xff0000,
        shininess: 100
    }));
    const paddle2 = new THREE.Mesh(paddleGeometry.clone(), new THREE.MeshPhongMaterial({ 
        color: 0x0000ff,
        shininess: 100
    }));

    const paddle1X = mapX(PADDLE_WIDTH_SERVER / 2);
    const paddle2X = mapX(CANVAS_WIDTH - PADDLE_WIDTH_SERVER / 2);
    paddle1.position.set(paddle1X, 1, 0);
    paddle2.position.set(paddle2X, 1, 0);
    scene.add(paddle1);
    scene.add(paddle2);

    // 공
    const ballRadius = (BALL_RADIUS_SERVER / CANVAS_WIDTH) * TABLE_WIDTH;
    const ballGeometry = new THREE.SphereGeometry(ballRadius, 32, 32);
    const ball = new THREE.Mesh(ballGeometry, new THREE.MeshPhongMaterial({ 
        color: 0xffffff,
        shininess: 100,
        emissive: 0x444444
    }));
    ball.position.set(0, 1, 0);
    scene.add(ball);

    // 조명
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const spotLight = new THREE.SpotLight(0xffffff, 0.8);
    spotLight.position.set(0, 15, 0);
    spotLight.castShadow = true;
    scene.add(spotLight);

    // 카메라 위치 설정
    camera.position.set(0, 12, 15);
    camera.lookAt(0, 0, 0);

    // 게임 로직 변수
    let ballSpeed = 0.2;
    let ballDX = ballSpeed;
    let ballDY = ballSpeed;
    const paddleSpeed = 0.3;

    const keys = {
        w: false,
        s: false,
        ArrowUp: false,
        ArrowDown: false
    };

    document.addEventListener('keydown', (e) => {
        if (e.key in keys) {
            console.log(e.key);
            e.preventDefault();
            keys[e.key] = true;
        }
    });

    document.addEventListener('keyup', (e) => {
        if (e.key in keys) {
            console.log(e.key);
            e.preventDefault();
            keys[e.key] = false;
        }
    });

    function movePaddles() {
        // paddleDepth/2를 고려하여 이동 제한
        if (keys.w && paddle1.position.z - paddleDepth/2 > -TABLE_DEPTH/2) {
            paddle1.position.z -= paddleSpeed;
        }
        if (keys.s && paddle1.position.z + paddleDepth/2 < TABLE_DEPTH/2) {
            paddle1.position.z += paddleSpeed;
        }
        if (keys.ArrowUp && paddle2.position.z - paddleDepth/2 > -TABLE_DEPTH/2) {
            paddle2.position.z -= paddleSpeed;
        }
        if (keys.ArrowDown && paddle2.position.z + paddleDepth/2 < TABLE_DEPTH/2) {
            paddle2.position.z += paddleSpeed;
        }
    }

    function resetBall() {
        ball.position.set(0, 1, 0);
        ballDX = Math.random() < 0.5 ? ballSpeed : -ballSpeed;
        ballDY = (Math.random() - 0.5) * ballSpeed;
    }

    function endGame(winner) {
        localStorage.setItem('matchResult', 'completed');
        localStorage.setItem('winner', winner);
        window.location.hash = '#/tournament';
    }

    function checkGameEnd() {
        if (player1Score >= 5) {
            endGame(localStorage.getItem('player1'));
            return true;
        } else if (player2Score >= 5) {
            endGame(localStorage.getItem('player2'));
            return true;
        }
        return false;
    }

    function updateScore() {
        const player1Name = localStorage.getItem('player1');
        const player2Name = localStorage.getItem('player2');
        scoreBoard.textContent = `${player1Name}: ${player1Score} | ${player2Name}: ${player2Score}`;
        checkGameEnd();
    }

    function detectCollision() {
        // 상하 벽과 충돌
        if (ball.position.z + ballRadius > TABLE_DEPTH/2 || ball.position.z - ballRadius < -TABLE_DEPTH/2) {
            ballDY = -ballDY;
        }

        // 패들과 충돌
        if (ballDX < 0) {
            if (ball.position.x - ballRadius < paddle1.position.x + paddleWidth/2 &&
                ball.position.z > paddle1.position.z - paddleDepth/2 &&
                ball.position.z < paddle1.position.z + paddleDepth/2) {
                ballDX = -ballDX;
            }
        } else {
            if (ball.position.x + ballRadius > paddle2.position.x - paddleWidth/2 &&
                ball.position.z > paddle2.position.z - paddleDepth/2 &&
                ball.position.z < paddle2.position.z + paddleDepth/2) {
                ballDX = -ballDX;
            }
        }

        // 득점 체크
        if (ball.position.x < -TABLE_WIDTH/2) {
            player2Score++;
            updateScore();
            resetBall();
        } else if (ball.position.x > TABLE_WIDTH/2) {
            player1Score++;
            updateScore();
            resetBall();
        }
    }

    // 창 크기 조정 이벤트
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // 게임 루프
    function animate() {
        if (checkGameEnd()) {
            return; // 게임이 끝나면 animate 중단
        }

        requestAnimationFrame(animate);

        movePaddles();
        
        ball.position.x += ballDX;
        ball.position.z += ballDY;
        ball.rotation.x += 0.05;
        ball.rotation.z += 0.05;

        detectCollision();
        
        renderer.render(scene, camera);
    }

    resetBall();
    updateScore();
    animate();
}