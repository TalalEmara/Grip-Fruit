
import pygame
import math
import random
import sys

# ── Palette ──────────────────────────────────────────────────────────────────
C_CREAM      = (245, 235, 200)
C_CREAM_DARK = (225, 210, 165)
C_TEXT_DARK  = (55,  35,   5)
C_TEXT_MED   = (90,  60,  15)
C_GOLD       = (200, 155,  50)
C_GOLD_DIM   = (150, 110,  30)
C_GREEN      = (25,  100,  50)  
C_GREEN_DIM  = (18,   70,  35)
C_AMBER      = (200, 130,  20)
C_AMBER_DIM  = (140,  90,  15)
C_RED        = (175,  45,  30)
C_RED_DIM    = (120,  30,  20)

# ── Replace this path with your wood background image ────────────────────────
BG_IMAGE_PATH = "assets\images\startscreen.png"

DIFFICULTIES = [
    {"name": "EASY",   "subtitle": "Slow fruits · Forgiving grips",      "color": C_GREEN, "color_dim": C_GREEN_DIM},
    {"name": "MEDIUM", "subtitle": "Mixed speed · Some rotten fruits",    "color": C_AMBER, "color_dim": C_AMBER_DIM},
    {"name": "HARD",   "subtitle": "Fast & many rotten · High precision", "color": C_RED,   "color_dim": C_RED_DIM},
]


