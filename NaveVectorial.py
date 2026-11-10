import sys
import math
import pygame

# ==============================================================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN DEL LIENZO
# ==============================================================================
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colores (RGB)
BLACK = (15, 15, 20)
WHITE = (240, 240, 240)
CYAN = (0, 255, 220)
YELLOW = (255, 220, 0)

pygame.init()
# La ventana se crea utilizando Double Buffering por defecto en Pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Nave Espacial Vectorial 2D")
clock = pygame.time.Clock()

# ==============================================================================
# 2. PROPIEDADES DE LA NAVE Y MODELO LOCAL
# ==============================================================================
# Modelo local del triángulo respecto al origen (0, 0)
# Proa (punta) posicionada exactamente en (0, -25)
LOCAL_SHIP_MODEL = [
    (0, -25),   # Proa (Punta)
    (-15, 15),  # Esquina inferior izquierda
    (15, 15)    # Esquina inferior derecha
]

# Estado inicial de la nave (Espacio de Pantalla: 400, 300)
ship_x = WIDTH / 2.0
ship_y = HEIGHT / 2.0
ship_angle = 0.0  # Ángulo de rotación en grados (0° apunta hacia arriba)

ROTATION_SPEED = 180.0  # Grados por segundo
ACCELERATION = 300.0     # Píxeles por segundo al avanzar

# Configuración de disparos
bullets = []  # Lista dinámica de proyectiles
BULLET_SPEED = 600.0   # Píxeles por segundo (más rápido que la nave)
COOLDOWN_MS = 250      # Tiempo mínimo entre disparos (milisegundos)
last_shot_time = 0

# ==============================================================================
# BUCLE PRINCIPAL DE LA SIMULACIÓN
# ==============================================================================
running = True
while running:
    # Delta time en segundos para asegurar movimiento fluido e independiente del frame rate
    dt = clock.tick(FPS) / 1000.0
    current_time = pygame.time.get_ticks()

    # --------------------------------------------------------------------------
    # GESTIÓN DE EVENTOS
    # --------------------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --------------------------------------------------------------------------
    # CAPTURA DE TECLADO Y CONTROLES EN TIEMPO REAL
    # --------------------------------------------------------------------------
    keys = pygame.key.get_pressed()

    # 3. Rotación Geométrica (A / D o Flechas Izquierda / Derecha)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        ship_angle -= ROTATION_SPEED * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        ship_angle += ROTATION_SPEED * dt

    # Mantiene el ángulo en el rango [0, 360)
    ship_angle %= 360.0

    # 4. Avance Vectorial Continuo (W o Flecha Arriba)
    # Convertimos el ángulo a radianes para las funciones trigonométricas.
    # Restamos 90° debido a que la proa apunta hacia arriba (0, -25) en el modelo local.
    rad = math.radians(ship_angle - 90)

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        ship_x += math.cos(rad) * ACCELERATION * dt
        ship_y += math.sin(rad) * ACCELERATION * dt

    # --------------------------------------------------------------------------
    # RETO OPCIONAL: SCREEN WRAPPING (PANTALLA ENVOLVENTE)
    # --------------------------------------------------------------------------
    if ship_x > WIDTH:
        ship_x = 0
    elif ship_x < 0:
        ship_x = WIDTH

    if ship_y > HEIGHT:
        ship_y = 0
    elif ship_y < 0:
        ship_y = HEIGHT

    # --------------------------------------------------------------------------
    # 5. TRANSFORMACIÓN DEL MODELO LOCAL A ESPACIO PANTALLA
    # --------------------------------------------------------------------------
    world_ship_vertices = []
    for lx, ly in LOCAL_SHIP_MODEL:
        # Rotación geométrica 2D en torno al origen local
        rx = lx * math.cos(rad + math.pi/2) - ly * math.sin(rad + math.pi/2)
        ry = lx * math.sin(rad + math.pi/2) + ly * math.cos(rad + math.pi/2)
        
        # Traslación a la posición actual de la nave en el mundo/pantalla
        wx = rx + ship_x
        wy = ry + ship_y
        world_ship_vertices.append((wx, wy))

    # La punta de la nave (proa) es siempre el primer vértice transformado
    nose_x, nose_y = world_ship_vertices[0]

    # --------------------------------------------------------------------------
    # GENERACIÓN DINÁMICA DE PROYECTILES (Barra Espaciadora)
    # --------------------------------------------------------------------------
    if keys[pygame.K_SPACE]:
        if current_time - last_shot_time >= COOLDOWN_MS:
            # Calcular vector de velocidad del proyectil basado en la orientación de la proa
            vx = math.cos(rad) * BULLET_SPEED
            vy = math.sin(rad) * BULLET_SPEED
            
            # Instanciar proyectil como diccionario
            bullets.append({
                'x': nose_x,
                'y': nose_y,
                'vx': vx,
                'vy': vy,
                'life': 2.0  # Tiempo de vida en segundos
            })
            last_shot_time = current_time

    # --------------------------------------------------------------------------
    # 6. GESTIÓN DE MEMORIA Y CICLO DE VIDA DE PROYECTILES
    # --------------------------------------------------------------------------
    active_bullets = []
    for b in bullets:
        # Actualizar posición del proyectil
        b['x'] += b['vx'] * dt
        b['y'] += b['vy'] * dt
        b['life'] -= dt

        # Criterio de eliminación de memoria:
        # Mantener solo si está dentro de la pantalla y le queda tiempo de vida
        in_bounds = (0 <= b['x'] <= WIDTH) and (0 <= b['y'] <= HEIGHT)
        if in_bounds and b['life'] > 0:
            active_bullets.append(b)

    # Reemplazar la lista con solo los proyectiles activos
    bullets = active_bullets

    # --------------------------------------------------------------------------
    # RENDERIZADO / DIBUJO EN PANTALLA
    # --------------------------------------------------------------------------
    screen.fill(BLACK)

    # Dibujar proyectiles
    for b in bullets:
        pygame.draw.circle(screen, YELLOW, (int(b['x']), int(b['y'])), 3)

    # Dibujar nave vectorial (Triángulo)
    pygame.draw.polygon(screen, CYAN, world_ship_vertices, 2)

    # Actualizar pantalla (Double Buffering)
    pygame.display.flip()

# Salida limpia del programa
pygame.quit()
sys.exit()