import pygame
import math
import sys
from random import uniform, choice


# ──────────────────────────────────────────────────────────────────
#  WARM KITCHEN PALETTE
# ──────────────────────────────────────────────────────────────────
C_BG_WARM      = ( 62,  40,  22)
C_BG_MID       = ( 85,  57,  32)
C_PARCHMENT    = (245, 232, 205)
C_PARCHMENT_DK = (210, 190, 155)
C_WOOD_LIGHT   = (185, 140,  85)
C_WOOD_DARK    = (110,  72,  35)
C_SAGE         = ( 90, 145,  90)
C_SAGE_LIGHT   = (155, 205, 140)
C_SAGE_DK      = ( 52,  95,  52)
C_TERRACOTTA   = (195,  90,  55)
C_GOLDEN       = (200, 155,  35)
C_INK          = ( 40,  28,  18)
C_INK_SOFT     = ( 95,  68,  45)
C_WHITE_WARM   = (252, 248, 238)


# ──────────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


# ──────────────────────────────────────────────────────────────────
#  FALLING PETALS
# ──────────────────────────────────────────────────────────────────
PETAL_COLORS = [
    (230, 100,  70),
    (240, 200,  65),
    (100, 175,  80),
    (215, 165, 100),
    (180,  80,  80),
    (170, 220, 155),
]

class Petal:
    def __init__(self, w, h):
        self.x      = uniform(0, w)
        self.y      = uniform(-50, -5)
        self.vx     = uniform(-0.5, 0.5)
        self.vy     = uniform(0.7, 1.8)
        self.angle  = uniform(0, 360)
        self.spin   = uniform(-1.5, 1.5)
        self.pw     = int(uniform(9, 20))
        self.ph     = int(self.pw * uniform(0.35, 0.60))
        self.color  = choice(PETAL_COLORS)
        self.life   = 1.0
        self.ab     = int(uniform(130, 200))
        self.screen_h = h

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin
        if self.y > self.screen_h + 20:
            self.life = 0

    def draw(self, surface):
        s = pygame.Surface((self.pw * 2, self.ph * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*self.color, self.ab),
                            (0, 0, self.pw * 2, self.ph * 2))
        rs = pygame.transform.rotate(s, self.angle)
        surface.blit(rs, (int(self.x) - rs.get_width()  // 2,
                          int(self.y) - rs.get_height() // 2))


# ──────────────────────────────────────────────────────────────────
#  DRAWING PRIMITIVES
# ──────────────────────────────────────────────────────────────────

def draw_panel(surface, rect, fill=C_PARCHMENT, border=C_WOOD_DARK,
               alpha=248, radius=14, shadow=True):
    if shadow:
        sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 55),
                         (0, 0, rect.width + 8, rect.height + 8),
                         border_radius=radius + 3)
        surface.blit(sh, (rect.x + 4, rect.y + 7))
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha),
                     (0, 0, rect.width, rect.height), border_radius=radius)
    pygame.draw.rect(s, (*border, 210),
                     (0, 0, rect.width, rect.height), width=3, border_radius=radius)
    surface.blit(s, rect.topleft)


