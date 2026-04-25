import pygame
import json
import math
import random
from pathlib import Path


# ── Palette — warm cozy kitchen ───────────────────────────────────────────────
BG_WALL       = (232, 218, 192)   # warm linen wall
BG_WOOD       = (155, 105,  58)   # walnut counter
BG_WOOD_LIGHT = (185, 135,  78)   # lighter plank
BG_CARD       = (248, 238, 215)   # aged parchment
BG_CARD_SEL   = (255, 248, 228)   # selected cream
CORK          = (192, 155, 102)   # corkboard
CORK_DARK     = (162, 125,  72)   # wood frame
PIN_RED       = (198,  58,  52)
PIN_BLUE      = ( 68, 118, 188)
PIN_GREEN     = ( 78, 158,  88)
ACCENT_BROWN  = (115,  68,  22)
ACCENT_RUST   = (182,  85,  40)
ACCENT_GREEN  = ( 82, 144,  72)
ACCENT_YELLOW = (208, 172,  48)
TEXT_INK      = ( 50,  30,   8)
TEXT_BROWN    = (100,  60,  18)
TEXT_FADED    = (148, 118,  78)
TEXT_LIGHT    = (238, 222, 200)
# ─────────────────────────────────────────────────────────────────────────────


def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rrect(surf, color, rect, radius, alpha=None):
    if alpha is not None:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)


def bake_background(surf, w, h, font_note):
    surf.fill(BG_WALL)
    # Wallpaper stripes
    for x in range(0, w, 18):
        c = (BG_WALL[0] - 7, BG_WALL[1] - 6, BG_WALL[2] - 5)
        pygame.draw.line(surf, c, (x, 0), (x, h), 1)

    # Wood counter bottom strip
    counter_y = h - 76
    for row in range(4):
        col = BG_WOOD_LIGHT if row % 2 == 0 else BG_WOOD
        pygame.draw.rect(surf, col, (0, counter_y + row * 20, w, 20))
        pygame.draw.line(surf, BG_WOOD, (0, counter_y + row * 20), (w, counter_y + row * 20), 1)

    # Cork board on left
    bx, by, bw, bh = 16, 10, 215, 88
    # wood frame
    pygame.draw.rect(surf, CORK_DARK, (bx - 7, by - 7, bw + 14, bh + 14), border_radius=10)
    # cork surface
    pygame.draw.rect(surf, CORK, (bx, by, bw, bh), border_radius=8)
    # cork texture
    rng = random.Random(7)
    for _ in range(200):
        dx = rng.randint(bx + 4, bx + bw - 4)
        dy = rng.randint(by + 4, by + bh - 4)
        dc = tuple(max(0, min(255, CORK[i] + rng.randint(-18, 18))) for i in range(3))
        pygame.draw.circle(surf, dc, (dx, dy), rng.randint(1, 3))

    # Sticky note 1 — yellow, slight tilt
    _sticky(surf, 24, 16, 78, 56, (255, 232, 110), ["Grip", "Fruit!"], font_note, TEXT_INK,  3)
    draw_pin(surf, 63, 18, PIN_RED)

    # Sticky note 2 — blue
    _sticky(surf, 112, 20, 88, 50, (190, 220, 255), ["Keep", "Going!"], font_note, (30, 60, 120), -2)
    draw_pin(surf, 156, 22, PIN_BLUE)

    # Sticky note 3 — green
    _sticky(surf, 68,  58, 72, 40, (190, 240, 195), ["Fresh", "Start"],font_note, (30, 90, 40),  1)
    draw_pin(surf, 104, 60, PIN_GREEN)


