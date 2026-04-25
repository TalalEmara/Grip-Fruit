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
C_PURPLE     = (100, 80, 140)
C_PURPLE_DIM = (70,  55, 100)

BG_IMAGE_PATH = "assets/images/startscreen.png"

DIFFICULTIES = [
    {"name": "EASY",   "subtitle": "Slow fruits · Forgiving grips",      "color": C_GREEN,  "color_dim": C_GREEN_DIM},
    {"name": "MEDIUM", "subtitle": "Mixed speed · Some rotten fruits",    "color": C_AMBER,  "color_dim": C_AMBER_DIM},
    {"name": "HARD",   "subtitle": "Fast & many rotten · High precision", "color": C_RED,    "color_dim": C_RED_DIM},
    {"name": "CUSTOM", "subtitle": "Create your own challenge",           "color": C_PURPLE, "color_dim": C_PURPLE_DIM},
]

# ── Screen layout constants ───────────────────────────────────────────────────
SW = 900   # screen width
SH = 620   # screen height

TITLE_CY      = 110   # vertical centre of the title card
BUTTONS_CY    = 330   # vertical centre of difficulty buttons
START_CY      = 465   # vertical centre of start button
PANEL_X       = SW - 320  # left edge of custom panel (when no overlap needed)
PANEL_Y       = 10


# ─────────────────────────────────────────────────────────────────────────────
class Background:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.image = None
        try:
            img = pygame.image.load(BG_IMAGE_PATH).convert()
            self.image = pygame.transform.scale(img, (width, height))
        except Exception:
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
                pygame.draw.rect(surface, p["color"], (0, p["y"], self.w, p["h"]))
                pygame.draw.line(surface, (50, 28, 5), (0, p["y"]), (self.w, p["y"]), 1)


# ─────────────────────────────────────────────────────────────────────────────
class TitleCard:
    RULES = [
        {"dot": C_GREEN, "text": "Grip the good fruits to score points"},
        {"dot": C_RED,   "text": "Avoid rotten fruits & ketchup"},
    ]
    CARD_W = 560
    CARD_H = 155
    RADIUS = 18

    def __init__(self, cx, cy, font_title, font_rule):
        self.cx, self.cy   = cx, cy
        self.font_title    = font_title
        self.font_rule     = font_rule
        self.rect          = pygame.Rect(cx - self.CARD_W // 2,
                                         cy - self.CARD_H // 2,
                                         self.CARD_W, self.CARD_H)

    def draw(self, surface):
        r = self.rect
        sh = pygame.Surface((r.w + 10, r.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 70), (0, 0, r.w + 10, r.h + 10), border_radius=self.RADIUS)
        surface.blit(sh, (r.x - 2, r.y + 8))

        _fill_rounded(surface, r, C_CREAM, self.RADIUS)
        _fill_rounded(surface, pygame.Rect(r.x, r.y, r.w, 8), C_GOLD, self.RADIUS, clip=r)
        _fill_rounded(surface, pygame.Rect(r.x, r.bottom - 8, r.w, 8), C_GOLD, self.RADIUS, clip=r)

        ts = self.font_title.render("GRIP FRUIT", True, C_GREEN)
        title_y = r.y + 42
        surface.blit(ts, ts.get_rect(center=(self.cx, title_y)))

        div_y = title_y + 34
        pygame.draw.line(surface, C_GOLD, (r.x + 40, div_y), (r.right - 40, div_y), 2)

        rule_start_y = div_y + 20
        for i, rule in enumerate(self.RULES):
            ry = rule_start_y + i * 28
            dot_x = r.x + 52
            pygame.draw.circle(surface, rule["dot"], (dot_x, ry), 7)
            pygame.draw.circle(surface, C_CREAM_DARK, (dot_x, ry), 7, 2)
            tl = self.font_rule.render(rule["text"], True, C_TEXT_MED)
            surface.blit(tl, tl.get_rect(midleft=(dot_x + 18, ry)))


