const socket = io();

// Listen for score updates
socket.on('update_scores', data => {
    const scores = data.scores;
    const doubleRounds = data.double_rounds;
    const totals = data.totals;

    for (const team in scores) {
        scores[team].forEach((score, round) => {
            const cell = document.querySelector(`#score_${team.replaceAll(" ", "")}_${round + 1}`);
            console.log(cell);
            if (cell) cell.value = score;
        });

        const doubleRound = doubleRounds[team];
        if (doubleRound) {
            const radio = document.querySelector(`#double_${team.replaceAll(" ", "")}_${doubleRound}`);
            if (radio) radio.checked = true;
        }

        const totalCell = document.querySelector(`#total_${team.replaceAll(" ", "")}`);
        if (totalCell) totalCell.textContent = totals[team];
    }
});

// Listen for single cell updates
socket.on('update_single_cell', data => {
    const { team, round_num, score, total_score } = data;

    // Update only the specified cell if round_num is provided
    if (round_num) {
        const cell = document.querySelector(`#score_${team.replaceAll(" ", "")}_${round_num}`);
        if (cell) {
            cell.value = score;
        }
    }

    // Update the total score for the team
    const totalCell = document.querySelector(`#total_${team.replaceAll(" ", "")}`);
    if (totalCell) {
        totalCell.textContent = total_score;
    }
});

function updateScore(team, roundNum, score) {
    if (score.length == 0) {
        return;
    }

    socket.emit('update_score', { team, round_num: roundNum, score });
}

function updateDoubleRound(team, roundNum) {
    socket.emit('update_double_round', { team, round_num: roundNum });
}