def _sticky(surf, x, y, w, h, bg, lines, font, tc, angle):
    note = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(note, (0, 0, 0, 38), (3, 3, w, h), border_radius=3)
    pygame.draw.rect(note, (*bg, 235), (0, 0, w, h), border_radius=3)
    pygame.draw.polygon(note, (max(0,bg[0]-30), max(0,bg[1]-30), max(0,bg[2]-30), 210),
                        [(w - 10, 0), (w, 0), (w, 10)])
    for i, line in enumerate(lines):
        ts = font.render(line, True, tc)
        note.blit(ts, (6, 5 + i * (font.get_height() + 1)))
    if angle:
        note = pygame.transform.rotate(note, angle)
    surf.blit(note, note.get_rect(center=(x + w // 2, y + h // 2)))


def draw_pin(surf, cx, cy, color):
    pygame.draw.circle(surf, color, (cx, cy), 7)
    pygame.draw.circle(surf, tuple(min(255, c + 65) for c in color), (cx - 2, cy - 2), 3)
    pygame.draw.line(surf, (70, 50, 30), (cx, cy + 7), (cx, cy + 13), 2)


class ExperimentPickerScreen:
    MARGIN   = 42
    HEADER_H = 106
    ROW_H    = 62
    ROW_GAP  = 7

    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grip Fruit — Pick Experiment")
        self.clock  = pygame.time.Clock()

        def _f(names, size, bold=False):
            for n in names:
                try:
                    return pygame.font.SysFont(n, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.SysFont("arial", size, bold=bold)

        self.f_title = _f(["georgia","garamond","palatino"], 36, bold=True)
        self.f_label = _f(["georgia","garamond"],            20, bold=True)
        self.f_meta  = _f(["trebuchetms","verdana"],         15)
        self.f_hint  = _f(["trebuchetms","verdana"],         14)
        self.f_note  = _f(["georgia"],                       13)
        self.f_badge = _f(["trebuchetms"],                   13, bold=True)

        history = self._list_saved_experiments()
        self.options = [{"type":"new","label":"Start New Experiment","meta":"Begin a fresh session"}]
        for item in history:
            self.options.append({
                "type":       "saved",
                "file_path":  item["file_path"],
                "label":      item["name"],
                "meta":       f"{item['difficulty']}  ·  score {item['final_score']}  ·  {item['created_at']}",
                "score":      item["final_score"],
            })

        self.selected_idx     = 0
        self.scroll_top       = 0
        self.anim_t           = 0.0
        self.hover_alphas     = [0.0] * len(self.options)

        list_h = self.height - self.HEADER_H - 80
        self.max_visible_rows = max(1, list_h // (self.ROW_H + self.ROW_GAP))

        # Bake static background
        self._bg = pygame.Surface((self.width, self.height))
        bake_background(self._bg, self.width, self.height, self.f_note)

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            self.anim_t += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "quit", None
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_idx = (self.selected_idx - 1) % len(self.options)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_idx = (self.selected_idx + 1) % len(self.options)
                    if event.key == pygame.K_RETURN:
                        opt = self.options[self.selected_idx]
                        if opt["type"] == "new":
                            return "new", None
                        summary = self._load_saved_summary(opt["file_path"])
                        if summary:
                            return "saved", summary

            self._update_scroll()
            self._update_alphas(dt)
            self._draw()
            pygame.display.flip()

    def _update_scroll(self):
        if self.selected_idx < self.scroll_top:
            self.scroll_top = self.selected_idx
        if self.selected_idx >= self.scroll_top + self.max_visible_rows:
            self.scroll_top = self.selected_idx - self.max_visible_rows + 1

    def _update_alphas(self, dt):
        for i in range(len(self.options)):
            target = 1.0 if i == self.selected_idx else 0.0
            self.hover_alphas[i] += (target - self.hover_alphas[i]) * min(1.0, 8.0 * dt)

    def _draw(self):
        self.screen.blit(self._bg, (0, 0))
        self._draw_header()
        self._draw_list()
        self._draw_footer()

    def _draw_header(self):
        tx = 248
        # Title with wavy underline
        title = self.f_title.render("Choose Experiment", True, ACCENT_BROWN)
        self.screen.blit(title, (tx, 24))
        uy = 68
        for i in range(0, title.get_width(), 5):
            dy = int(2 * math.sin(i * 0.3 + self.anim_t * 2.2))
            pygame.draw.circle(self.screen, ACCENT_RUST, (tx + i, uy + dy), 1)

        # Sessions tag
        count = len(self.options) - 1
        tag   = self.f_badge.render(f"{count} sessions saved", True, TEXT_LIGHT)
        tw, th = tag.get_size()
        rrect(self.screen, ACCENT_BROWN, (tx, 74, tw + 16, th + 6), radius=7, alpha=210)
        self.screen.blit(tag, (tx + 8, 77))

        # Dashed divider
        dy = self.HEADER_H - 5
        for i in range(0, self.width - self.MARGIN * 2, 14):
            pygame.draw.line(self.screen, CORK_DARK,
                             (self.MARGIN + i, dy), (self.MARGIN + i + 9, dy), 2)

    def _draw_list(self):
        M        = self.MARGIN
        start_y  = self.HEADER_H + 6
        step     = self.ROW_H + self.ROW_GAP
        total    = len(self.options)
        row_w    = self.width - M * 2 - 22

        for i, opt in enumerate(self.options[self.scroll_top : self.scroll_top + self.max_visible_rows]):
            abs_i = self.scroll_top + i
            self._draw_row(opt, self.hover_alphas[abs_i],
                           opt["type"] == "new",
                           M, start_y + i * step, row_w, self.ROW_H)

        if total == 1:
            self.screen.blit(
                self.f_note.render("No saved sessions yet — start a new one!", True, TEXT_FADED),
                (M + 14, start_y + step + 10))

        if total > self.max_visible_rows:
            sx = self.width - M - 14
            th = self.max_visible_rows * step - self.ROW_GAP
            pygame.draw.rect(self.screen, (200, 175, 130), (sx, start_y, 6, th), border_radius=3)
            thm  = max(22, int(th * self.max_visible_rows / total))
            thtop = start_y + int((self.scroll_top / total) * th)
            pygame.draw.rect(self.screen, ACCENT_BROWN, (sx, thtop, 6, thm), border_radius=3)
            if self.scroll_top > 0:
                self.screen.blit(self.f_hint.render("▲ more", True, TEXT_FADED), (M, start_y - 18))
            if self.scroll_top + self.max_visible_rows < total:
                self.screen.blit(
                    self.f_hint.render("▼ more", True, TEXT_FADED),
                    (M, start_y + self.max_visible_rows * step + 4))

    def _draw_row(self, opt, t, is_new, x, y, w, h):
        # Drop shadow when selected
        if t > 0.05:
            rrect(self.screen, (90, 60, 20), (x + 3, y + 4, w, h), radius=10, alpha=int(55 * t))

        # Card
        rrect(self.screen, lerp_color(BG_CARD, BG_CARD_SEL, t), (x, y, w, h), radius=10)

        # Left colour tab
        tab = lerp_color((125, 180, 115) if is_new else (175, 130, 75),
                         ACCENT_GREEN    if is_new else ACCENT_RUST, t)
        pygame.draw.rect(self.screen, tab, (x, y, 6, h), border_radius=10)

        # Border
        pygame.draw.rect(self.screen,
                         lerp_color((198, 178, 138), ACCENT_BROWN, t),
                         (x, y, w, h), 1 if t < 0.5 else 2, border_radius=10)

        # Icon
        icx, icy, icr = x + 20, y + h // 2, 19
        ic_bg = lerp_color((240, 195, 135) if not is_new else (155, 205, 148),
                           ACCENT_YELLOW   if not is_new else ACCENT_GREEN, t * 0.6)
        pygame.draw.circle(self.screen, ic_bg, (icx, icy), icr)
        pygame.draw.circle(self.screen,
                           lerp_color(CORK_DARK, ACCENT_RUST if not is_new else ACCENT_GREEN, t),
                           (icx, icy), icr, 2)

        if is_new:
            pc = lerp_color((50, 110, 40), TEXT_INK, t)
            for dx, dy in [((-8,0),(8,0)), ((0,-8),(0,8))]:
                pygame.draw.line(self.screen, pc,
                                 (icx + dx[0], icy + dx[1]),
                                 (icx + dy[0], icy + dy[1]), 2)
        else:
            sc = lerp_color((195, 155, 75), ACCENT_YELLOW, t)
            for a in range(0, 360, 60):
                ang = math.radians(a)
                ex = icx + int((icr - 3) * math.cos(ang))
                ey = icy + int((icr - 3) * math.sin(ang))
                pygame.draw.line(self.screen, sc, (icx, icy), (ex, ey), 1)
            pygame.draw.circle(self.screen, sc, (icx, icy), 4)

        # Text
        tx = icx + icr + 13
        lc = lerp_color(TEXT_BROWN, TEXT_INK, t)
        if is_new:
            lc = lerp_color((72, 132, 62), ACCENT_GREEN, t)
        self.screen.blit(self.f_label.render(opt["label"], True, lc), (tx, y + 12))
        self.screen.blit(
            self.f_meta.render(opt["meta"], True, lerp_color(TEXT_FADED, TEXT_BROWN, t)),
            (tx, y + 36))

        # Score star badge
        if not is_new and t > 0.3 and "score" in opt:
            ss  = self.f_badge.render(f"★ {opt['score']}", True, ACCENT_YELLOW)
            alpha_s = pygame.Surface(ss.get_size(), pygame.SRCALPHA)
            alpha_s.blit(ss, (0, 0))
            alpha_s.set_alpha(int(255 * min(1.0, (t - 0.3) / 0.7)))
            self.screen.blit(alpha_s, (x + w - ss.get_width() - 20, y + (h - ss.get_height()) // 2))

        # Enter hint
        if t > 0.65:
            hs  = self.f_hint.render("ENTER ↵", True,
                                     lerp_color(TEXT_FADED, ACCENT_BROWN if not is_new else ACCENT_GREEN, t))
            ha  = pygame.Surface(hs.get_size(), pygame.SRCALPHA)
            ha.blit(hs, (0, 0))
            ha.set_alpha(int(255 * ((t - 0.65) / 0.35)))
            self.screen.blit(ha, (x + w - hs.get_width() - 22,
                                  y + (h - hs.get_height()) // 2))

    def _draw_footer(self):
        M, fy = self.MARGIN, self.height - 46
        cx = M + 10
        for key, desc in [("↑ ↓", "Navigate"), ("Enter", "Open"), ("Esc", "Quit")]:
            ks = self.f_badge.render(key, True, TEXT_LIGHT)
            kw, kh = ks.get_size()
            rrect(self.screen, ACCENT_BROWN, (cx, fy, kw + 12, kh + 6), radius=6, alpha=205)
            self.screen.blit(ks, (cx + 6, fy + 3))
            cx += kw + 14
            ds = self.f_hint.render(desc, True, (210, 188, 158))
            self.screen.blit(ds, (cx, fy + 3))
            cx += ds.get_width() + 26

    def _list_saved_experiments(self):
        d = Path(__file__).resolve().parent.parent / "data" / "experiments"
        if not d.exists():
            return []
        items = []
        for fp in sorted(d.glob("exp-*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            items.append({
                "name":        fp.stem,
                "created_at":  data.get("created_at", "-"),
                "difficulty":  data.get("difficulty", {}).get("name", "UNKNOWN"),
                "final_score": data.get("summary", {}).get("final_score", 0),
                "file_path":   str(fp),
            })
        return items

    def _load_saved_summary(self, file_path):
        try:
            return json.loads(Path(file_path).read_text(encoding="utf-8")).get("summary")
        except Exception:
            return None