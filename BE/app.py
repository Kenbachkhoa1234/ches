# backend/app.py

from flask import Flask, render_template, request, jsonify # type: ignore
from flask_sock import Sock # type: ignore
from chess_engine import ChessEngine
import json
import random
import string
import uuid
import chess

app = Flask(__name__, 
            static_folder='../FE', 
            template_folder='../FE')
sock = Sock(app)

# --- Quản lý trạng thái Game ---
games = {} # {game_id: game_data}
rooms = {} # {room_code: game_id}
room_players = {} # {game_id: {session_id: 'color'}}

# --- Quản lý WebSocket Sessions ---
ws_sessions = {} # {session_id: ws}

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

# --- WebSocket cho Multiplayer (Tạo phòng / Tham gia phòng) ---

@sock.route('/ws/multiplayer')
def multiplayer_ws(ws):
    session_id = str(uuid.uuid4())
    ws_sessions[session_id] = ws
    print(f"[WS] New connection: {session_id}")
    current_game_id = None

    try:
        while True:
            data = ws.receive()
            if data is None:
                break
                
            message = json.loads(data)
            action = message.get('action')
            
            # --- 1. Tạo phòng mới ---
            if action == 'create_room':
                room_code = generate_room_code()
                game_id = str(uuid.uuid4())
                engine = ChessEngine()
                
                games[game_id] = {
                    'engine': engine, 
                    'mode': 'Multiplayer',
                    'status': 'waiting'
                }
                rooms[room_code] = game_id
                room_players[game_id] = {session_id: 'white'}
                current_game_id = game_id
                
                print(f"[WS] Room created: {room_code} (Game ID: {game_id})")
                
                ws.send(json.dumps({
                    'type': 'room_created',
                    'room_code': room_code,
                    'player_color': 'white',
                    'game_id': game_id,
                    'message': f'Phòng tạo thành công. Mã phòng: {room_code}. Đợi người chơi khác...'
                }))
            
            # --- 2. Tham gia phòng ---
            elif action == 'join_room':
                room_code = message.get('room_code')
                game_id = rooms.get(room_code)
                
                if not game_id:
                    ws.send(json.dumps({
                        'type': 'error',
                        'message': 'Mã phòng không tồn tại!'
                    }))
                    continue
                
                game_data = games.get(game_id)
                players = room_players.get(game_id, {})
                
                if len(players) >= 2:
                    ws.send(json.dumps({
                        'type': 'error',
                        'message': 'Phòng đã đầy (2/2 người chơi)!'
                    }))
                    continue
                
                # Thêm người chơi thứ 2 (màu đen)
                players[session_id] = 'black'
                room_players[game_id] = players
                current_game_id = game_id
                games[game_id]['status'] = 'playing'
                
                print(f"[WS] Player joined room {room_code}")
                
                # Thông báo cho cả hai người chơi
                status = game_data['engine'].get_status()
                for sid, color in players.items():
                    if sid in ws_sessions:
                        ws_sessions[sid].send(json.dumps({
                            'type': 'game_start',
                            'player_color': color,
                            'game_id': game_id,
                            'game_status': status,
                            'message': f'Trò chơi bắt đầu! Bạn đóng vai trò: {"Trắng (Đi trước)" if color == "white" else "Đen"}'
                        }))
            
            # --- 3. Thực hiện nước đi ---
            elif action == 'move':
                if not current_game_id or current_game_id not in games:
                    ws.send(json.dumps({
                        'type': 'error',
                        'message': 'Game không tồn tại!'
                    }))
                    continue
                
                uci_move = message.get('uci')
                game_data = games[current_game_id]
                engine = game_data['engine']
                players = room_players.get(current_game_id, {})
                player_color = players.get(session_id)
                
                # Kiểm tra lượt đi
                current_turn = 'white' if engine.board.turn == chess.WHITE else 'black'
                if player_color != current_turn:
                    ws.send(json.dumps({
                        'type': 'error',
                        'message': 'Không phải lượt của bạn!'
                    }))
                    continue
                
                # Thực hiện nước đi
                if engine.make_move(uci_move):
                    new_status = engine.get_status()
                    
                    # Gửi trạng thái mới cho tất cả người chơi
                    for sid, color in players.items():
                        if sid in ws_sessions:
                            ws_sessions[sid].send(json.dumps({
                                'type': 'move_update',
                                'game_status': new_status,
                                'last_move_by': player_color
                            }))
                    
                    # Kiểm tra kết thúc game
                    if engine.is_game_over():
                        outcome = engine.board.outcome()
                        result = outcome.result() if outcome else None
                        
                        for sid in players.keys():
                            if sid in ws_sessions:
                                ws_sessions[sid].send(json.dumps({
                                    'type': 'game_over',
                                    'result': result,
                                    'message': f'Trò chơi kết thúc. Kết quả: {result}'
                                }))
                else:
                    ws.send(json.dumps({
                        'type': 'error',
                        'message': 'Nước đi không hợp lệ!'
                    }))
            
            # --- 4. Lấy trạng thái hiện tại ---
            elif action == 'get_status':
                if current_game_id and current_game_id in games:
                    game_data = games[current_game_id]
                    engine = game_data['engine']
                    status = engine.get_status()
                    
                    ws.send(json.dumps({
                        'type': 'status',
                        'game_status': status
                    }))
            
            # --- 5. Lấy danh sách nước đi hợp lệ ---
            elif action == 'get_legal_moves':
                if current_game_id and current_game_id in games:
                    game_data = games[current_game_id]
                    engine = game_data['engine']
                    
                    ws.send(json.dumps({
                        'type': 'legal_moves',
                        'moves': [move.uci() for move in engine.board.legal_moves]
                    }))
            
            # --- 6. Kết thúc game ---
            elif action == 'resign':
                if current_game_id and current_game_id in games:
                    players = room_players.get(current_game_id, {})
                    player_color = players.get(session_id)
                    opponent_color = 'black' if player_color == 'white' else 'white'
                    
                    for sid, color in players.items():
                        if sid in ws_sessions:
                            msg = f'Bạn thắng! Đối thủ ({player_color}) đã đầu hàng.' if color != player_color else f'Bạn đã đầu hàng. Đối thủ ({opponent_color}) thắng.'
                            ws_sessions[sid].send(json.dumps({
                                'type': 'game_over',
                                'result': f'0-1' if player_color == 'white' else '1-0',
                                'message': msg
                            }))
                    
                    # Dọn dẹp
                    room_code = next((code for code, gid in rooms.items() if gid == current_game_id), None)
                    if room_code:
                        del rooms[room_code]
                    del games[current_game_id]
                    del room_players[current_game_id]
                    current_game_id = None
            
    except Exception as e:
        print(f"[WS] Error for {session_id}: {e}")
    finally:
        print(f"[WS] Connection closed: {session_id}")
        if session_id in ws_sessions:
            del ws_sessions[session_id]

if __name__ == '__main__':
    # Chạy trên cổng 5000
    app.run(debug=True, host='0.0.0.0', port=5000)