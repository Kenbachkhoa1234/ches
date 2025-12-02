import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from BE.chess_engine import ChessEngine
import json
import random
import string
import uuid
import chess

app = Flask(__name__, 
            static_folder='../FE', 
            template_folder='../FE')

# --- Quản lý trạng thái Game ---
games = {}
rooms = {}
room_players = {}

def generate_room_code():
    """Tạo mã phòng ngẫu nhiên 6 chữ số."""
    return ''.join(random.choices(string.digits.replace('0', ''), k=6))

@app.route('/')
def index():
    """Phục vụ trang HTML chính."""
    return render_template('multiplayer.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/create_room', methods=['POST'])
def create_room_api():
    """API để tạo phòng (REST thay vì WebSocket)"""
    room_code = generate_room_code()
    game_id = str(uuid.uuid4())
    engine = ChessEngine()
    
    games[game_id] = {
        'engine': engine, 
        'mode': 'Multiplayer',
        'status': 'waiting'
    }
    rooms[room_code] = game_id
    room_players[game_id] = {}
    
    return jsonify({
        'type': 'room_created',
        'room_code': room_code,
        'player_color': 'white',
        'game_id': game_id,
        'message': f'Phòng tạo thành công. Mã phòng: {room_code}'
    })

@app.route('/api/join_room/<room_code>', methods=['POST'])
def join_room_api(room_code):
    """API để tham gia phòng"""
    game_id = rooms.get(room_code)
    
    if not game_id:
        return jsonify({
            'type': 'error',
            'message': 'Mã phòng không tồn tại!'
        }), 404
    
    game_data = games.get(game_id)
    players = room_players.get(game_id, {})
    
    if len(players) >= 1:
        return jsonify({
            'type': 'error',
            'message': 'Phòng đã đầy (2/2 người chơi)!'
        }), 400
    
    # Thêm người chơi thứ 2
    session_id = str(uuid.uuid4())
    players[session_id] = 'black'
    room_players[game_id] = players
    games[game_id]['status'] = 'playing'
    
    status = game_data['engine'].get_status()
    
    return jsonify({
        'type': 'game_start',
        'player_color': 'black',
        'game_id': game_id,
        'session_id': session_id,
        'game_status': status,
        'message': f'Trò chơi bắt đầu! Bạn đóng vai trò: Đen'
    })

@app.route('/api/get_game/<game_id>', methods=['GET'])
def get_game(game_id):
    """Lấy trạng thái game hiện tại"""
    game_data = games.get(game_id)
    if not game_data:
        return jsonify({'error': 'Game not found'}), 404
    
    status = game_data['engine'].get_status()
    return jsonify({'game_status': status})

@app.route('/api/make_move/<game_id>', methods=['POST'])
def make_move_api(game_id):
    """Thực hiện nước đi"""
    game_data = games.get(game_id)
    if not game_data:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    uci_move = data.get('uci')
    player_color = data.get('player_color')
    
    engine = game_data['engine']
    
    # Kiểm tra lượt đi
    current_turn = 'white' if engine.board.turn == chess.WHITE else 'black'
    if player_color != current_turn:
        return jsonify({
            'type': 'error',
            'message': 'Không phải lượt của bạn!'
        }), 400
    
    # Thực hiện nước đi
    if engine.make_move(uci_move):
        new_status = engine.get_status()
        
        # Kiểm tra kết thúc game
        if engine.is_game_over():
            outcome = engine.board.outcome()
            result = outcome.result() if outcome else None
            
            return jsonify({
                'type': 'game_over',
                'game_status': new_status,
                'result': result,
                'message': f'Trò chơi kết thúc. Kết quả: {result}'
            })
        
        return jsonify({
            'type': 'move_update',
            'game_status': new_status,
            'last_move_by': player_color
        })
    else:
        return jsonify({
            'type': 'error',
            'message': 'Nước đi không hợp lệ!'
        }), 400

@app.route('/api/resign/<game_id>', methods=['POST'])
def resign_api(game_id):
    """Đầu hàng"""
    game_data = games.get(game_id)
    if not game_data:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    player_color = data.get('player_color')
    
    opponent_color = 'black' if player_color == 'white' else 'white'
    result = '0-1' if player_color == 'white' else '1-0'
    
    # Dọn dẹp
    room_code = next((code for code, gid in rooms.items() if gid == game_id), None)
    if room_code:
        del rooms[room_code]
    if game_id in games:
        del games[game_id]
    if game_id in room_players:
        del room_players[game_id]
    
    return jsonify({
        'type': 'game_over',
        'result': result,
        'message': f'Bạn đã đầu hàng. Kết quả: {result}'
    })

# For Vercel
def handler(request):
    return app(request)
