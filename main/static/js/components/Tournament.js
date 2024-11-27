export default async function Tournament() {
    const template = `
        <div class="tournament-container">
            <div class="tournament-bracket">
                <!-- 4강 -->
                <div class="round">
                    <div class="round-title">준결승</div>
                    <div class="match" id="semifinal1">
                        <div class="match-date">2024.10.24 19:00</div>
                        <div class="team" id="team1">
                            <div class="team-logo">1</div>
                            <div class="team-name">Player 1</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="team" id="team2">
                            <div class="team-logo">2</div>
                            <div class="team-name">Player 2</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="connector"></div>
                    </div>
                    <div class="match" id="semifinal2">
                        <div class="match-date">2024.10.24 21:00</div>
                        <div class="team" id="team3">
                            <div class="team-logo">3</div>
                            <div class="team-name">Player 3</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="team" id="team4">
                            <div class="team-logo">4</div>
                            <div class="team-name">Player 4</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="connector"></div>
                    </div>
                </div>

                <!-- 결승 -->
                <div class="round">
                    <div class="round-title">결승전</div>
                    <div class="match" id="final">
                        <div class="match-date">2024.10.27 19:00</div>
                        <div class="team" id="finalist1">
                            <div class="team-logo">?</div>
                            <div class="team-name">미정</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="team" id="finalist2">
                            <div class="team-logo">?</div>
                            <div class="team-name">미정</div>
                            <div class="team-score"></div>
                        </div>
                        <div class="connector"></div>
                    </div>
                </div>

                <!-- 우승자 -->
                <div class="round">
                    <div class="round-title">우승팀</div>
                    <div class="champion">
                        <div class="champion-team" id="champion">
                            <div class="trophy-icon">🏆</div>
                            <div class="champion-logo">?</div>
                            <div class="champion-name">미정</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 닉네임 입력 버튼 -->
            <div class="nickname-buttons">
                <button class="nickname-button" data-player="1">Enter Player 1</button>
                <button class="nickname-button" data-player="2">Enter Player 2</button>
                <button class="nickname-button" data-player="3">Enter Player 3</button>
                <button class="nickname-button" data-player="4">Enter Player 4</button>
            </div>

            <!-- 게임 시작 버튼 -->
            <div>
                <button class="nickname-button" id="startSemifinal1">게임 시작 (준결승 1)</button>
                <button class="nickname-button" id="startSemifinal2" style="display: none;">게임 시작 (준결승 2)</button>
                <button class="nickname-button" id="startFinal" style="display: none;">결승전 시작</button>
            </div>
        </div>
    `;

    setTimeout(() => {
        const tournament = initializeTournament();
        
        document.querySelectorAll('.nickname-button[data-player]').forEach(button => {
            button.addEventListener('click', () => {
                const player = parseInt(button.dataset.player);
                tournament.setNickname(button, player);
            });
        });

        tournament.restoreState();
        tournament.initializeEventListeners();
    }, 0);

    return template;
}