# ─────────────────────────────────────────────────────────────────────────────
class DifficultyButton:
    CARD_W = 190
    CARD_H = 120
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

        sh = pygame.Surface((self.CARD_W + 8, self.CARD_H + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90), (0, 0, self.CARD_W + 8, self.CARD_H + 8), border_radius=self.RADIUS)
        surface.blit(sh, (dr.x - 2, dr.y + 8))

        _fill_rounded(surface, dr, C_CREAM, self.RADIUS)
        _fill_rounded(surface, pygame.Rect(dr.x, dr.y, self.CARD_W, 40), color, self.RADIUS, clip=dr)

        ns = self.font_name.render(self.data["name"], True, C_CREAM)
        surface.blit(ns, ns.get_rect(midleft=(dr.x + 14, dr.y + 20)))

        lines = _wrap(self.data["subtitle"], self.font_sub, self.CARD_W - 24)
        for i, line in enumerate(lines):
            ls = self.font_sub.render(line, True, C_TEXT_MED)
            surface.blit(ls, (dr.x + 12, dr.y + 50 + i * 18))

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
        self.w, self.h = 260, 54
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
        r  = pygame.Rect(self.rect.centerx - sw // 2, self.rect.centery - sh // 2, sw, sh)
        _fill_rounded(surface, r, C_GOLD if self.hovered else C_GOLD_DIM, 12)
        label = self.font.render("START GAME", True, C_TEXT_DARK)
        surface.blit(label, label.get_rect(center=r.center))

    def handle_click(self):
        return self.hovered


# ─────────────────────────────────────────────────────────────────────────────
class Stepper:
    """A labelled +/− stepper widget for a single numeric setting."""

    BTN_W = 26
    BTN_H = 26
    ROW_H = 36

    def __init__(self, x, y, width, label, key, min_val, max_val, step, fmt, config, font_label, font_val):
        self.x, self.y   = x, y
        self.width        = width
        self.label        = label
        self.key          = key
        self.min_val      = min_val
        self.max_val      = max_val
        self.step         = step
        self.fmt          = fmt          # e.g. "{:.0f}" or "{:.2f}"
        self.config       = config
        self.font_label   = font_label
        self.font_val     = font_val

        # Button rects
        self.rect_minus = pygame.Rect(x + width - self.BTN_W * 2 - 6, y, self.BTN_W, self.BTN_H)
        self.rect_plus  = pygame.Rect(x + width - self.BTN_W, y, self.BTN_W, self.BTN_H)

    def handle_click(self, pos):
        if self.rect_minus.collidepoint(pos):
            self.config[self.key] = round(
                max(self.min_val, self.config[self.key] - self.step), 6)
        elif self.rect_plus.collidepoint(pos):
            self.config[self.key] = round(
                min(self.max_val, self.config[self.key] + self.step), 6)

    def draw(self, surface):
        # label
        lbl = self.font_label.render(self.label, True, C_TEXT_DARK)
        surface.blit(lbl, (self.x, self.y + 5))

        # value centred between the buttons
        val_str = self.fmt.format(self.config[self.key])
        vs = self.font_val.render(val_str, True, C_TEXT_DARK)
        surface.blit(vs, vs.get_rect(center=(self.rect_minus.x - 20, self.y + self.BTN_H // 2)))

        # minus button
        for rect, sym in ((self.rect_minus, "−"), (self.rect_plus, "+")):
            _fill_rounded(surface, rect, C_GOLD_DIM, 6)
            s = self.font_val.render(sym, True, C_CREAM)
            surface.blit(s, s.get_rect(center=rect.center))


# ─────────────────────────────────────────────────────────────────────────────
class ToggleRow:
    """A simple toggle between two string values (e.g. FIXED / RANDOM)."""

    H = 28

    def __init__(self, x, y, width, label, key, options, config, font_label, font_val):
        self.x, self.y  = x, y
        self.width       = width
        self.label       = label
        self.key         = key
        self.options     = options
        self.config      = config
        self.font_label  = font_label
        self.font_val    = font_val
        self.rect        = pygame.Rect(x + width - 80, y, 80, self.H)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            idx = self.options.index(self.config[self.key])
            self.config[self.key] = self.options[(idx + 1) % len(self.options)]

    def draw(self, surface):
        lbl = self.font_label.render(self.label, True, C_TEXT_DARK)
        surface.blit(lbl, (self.x, self.y + 4))
        _fill_rounded(surface, self.rect, C_PURPLE, 8)
        vs = self.font_val.render(self.config[self.key], True, C_CREAM)
        surface.blit(vs, vs.get_rect(center=self.rect.center))


# ─────────────────────────────────────────────────────────────────────────────
class CustomizationPanel:
    """
    Slide-in panel exposing every LevelManager constructor argument.

    Config keys match LevelManager's parameter names exactly so the caller
    can unpack them directly.
    """
    WIDTH  = 290
    RADIUS = 16
    PAD    = 18

    # Row spacing
    ROW_GAP = 44

    def __init__(self, x, y, font_label, font_val, font_heading):
        self.x, self.y       = x, y
        self.font_label      = font_label
        self.font_val        = font_val
        self.font_heading    = font_heading
        self.visible         = False

        self.config = {
            # timing (stored as seconds; convert to frames when building LevelManager)
            "item_timeout_s":   1.67,   # frames ÷ 60
            "spawn_delay_s":    1.00,
            # counts
            "total_items":      10,
            # weights (must sum ≤ 1; we normalise before use)
            "fresh_weight":     0.70,
            "rotten_weight":    0.20,
            "ketchup_weight":   0.10,
            # mode
            "sequence_mode":    "random",   # "fixed" | "random"
        }

        # height is computed from number of rows
        num_rows = 7  # timeout, delay, total, fresh, rotten, ketchup, mode
        self.height = self.PAD * 2 + 28 + num_rows * self.ROW_GAP + 10

        rx = x + self.PAD
        ry = y + self.PAD + 30   # leave room for heading

        def stepper(label, key, mn, mx, step, fmt, row):
            return Stepper(rx, ry + row * self.ROW_GAP,
                           self.WIDTH - self.PAD * 2,
                           label, key, mn, mx, step, fmt,
                           self.config, font_label, font_val)

        self._rows = [
            stepper("Item timeout (s)",  "item_timeout_s",  0.5, 10.0, 0.17, "{:.2f}", 0),
            stepper("Spawn delay (s)",   "spawn_delay_s",   0.2,  5.0, 0.17, "{:.2f}", 1),
            stepper("Total items",       "total_items",     1,   50,   1,    "{:.0f}", 2),
            stepper("Fresh weight",      "fresh_weight",    0.0,  1.0, 0.05, "{:.2f}", 3),
            stepper("Rotten weight",     "rotten_weight",   0.0,  1.0, 0.05, "{:.2f}", 4),
            stepper("Ketchup weight",    "ketchup_weight",  0.0,  1.0, 0.05, "{:.2f}", 5),
            ToggleRow(rx, ry + 6 * self.ROW_GAP,
                      self.WIDTH - self.PAD * 2,
                      "Sequence mode", "sequence_mode",
                      ["random", "fixed"],
                      self.config, font_label, font_val),
        ]

    # ── Public ───────────────────────────────────────────────────────────────
    def get_config(self) -> dict:
        """Return config ready to be passed to LevelManager (frames, not seconds)."""
        c = self.config
        return {
            "item_timeout":   round(c["item_timeout_s"] * 60),
            "spawn_delay":    round(c["spawn_delay_s"] * 60),
            "total_items":    int(c["total_items"]),
            "fresh_weight":   c["fresh_weight"],
            "rotten_weight":  c["rotten_weight"],
            "ketchup_weight": c["ketchup_weight"],
            "sequence_mode":  c["sequence_mode"],
        }

    def handle_click(self, pos):
        if not self.visible:
            return
        for row in self._rows:
            row.handle_click(pos)

    def draw(self, surface):
        if not self.visible:
            return

        panel_rect = pygame.Rect(self.x, self.y, self.WIDTH, self.height)

        # shadow
        sh = pygame.Surface((self.WIDTH + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 80),
                         (0, 0, self.WIDTH + 10, self.height + 10),
                         border_radius=self.RADIUS)
        surface.blit(sh, (self.x - 2, self.y + 8))

        # body
        _fill_rounded(surface, panel_rect, C_CREAM, self.RADIUS)
        # purple top bar (matches CUSTOM button colour)
        _fill_rounded(surface, pygame.Rect(self.x, self.y, self.WIDTH, 30),
                      C_PURPLE, self.RADIUS, clip=panel_rect)

        # heading
        hd = self.font_heading.render("CUSTOM SETTINGS", True, C_CREAM)
        surface.blit(hd, hd.get_rect(midleft=(self.x + self.PAD, self.y + 15)))

        # divider
        div_y = self.y + 34
        pygame.draw.line(surface, C_GOLD,
                         (self.x + 12, div_y), (self.x + self.WIDTH - 12, div_y), 1)

        # weight-sum hint
        ws = round(self.config["fresh_weight"] + self.config["rotten_weight"]
                   + self.config["ketchup_weight"], 2)
        color = C_GREEN if abs(ws - 1.0) < 0.01 else C_RED
        hint = f"Weight sum: {ws:.2f}  {'✓' if abs(ws-1.0)<0.01 else '≠ 1.0'}"
        hs = self.font_label.render(hint, True, color)
        surface.blit(hs, hs.get_rect(midright=(self.x + self.WIDTH - self.PAD,
                                                self.y + self.height - 10)))

        # rows
        for row in self._rows:
            row.draw(surface)

        # border
        _stroke_rounded(surface, panel_rect, C_PURPLE, self.RADIUS, 2)


# ─────────────────────────────────────────────────────────────────────────────
class StartScreen:
    WIDTH  = SW
    HEIGHT = SH

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Grip Fruit")
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock  = pygame.time.Clock()

        font_title   = pygame.font.SysFont("Georgia", 52, bold=True)
        font_card    = pygame.font.SysFont("Arial",   19, bold=True)
        font_sub     = pygame.font.SysFont("Arial",   13)
        font_btn     = pygame.font.SysFont("Georgia", 22, bold=True)
        font_rule    = pygame.font.SysFont("Georgia", 14, italic=True)
        font_heading = pygame.font.SysFont("Arial",   13, bold=True)
        font_val     = pygame.font.SysFont("Arial",   13, bold=True)

        self.bg         = Background(self.WIDTH, self.HEIGHT)
        self.title_card = TitleCard(self.WIDTH // 2, TITLE_CY, font_title, font_rule)

        # ── Difficulty buttons: 4 cards centred, evenly spaced ────────────────
        n        = len(DIFFICULTIES)
        spacing  = 205
        total_w  = spacing * (n - 1)
        start_x  = self.WIDTH // 2 - total_w // 2

        self.buttons = [
            DifficultyButton(i, DIFFICULTIES[i],
                             start_x + i * spacing, BUTTONS_CY,
                             font_card, font_sub)
            for i in range(n)
        ]
        self.buttons[0].selected = True
        self.selected_index = 0

        self.start_btn = StartButton(self.WIDTH // 2, START_CY, font_btn)

        # Panel sits to the right; slides in only when CUSTOM is selected
        self.customization_panel = CustomizationPanel(
            self.WIDTH - CustomizationPanel.WIDTH - 14, PANEL_Y,
            font_sub, font_val, font_heading
        )

        self.running = True
        self.chosen  = None

    # ── Loop ─────────────────────────────────────────────────────────────────
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
                self.customization_panel.handle_click(e.pos)
                for i, btn in enumerate(self.buttons):
                    if btn.handle_click():
                        self._select(i)
                if self.start_btn.handle_click():
                    self._start()

    def _move(self, d):
        self._select((self.selected_index + d) % len(self.buttons))

    def _select(self, i):
        for b in self.buttons:
            b.selected = False
        self.selected_index = i
        self.buttons[i].selected = True
        self.customization_panel.visible = (DIFFICULTIES[i]["name"] == "CUSTOM")

    def _start(self):
        chosen_diff = DIFFICULTIES[self.selected_index]
        if chosen_diff["name"] == "CUSTOM":
            self.chosen = self.customization_panel.get_config()
            self.chosen["name"] = "CUSTOM"
        else:
            self.chosen = chosen_diff
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
        self.customization_panel.draw(self.screen)
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


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    screen = StartScreen()
    chosen = screen.run()
    if chosen:
        print(f"\n✓ Starting on: {chosen['name']}")
        if chosen["name"] == "CUSTOM":
            for k, v in chosen.items():
                if k != "name":
                    print(f"   {k}: {v}")
    sys.exit(0)