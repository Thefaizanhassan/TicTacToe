from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Game state
class GameState:
    def __init__(self):
        self.grid = [[None]*3 for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.is_draw = False

game = GameState()

class Move(BaseModel):
    row: int
    col: int
    player: str

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/game")
async def get_game_state():
    return {
        "grid": game.grid,
        "current_player": game.current_player,
        "winner": game.winner,
        "is_draw": game.is_draw
    }

@app.post("/api/move")
async def make_move(move: Move):
    if game.winner or game.is_draw:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game.grid[move.row][move.col] is not None:
        raise HTTPException(status_code=400, detail="Cell already occupied")
    
    if move.player != game.current_player:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    game.grid[move.row][move.col] = move.player
    
    # Check for winner
    game.winner = check_winner(game.grid)
    
    # Check for draw
    if not game.winner and all(all(cell is not None for cell in row) for row in game.grid):
        game.is_draw = True
    
    # Switch player
    if not game.winner and not game.is_draw:
        game.current_player = 'O' if game.current_player == 'X' else 'X'
    
    return {
        "grid": game.grid,
        "current_player": game.current_player,
        "winner": game.winner,
        "is_draw": game.is_draw
    }

@app.post("/api/reset")
async def reset_game():
    game.__init__()
    return {
        "grid": game.grid,
        "current_player": game.current_player,
        "winner": game.winner,
        "is_draw": game.is_draw
    }

def check_winner(grid):
    # Check rows
    for row in grid:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    
    # Check columns
    for col in range(3):
        if grid[0][col] == grid[1][col] == grid[2][col] and grid[0][col] is not None:
            return grid[0][col]
    
    # Check diago\'nals
    if grid[0][0] == grid[1][1] == grid[2][2] and grid[0][0] is not None:
        return grid[0][0]
    if grid[0][2] == grid[1][1] == grid[2][0] and grid[0][2] is not None:
        return grid[0][2]
    
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 