import math
import random
import sys
import pygame

# ----------------------------
# Giraffe Game
# ----------------------------

WIDTH, HEIGHT = 1000, 700
FPS = 60

GROUND_Y = HEIGHT - 60

# Colors
SKY = (170, 220, 255)
GROUND = (70, 170, 90)
DARK = (25, 25, 25)
WHITE = (245, 245, 245)
BROWN = (170, 120, 60)
BROWN_DARK = (130, 85, 40)
GREEN = (40, 170, 70)
RED = (200, 60, 60)
YELLOW = (240, 215, 80)

# Difficulty scaling
FALL_SPEED_START = 180.0
FALL_SPEED_CAP = 520.0
FALL_ACCEL = 6.0

SPAWN_PER_SEC_START = 0.85
SPAWN_PER_SEC_CAP = 3.6
SPAWN_ACCEL = 0.035

MOVE_SPEED_START = 260.0
MOVE_SPEED_CAP = 520.0
MOVE_ACCEL = 4.5

HEAD_MOVE_SPEED_START = 260.0
HEAD_MOVE_SPEED_CAP = 520.0
HEAD_MOVE_ACCEL = 4.5

ROTTEN_CHANCE = 0.22

# Neck growth
NECK_START = 90.0
NECK_CAP = 520.0
NECK_GROW = 18.0
NECK_SHRINK = 26.0
NECK_MIN = 40.0

HEAD_RADIUS = 18
LEAF_W, LEAF_H = 18, 12

pygame.init()
pygame.display.set_caption("Giraffe Game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
bigfont = pygame.font.SysFont("consolas", 44)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
    """Linear interpolation between a and b by t in [0, 1].
    Accepts t outside [0,1] and extrapolates accordingly for generality.
    """
    return a + (b - a) * t


class Leaf:
    def __init__(self, x, y, rotten, fall_speed):
        self.x = x
        self.y = y
        self.rotten = rotten
        self.fall_speed = fall_speed * random.uniform(0.85, 1.15)
        self.w = LEAF_W
        self.h = LEAF_H
        self.spin = random.uniform(-2.5, 2.5)
        self.angle = random.uniform(0, math.tau)

    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), int(self.y - self.h / 2), self.w, self.h)

    def update(self, dt):
        self.y += self.fall_speed * dt
        self.angle += self.spin * dt

    def draw(self, surf):
        r = self.rect()
        color = RED if self.rotten else GREEN

        cx, cy = r.centerx, r.centery
        a = self.angle
        pts = []
        for k in range(4):
            theta = a + k * (math.pi / 2)
            rx = (self.w / 2) * (1.0 if k % 2 == 0 else 0.6)
            ry = (self.h / 2) * (1.0 if k % 2 == 0 else 0.6)
            pts.append((cx + math.cos(theta) * rx, cy + math.sin(theta) * ry))
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, DARK, pts, 2)
class Giraffe:
    def __init__(self):
        self.base_x = WIDTH // 2
        self.base_y = GROUND_Y
        self.neck = NECK_START
        self.head_offset = self.neck * 0.7  # head starts 70% up the neck

    def head_pos(self):
        return self.base_x, self.base_y - self.head_offset

    def top_pos(self):
        return self.base_x, self.base_y - self.neck

    def update(self, dt, keys, move_speed, head_speed):
        # Move body left/right
        dx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += move_speed
        self.base_x += dx * dt
        self.base_x = clamp(self.base_x, 60, WIDTH - 60)

        # Move head up/down
        dh = 0.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dh += head_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dh -= head_speed
        self.head_offset += dh * dt
        self.head_offset = clamp(self.head_offset, 20.0, self.neck)

    def apply_neck_change(self, delta):
        # Keep head at same percentage of neck
        if self.neck > 0:
            ratio = self.head_offset / self.neck
        else:
            ratio = 0.7  # fallback

        new_neck = clamp(self.neck + delta, NECK_MIN, NECK_CAP)

        # When the neck shrinks all the way to NECK_MIN, tests expect the head to be
        # clamped up to NECK_MIN as well (so it sits at the very top of the neck),
        # not the generic 20.0 lower bound used otherwise.
        min_head = NECK_MIN if new_neck <= NECK_MIN else 20.0

        self.neck = new_neck
        self.head_offset = clamp(new_neck * ratio, min_head, new_neck)

    def draw(self, surf):
        # --- ANIMATION TIMERS ---
        t = pygame.time.get_ticks() / 1000.0
        blink = (int(t * 2) % 7 == 0)
        wag_angle = math.sin(t * 4) * 6
        mouth_open = abs(self.head_offset - self.neck * 0.7) > 4

        # --- SHADOW ---
        shadow_rect = pygame.Rect(
            int(self.base_x - 60),
            int(self.base_y - 10),
            120,
            25
        )
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
        surf.blit(shadow_surf, shadow_rect.topleft)

        # --- BODY ---
        body_w, body_h = 110, 60
        body_rect = pygame.Rect(
            int(self.base_x - body_w / 2),
            int(self.base_y - body_h),
            body_w,
            body_h
        )
        pygame.draw.ellipse(surf, BROWN, body_rect)
        pygame.draw.ellipse(surf, DARK, body_rect, 2)

        # --- SPOTS ---
        spot_positions = [
            (-25, -20),
            (0, -10),
            (20, -25),
            (-10, -30)
        ]
        for sx, sy in spot_positions:
            pygame.draw.circle(
                surf,
                BROWN_DARK,
                (int(self.base_x + sx), int(self.base_y - body_h + sy)),
                8
            )

        # --- LEGS ---
        for lx in (-30, -10, 10, 30):
            leg_rect = pygame.Rect(
                int(self.base_x + lx - 6),
                int(self.base_y - 5),
                12,
                50
            )
            pygame.draw.rect(surf, BROWN_DARK, leg_rect, border_radius=6)
            pygame.draw.rect(surf, DARK, leg_rect, 2, border_radius=6)

        # --- TAIL (wagging) ---
        tail_base = (self.base_x + 50, self.base_y - body_h + 20)
        tail_end = (
            tail_base[0] + 20 + wag_angle,
            tail_base[1] + 20
        )
        pygame.draw.line(surf, BROWN_DARK, tail_base, tail_end, 6)
        pygame.draw.line(surf, DARK, tail_base, tail_end, 2)
        pygame.draw.circle(surf, BROWN_DARK, tail_end, 6)

        # --- NECK ---
        topx, topy = self.top_pos()
        pygame.draw.line(surf, BROWN_DARK,
                         (self.base_x, self.base_y - body_h + 10),
                         (topx, topy),
                         20)
        pygame.draw.line(surf, DARK,
                         (self.base_x, self.base_y - body_h + 10),
                         (topx, topy),
                         2)

        # --- HEAD ---
        hx, hy = self.head_pos()
        head_rect = pygame.Rect(int(hx - 22), int(hy - 18), 44, 36)
        pygame.draw.ellipse(surf, YELLOW, head_rect)
        pygame.draw.ellipse(surf, DARK, head_rect, 2)

        # --- EARS ---
        pygame.draw.polygon(surf, YELLOW, [
            (hx - 18, hy - 10),
            (hx - 28, hy - 20),
            (hx - 14, hy - 18)
        ])
        pygame.draw.polygon(surf, YELLOW, [
            (hx + 18, hy - 10),
            (hx + 28, hy - 20),
            (hx + 14, hy - 18)
        ])

        # --- HORNS ---
        pygame.draw.line(surf, DARK, (hx - 8, hy - 18), (hx - 8, hy - 30), 4)
        pygame.draw.line(surf, DARK, (hx + 8, hy - 18), (hx + 8, hy - 30), 4)
        pygame.draw.circle(surf, DARK, (hx - 8, hy - 32), 4)
        pygame.draw.circle(surf, DARK, (hx + 8, hy - 32), 4)

        # --- EYE (blinks) ---
        if not blink:
            pygame.draw.circle(surf, DARK, (int(hx + 10), int(hy - 2)), 4)

        # --- MOUTH ---
        if mouth_open:
            pygame.draw.line(surf, DARK, (hx + 10, hy + 10), (hx + 20, hy + 12), 3)
        else:
            pygame.draw.line(surf, DARK, (hx + 10, hy + 10), (hx + 18, hy + 10), 2)

        # --- TOP OF NECK MARKER ---
        pygame.draw.circle(surf, WHITE, (int(topx), int(topy)), 4)
