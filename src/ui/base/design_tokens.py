"""
Cyberpunk Design Tokens
========================
Single source of truth untuk Cyberpunk theme

File: src/ui/base/design_tokens.py (NEW FILE)
"""


class CyberpunkColors:
    """Cyberpunk color palette - Neon & Dark"""
    
    # ========== PRIMARY COLORS (NEON) ==========
    NEON_CYAN = '#00F5FF'          # Primary - Electric cyan
    NEON_CYAN_GLOW = '#00F5FF80'   # 50% opacity for glow
    NEON_CYAN_DIM = '#00B8D4'      # Dimmed cyan
    
    NEON_PINK = '#FF006E'          # Accent - Hot pink
    NEON_PINK_GLOW = '#FF006E80'   
    NEON_PINK_DIM = '#E91E63'
    
    NEON_GREEN = '#39FF14'         # Success - Neon green
    NEON_GREEN_GLOW = '#39FF1480'
    NEON_GREEN_DIM = '#00E676'
    
    NEON_ORANGE = '#FF6B35'        # Warning - Cyber orange
    NEON_ORANGE_GLOW = '#FF6B3580'
    NEON_ORANGE_DIM = '#FF5722'
    
    NEON_PURPLE = '#B026FF'        # Info - Electric purple
    NEON_PURPLE_GLOW = '#B026FF80'
    NEON_PURPLE_DIM = '#9C27B0'
    
    # ========== BACKGROUND COLORS (DARK) ==========
    BG_VOID = '#0A0A0F'            # Deepest background (almost black with blue tint)
    BG_DARK = '#0D0D14'            # App background
    BG_SURFACE = '#1A1F2E'         # Surface (cards, panels) - dark blue-gray
    BG_ELEVATED = '#232938'        # Elevated elements
    BG_INPUT = '#1A1F2E'           # Input fields
    BG_HOVER = '#2D3548'           # Hover state
    BG_ACTIVE = '#3A4355'          # Active/pressed state
    
    # ========== TEXT COLORS ==========
    TEXT_PRIMARY = '#FFFFFF'       # Pure white
    TEXT_SECONDARY = '#B0E0E6'     # Light cyan tint
    TEXT_TERTIARY = '#8B9DC3'      # Muted blue-gray
    TEXT_DISABLED = '#4A5568'      # Dark gray
    TEXT_PLACEHOLDER = '#667085'   # Placeholder text
    
    # ========== BORDER & LINES ==========
    BORDER_DEFAULT = '#2D3748'     # Default border
    BORDER_LIGHT = '#3A4556'       # Light border
    BORDER_FOCUS = NEON_CYAN       # Focus border (neon cyan)
    BORDER_ERROR = NEON_PINK       # Error border (neon pink)
    
    # ========== GRID & PATTERNS ==========
    GRID_LINE = '#1E2738'          # Cyber grid lines
    SCAN_LINE = '#00F5FF20'        # Scan line effect (subtle cyan)


class CyberpunkTypography:
    """Typography scale - Futuristic feel"""
    
    # Font families (fallback to system fonts)
    FONT_PRIMARY = "'Rajdhani', 'Orbitron', 'Exo 2', 'Segoe UI', sans-serif"
    FONT_MONO = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"
    
    # Font sizes (px)
    SIZE_XXXL = 32   # Page titles
    SIZE_XXL = 24    # Section headers
    SIZE_XL = 18     # Card headers
    SIZE_L = 16      # Large text
    SIZE_M = 13      # Body text (default)
    SIZE_S = 11      # Small text
    SIZE_XS = 10     # Tiny text
    
    # Font weights
    WEIGHT_LIGHT = 300
    WEIGHT_REGULAR = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_BOLD = 700
    WEIGHT_BLACK = 900


class CyberpunkSpacing:
    """Spacing scale - 4px base unit"""
    
    XS = 4      # 4px
    SM = 8      # 8px
    MD = 12     # 12px
    LG = 16     # 16px
    XL = 24     # 24px
    XXL = 32    # 32px
    XXXL = 48   # 48px


class CyberpunkSizes:
    """Component sizes"""
    
    # Button heights
    BUTTON_SM = 32
    BUTTON_MD = 40
    BUTTON_LG = 48
    BUTTON_XL = 56
    
    # Input heights
    INPUT_SM = 32
    INPUT_MD = 40
    INPUT_LG = 48
    
    # Border radius
    RADIUS_SM = 3
    RADIUS_MD = 6
    RADIUS_LG = 10
    RADIUS_XL = 16
    RADIUS_FULL = 9999  # Pill shape
    
    # Icon sizes
    ICON_SM = 16
    ICON_MD = 24
    ICON_LG = 32