function initializeTournament() {
    const tournamentState = {
        nicknames: {},
        semifinal1Winner: null,
        semifinal1WinnerLog: null,
        semifinal2Winner: null,
        semifinal2WinnerLog: null,
        champion: null,
        currentStage: 'semifinal1'
    };

    // 저장된 상태가 있으면 복원
    const savedState = localStorage.getItem('tournamentState');
    if (savedState) {
        const state = JSON.parse(savedState);
        Object.assign(tournamentState, state);
    }

    return {
        setNickname: function(button, player) {
            let nickname = prompt("Enter your nickname:");
            if (nickname) {
                button.textContent = nickname;
                tournamentState.nicknames[player] = nickname;
                this.updateBracket(player, nickname);
                this.saveState();
            }
        },

        saveState: function() {
            localStorage.setItem('tournamentState', JSON.stringify(tournamentState));
        },

        clearTournamentStorage: function() {
            localStorage.removeItem('tournamentState');
            localStorage.removeItem('currentMatch');
            localStorage.removeItem('player1');
            localStorage.removeItem('player2');
            localStorage.removeItem('matchResult');
            localStorage.removeItem('winner');
        },

        updateBracket: function(player, nickname) {
            const teamElement = document.querySelector(`#team${player} .team-name`);
            if (teamElement) {
                teamElement.textContent = nickname;
            }
        },

        handleSemifinal1Result: function(winner, isRestore = false) {
            tournamentState.semifinal1Winner = winner;
            
            // 승자/패자 표시
            const team1 = document.querySelector('#team1');
            const team2 = document.querySelector('#team2');
            if (winner === tournamentState.nicknames[1]) {
                team2.classList.add('eliminated');
                team1.classList.add('winner');
            } else {
                team1.classList.add('eliminated');
                team2.classList.add('winner');
            }
            
            // 결승 진출자 업데이트
            const finalist1 = document.querySelector('#finalist1');
            if (finalist1) {
                finalist1.querySelector('.team-name').textContent = winner;
                finalist1.querySelector('.team-logo').textContent = winner === tournamentState.nicknames[1] ? '1' : '2';
            }
            
            // 버튼 상태 업데이트
            this.updateGameButtons();
            
            if (!isRestore) {
                this.saveState();
            }
        },

        handleSemifinal2Result: function(winner, isRestore = false) {
            tournamentState.semifinal2Winner = winner;
            const finalist2 = document.querySelector('#finalist2');
            if (finalist2) {
                finalist2.querySelector('.team-name').textContent = winner;
                finalist2.querySelector('.team-logo').textContent = '2';
            }
            if (!isRestore) {
                this.saveState();
                this.updateGameButtons();
            }
        },

        handleFinalResult: function(winner, isRestore = false) {
            tournamentState.champion = winner;
            const championElement = document.querySelector('#champion');
            if (championElement) {
                championElement.querySelector('.champion-name').textContent = winner;
                championElement.querySelector('.champion-logo').textContent = '👑';
            }
            if (!isRestore) {
                this.saveState();
                this.updateGameButtons();
            }
        },

        updateGameButtons: function() {
            const semifinal1Btn = document.getElementById('startSemifinal1');
            const semifinal2Btn = document.getElementById('startSemifinal2');
            const finalBtn = document.getElementById('startFinal');

            if (tournamentState.semifinal1Winner) {
                semifinal1Btn.style.display = 'none';
                semifinal2Btn.style.display = 'inline';
            }
            if (tournamentState.semifinal2Winner) {
                semifinal2Btn.style.display = 'none';
                finalBtn.style.display = 'inline';
            }
            if (tournamentState.champion) {
                finalBtn.style.display = 'none';
            }
        },

        restoreState: function() {
            // 닉네임 버튼 상태 복원
            Object.entries(tournamentState.nicknames).forEach(([player, nickname]) => {
                const button = document.querySelector(`button[data-player="${player}"]`);
                if (button) {
                    button.textContent = nickname;
                    this.updateBracket(parseInt(player), nickname);
                }
            });

            // 게임 진행 상태 복원
            if (tournamentState.semifinal1Winner) {
                this.handleSemifinal1Result(tournamentState.semifinal1Winner, true);
            }
            if (tournamentState.semifinal2Winner) {
                this.handleSemifinal2Result(tournamentState.semifinal2Winner, true);
            }
            if (tournamentState.champion) {
                this.handleFinalResult(tournamentState.champion, true);
            }

            // 버튼 상태 명시적 업데이트
            const semifinal1Btn = document.getElementById('startSemifinal1');
            const semifinal2Btn = document.getElementById('startSemifinal2');
            const finalBtn = document.getElementById('startFinal');

            if (tournamentState.semifinal1Winner) {
                if (semifinal1Btn) semifinal1Btn.style.display = 'none';
                if (semifinal2Btn) semifinal2Btn.style.display = 'inline';
            }
            if (tournamentState.semifinal2Winner) {
                if (semifinal2Btn) semifinal2Btn.style.display = 'none';
                if (finalBtn) finalBtn.style.display = 'inline';
            }
            if (tournamentState.champion) {
                if (finalBtn) finalBtn.style.display = 'none';
            }
        },

        initializeEventListeners: function() {
            document.getElementById('startSemifinal1').addEventListener('click', () => {
                if (!tournamentState.nicknames[1] || !tournamentState.nicknames[2]) {
                    alert("플레이어 1과 2의 닉네임을 모두 입력해주세요!");
                    return;
                }
                localStorage.setItem('currentMatch', 'semifinal1');
                localStorage.setItem('player1', tournamentState.nicknames[1]);
                localStorage.setItem('player2', tournamentState.nicknames[2]);
                window.history.pushState({}, '', '/tournament/game');
                window.dispatchEvent(new Event('popstate'));
            });

            document.getElementById('startSemifinal2').addEventListener('click', () => {
                if (!tournamentState.nicknames[3] || !tournamentState.nicknames[4]) {
                    alert("플레이어 3과 4의 닉네임을 모두 입력해주세요!");
                    return;
                }
                localStorage.setItem('currentMatch', 'semifinal2');
                localStorage.setItem('player1', tournamentState.nicknames[3]);
                localStorage.setItem('player2', tournamentState.nicknames[4]);
                window.history.pushState({}, '', '/tournament/game');
                window.dispatchEvent(new Event('popstate'));
            });

            document.getElementById('startFinal').addEventListener('click', () => {
                localStorage.setItem('currentMatch', 'final');
                localStorage.setItem('player1', tournamentState.semifinal1Winner);
                localStorage.setItem('player2', tournamentState.semifinal2Winner);
                window.history.pushState({}, '', '/tournament/game');
                window.dispatchEvent(new Event('popstate'));
            });

            const matchResult = localStorage.getItem('matchResult');
            if (matchResult === 'completed') {
                const winner = localStorage.getItem('winner');
                const matchType = localStorage.getItem('currentMatch');
                
                if (matchType === 'semifinal1') {
                    this.handleSemifinal1Result(winner);
                    // 준결승1 버튼 숨기고 준결승2 버튼 보이기
                    const semifinal1Btn = document.getElementById('startSemifinal1');
                    const semifinal2Btn = document.getElementById('startSemifinal2');
                    if (semifinal1Btn) semifinal1Btn.style.display = 'none';
                    if (semifinal2Btn) semifinal2Btn.style.display = 'inline';
                } else if (matchType === 'semifinal2') {
                    this.handleSemifinal2Result(winner);
                } else if (matchType === 'final') {
                    this.handleFinalResult(winner);
                }
                
                localStorage.removeItem('matchResult');
                localStorage.removeItem('winner');
                localStorage.removeItem('currentMatch');
            }
        }
    };
} 