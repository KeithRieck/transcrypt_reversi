import eval_functions
from bedlam import Game
from bedlam import Scene
from board import BLACK
from board import Board
from board import WHITE

# __pragma__('skip')
document = window = Math = Date = console = 0  # Prevent complaints by optional static checker
# __pragma__('noskip')
# __pragma__('noalias', 'clear')

WHITE_TO_MOVE_STATE = 'WHITE_TO_MOVE_STATE'
BLACK_TO_MOVE_STATE = 'BLACK_TO_MOVE_STATE'
GAME_OVER_STATE = 'GAME_OVER_STATE'
THINK_TIME = 2 * 1000
DISPLAY_TIME = 3 * 1000


class ReversiScene(Scene):
    def __init__(self, game, name):
        Scene.__init__(self, game, name)
        self.current_board = None
        self.radius = 20
        self.padding = 8
        self.px = 10
        self.py = 20
        self.hoverX = None
        self.hoverY = None
        self.eval_function = eval_functions.F1()
        self.game_state = WHITE_TO_MOVE_STATE
        self.think_until = -1
        self.display_until = -1
        self.display = ''
        self.consecutive_passes = 0

    def set_current_board(self, board):
        self.current_board = board

    def __find_cell(self, mouse_x, mouse_y):
        r = 2 * self.radius + 2 * self.padding
        x = Math.floor((mouse_x - self.px - self.padding) / r)
        y = Math.floor((mouse_y - self.py - self.padding) / r)
        if x < 0 or x >= 8 or y < 0 or y >= 8:
            return None, None
        return x, y

    def __handle_mouseup(self, event):
        x, y = self.__find_cell(event.offsetX, event.offsetY)
        console.log('click:  cell=' + x + ',' + y + '    ' + self.current_board.is_piece(x, y))
        if self.game_state == WHITE_TO_MOVE_STATE:
            move = self.current_board.is_move(x, y)
            if move is not None:
                self.__make_move(move)

    def __handle_mousemove(self, event):
        self.hoverX, self.hoverY = self.__find_cell(event.offsetX, event.offsetY)

    def __make_move(self, move):
        console.log('\n\n- - - - - - - - - - - - - \n')
        console.log(self.current_board.show())
        if move is not None:
            console.log('Move = ' + move.x + ',' + move.y + '  : ' + move.player)
            self.current_board = Board(self.current_board, move)
            self.consecutive_passes = 0
        else:
            console.log('PASS: ' + self.current_board.next_player())
            self.__display_message('PASS: ' + self.current_board.next_player())
            self.current_board.switch_player()
            self.consecutive_passes = self.consecutive_passes + 1
        self.game_state = BLACK_TO_MOVE_STATE if self.game_state == WHITE_TO_MOVE_STATE else WHITE_TO_MOVE_STATE
        self.think_until = -1
        if len(self.current_board) == 64 or self.consecutive_passes >= 2 \
                or self.current_board.count(WHITE) == 0 or self.current_board.count(BLACK) == 0:
            self.__display_message('Game over')
            self.game_state = GAME_OVER_STATE
        console.log(self.current_board.show())
        console.log('State = ' + self.game_state)
        console.log('- - - - - - - - - - - - - \n\n')

    def __display_message(self, message):
        self.display_until = self.game.get_time() + DISPLAY_TIME
        self.display = message

    def __draw_board(self, ctx):
        r = 2 * self.radius + 2 * self.padding
        bsize = 8 * r + self.padding
        ctx.save()
        ctx.strokeStyle = '#666666'
        ctx.lineWidth = 1
        ctx.beginPath()
        for n in range(8 + 1):
            ctx.moveTo(self.px + self.padding, self.py + self.padding + n * r)
            ctx.lineTo(self.px + self.padding + 8 * r, self.py + self.padding + n * r)
            ctx.moveTo(self.px + self.padding + n * r, self.py + self.padding)
            ctx.lineTo(self.px + self.padding + n * r, self.py + self.padding + 8 * r)
        ctx.stroke()
        ctx.strokeStyle = 'black'
        ctx.lineWidth = 2
        if self.current_board is not None:
            for x in range(8):
                for y in range(8):
                    if self.current_board.is_piece(x, y) is None:
                        continue
                    ctx.beginPath()
                    ctx.fillStyle = '#000000' if self.current_board.is_piece(x, y) == BLACK else '#CCCCCC'
                    ctx.moveTo((x + 1) * r + self.radius - self.padding, (y + 1) * r)
                    ctx.arc((x + 1) * r - self.padding, (y + 1) * r, self.radius, 0, 2 * Math.PI)
                    ctx.fill()
        if self.hoverX is not None and self.current_board.is_move(self.hoverX, self.hoverY):
            ctx.strokeStyle = '#CCCCCC'
            ctx.beginPath()
            ctx.moveTo((self.hoverX + 1) * r + self.radius - self.padding, (self.hoverY + 1) * r)
            ctx.arc((self.hoverX + 1) * r - self.padding, (self.hoverY + 1) * r, self.radius, 0, 2 * Math.PI)
            ctx.stroke()
        ctx.fillStyle = 'green'
        ctx.fillRect(self.px, self.py, self.px + bsize, self.py + bsize)
        ctx.fillStyle = 'black'
        ctx.font = '18pt sans-serif'
        tx = self.px + bsize + 20
        ty = self.py + r - 10
        ctx.fillText('WHITE: ' + self.current_board.count(WHITE), tx, ty)
        ty = ty + 32
        ctx.fillText('BLACK: ' + self.current_board.count(BLACK), tx, ty)
        ty = ty + 32
        if self.game_state == GAME_OVER_STATE:
            if self.current_board.count(WHITE) > self.current_board.count(BLACK):
                ctx.fillText('WHITE wins', tx, ty)
            else:
                ctx.fillText('BLACK wins', tx, ty)
        else:
            ctx.fillText(self.current_board.next_player() + ' to play', tx, ty)
        ty = ty + 32
        if self.display_until > 0:
            ctx.fillText(self.display, tx, ty)
            if self.game.get_time() > self.display_until:
                self.display_until = -1
        ctx.restore()

    def draw(self, ctx):
        Scene.draw(self, ctx)
        self.__draw_board(ctx)

    def update(self, delta_time):
        Scene.update(self, delta_time)
        if self.game_state == BLACK_TO_MOVE_STATE:
            if self.think_until < 0:
                self.think_until = self.game.get_time() + THINK_TIME
            if self.game.get_time() < self.think_until:
                self.__search(self.current_board)
                return
            if self.current_board.move_count() == 0:
                self.__make_move(None)
                return
            best_move = self.__search(self.current_board)
            if best_move is not None:
                self.__make_move(best_move)

    def __search(self, board):
        move = board.next_pending_move()
        if move is not None:
            if move.board is None:
                move.board = Board(self.current_board, move)
            self.eval_function.eval_move(move.board, move)
            return None
        else:
            return board.best_move()


class ReversiGame(Game):
    def __init__(self, loop_time=20):
        Game.__init__(self, 'Reversi', loop_time)
        scene = ReversiScene(self, 'REVERSI')
        self.append(scene)
        b = Board()
        scene.set_current_board(b)