class CyberpunkEffects:
    """Visual effects - Glows, shadows, animations"""
    
    # Glow effects (box-shadow)
    GLOW_CYAN_SM = f'0 0 8px {CyberpunkColors.NEON_CYAN_GLOW}'
    GLOW_CYAN_MD = f'0 0 16px {CyberpunkColors.NEON_CYAN_GLOW}'
    GLOW_CYAN_LG = f'0 0 24px {CyberpunkColors.NEON_CYAN_GLOW}, 0 0 48px {CyberpunkColors.NEON_CYAN_GLOW}'
    
    GLOW_PINK_SM = f'0 0 8px {CyberpunkColors.NEON_PINK_GLOW}'
    GLOW_PINK_MD = f'0 0 16px {CyberpunkColors.NEON_PINK_GLOW}'
    
    GLOW_GREEN_SM = f'0 0 8px {CyberpunkColors.NEON_GREEN_GLOW}'
    GLOW_GREEN_MD = f'0 0 16px {CyberpunkColors.NEON_GREEN_GLOW}'
    
    # Shadow (subtle depth)
    SHADOW_SM = '0 2px 8px rgba(0, 0, 0, 0.4)'
    SHADOW_MD = '0 4px 16px rgba(0, 0, 0, 0.5)'
    SHADOW_LG = '0 8px 32px rgba(0, 0, 0, 0.6)'
    
    # Animation durations (ms)
    DURATION_FAST = 150
    DURATION_NORMAL = 250
    DURATION_SLOW = 400


# ========== SEMANTIC COLOR MAPPING ==========

class CyberpunkSemantic:
    """Semantic color mapping untuk components"""
    
    # Button variants
    BUTTON_PRIMARY = CyberpunkColors.NEON_CYAN
    BUTTON_SUCCESS = CyberpunkColors.NEON_GREEN
    BUTTON_WARNING = CyberpunkColors.NEON_ORANGE
    BUTTON_DANGER = CyberpunkColors.NEON_PINK
    BUTTON_INFO = CyberpunkColors.NEON_PURPLE
    BUTTON_DEFAULT = CyberpunkColors.BG_ELEVATED
    
    # Status colors
    STATUS_SUCCESS = CyberpunkColors.NEON_GREEN
    STATUS_WARNING = CyberpunkColors.NEON_ORANGE
    STATUS_ERROR = CyberpunkColors.NEON_PINK
    STATUS_INFO = CyberpunkColors.NEON_CYAN


# ========== HELPER FUNCTIONS ==========

def get_color(name: str) -> str:
    """
    Get color by semantic name
    
    Usage:
        color = get_color('primary')
    """
    color_map = {
        'primary': CyberpunkColors.NEON_CYAN,
        'accent': CyberpunkColors.NEON_PINK,
        'success': CyberpunkColors.NEON_GREEN,
        'warning': CyberpunkColors.NEON_ORANGE,
        'danger': CyberpunkColors.NEON_PINK,
        'info': CyberpunkColors.NEON_PURPLE,
        
        'bg-void': CyberpunkColors.BG_VOID,
        'bg-dark': CyberpunkColors.BG_DARK,
        'bg-surface': CyberpunkColors.BG_SURFACE,
        'bg-elevated': CyberpunkColors.BG_ELEVATED,
        
        'text-primary': CyberpunkColors.TEXT_PRIMARY,
        'text-secondary': CyberpunkColors.TEXT_SECONDARY,
        
        'border': CyberpunkColors.BORDER_DEFAULT,
        'border-focus': CyberpunkColors.BORDER_FOCUS,
    }
    return color_map.get(name, CyberpunkColors.TEXT_PRIMARY)


def get_glow(color: str = 'cyan', size: str = 'md') -> str:
    """
    Get glow effect by color and size
    
    Usage:
        glow = get_glow('cyan', 'md')
    """
    glows = {
        'cyan': {
            'sm': CyberpunkEffects.GLOW_CYAN_SM,
            'md': CyberpunkEffects.GLOW_CYAN_MD,
            'lg': CyberpunkEffects.GLOW_CYAN_LG,
        },
        'pink': {
            'sm': CyberpunkEffects.GLOW_PINK_SM,
            'md': CyberpunkEffects.GLOW_PINK_MD,
        },
        'green': {
            'sm': CyberpunkEffects.GLOW_GREEN_SM,
            'md': CyberpunkEffects.GLOW_GREEN_MD,
        },
    }
    return glows.get(color, {}).get(size, CyberpunkEffects.GLOW_CYAN_MD)