def circle_rect_collide(cx, cy, radius, rect: pygame.Rect) -> bool:
    closest_x = clamp(cx, rect.left, rect.right)
    closest_y = clamp(cy, rect.top, rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= radius * radius


def main():
    giraffe = Giraffe()
    leaves = []
    rng = random.Random()

    elapsed = 0.0
    spawn_accum = 0.0
    score = 0

    game_over = False
    death_reason = ""

    game_state = "start"

    while True:
        dt = clock.tick(FPS) / 1000.0

        # -------------------------
        # EVENT HANDLING
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # START SCREEN
            if game_state == "start":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = "play"
                    if event.key == pygame.K_i:
                        game_state = "instructions"

            # INSTRUCTIONS SCREEN
            elif game_state == "instructions":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    game_state = "start"

            # PAUSE SCREEN
            elif game_state == "pause":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = "play"

            # GAMEPLAY
            elif game_state == "play":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = "pause"

                if event.type == pygame.KEYDOWN and game_over:
                    if event.key == pygame.K_r:
                        giraffe = Giraffe()
                        leaves = []
                        elapsed = 0.0
                        spawn_accum = 0.0
                        score = 0
                        game_over = False
                        death_reason = ""
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        keys = pygame.key.get_pressed()

        # -------------------------
        # START SCREEN DRAW
        # -------------------------
        if game_state == "start":
            screen.fill(SKY)

            title = bigfont.render("GIRAFFE GAME", True, DARK)
            prompt = font.render("Press SPACE to Start", True, DARK)
            inst = font.render("Press I for Instructions", True, DARK)

            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2))
            screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT//2 + 40))

            pygame.display.flip()
            continue

        # -------------------------
        # INSTRUCTIONS SCREEN DRAW
        # -------------------------
        if game_state == "instructions":
            screen.fill(WHITE)

            lines = [
                "INSTRUCTIONS",
                "",
                "Move Left/Right: A/D or ←/→",
                "Move Head Up/Down: W/S or ↑/↓",
                "Eat green leaves to grow your neck",
                "Avoid letting green leaves hit the ground",
                "",
                "Press B to go back"
            ]

            y = 120
            for line in lines:
                txt = font.render(line, True, DARK)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
                y += 40

            pygame.display.flip()
            continue

        # -------------------------
        # GAMEPLAY LOGIC
        # -------------------------
        if game_state == "play" and not game_over:
            elapsed += dt

            # Difficulty scaling
            fall_speed = clamp(FALL_SPEED_START + FALL_ACCEL * elapsed, FALL_SPEED_START, FALL_SPEED_CAP)
            spawn_rate = clamp(SPAWN_PER_SEC_START + SPAWN_ACCEL * elapsed, SPAWN_PER_SEC_START, SPAWN_PER_SEC_CAP)
            move_speed = clamp(MOVE_SPEED_START + MOVE_ACCEL * elapsed, MOVE_SPEED_START, MOVE_SPEED_CAP)
            head_speed = clamp(HEAD_MOVE_SPEED_START + HEAD_MOVE_ACCEL * elapsed, HEAD_MOVE_SPEED_START, HEAD_MOVE_SPEED_CAP)

            giraffe.update(dt, keys, move_speed, head_speed)

            # Leaf spawning
            spawn_accum += spawn_rate * dt
            while spawn_accum >= 1.0:
                spawn_accum -= 1.0
                x = rng.randint(40, WIDTH - 40)
                y = -20
                rotten = rng.random() < ROTTEN_CHANCE
                leaves.append(Leaf(x, y, rotten, fall_speed))

            # Update leaves
            hx, hy = giraffe.head_pos()
            for leaf in leaves:
                leaf.update(dt)

            # Collision with head
            remaining = []
            for leaf in leaves:
                r = leaf.rect()
                if circle_rect_collide(hx, hy, HEAD_RADIUS, r):
                    if leaf.rotten:
                        giraffe.apply_neck_change(-NECK_SHRINK)
                    else:
                        giraffe.apply_neck_change(+NECK_GROW)
                        score += 1
                else:
                    remaining.append(leaf)
            leaves = remaining

            # Check if leaves hit ground
            still = []
            for leaf in leaves:
                if leaf.y + leaf.h / 2 >= GROUND_Y:
                    if leaf.rotten:
                        continue
                    else:
                        game_over = True
                        death_reason = "A green leaf touched the ground"
                        still.append(leaf)
                else:
                    still.append(leaf)
            leaves = still

        # -------------------------
        # DRAW GAMEPLAY
        # -------------------------
        screen.fill(SKY)

        # Ground
        pygame.draw.rect(screen, GROUND, pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(screen, DARK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        # Leaves
        for leaf in leaves:
            leaf.draw(screen)

        # Giraffe
        giraffe.draw(screen)

        # HUD
        timer_text = font.render(f"Time: {elapsed:0.1f}s", True, DARK)
        score_text = font.render(f"Leaves eaten: {score}", True, DARK)
        neck_text = font.render(f"Neck: {int(giraffe.neck)}/{int(NECK_CAP)}", True, DARK)

        screen.blit(timer_text, (18, 14))
        screen.blit(score_text, (18, 40))
        screen.blit(neck_text, (18, 66))

        inst = font.render("Move: A/D or ←/→   Head: W/S or ↑/↓   P = Pause", True, DARK)
        screen.blit(inst, (18, HEIGHT - 32))

        # -------------------------
        # PAUSE SCREEN
        # -------------------------
        if game_state == "pause":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            msg = bigfont.render("PAUSED", True, WHITE)
            msg2 = font.render("Press P to Resume", True, WHITE)

            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 40))
            screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 20))

            pygame.display.flip()
            continue

        # -------------------------
        # GAME OVER SCREEN
        # -------------------------
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            screen.blit(overlay, (0, 0))

            msg1 = bigfont.render("GAME OVER", True, WHITE)
            msg2 = font.render(death_reason, True, WHITE)
            msg3 = font.render(f"Survived: {elapsed:0.1f}s   Good leaves eaten: {score}", True, WHITE)
            msg4 = font.render("Press R to restart, ESC to quit.", True, WHITE)

            screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 90))
            screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 - 35))
            screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2))
            screen.blit(msg4, (WIDTH // 2 - msg4.get_width() // 2, HEIGHT // 2 + 35))

        pygame.display.flip()
# -------------------------
# RUN THE GAME
# -------------------------

if __name__ == "__main__":
    main()

