import random
from item import FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP


FIXED   = "fixed"
RANDOM  = "weighted_random"

# For debugging
DEFAULT_SEQUENCE = [
    FRESH_FRUIT, FRESH_FRUIT, ROTTEN_FRUIT,
    FRESH_FRUIT, FRESH_FRUIT, KETCHUP,
    FRESH_FRUIT, FRESH_FRUIT, FRESH_FRUIT, ROTTEN_FRUIT,
]


class LevelManager:
    """

    item_timeout 
    spawn_delay  (in frames)
    sequence_mode : str
        FIXED           
        RANDOM (default)
    sequence : list[str] used when sequence_mode == FIXED.
    """

    def __init__(
        self,
        level_id:      int   = 1,
        level_name:    str   = "Level 1",
        total_items:   int   = 10,
        item_timeout:  int   = 100,   # frames  (~1.67 s at 60 fps)
        spawn_delay:   int   = 60,    # frames  (~1.00 s at 60 fps)
        sequence_mode: str   = RANDOM,
        sequence:      list  = None,
        fresh_weight:  float = 0.60,
        rotten_weight: float = 0.25,
        ketchup_weight: float = 0.15,
    ):
        
        self.level_id   = level_id
        self.level_name = level_name
        self.item_timeout = item_timeout
        self.spawn_delay  = spawn_delay

        self.total_items   = total_items
        self.items_spawned = 0          # how many have appeared so far
        self.items_done    = 0          # how many have been resolved (squeezed or timed-out)

        self.sequence_mode = sequence_mode

        # fall back to the default 
        self.sequence       = sequence if sequence is not None else DEFAULT_SEQUENCE
        self._sequence_idx  = 0         # current position inside the fixed list

        # Weighted random pools
        self._item_types   = [FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP]
        self._item_weights = [fresh_weight, rotten_weight, ketchup_weight]

        # ── State ─────────────────────────────────────────────────────────────
        self.is_active    = False       # True while the level is running
        self.is_complete  = False       # True once total_items have been resolved
        self._spawn_timer = 0           # counts down before the next item spawns


    def start(self):
        """Call once to begin the level."""
        self.is_active    = True
        self.is_complete  = False
        self.items_spawned = 0
        self.items_done    = 0
        self._sequence_idx = 0
        self._spawn_timer  = 0   
    def update(self, current_item) -> bool:
        """
            True  → a new item should be created this frame (caller's job).
            False → nothing to do yet.
        """
        if not self.is_active or self.is_complete:
            return False

        if current_item is not None and not current_item.is_on_screen:
            self.items_done += 1
            # Check level completion
            if self.items_done >= self.total_items:
                self.is_complete = True
                self.is_active   = False
                return False

        if current_item is None or not current_item.is_on_screen:
            if self.items_spawned >= self.total_items:
                return False          

            self._spawn_timer += 1
            if self._spawn_timer >= self.spawn_delay:
                self._spawn_timer = 0
                return True             # signal: spawn the next item

        return False

    def next_item_type(self) -> str:
        if self.sequence_mode == FIXED:
            item_type = self.sequence[self._sequence_idx % len(self.sequence)]
            self._sequence_idx += 1
        else:
            item_type = random.choices(self._item_types, weights=self._item_weights, k=1)[0]

        self.items_spawned += 1
        return item_type

    def get_item_timeout(self) -> int:
        return self.item_timeout

    def get_summary(self) -> dict:
    
        return {
            "level_id":      self.level_id,
            "level_name":    self.level_name,
            "total_items":   self.total_items,
            "items_spawned": self.items_spawned,
            "items_done":    self.items_done,
            "is_complete":   self.is_complete,
        }

    def reset(self):
        self.start()


# ── Built-in level presets (provided by AI)────────────────────────────────────────────────────

def make_warmup_level() -> LevelManager:
    """Easy warm-up: slow timeout, long gaps, mostly fresh fruit."""
    return LevelManager(
        level_id      = 1,
        level_name    = "Warm-up",
        total_items   = 8,
        item_timeout  = 150,   # very generous
        spawn_delay   = 90,
        sequence_mode = FIXED,
        sequence      = [
            FRESH_FRUIT, FRESH_FRUIT, FRESH_FRUIT,
            ROTTEN_FRUIT,
            FRESH_FRUIT, FRESH_FRUIT, FRESH_FRUIT,
            KETCHUP,
        ],
    )


def make_standard_level() -> LevelManager:
    """Balanced mid-game level."""
    return LevelManager(
        level_id      = 2,
        level_name    = "Standard",
        total_items   = 12,
        item_timeout  = 100,
        spawn_delay   = 60,
        sequence_mode = RANDOM,
        fresh_weight  = 0.60,
        rotten_weight = 0.25,
        ketchup_weight= 0.15,
    )


def make_challenge_level() -> LevelManager:
    """Fast, tricky level for advanced players."""
    return LevelManager(
        level_id      = 3,
        level_name    = "Challenge",
        total_items   = 15,
        item_timeout  = 60,    # only ~1 second at 60 fps
        spawn_delay   = 30,
        sequence_mode = RANDOM,
        fresh_weight  = 0.55,
        rotten_weight = 0.25,
        ketchup_weight= 0.20,
    )