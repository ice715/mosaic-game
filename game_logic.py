# game_logic.py

BOARD_SIZES = [7, 6, 5, 4, 3, 2, 1]

NEUTRAL = "N"
PLAYER1 = "P1"
PLAYER2 = "P2"

BASE_COLORS = {
    NEUTRAL: (150, 150, 150),
    # PLAYER1: (200, 50, 50),
    PLAYER1: (50, 200, 50),
    PLAYER2: (50, 50, 200)
}

def shaded_color(base_color, level):
    factor = 1.0 - level * 0.15
    if factor < 0.15:
        factor = 0.15
    return tuple(int(c * factor) for c in base_color)


class MosaicGame:
    def __init__(self):
        self.boards = [
            [[[] for _ in range(size)] for _ in range(size)]
            for size in BOARD_SIZES
        ]
        center = BOARD_SIZES[0] // 2
        self.boards[0][center][center].append(NEUTRAL)

        self.current_player = PLAYER1
        self.winner = None
        self.pieces_left = {PLAYER1: 70, PLAYER2: 70}

    def level_in_use(self, level):
        size = len(self.boards[level])
        # 駒があるか
        if any(len(self.boards[level][y][x]) > 0 for y in range(size) for x in range(size)):
            return True
        # 置ける可能性の判定（下層で正方形できてるか）
        if level > 0:
            lower_size = len(self.boards[level - 1])
            lower = self.boards[level - 1]
            for y in range(lower_size - 1):
                for x in range(lower_size - 1):
                    square = [lower[y][x], lower[y][x + 1], lower[y + 1][x], lower[y + 1][x + 1]]
                    if all(len(s) > 0 for s in square):
                        return True
        return False
    
    def can_place(self, level, x, y):
        size = len(self.boards[level])
        if x < 0 or y < 0 or x >= size or y >= size:
            return False
        if len(self.boards[level][y][x]) > 0:
            # すでに置かれてるので置けない
            return False

        if level == 0:
            # 基層は空いていればどこでも置ける
            return True

        else:
            lower = self.boards[level - 1]
            lower_size = len(lower)
            # 下層の4マスが存在する範囲か確認
            if x + 1 >= lower_size or y + 1 >= lower_size:
                return False

            # 下層の4マスすべてに1つ以上駒があるか？
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                if len(lower[y + dy][x + dx]) == 0:
                    return False
            # 上層のここは空き（既に判定済み）なので置ける
            return True

    def place_piece(self, player, level, x, y, auto=False):
        if self.winner:
            return False
        if player != self.current_player and not auto:
            return False
        if not self.can_place(level, x, y):
            return False

        self.boards[level][y][x].append(player)
        # if not auto:
        self.pieces_left[player] -= 1
        if self.pieces_left[player] == 0:
            self.winner = player
            return True

        self._check_and_auto_place(level)

        if not auto:
            self.current_player = PLAYER1 if self.current_player == PLAYER2 else PLAYER2
        return True

    def _check_and_auto_place(self, level):
        if level + 1 >= len(self.boards):
            return
        size = len(self.boards[level])
        for y in range(size - 1):
            for x in range(size - 1):
                square = [
                    self.boards[level][y][x],
                    self.boards[level][y][x + 1],
                    self.boards[level][y + 1][x],
                    self.boards[level][y + 1][x + 1]
                ]
                if all(len(s) > 0 for s in square):
                    top_colors = [s[-1] for s in square]
                    target_color = self._auto_color(top_colors)
                    if target_color:
                        # 自動配置は強制的に置く
                        self.place_piece(target_color, level + 1, x, y, auto=True)

    def _auto_color(self, colors):
        if colors.count(NEUTRAL) > 1:
            return None
        if NEUTRAL not in colors:
            for c in (PLAYER1, PLAYER2):
                if colors.count(c) >= 3:
                    return c
        else:
            others = [c for c in colors if c != NEUTRAL]
            if len(set(others)) == 1:
                return others[0]
        return None
