import math
import random
import sys
import pygame

# ----------------------------
# Giraffe
# ----------------------------

WIDTH, HEIGHT = 1000, 700  # zoomed out view
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

# Difficulty ramp + caps
RAMP_START = 0.0

FALL_SPEED_START = 180.0       # px/sec
FALL_SPEED_CAP = 520.0         # px/sec
FALL_ACCEL = 6.0               # px/sec^2 (ramps with time)

SPAWN_PER_SEC_START = 0.85     # leaves/sec
SPAWN_PER_SEC_CAP = 3.6        # leaves/sec
SPAWN_ACCEL = 0.035            # leaves/sec^2 (ramps with time)

MOVE_SPEED_START = 260.0       # px/sec (giraffe base move)
MOVE_SPEED_CAP = 520.0
MOVE_ACCEL = 4.5               # px/sec^2

HEAD_MOVE_SPEED_START = 260.0  # px/sec (head up/down along neck)
HEAD_MOVE_SPEED_CAP = 520.0
HEAD_MOVE_ACCEL = 4.5

ROTTEN_CHANCE = 0.22           # chance a leaf is rotten

# Giraffe neck growth
NECK_START = 90.0
NECK_CAP = 520.0               # fixed cap height
NECK_GROW = 18.0               # per good leaf
NECK_SHRINK = 26.0             # per rotten leaf (bigger penalty)
NECK_MIN = 40.0

# Head size/collision
HEAD_RADIUS = 18

# Leaf size/speed variance
LEAF_W, LEAF_H = 18, 12

pygame.init()
pygame.display.set_caption("Giraffe")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
bigfont = pygame.font.SysFont("consolas", 44)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def lerp(a, b, t):
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

        # How the leaf looks, its a rotated diamond
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

        # head position along neck (0 = at base, neck = at top)
        self.head_offset = self.neck * 0.7

    def head_pos(self):
        # neck goes straight up
        hx = self.base_x
        hy = self.base_y - self.head_offset
        return hx, hy

    def top_pos(self):
        return self.base_x, self.base_y - self.neck

    def update(self, dt, keys, move_speed, head_speed):
        # left/right move base
        dx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += move_speed
        self.base_x += dx * dt
        self.base_x = clamp(self.base_x, 60, WIDTH - 60)

        # head up/down (along neck)
        dh = 0.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dh += head_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dh -= head_speed
        self.head_offset += dh * dt

        # keep head within [some minimum, neck]
        self.head_offset = clamp(self.head_offset, 20.0, self.neck)

    def apply_neck_change(self, delta):
        self.neck = clamp(self.neck + delta, NECK_MIN, NECK_CAP)
        # keep head_offset valid after neck changes
        self.head_offset = clamp(self.head_offset, 20.0, self.neck)

    def draw(self, surf):
        # body
        body_w, body_h = 80, 45
        body = pygame.Rect(int(self.base_x - body_w / 2), int(self.base_y - body_h), body_w, body_h)
        pygame.draw.rect(surf, BROWN, body, border_radius=10)
        pygame.draw.rect(surf, DARK, body, 2, border_radius=10)

        # legs
        for lx in (-25, -8, 8, 25):
            leg = pygame.Rect(int(self.base_x + lx - 5), int(self.base_y - 5), 10, 45)
            pygame.draw.rect(surf, BROWN_DARK, leg, border_radius=6)
            pygame.draw.rect(surf, DARK, leg, 2, border_radius=6)

        # neck (straight line thick) 
        topx, topy = self.top_pos()
        pygame.draw.line(surf, BROWN_DARK, (self.base_x, self.base_y - body_h + 8), (topx, topy), 16)
        pygame.draw.line(surf, DARK, (self.base_x, self.base_y - body_h + 8), (topx, topy), 2)

        # head
        hx, hy = self.head_pos()
        pygame.draw.circle(surf, YELLOW, (int(hx), int(hy)), HEAD_RADIUS)
        pygame.draw.circle(surf, DARK, (int(hx), int(hy)), HEAD_RADIUS, 2)

        # "snout" indicator
        pygame.draw.circle(surf, DARK, (int(hx + 6), int(hy + 2)), 3)

        # marker at top of full neck (helps visualize max growth)
        pygame.draw.circle(surf, (255, 255, 255), (int(topx), int(topy)), 4)


def circle_rect_collide(cx, cy, radius, rect: pygame.Rect) -> bool:
    # clamp circle center to rect
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
    score = 0  # how many good leaves were eaten

    game_over = False
    death_reason = ""

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    # restart
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

        if not game_over:
            elapsed += dt

            # ramp values with caps
            fall_speed = clamp(FALL_SPEED_START + FALL_ACCEL * elapsed, FALL_SPEED_START, FALL_SPEED_CAP)
            spawn_rate = clamp(SPAWN_PER_SEC_START + SPAWN_ACCEL * elapsed, SPAWN_PER_SEC_START, SPAWN_PER_SEC_CAP)
            move_speed = clamp(MOVE_SPEED_START + MOVE_ACCEL * elapsed, MOVE_SPEED_START, MOVE_SPEED_CAP)
            head_speed = clamp(HEAD_MOVE_SPEED_START + HEAD_MOVE_ACCEL * elapsed, HEAD_MOVE_SPEED_START, HEAD_MOVE_SPEED_CAP)

            giraffe.update(dt, keys, move_speed, head_speed)

            # spawning (rate = leaves/sec)
            spawn_accum += spawn_rate * dt
            while spawn_accum >= 1.0:
                spawn_accum -= 1.0
                x = rng.randint(40, WIDTH - 40)
                y = -20
                rotten = rng.random() < ROTTEN_CHANCE
                leaves.append(Leaf(x, y, rotten, fall_speed))

            # update leaves + collisions
            hx, hy = giraffe.head_pos()
            for leaf in leaves:
                leaf.update(dt)

            # This eats the leaves if the head touches them
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

            # This is where the game fails if the leaf hits the ground 
            still = []
            for leaf in leaves:
                if leaf.y + leaf.h / 2 >= GROUND_Y:
                    if leaf.rotten:
                        # rotten leaf just splats / disappears
                        continue
                    else:
                        game_over = True
                        death_reason = "A green leaf touched the ground"
                        still.append(leaf)
                else:
                    still.append(leaf)
            leaves = still

        # ----------------
        # Draw
        # ----------------
        screen.fill(SKY)

        # ground
        pygame.draw.rect(screen, GROUND, pygame.Rect(0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(screen, DARK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        # leaves
        for leaf in leaves:
            leaf.draw(screen)

        # giraffe
        giraffe.draw(screen)

        # HUD
        timer_text = font.render(f"Time: {elapsed:0.1f}s", True, DARK)
        score_text = font.render(f"Leaves eaten: {score}", True, DARK)
        neck_text = font.render(f"Neck: {int(giraffe.neck)}/{int(NECK_CAP)}", True, DARK)

        screen.blit(timer_text, (18, 14))
        screen.blit(score_text, (18, 40))
        screen.blit(neck_text, (18, 66))

        # instructions
        inst = font.render("Move: A/D or ←/→   Head: W/S or ↑/↓   (R to restart after game over)", True, DARK)
        screen.blit(inst, (18, HEIGHT - 32))

        # Game over overlay
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


if __name__ == "__main__":
    main()
