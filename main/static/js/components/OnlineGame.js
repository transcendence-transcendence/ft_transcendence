import { apiGet } from '../api.js';

export default async function OnlineGame() {
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
    // 현재 사용자 정보 가져오기
    let currentUser;
    try {
        const response = await apiGet('/auth/status');
        const data = response;
        currentUser = data.username;
    } catch (error) {
        console.error('Failed to fetch user status:', error);
        return '<div>Error: Failed to load game</div>';
    }

    const urlParams = new URLSearchParams(window.location.search);
    const roomName = urlParams.get('room') || 'default';

    const template = `
    <div class="game-container">
        <div class="game-overlay">
            <div id="scoreBoard">플레이어 1: 0 | 플레이어 2: 0</div>
            <div id="waitMessage">게임을 시작하려면 준비 버튼을 눌러주세요.</div>
            <button id="readyButton" style="display: none;">I'm Ready!</button>
        </div>
        <div id="gameCanvas"></div>
    </div>
    <link rel="stylesheet" href="/static/css/game.css">
`;

    setTimeout(() => {
        initializeGame(roomName, currentUser);
    }, 0);

    return template;
}

function initializeGame(roomName, currentUser) {
    // Three.js 초기 설정
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x1a1a1a);
    document.getElementById('gameCanvas').appendChild(renderer.domElement);

    // 게임 상태 변수
    const scoreBoard = document.getElementById('scoreBoard');
    const waitMessageDiv = document.getElementById('waitMessage');
    const readyButton = document.getElementById('readyButton');
    let isGameStarted = false;
    let isReady = false;
    
    let player1 = null;
    let player2 = null;
    let player1Score = 0;
    let player2Score = 0;

    // 게임 필드 크기 상수
    const TABLE_WIDTH = 20;
    const TABLE_DEPTH = 10;
    const PADDLE_LIMIT = TABLE_DEPTH / 2 - 1; // 패들 이동 제한

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

    function mapZ(y) { // Note: Mapping y to z in the 3D space
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

    // 패들 크기 및 위치 설정
    const paddleWidth = mapWidth(PADDLE_WIDTH_SERVER);
    const paddleHeight = 1.5; // Y축 높이 (두께)
    const paddleDepth = mapDepth(PADDLE_HEIGHT_SERVER);

    const paddleGeometry = new THREE.BoxGeometry(paddleWidth, paddleHeight, paddleDepth);
    const paddleMaterial1 = new THREE.MeshPhongMaterial({ 
        color: 0xff0000,
        shininess: 100
    });
    const paddleMaterial2 = new THREE.MeshPhongMaterial({ 
        color: 0x0000ff,
        shininess: 100
    });

    const paddle1 = new THREE.Mesh(paddleGeometry, paddleMaterial1);
    const paddle2 = new THREE.Mesh(paddleGeometry.clone(), paddleMaterial2);

    // 패들 초기 위치 설정
    const paddle1X = mapX(PADDLE_WIDTH_SERVER / 2);
    const paddle2X = mapX(CANVAS_WIDTH - PADDLE_WIDTH_SERVER / 2);

    paddle1.position.set(paddle1X, 1, 0);
    paddle2.position.set(paddle2X, 1, 0);

    scene.add(paddle1);
    scene.add(paddle2);

    // 공
    const ballRadius = (BALL_RADIUS_SERVER / CANVAS_WIDTH) * TABLE_WIDTH;
    const ballGeometry = new THREE.SphereGeometry(ballRadius, 32, 32);
    const ballMaterial = new THREE.MeshPhongMaterial({ 
        color: 0xffffff,
        shininess: 100,
        emissive: 0x444444 // 발광 효과 추가
    });
    const ball = new THREE.Mesh(ballGeometry, ballMaterial);
    ball.position.y = 1; // 공의 시작 높이 설정
    scene.add(ball);

    // 조명
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const spotLight = new THREE.SpotLight(0xffffff, 0.8);
    spotLight.position.set(0, 15, 0);
    spotLight.castShadow = true;
    scene.add(spotLight);

    // 보조 조명 추가
    const frontLight = new THREE.DirectionalLight(0xffffff, 0.5);
    frontLight.position.set(0, 5, 15);
    scene.add(frontLight);

    // 카메라 위치 설정
    camera.position.set(0, 12, 15); // 카메라 위치 조정
    camera.lookAt(0, 0, 0);

    // WebSocket 연결
    const gameSocket = new WebSocket(
        `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/game/room/${roomName}/`
    );

    gameSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'players_ready') {
            player1 = data.player1;
            player2 = data.player2;
            readyButton.style.display = 'block';
            waitMessageDiv.textContent = '게임을 시작하려면 준비 버튼을 눌러주세요.';
        }

        if (data.type === 'start_game') {
            isGameStarted = true;
            readyButton.style.display = 'none';
            waitMessageDiv.style.display = 'none';
        }

        if (data.type === 'game_state') {
            const gameState = data.data;
            restoreGameState(gameState);
        }

        if (data.type === 'game_over') {
            gameSocket.close();
            alert(data.winner + '가 5점에 도달하여 승리하였습니다!');
            window.location.hash = '#/';
        }
    };

    window.onload = function() {
        // 만약 이전에 준비 상태였다면, isReady를 true로 설정
        // 로컬 스토리지 등을 사용하여 준비 상태를 저장할 수 있음
        // 예시로는 isReady가 true인지 확인하고 서버에 알림
        if (isReady) {
            gameSocket.send(JSON.stringify({
                'type': 'ready',
                'player': currentUser,
                'ready': isReady
            }));
        }
    };

    // 게임 상태 복원
    function restoreGameState(gameState) {
        // 자신의 ready 상태를 확인하여 isReady 변수와 버튼 텍스트를 업데이트
        const playerData = gameState.players[currentUser];
        if (playerData.ready) {
            isReady = playerData.ready;
            waitMessageDiv.style.display = 'none';
            readyButton.textContent = isReady ? 'Cancel Ready' : 'I\'m Ready!';
            gameSocket.send(JSON.stringify({
                'type': 'ready',
                'player': currentUser,
                'ready': isReady
            }));
        }

        // 3D 오브젝트 위치 업데이트
        const ballData = gameState.ball;
        // 서버의 좌표를 클라이언트의 좌표로 변환
        ball.position.x = mapX(ballData.x);
        ball.position.z = mapZ(ballData.y);
        ball.position.y = 1; // 공의 높이 유지

        const paddle1Data = gameState.players[player1];
        const paddle2Data = gameState.players[player2];

        if (paddle1Data) {
            // 패들 위치를 테이블 범위 내로 제한
            const z1 = Math.max(-PADDLE_LIMIT, Math.min(PADDLE_LIMIT, mapZ(paddle1Data.y + PADDLE_HEIGHT_SERVER / 2)));
            paddle1.position.z = z1;
            player1Score = paddle1Data.score;
        }

        if (paddle2Data) {
            const z2 = Math.max(-PADDLE_LIMIT, Math.min(PADDLE_LIMIT, mapZ(paddle2Data.y + PADDLE_HEIGHT_SERVER / 2)));
            paddle2.position.z = z2;
            player2Score = paddle2Data.score;
        }

        updateScore();
    }

    function updateScore() {
        scoreBoard.textContent = `${player1} : ${player1Score} | ${player2} : ${player2Score}`;
    }

    // 키보드 이벤트 처리
    document.addEventListener('keydown', (e) => {
        if (!isGameStarted) return;

        if (currentUser === player1) {
            if (e.key === 'w') {
                sendPaddleMove(-1);
            }
            if (e.key === 's') {
                sendPaddleMove(1);
            }
        }

        if (currentUser === player2) {
            if (e.key === 'ArrowUp') {
                sendPaddleMove(-1);
            }
            if (e.key === 'ArrowDown') {
                sendPaddleMove(1);
            }
        }
    });

    document.addEventListener('keyup', (e) => {
        if (!isGameStarted) return;

        if (currentUser === player1) {
            if (e.key === 'w' || e.key === 's') {
                sendPaddleStop();
            }
        }

        if (currentUser === player2) {
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                sendPaddleStop();
            }
        }
    });

    function sendPaddleMove(direction) {
        gameSocket.send(JSON.stringify({
            'type': 'paddle_move',
            'player': currentUser,
            'direction': direction
        }));
    }

    function sendPaddleStop() {
        gameSocket.send(JSON.stringify({
            'type': 'paddle_stop',
            'player': currentUser
        }));
    }

    // Ready 버튼 이벤트
    readyButton.onclick = function() {
        isReady = !isReady;
        readyButton.textContent = isReady ? 'Cancel Ready' : 'I\'m Ready!';
        gameSocket.send(JSON.stringify({
            'type': 'ready',
            'player': currentUser,
            'ready': isReady
        }));
    };

    // 창 크기 조정 이벤트
    window.addEventListener('resize', onWindowResize, false);

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    // 애니메이션 루프
    function animate() {
        requestAnimationFrame(animate);

        // 공 회전 애니메이션
        if (isGameStarted) {
            ball.rotation.x += 0.05;
            ball.rotation.z += 0.05;
        }

        renderer.render(scene, camera);
    }
    animate();
} 