def draw_arc_gauge(surface, cx, cy, radius, pct, fg,
                   bg=C_PARCHMENT_DK, thickness=11,
                   start=math.pi * 0.78, span=math.pi * 1.44):
    steps = 100
    bg_pts = [(cx + math.cos(start - i/steps*span)*radius,
               cy - math.sin(start - i/steps*span)*radius)
              for i in range(steps + 1)]
    if len(bg_pts) > 1:
        pygame.draw.lines(surface, bg, False, bg_pts, thickness)
    n = max(1, int(steps * min(pct, 1.0)))
    fg_pts = [(cx + math.cos(start - i/steps*span)*radius,
               cy - math.sin(start - i/steps*span)*radius)
              for i in range(n + 1)]
    if len(fg_pts) > 1:
        pygame.draw.lines(surface, fg, False, fg_pts, thickness)
        ex = cx + math.cos(start - n/steps*span) * radius
        ey = cy - math.sin(start - n/steps*span) * radius
        pygame.draw.circle(surface, fg, (int(ex), int(ey)), thickness // 2 + 1)


def draw_bar(surface, x, y, w, h, pct, fg, bg=C_PARCHMENT_DK, radius=5):
    pygame.draw.rect(surface, bg,  (x, y, w, h), border_radius=radius)
    fw = int(w * min(max(pct, 0), 1.0))
    if fw > 0:
        pygame.draw.rect(surface, fg, (x, y, fw, h), border_radius=radius)


def divider(surface, x, y, w, thick=3):
    pygame.draw.rect(surface, C_WOOD_LIGHT, (x, y, w, thick), border_radius=2)
    if thick > 1:
        pygame.draw.rect(surface, C_WOOD_DARK, (x, y + thick, w, 1))


def motivational_msg(acc):
    if   acc >= 0.85: return "Outstanding session — fantastic work!"
    elif acc >= 0.70: return "Great effort — your grip is getting stronger!"
    elif acc >= 0.50: return "Good session — keep practising every day."
    elif acc >= 0.30: return "Nice work — every rep counts!"
    else:             return "You showed up — that's what matters most."


# ──────────────────────────────────────────────────────────────────
#  BACKGROUND — warm wood planks
# ──────────────────────────────────────────────────────────────────

def draw_bg(surface, w, h):
    surface.fill(C_BG_WARM)
    for i in range(0, h, 18):
        shade = 7 if (i // 18) % 2 == 0 else 0
        c = (C_BG_MID[0]+shade, C_BG_MID[1]+shade//2, C_BG_MID[2])
        pygame.draw.rect(surface, c, (0, i, w, 17))


# ──────────────────────────────────────────────────────────────────
#  END SCREEN
# ──────────────────────────────────────────────────────────────────

class EndScreen:
    def __init__(self, surface, summary):
        self.surface = surface
        self.W, self.H = surface.get_size()
        self.stats = summary.get("statistics", {})
        self.score = summary.get("final_score", 0)
        self.total = max(self.stats.get("total_attempts", 1), 1)

        self.p_pct = self.stats.get("perfect_grips",    0) / self.total
        self.c_pct = self.stats.get("compensated_grips",0) / self.total
        self.w_pct = self.stats.get("wrong_objects",    0) / self.total

        self.tick   = 0
        self.anim_t = 0.0
        self.done   = False

        self.petals = [Petal(self.W, self.H) for _ in range(32)]

        self.f_title = pygame.font.SysFont("georgia",  44, bold=True)
        self.f_sub   = pygame.font.SysFont("georgia",  14)
        self.f_score = pygame.font.SysFont("impact",   80)
        self.f_big   = pygame.font.SysFont("impact",   36)
        self.f_med   = pygame.font.SysFont("georgia",  24, bold=True)
        self.f_lbl   = pygame.font.SysFont("georgia",  12, bold=True)
        self.f_sm    = pygame.font.SysFont("georgia",  12)
        self.f_msg   = pygame.font.SysFont("georgia",  13, italic=True)
        self.f_btn   = pygame.font.SysFont("georgia",  21, bold=True)

        self._btn_r = pygame.Rect(0, 0, 0, 0)
        self._btn_q = pygame.Rect(0, 0, 0, 0)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            a = self._events()
            if a:
                return a
            self._update()
            self._draw()
            pygame.display.flip()

    def _events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return "quit"
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: return "quit"
                if ev.key in (pygame.K_RETURN, pygame.K_r): return "restart"
            if ev.type == pygame.MOUSEBUTTONDOWN and self.done:
                mx, my = ev.pos
                if self._btn_r.collidepoint(mx, my): return "restart"
                if self._btn_q.collidepoint(mx, my): return "quit"
        return None

    def _update(self):
        self.tick += 1
        if not self.done:
            self.anim_t = min(1.0, self.anim_t + 0.018)
            if self.anim_t >= 1.0:
                self.done = True
        for p in self.petals:
            p.update()
        self.petals = [p for p in self.petals if p.life > 0]
        while len(self.petals) < 30:
            self.petals.append(Petal(self.W, self.H))

    def _draw(self):
        t = ease_out_cubic(self.anim_t)

        draw_bg(self.surface, self.W, self.H)
        for p in self.petals:
            p.draw(self.surface)

        # ── HEADER ──────────────────────────────────────────────
        hy = int(lerp(-55, 20, t))
        ts = self.f_title.render("Session Complete", True, C_PARCHMENT)
        self.surface.blit(ts, (self.W//2 - ts.get_width()//2, hy))
        ss = self.f_sub.render("Grip Fruit  ·  Rehabilitation Training",
                               True, C_WOOD_LIGHT)
        self.surface.blit(ss, (self.W//2 - ss.get_width()//2, hy + 52))
        divider(self.surface, self.W//2 - 260, hy + 74, 520, thick=3)

        # ── LAYOUT ──────────────────────────────────────────────
        cy   = 118          # content top y
        ph   = 350          # INCREASED: Panel height (was 306)
        PAD  = 26
        PW_L = 282          # WIDENED: Matches right panel width for symmetry (was 228)
        PW_C = 316
        PW_R = 282
        total_w = PW_L + PW_C + PW_R + PAD * 2
        lx  = self.W // 2 - total_w // 2
        sl  = int(lerp(55, 0, t))   # slide amount

        RL = pygame.Rect(lx - sl,                        cy, PW_L, ph)
        RC = pygame.Rect(lx + PW_L + PAD,                cy + int(lerp(28,0,t)), PW_C, ph)
        RR = pygame.Rect(lx + PW_L + PW_C + PAD*2 + sl, cy, PW_R, ph)

        # ── LEFT: Score panel ────────────────────────────────────
        draw_panel(self.surface, RL)

        lbl_s = self.f_lbl.render("TOTAL SCORE", True, C_INK_SOFT)
        self.surface.blit(lbl_s, (RL.centerx - lbl_s.get_width() // 2, RL.y + 16))
        divider(self.surface, RL.x + 18, RL.y + 36, RL.width - 36, thick=2)

        sc_s = self.f_score.render(str(int(self.score * t)), True, C_SAGE_DK)
        # Centered vertically using RL.centery
        self.surface.blit(sc_s, (RL.centerx - sc_s.get_width() // 2, RL.centery - sc_s.get_height() // 2))

        # Accuracy badge (Shifted down to balance the taller box)
        acc = self.p_pct

        msg_s = self.f_msg.render(motivational_msg(acc), True, C_INK_SOFT)
        self.surface.blit(msg_s, (RL.centerx - msg_s.get_width() // 2, RL.y + 295))

        # ── CENTRE: Arc gauges ───────────────────────────────────
        draw_panel(self.surface, RC)

        ct = self.f_lbl.render("GRIP BREAKDOWN", True, C_INK_SOFT)
        self.surface.blit(ct, (RC.centerx - ct.get_width()//2, RC.y + 16))
        divider(self.surface, RC.x + 18, RC.y + 36, RC.width - 36, thick=2)

        gcx = RC.centerx
        gcy = RC.y + 170 # Shifted gauge center down

        GAUGES = [
            (56,  self.p_pct * t, C_SAGE,       "Perfect",     self.stats.get("perfect_grips",    0), 13),
            (80,  self.c_pct * t, C_GOLDEN,     "Compensated", self.stats.get("compensated_grips", 0), 11),
            (106, self.w_pct * t, C_TERRACOTTA, "Wrong",       self.stats.get("wrong_objects",      0), 10),
        ]
        for r, pct, col, _, _, thick in GAUGES:
            draw_arc_gauge(self.surface, gcx, gcy, r, pct, col,
                           bg=C_PARCHMENT_DK, thickness=thick)

        tot_n = self.f_med.render(str(self.stats.get("total_attempts", 0)), True, C_INK)
        tot_l = self.f_lbl.render("ATTEMPTS", True, C_INK_SOFT)
        self.surface.blit(tot_n, (gcx - tot_n.get_width()//2, gcy - 18))
        self.surface.blit(tot_l, (gcx - tot_l.get_width()//2, gcy + 12))

        # Legend (Shifted down)
        leg_y = RC.y + 290
        leg_spacing = (RC.width - 28) // len(GAUGES)
        for i, (_, _, col, label, count, _) in enumerate(GAUGES):
            lx2 = RC.x + 14 + i * leg_spacing + leg_spacing // 2
            pygame.draw.circle(self.surface, col, (lx2, leg_y + 6), 5)
            ln = self.f_sm.render(f"{label} ({count})", True, C_INK_SOFT)
            self.surface.blit(ln, (lx2 - ln.get_width()//2, leg_y + 15))

        # ── RIGHT: Bar stats ─────────────────────────────────────
        draw_panel(self.surface, RR)

        rt = self.f_lbl.render("STATISTICS", True, C_INK_SOFT)
        self.surface.blit(rt, (RR.centerx - rt.get_width()//2, RR.y + 16))
        divider(self.surface, RR.x + 18, RR.y + 36, RR.width - 36, thick=2)

        BARS = [
            ("Perfect Grips",   self.p_pct, C_SAGE,       self.stats.get("perfect_grips",    0)),
            ("Compensated",     self.c_pct, C_GOLDEN,     self.stats.get("compensated_grips", 0)),
            ("Wrong Objects",   self.w_pct, C_TERRACOTTA, self.stats.get("wrong_objects",      0)),
        ]
        bx  = RR.x + 20
        bw  = RR.width - 40
        by0 = RR.y + 52

        for i, (label, pct, col, count) in enumerate(BARS):
            by = by0 + i * 85 # Spaced the bars out slightly more
            l_s = self.f_lbl.render(label.upper(), True, C_INK_SOFT)
            c_s = self.f_med.render(str(count), True, col)
            p_s = self.f_sm.render(f"{int(pct * 100)}%", True, C_INK_SOFT)
            self.surface.blit(l_s, (bx, by))
            self.surface.blit(c_s, (bx, by + 16))
            self.surface.blit(p_s, (RR.right - 20 - p_s.get_width(), by + 20))
            draw_bar(self.surface, bx, by + 50, bw, 13, pct * t, col)

        # Bottom section (Shifted down)
        divider(self.surface, RR.x + 18, RR.y + 310, RR.width - 36, thick=1)
        tl = self.f_sm.render(
            f"Total attempts:  {self.stats.get('total_attempts', 0)}",
            True, C_INK_SOFT)
        self.surface.blit(tl, (RR.centerx - tl.get_width()//2, RR.y + 318))

        # ── BUTTONS ──────────────────────────────────────────────
        btn_y = cy + ph + 28
        bw2, bh = 210, 52
        self._btn_r = pygame.Rect(self.W//2 - bw2 - 16, btn_y, bw2, bh)
        self._btn_q = pygame.Rect(self.W//2 + 16,       btn_y, bw2, bh)

        mx, my = pygame.mouse.get_pos()
        for rect, text, fill, border in [
            (self._btn_r, "Play Again  [R]", C_SAGE_DK,   C_SAGE),
            (self._btn_q, "Quit  [Esc]",     C_WOOD_DARK, C_WOOD_LIGHT),
        ]:
            hov = rect.collidepoint(mx, my)
            draw_panel(self.surface, rect,
                       fill=fill if hov else C_PARCHMENT,
                       border=border if hov else C_WOOD_DARK,
                       alpha=245, radius=10, shadow=True)
            bs = self.f_btn.render(text, True,
                                    C_WHITE_WARM if hov else C_INK)
            self.surface.blit(bs, (rect.centerx - bs.get_width()//2,
                                    rect.centery - bs.get_height()//2))


# ──────────────────────────────────────────────────────────────────
#  PUBLIC API
# ──────────────────────────────────────────────────────────────────

def show_end_screen(screen, summary: dict) -> str:
    return EndScreen(screen, summary).run()

