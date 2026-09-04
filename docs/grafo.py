#!/usr/bin/env python3
"""Genera el grafo de ejemplo del README: un vault ficticio con la estética
del graph view de Obsidian. Sin datos reales de nadie."""
import math

W, H = 1200, 640
BG, EDGE, NODE, HUB, TEXT, DIM = "#191919", "#3a3a3a", "#bdbdbd", "#e8e8e8", "#a8a8a8", "#6e6e6e"

# (id, x, y, radio, etiqueta, anclaje del texto, dy del texto)
N = {
    "MEMORY":        (600, 320, 15, "MEMORY", "middle", 34),

    # contextos raíz
    "tu-nombre":     (330, 190, 12, "tu-nombre", "middle", -20),
    "acme":          (880, 250, 13, "acme", "middle", -20),
    "arch-linux":    (430, 500, 11, "arch-linux", "middle", 28),

    # repos de la organización
    "acme-api":      (1060, 140, 10, "acme-api", "start", 5),
    "acme-web":      (1090, 330, 10, "acme-web", "start", 5),
    "acme-infra":    (980, 460, 10, "acme-infra", "start", 5),

    # lo propio
    "mi-side-project": (140, 120, 10, "mi-side-project", "middle", -18),
    "el-blog":         (120, 300, 9, "el-blog", "end", 5),

    # decisiones y técnicas
    "pagos-van-por-cola":        (1130, 40, 8, "pagos-van-por-cola", "end", -14),
    "por-que-no-usamos-orm":     (900, 100, 8, "por-que-no-usamos-orm", "middle", -14),
    "el-cron-corre-en-utc":      (1150, 560, 8, "el-cron-corre-en-utc", "end", 22),
    "docker-cachea-el-lock":     (830, 570, 8, "docker-cachea-el-lock", "middle", 22),
    "el-portapapeles-necesita-x": (270, 600, 8, "el-portapapeles-necesita-x", "middle", 22),
    "systemd-arranca-sin-path":  (600, 540, 8, "systemd-arranca-sin-path", "middle", 22),
    "el-deploy-borra-el-cache":  (400, 60, 8, "el-deploy-borra-el-cache", "middle", -14),
    "una-nota-por-hecho":        (640, 130, 8, "una-nota-por-hecho", "start", -14),
    "los-specs-no-van-en-un-pr": (170, 430, 8, "los-specs-no-van-en-un-pr", "middle", 22),
}

E = [
    # el índice solo apunta a los contextos raíz y a lo transversal
    ("MEMORY", "tu-nombre"), ("MEMORY", "acme"), ("MEMORY", "arch-linux"),
    ("MEMORY", "una-nota-por-hecho"), ("MEMORY", "los-specs-no-van-en-un-pr"),
    # cada contexto indexa a sus hijos
    ("acme", "acme-api"), ("acme", "acme-web"), ("acme", "acme-infra"),
    ("tu-nombre", "mi-side-project"), ("tu-nombre", "el-blog"),
    # las notas cuelgan de su contexto, y una nota puede tener dos dueños
    ("acme-api", "pagos-van-por-cola"), ("acme", "pagos-van-por-cola"),
    ("acme-api", "por-que-no-usamos-orm"),
    ("acme-infra", "el-cron-corre-en-utc"), ("acme-infra", "docker-cachea-el-lock"),
    ("acme-web", "el-deploy-borra-el-cache"),
    ("arch-linux", "el-portapapeles-necesita-x"), ("arch-linux", "systemd-arranca-sin-path"),
    ("mi-side-project", "el-deploy-borra-el-cache"),
    ("acme-web", "acme-api"),
    ("el-blog", "los-specs-no-van-en-un-pr"),
]


def borde(a, b):
    """Recorta la arista en el borde de cada círculo, para que la flecha no
    quede tapada por el nodo (así se ven en Obsidian)."""
    x1, y1, r1 = N[a][0], N[a][1], N[a][2]
    x2, y2, r2 = N[b][0], N[b][1], N[b][2]
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    return x1 + ux * (r1 + 2), y1 + uy * (r1 + 2), x2 - ux * (r2 + 7), y2 - uy * (r2 + 7)


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="ui-sans-serif,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
    f'markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{EDGE}"/></marker></defs>',
]

for a, b in E:
    x1, y1, x2, y2 = borde(a, b)
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
               f'stroke="{EDGE}" stroke-width="1.1" marker-end="url(#f)"/>')

for k, (x, y, r, etiqueta, anclaje, dy) in N.items():
    hub = k in ("MEMORY", "acme", "tu-nombre", "arch-linux")
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{HUB if hub else NODE}"/>')
    dx = {"start": r + 8, "end": -(r + 8), "middle": 0}[anclaje]
    out.append(f'<text x="{x + dx}" y="{y + dy}" fill="{TEXT if hub else DIM}" '
               f'font-size="{14 if hub else 12}" text-anchor="{anclaje}">{etiqueta}</text>')

out.append('</svg>')
open("/home/wdcprado/Projects/harness/claude/better-agent-brain/docs/grafo.svg", "w").write("\n".join(out))
print("ok")