# ─────────────────────────────────────────────────────────────────────────────
class Background:
    """Loads image if found, otherwise draws procedural wood planks as fallback."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.image = None
        try:
            img = pygame.image.load(BG_IMAGE_PATH).convert()
            self.image = pygame.transform.scale(img, (width, height))
        except Exception:
            # fallback: generate planks
            self._planks = []
            y = 0
            cols = [(74, 42, 10), (101, 58, 14), (130, 80, 25),
                    (115, 68, 18), (88, 50, 12)]
            while y < height + 60:
                h = random.randint(26, 46)
                self._planks.append({"y": y, "h": h, "color": random.choice(cols)})
                y += h

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (0, 0))
        else:
            for p in self._planks:
                pygame.draw.rect(surface, p["color"],
                                 (0, p["y"], self.w, p["h"]))
                pygame.draw.line(surface, (50, 28, 5),
                                 (0, p["y"]), (self.w, p["y"]), 1)


# ─────────────────────────────────────────────────────────────────────────────
class TitleCard:
    """
    Single parchment card containing:
      - 'GRIP FRUIT' title (dark green, fixed)
      - Gold divider
      - Three how-to-play rule rows with coloured dot icons
    """

    RULES = [
        {"dot": C_GREEN, "text": "Grip the good fruits to score points"},
        {"dot": C_RED,   "text": "Avoid rotten fruits & ketchup"},
    ]

    CARD_W = 620
    CARD_H = 170
    RADIUS = 18

    def __init__(self, cx, cy, font_title, font_rule):
        self.cx         = cx
        self.cy         = cy
        self.font_title = font_title
        self.font_rule  = font_rule
        self.rect       = pygame.Rect(cx - self.CARD_W // 2,
                                       cy - self.CARD_H // 2,
                                       self.CARD_W, self.CARD_H)

    def draw(self, surface):
        r = self.rect

        # ── drop shadow ──
        sh = pygame.Surface((r.w + 10, r.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 70), (0, 0, r.w + 10, r.h + 10),
                         border_radius=self.RADIUS)
        surface.blit(sh, (r.x - 2, r.y + 8))

        # ── card body ──
        _fill_rounded(surface, r, C_CREAM, self.RADIUS)

        # gold top bar
        _fill_rounded(surface, pygame.Rect(r.x, r.y, r.w, 8),
                      C_GOLD, self.RADIUS, clip=r)
        # gold bottom bar
        _fill_rounded(surface, pygame.Rect(r.x, r.bottom - 8, r.w, 8),
                      C_GOLD, self.RADIUS, clip=r)

        # ── title ──
        ts = self.font_title.render("GRIP FRUIT", True, C_GREEN)
        title_y = r.y + 44
        surface.blit(ts, ts.get_rect(center=(self.cx, title_y)))

        # ── gold divider ──
        div_y = title_y + 36
        pygame.draw.line(surface, C_GOLD,
                         (r.x + 40, div_y), (r.right - 40, div_y), 2)

        # ── rules ──
        rule_start_y = div_y + 22
        for i, rule in enumerate(self.RULES):
            ry = rule_start_y + i * 30

            # coloured dot
            dot_x = r.x + 52
            pygame.draw.circle(surface, rule["dot"], (dot_x, ry), 8)
            pygame.draw.circle(surface, C_CREAM_DARK, (dot_x, ry), 8, 2)

            # rule text
            tl = self.font_rule.render(rule["text"], True, C_TEXT_MED)
            surface.blit(tl, tl.get_rect(midleft=(dot_x + 20, ry)))


# ─────────────────────────────────────────────────────────────────────────────
class DifficultyButton:
    CARD_W = 220
    CARD_H = 140
    RADIUS = 14

    def __init__(self, index, data, cx, cy, font_name, font_sub):
        self.index     = index
        self.data      = data
        self.rect      = pygame.Rect(cx - self.CARD_W // 2, cy - self.CARD_H // 2,
                                      self.CARD_W, self.CARD_H)
        self.font_name = font_name
        self.font_sub  = font_sub
        self.hovered   = False
        self.selected  = False
        self._lift     = 0.0

    def update(self, mouse_pos, dt):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = -10.0 if (self.hovered or self.selected) else 0.0
        self._lift += (target - self._lift) * min(dt * 12, 1.0)

    def draw(self, surface):
        color     = self.data["color"]
        color_dim = self.data["color_dim"]
        dr        = self.rect.move(0, int(self._lift))

        # shadow
        sh = pygame.Surface((self.CARD_W + 8, self.CARD_H + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90),
                         (0, 0, self.CARD_W + 8, self.CARD_H + 8),
                         border_radius=self.RADIUS)
        surface.blit(sh, (dr.x - 2, dr.y + 8))

        # card body
        _fill_rounded(surface, dr, C_CREAM, self.RADIUS)

        # colored top bar
        _fill_rounded(surface, pygame.Rect(dr.x, dr.y, self.CARD_W, 46),
                      color, self.RADIUS, clip=dr)

        # difficulty name
        ns = self.font_name.render(self.data["name"], True, C_CREAM)
        surface.blit(ns, ns.get_rect(midleft=(dr.x + 16, dr.y + 23)))

        # subtitle
        lines = _wrap(self.data["subtitle"], self.font_sub, self.CARD_W - 28)
        for i, line in enumerate(lines):
            ls = self.font_sub.render(line, True, C_TEXT_MED)
            surface.blit(ls, (dr.x + 14, dr.y + 58 + i * 20))

        # selection / hover outline
        if self.selected:
            _stroke_rounded(surface, dr, color, self.RADIUS, 3)
        elif self.hovered:
            _stroke_rounded(surface, dr, color_dim, self.RADIUS, 2)

    def handle_click(self):
        if self.hovered:
            self.selected = True
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
class StartButton:
    def __init__(self, cx, cy, font):
        self.font      = font
        self.w, self.h = 280, 60
        self.rect      = pygame.Rect(cx - self.w // 2, cy - self.h // 2, self.w, self.h)
        self.hovered   = False
        self.scale     = 1.0

    def update(self, mouse_pos, dt):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.05 if self.hovered else 1.0
        self.scale += (target - self.scale) * min(dt * 14, 1.0)

    def draw(self, surface):
        sw = int(self.w * self.scale)
        sh = int(self.h * self.scale)
        r  = pygame.Rect(self.rect.centerx - sw // 2,
                          self.rect.centery - sh // 2, sw, sh)
        _fill_rounded(surface, r, C_GOLD if self.hovered else C_GOLD_DIM, 12)
        label = self.font.render("START GAME", True, C_TEXT_DARK)
        surface.blit(label, label.get_rect(center=r.center))

    def handle_click(self):
        return self.hovered


# ─────────────────────────────────────────────────────────────────────────────
class StartScreen:
    WIDTH  = 860
    HEIGHT = 600

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Grip Fruit")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock  = pygame.time.Clock()

        font_title = pygame.font.SysFont("Georgia", 58, bold=True)
        font_card  = pygame.font.SysFont("Arial",   22, bold=True)
        font_sub   = pygame.font.SysFont("Arial",   14)
        font_btn   = pygame.font.SysFont("Georgia", 24, bold=True)
        font_rule  = pygame.font.SysFont("Georgia", 15, italic=True)

        self.bg         = Background(self.WIDTH, self.HEIGHT)
        self.title_card = TitleCard(self.WIDTH // 2, 140, font_title, font_rule)

        spacing = 232
        base_x  = self.WIDTH // 2 - spacing
        self.buttons = [
            DifficultyButton(i, DIFFICULTIES[i],
                             base_x + i * spacing, 400,
                             font_card, font_sub)
            for i in range(3)
        ]
        self.buttons[0].selected = True

        self.start_btn      = StartButton(self.WIDTH // 2, 520, font_btn)
        self.selected_index = 0
        self.running        = True
        self.chosen         = None

    # ── loop ─────────────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._events()
            self._update(dt)
            self._draw()
        pygame.quit()
        return self.chosen

    def _events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                elif e.key in (pygame.K_LEFT, pygame.K_a):
                    self._move(-1)
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    self._move(1)
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, btn in enumerate(self.buttons):
                    if btn.handle_click():
                        self._select(i)
                if self.start_btn.handle_click():
                    self._start()

    def _move(self, d):
        self._select((self.selected_index + d) % 3)

    def _select(self, i):
        for b in self.buttons:
            b.selected = False
        self.selected_index = i
        self.buttons[i].selected = True

    def _start(self):
        self.chosen  = DIFFICULTIES[self.selected_index]
        self.running = False

    def _update(self, dt):
        mouse = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse, dt)
        self.start_btn.update(mouse, dt)

    def _draw(self):
        self.bg.draw(self.screen)
        self.title_card.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)
        self.start_btn.draw(self.screen)
        pygame.display.flip()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _fill_rounded(surface, rect, color, radius, clip=None):
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    c = (*color, 255) if len(color) == 3 else color
    pygame.draw.rect(surf, c, (0, 0, rect.w, rect.h), border_radius=radius)
    if clip:
        cr   = clip.clip(rect)
        area = pygame.Rect(cr.x - rect.x, cr.y - rect.y, cr.w, cr.h)
        surface.blit(surf, (cr.x, cr.y), area=area)
    else:
        surface.blit(surf, rect.topleft)


def _stroke_rounded(surface, rect, color, radius, width):
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, 255), (0, 0, rect.w, rect.h),
                     width=width, border_radius=radius)
    surface.blit(surf, rect.topleft)


def _wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    screen = StartScreen()
    chosen = screen.run()
    if chosen:
        print(f"\n✓ Starting on: {chosen['name']}")
    sys.exit(0)

