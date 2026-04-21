import os
import sys
import random
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5), #上
    pg.K_DOWN: (0, 5), #下
    pg.K_LEFT: (-5, 0), #左
    pg.K_RIGHT: (5, 0) #右
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面内か画面外かを判定する関数
    引数：こうかとんRectまたは爆弾Rect
    戻り値：横方向，縦方向判定結果（True: 画面内，False: 画面外）
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: #横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向判定
        tate = False
    return yoko, tate


# ゲームオーバー
def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面の描写の関数
    """
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)

    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    overlay.blit(txt, (WIDTH//2 - 120, HEIGHT//2 - 40))

    go_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    overlay.blit(go_img, (WIDTH//2 - 200, HEIGHT//2 - 50))
    overlay.blit(go_img, (WIDTH//2 + 200, HEIGHT//2 - 50))

    screen.blit(overlay, (0, 0))
    pg.display.update()
    time.sleep(5)


def create_bomb_list():
    """
    爆弾の大きさ違いSurfaceリストと加速度リスト
    戻り値：(爆弾Surfaceリスト, 加速度リスト)
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)

    bb_accs = [a for a in range(1, 11)]

    return bb_imgs, bb_accs


def create_kk_imgs():
    img = pg.image.load("fig/3.png")

    kk_imgs = {
        (0, 0): pg.transform.rotozoom(img, 0, 0.9),   # 正面

        (5, 0): pg.transform.flip(
            pg.transform.rotozoom(img, 0, 0.9),
            True, False
        ),  # 右

        (-5, 0): pg.transform.rotozoom(img, 0, 0.9),  # 左

        (0, -5): pg.transform.rotozoom(img, -90, 0.9), # 上

        (0, 5): pg.transform.flip(
            pg.transform.rotozoom(img, 90, 0.9),
            True, False
        ),  # 下

        # ■ ここから斜め
        (5, -5): pg.transform.flip(
            pg.transform.rotozoom(img, -45, 0.9),
            True, False
        ),  # 右上

        (5, 5): pg.transform.flip(
            pg.transform.rotozoom(img, 45, 0.9),
            True, False
        ),  # 右下

        (-5, -5): pg.transform.rotozoom(img, -45, 0.9),  # 左上

        (-5, 5): pg.transform.rotozoom(img, 45, 0.9),     # 左下
    }

    return kk_imgs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    font = pg.font.Font(None, 80)
    go_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)  
    overlay = pg.Surface((WIDTH, HEIGHT)) # ゲームオーバー画面
    
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()  # 爆弾Rectを取得する
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾の初期横座標を設定する
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾の初期縦座標を設定する
    vx, vy = +5, +5  # 爆弾の速度

    clock = pg.time.Clock()
    tmr = 0
    
    bb_imgs, bb_accs = create_bomb_list()

    kk_imgs = create_kk_imgs()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外だったら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        mv = (sum_mv[0], sum_mv[1]) # 画像切り替え
        if mv in kk_imgs:
            kk_img = kk_imgs[mv]

        screen.blit(kk_img, kk_rct)

        avx = vx * bb_accs[min(tmr//500, 9)]
        avy = vy * bb_accs[min(tmr//500, 9)] #爆弾速度
        
        bb_img = bb_imgs[min(tmr//500, 9)]
        bb_rct.move_ip(avx, avy)
        
        bb_rct.width = bb_img.get_width()   
        bb_rct.height = bb_img.get_height()

        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向の判定
            vx *= -1
        if not tate:  # 縦方向の判定
            vy *= -1

        screen.blit(bb_img, bb_rct)  # 爆弾を表示させる
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()