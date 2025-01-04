document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const status = document.getElementById('status');
    const resetButton = document.getElementById('reset-button');

    const updateBoard = (gameState) => {
        gameState.grid.forEach((row, i) => {
            row.forEach((cell, j) => {
                const cellElement = document.querySelector(`[data-row="${i}"][data-col="${j}"]`);
                cellElement.textContent = cell || '';
            });
        });

        if (gameState.winner) {
            status.textContent = `Player ${gameState.winner} wins!`;
            status.classList.add('winner');
        } else if (gameState.is_draw) {
            status.textContent = "It's a draw!";
            status.classList.add('draw');
        } else {
            status.textContent = `Player ${gameState.current_player}'s Turn`;
            status.classList.remove('winner', 'draw');
        }
    };

    const makeMove = async (row, col) => {
        try {
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    row: row,
                    col: col,
                    player: status.textContent.includes('X') ? 'X' : 'O'
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail);
            }

            const gameState = await response.json();
            updateBoard(gameState);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const resetGame = async () => {
        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
            });
            const gameState = await response.json();
            updateBoard(gameState);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            makeMove(row, col);
        });
    });

    resetButton.addEventListener('click', resetGame);

    // Initial game state
    fetch('/api/game')
        .then(response => response.json())
        .then(gameState => updateBoard(gameState))
        .catch(error => console.error('Error:', error));
}); 