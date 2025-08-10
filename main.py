import pygame
from game_logic import MosaicGame, shaded_color, BASE_COLORS

pygame.init()
CELL_SIZE = 60
MARGIN = 20
BOARD_SIZE = 7
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE + MARGIN * 2  # 盤面幅
BOARD_HEIGHT = CELL_SIZE * BOARD_SIZE + MARGIN * 2  # 盤面高さ

# WINDOW_WIDTH = MARGIN * 2 + CELL_SIZE * BOARD_SIZE + MARGIN + BOARD_WIDTH +  150  # 断面ビュー分プラス
WINDOW_WIDTH = MARGIN * 2 + CELL_SIZE * BOARD_SIZE 
WINDOW_HEIGHT = MARGIN * 2 + CELL_SIZE * BOARD_SIZE + 30

game = MosaicGame()
font = pygame.font.SysFont(None, 36)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


def draw_board():
    screen.fill((240, 240, 240))
    offset_x = MARGIN
    offset_y = MARGIN

    for level, board in enumerate(game.boards):
        if not game.level_in_use(level):
            continue

        size = len(board)
        for y in range(size):
            for x in range(size):
                stack = board[y][x]
                rect_x = int(offset_x + x * CELL_SIZE + level * (CELL_SIZE / 2))
                rect_y = int(offset_y + y * CELL_SIZE + level * (CELL_SIZE / 2))
                pygame.draw.rect(screen, (200, 200, 200),
                                 (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 1)
                if stack:
                    base_color = BASE_COLORS[stack[-1]]
                    color = shaded_color(base_color, level)
                    alpha = int(255 * (0.4 + 0.15 * level))
                    if alpha > 255:
                        alpha = 255

                    circle_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    circle_surf.fill((0, 0, 0, 0))
                    pygame.draw.circle(circle_surf, color + (alpha,),
                                       (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2 - 4)
                    screen.blit(circle_surf, (rect_x, rect_y))

    info = f"Turn: {game.current_player} | P1: {game.pieces_left['P1']} | P2: {game.pieces_left['P2']}"
    if game.winner:
        info = f"Winner: {game.winner}"
    text = font.render(info, True, (0, 0, 0))
    screen.blit(text, (MARGIN, WINDOW_HEIGHT - 40))


def draw_side_view(fixed_x=0):
    offset_x = MARGIN + CELL_SIZE * BOARD_SIZE + 50
    offset_y = MARGIN
    for level in range(len(game.boards)):
        board = game.boards[level]
        size = len(board)
        for y in range(size):
            stack = board[y][fixed_x]
            rect_x = offset_x + level * (CELL_SIZE + 2)
            rect_y = offset_y + y * (CELL_SIZE + 2)
            pygame.draw.rect(screen, (180, 180, 180), (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 1)
            if stack:
                base_color = BASE_COLORS[stack[-1]]
                color = shaded_color(base_color, level)
                alpha = int(255 * (0.4 + 0.15 * level))
                alpha = min(alpha, 255)
                circle_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                circle_surf.fill((0, 0, 0, 0))
                pygame.draw.circle(circle_surf, color + (alpha,), (CELL_SIZE // 2, CELL_SIZE // 2),
                                   CELL_SIZE // 2 - 4)
                screen.blit(circle_surf, (rect_x, rect_y))


def get_cell_from_mouse(pos):
    mx, my = pos
    for level in reversed(range(len(game.boards))):
        if not game.level_in_use(level):
            continue
        board = game.boards[level]
        size = len(board)
        base_offset_x = MARGIN
        base_offset_y = MARGIN
        for y in range(size):
            for x in range(size):
                rect_x = int(base_offset_x + x * CELL_SIZE + level * (CELL_SIZE / 2))
                rect_y = int(base_offset_y + y * CELL_SIZE + level * (CELL_SIZE / 2))
                rect = pygame.Rect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
                if rect.collidepoint(mx, my):
                    # 置ける場合のみ上層の空セルを有効にする
                    if level > 0 and len(board[y][x]) == 0:
                        if not game.can_place(level, x, y):
                            continue
                    # print(f"Clicked Level:{level}, X:{x}, Y:{y}")
                    return level, x, y
    return None

def draw_board_perspective():
    offset_x = MARGIN + BOARD_WIDTH +  150  # 左側余白調整
    offset_y = 0 

    for level in range(len(game.boards)):
        board = game.boards[level]
        size = len(board)
        # layer_offset_x = -level * 15  # 階層ごとに左上方向へズレ
        # layer_offset_y = -level * 10
        layer_offset_x = -level * 20  # 好みの調整値に変えてみてください
        layer_offset_y = -level * 10

        for y in range(size):
            for x in range(size):
                stack = board[y][x]
                if not stack:
                    continue

                # レイヤーが0なら左上基準
                # レイヤーが1以上なら「正方形の中心」に移動
                if level == 0:
                    draw_x = offset_x + x * CELL_SIZE + layer_offset_x
                    draw_y = offset_y + y * CELL_SIZE + layer_offset_y
                else:
                    # 正方形の中心にずらす（セル半分ずつ）
                    draw_x = offset_x + x * CELL_SIZE + CELL_SIZE // 2 + layer_offset_x
                    draw_y = offset_y + y * CELL_SIZE + CELL_SIZE // 2 + layer_offset_y

                base_color = BASE_COLORS[stack[-1]]
                color = shaded_color(base_color, level)

                pygame.draw.circle(screen, color, (draw_x, draw_y), CELL_SIZE // 2 - 4)

def main_loop():
    clock = pygame.time.Clock()
    # fixed_x = 0  # 断面ビューで表示する列

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         fixed_x = max(0, fixed_x - 1)
            #     elif event.key == pygame.K_RIGHT:
            #         fixed_x = min(BOARD_SIZE - 1, fixed_x + 1)

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.winner:
                cell = get_cell_from_mouse(event.pos)
                if cell:
                    level, x, y = cell
                    if game.can_place(level, x, y):
                        game.place_piece(game.current_player, level, x, y)

        draw_board()
        # draw_side_view(fixed_x)
        # draw_board_perspective()

        pygame.display.flip()
        clock.tick(30)

    # 終了時に基層空きマスをログ出力
    # level = 0
    # board = game.boards[level]
    # size = len(board)
    # empty_positions = [(x, y) for y in range(size) for x in range(size) if len(board[y][x]) == 0]
    # print(f"Base empty positions: {empty_positions}")


if __name__ == "__main__":
    main_loop()
    pygame.quit()
