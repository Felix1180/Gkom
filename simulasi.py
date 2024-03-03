import pygame
import sys
import pygame_gui
from button import Button
import math

pygame.init()
pilihan = 0

# Konstanta layar
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Warna
WHITE = (255, 255, 255) # Screen
BLACK = (0, 0, 0) # Banyak
BLUE = (0, 0, 255) # Titik lengkung
YELLOW = (240, 240, 0) # Titik fokus
GREY = (220, 220, 220) # Grid
DARK_GREY = (150, 150, 150) # Bayangan
MAGENTA = (255, 0 , 255) # 1
TURQUOISE = (64, 224, 208) # 2
PURPLE = (128, 0 ,128) # 3

#Jari-jari lingkaran (cermin)
xr = 60
yr = 720

# Inisialisasi jarak titik fokus (nilai default)
jarak_titik_fokus = 150
jarak_titik_fokus2 = - jarak_titik_fokus
# Inisialisasi jarak benda (s) dan tinggi benda (h) (nilai default)
jarak_benda = 300
tinggi_benda = 120
lebar_benda = tinggi_benda * 0.1

# Inisialisasi visibilitas fitur
visible = True

# Membuat jendela simulasi
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometric Optic")

# Inisialisasi UI manager
ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Fungsi untuk menyembunyikan slider
def hide_sliders(sliders):
    if visible:
        for slider in sliders:
            slider.hide()
    else:
        for slider in sliders:
            slider.show()


def draw_arc(surface, color, rect, start_angle, stop_angle, titik_fokus, lebar):
    # Helper function to draw a single pixel
    def draw_pixel(x, y):
        pygame.draw.circle(surface, color, (int(x), int(y)), lebar)

    x0, y0, width, height = rect
    # Calculate center of ellipse
    cx = x0 + width // 2
    cy = y0 + height // 2

    # Calculate distance from focus point to the center of the program
    distance_to_center = abs(titik_fokus - width // 2)

    # Interpolate to find the radii
    min_radius_x = 50  # Minimum radius x when titik_fokus is at 0
    max_radius_x = 10  # Maximum radius x when titik_fokus is at 640
    max_focus_distance = 640  # Maximum distance titik_fokus from center for minimum radius
    rx = min_radius_x + (max_radius_x - min_radius_x) * (1 - distance_to_center / max_focus_distance)

    # Adjusting ry to be larger than rx to make it more elongated
    ry = 300  # You can adjust this factor to control the elongation

    # Midpoint algorithm for ellipse drawing
    def draw_arc_points(cx, cy, rx, ry, start_angle, stop_angle):
        # Convert angles to degrees
        start_angle = math.degrees(start_angle)
        stop_angle = math.degrees(stop_angle)

        # Ensure stop_angle is greater than start_angle
        if stop_angle <= start_angle:
            stop_angle += 360

        # Convert angles back to radians
        start_angle = math.radians(start_angle)
        stop_angle = math.radians(stop_angle)

        # Midpoint algorithm for ellipse drawing
        theta = start_angle
        while theta <= stop_angle:
            x = cx + int(rx * math.cos(theta))
            y = cy - int(ry * math.sin(theta))
            draw_pixel(x, y)
            theta += 1 / max(rx, ry)

    draw_arc_points(cx, cy, rx, ry, start_angle, stop_angle)

def draw_grid_DDA(surface, color, width, height, cell_size):
    # Gambar garis horizontal
    for y in range(0, height, cell_size):
        draw_line_DDA(surface, color, (0, y), (width, y), lebar=1)

    # Gambar garis vertikal
    for x in range(0, width, cell_size):
        draw_line_DDA(surface, color, (x, 0), (x, height), lebar=1)

# Fungsi DDA untuk menggambar garis
def draw_line_DDA(surface, color, start, end, sinar=False, dashed=False, terbalik=False, lebar=2):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    steps = max(abs(dx), abs(dy))

    if terbalik:
        x_increment = -dx / steps
        y_increment = -dy / steps
    else:
        x_increment = dx / steps
        y_increment = dy / steps

    x = start[0]
    y = start[1]

    draw = True
    length = 0

    if not sinar:
        for _ in range(int(steps)):
            if dashed:
                if draw:
                    pygame.draw.circle(surface, color, (int(x), int(y)), lebar)
            else:
                pygame.draw.circle(surface, color, (int(x), int(y)), lebar)

            x += x_increment
            y += y_increment
            length += 1

            if dashed and length >= 10:
                draw = not draw
                length = 0
    else:
        while (0 <= x < SCREEN_WIDTH) and (0 <= y < SCREEN_HEIGHT):
            if dashed:
                if draw:
                    pygame.draw.circle(surface, color, (int(x), int(y)), lebar)
            else:
                pygame.draw.circle(surface, color, (int(x), int(y)), lebar)
            x += x_increment
            y += y_increment
            length += 1

            if dashed and length >= 10:
                draw = not draw
                length = 0

# Fungsi untuk menggambar huruf pada layar
def draw_text(surface, text, color, position, size=18):
    font = pygame.font.SysFont("lucidaconsole", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)  # mengatur posisi teks ke tengah
    surface.blit(text_surface, text_rect)

# Fungsi untuk membuat slider
def create_slider(manager, rect, start_value, value_range):
    return pygame_gui.elements.UIHorizontalSlider(
        relative_rect=rect,
        start_value=start_value,
        value_range=value_range,
        manager=manager
    )

def create_button(manager, rect, text):
    return pygame_gui.elements.UIButton(
        relative_rect=rect,
        text=text,
        manager=manager
    )

# Loop utama
clock = pygame.time.Clock()

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Candara_Bold.ttf", size)

# Membuat slider untuk tinggi benda
distance_slider_tinggi = create_slider(ui_manager, pygame.Rect(270, 611.25, 480, 25), 50, (-360, 360))

# Membuat slider untuk jarak benda
distance_slider = create_slider(ui_manager, pygame.Rect(270, 647.5, 480, 25), 150, (640, -640))

# Membuat slider untuk titik fokus
distance_slider_fokus = create_slider(ui_manager, pygame.Rect(270, 683.75, 480, 25), 100, (640, 0))

allowed_characters = ["0","1","2","3","4","5","6","7","8","9","-"]

# Membuat input box untuk tinggi benda
tinggi_benda_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(SCREEN_WIDTH * 0.6, 611.25, 50, 25),
    manager=ui_manager,
)
tinggi_benda_input.set_allowed_characters(allowed_characters)
tinggi_benda_input.set_text(str(tinggi_benda))

jarak_benda_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(SCREEN_WIDTH * 0.6, 647.5, 50, 25),
    manager=ui_manager,
)
jarak_benda_input.set_allowed_characters(allowed_characters)
jarak_benda_input.set_text(str(jarak_benda))

# Membuat input box untuk jarak titik fokus
jarak_titik_fokus_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect(SCREEN_WIDTH * 0.6, 683.75, 50, 25),
    manager=ui_manager,
)
jarak_titik_fokus_input.set_allowed_characters('numbers')
jarak_titik_fokus_input.set_text(str(jarak_titik_fokus))
# List elemen
sliders = [tinggi_benda_input, jarak_benda_input, jarak_titik_fokus_input, distance_slider_tinggi, distance_slider,
           distance_slider_fokus]

# Membuat tombol untuk menyembunyikan dan menampilkan slider
hide_button = create_button(ui_manager, pygame.Rect(1140, 620, 100, 30), "Hide/Show")
back_button = create_button(ui_manager, pygame.Rect(1140, 670, 100,30), "<<<")

def main_menu():
    while True:
        screen.fill(WHITE)

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("Geometric Optics", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        cermin_surface = pygame.image.load("assets/Cermin.jpg")
        cermin_surface = pygame.transform.scale(cermin_surface, (300, 400))
        CERMIN_BUTTON = Button(cermin_surface, pos=(440, 360),
                               text_input="CONCAVE MIRROR", font=get_font(30), base_color="#000000", hovering_color="#808080")

        lensa_surface = pygame.image.load("assets/Lensa_Cembung.jpg")
        lensa_surface = pygame.transform.scale(lensa_surface, (300, 400))
        LENSA_BUTTON = Button(lensa_surface, pos=(840, 360),
                              text_input="CONVEX LENS", font=get_font(30), base_color="#000000", hovering_color="#808080")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [CERMIN_BUTTON, LENSA_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CERMIN_BUTTON.checkForInput(MENU_MOUSE_POS):
                    simulasi(1)
                    return
                elif LENSA_BUTTON.checkForInput(MENU_MOUSE_POS):
                    simulasi(2)
                    return

        pygame.display.flip()

def simulasi(pilihan):
    global jarak_benda, visible, jarak_titik_fokus, jarak_titik_fokus2, tinggi_benda, lebar_benda, BACK_BUTTON

    while True:
        time_delta = clock.tick(120) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                # Periksa jika event berasal dari input box
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == jarak_benda_input:
                        if -640 <= float(event.text) <= 640:
                            jarak_benda = float(event.text)

                        else:
                            jarak_benda = 200
                        jarak_benda_input.set_text(str(jarak_benda))

                    elif event.ui_element == jarak_titik_fokus_input:
                        if 0 <= float(event.text) <= 640:
                            jarak_titik_fokus = float(event.text)

                        else:
                            jarak_titik_fokus = 150

                        if pilihan == 2:
                            jarak_titik_fokus2 = - jarak_titik_fokus
                        jarak_titik_fokus_input.set_text(str(jarak_titik_fokus))

                    elif event.ui_element == tinggi_benda_input:
                        if -360 <= float(event.text) <= 360:
                            tinggi_benda = float(event.text)
                            lebar_benda = float(event.text) * 0.1

                        else:
                            tinggi_benda = 120
                            lebar_benda = tinggi_benda * 0.1
                        tinggi_benda_input.set_text(str(tinggi_benda))

                # Periksa jika event berasal dari slider
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    slider = event.ui_element
                    if slider == distance_slider:
                        jarak_benda = int(event.value)
                        jarak_benda_input.set_text(str(jarak_benda))

                    elif slider == distance_slider_fokus:
                        jarak_titik_fokus = int(event.value)
                        jarak_titik_fokus_input.set_text(str(jarak_titik_fokus))
                        if pilihan == 2:
                            jarak_titik_fokus2 = - jarak_titik_fokus

                    elif slider == distance_slider_tinggi:
                        tinggi_benda = int(event.value)
                        lebar_benda = int(event.value) * 0.1
                        tinggi_benda_input.set_text(str(tinggi_benda))

                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == hide_button:
                        hide_sliders(sliders)
                        visible = not visible
                    elif event.ui_element == back_button:
                        main_menu()
                        return

            ui_manager.process_events(event)

        if pilihan == 1:
            # Bersihkan layar
            screen.fill(WHITE)

            # Gambar grid
            draw_grid_DDA(screen, GREY, SCREEN_WIDTH, SCREEN_HEIGHT,60)  # Ubah nilai 60 sesuai dengan ukuran sel yang diinginkan

            # Gambar sumbu utama (x)
            draw_line_DDA(screen, BLACK, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2))

            # Gambar sumbu utama (y)
            draw_line_DDA(screen, BLACK, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT))

            # Menggambar cermin
            draw_arc(screen, BLACK, (-25, 0,  SCREEN_WIDTH, SCREEN_HEIGHT), math.radians(270), math.radians(90),jarak_titik_fokus, lebar=1)


            # Tentukan koordinat titik fokus (f)
            titik_fokus_x = (SCREEN_WIDTH // 2) - jarak_titik_fokus
            titik_fokus_y = SCREEN_HEIGHT // 2

            # Gambar penanda titik fokus (f)
            pygame.draw.circle(screen, YELLOW, (titik_fokus_x, titik_fokus_y), 8)

            # Tentukan koordinat jari-jari kelengkungan (R)
            jari_kelengkungan_x = (SCREEN_WIDTH // 2) - (2 * jarak_titik_fokus)
            jari_kelengkungan_y = SCREEN_HEIGHT // 2

            # Gambar penanda jari-jari kelengkungan (R)
            pygame.draw.circle(screen, BLUE, (jari_kelengkungan_x, jari_kelengkungan_y), 8)

            # Tentukan koordinat awal benda
            start_benda_x1 = (SCREEN_WIDTH // 2) - jarak_benda
            start_benda_y1 = SCREEN_HEIGHT // 2

            # Tentukan koordinat akhir benda inti
            end_benda_x1 = start_benda_x1
            end_benda_y1 = start_benda_y1 - tinggi_benda
            # ================================================#
            start_benda_x2 = start_benda_x1 - lebar_benda
            start_benda_y2 = start_benda_y1

            end_benda_x2 = start_benda_x2
            end_benda_y2 = start_benda_y1 - (tinggi_benda * 0.615)
            # ================================================#
            start_benda_x3 = start_benda_x1 + lebar_benda
            start_benda_y3 = start_benda_y1

            end_benda_x3 = start_benda_x3
            end_benda_y3 = start_benda_y1 - (tinggi_benda * 0.615)
            # ================================================#
            start_benda_x4 = end_benda_x2
            start_benda_y4 = end_benda_y2

            end_benda_x4 = end_benda_x2 - (tinggi_benda * 0.215)
            end_benda_y4 = end_benda_y2
            # ================================================#
            start_benda_x5 = end_benda_x3
            start_benda_y5 = end_benda_y3

            end_benda_x5 = end_benda_x3 + (tinggi_benda * 0.215)
            end_benda_y5 = end_benda_y3
            # ================================================#
            start_benda_x6 = end_benda_x4
            start_benda_y6 = end_benda_y4

            end_benda_x6 = end_benda_x1
            end_benda_y6 = end_benda_y1
            # ================================================#
            start_benda_x7 = end_benda_x5
            start_benda_y7 = end_benda_y5

            end_benda_x7 = end_benda_x1
            end_benda_y7 = end_benda_y1

            # Tentukan koordinat tulisan
            tulisan_x = SCREEN_WIDTH * 0.75
            tulisan_y = SCREEN_HEIGHT * 0.75

            if jarak_benda != 0 and tinggi_benda != 0 and jarak_titik_fokus != 0:

                # Gambar benda menggunakan DDA
                # draw_line_DDA(screen, GREY, (start_benda_x1, start_benda_y1), (end_benda_x1, end_benda_y1))
                draw_line_DDA(screen, BLACK, (start_benda_x2, start_benda_y2), (end_benda_x2, end_benda_y2))
                draw_line_DDA(screen, BLACK, (start_benda_x3, start_benda_y3), (end_benda_x3, end_benda_y3))
                draw_line_DDA(screen, BLACK, (start_benda_x4, start_benda_y4), (end_benda_x4, end_benda_y4))
                draw_line_DDA(screen, BLACK, (start_benda_x5, start_benda_y5), (end_benda_x5, end_benda_y5))
                draw_line_DDA(screen, BLACK, (start_benda_x6, start_benda_y6), (end_benda_x6, end_benda_y6))
                draw_line_DDA(screen, BLACK, (start_benda_x7, start_benda_y7), (end_benda_x7, end_benda_y7))
                draw_text(screen, "Objek", BLACK, (end_benda_x1, start_benda_y1 - (tinggi_benda * 1.2)))

                # Pemeriksaan jarak benda dan jarak titik fokus
                if jarak_benda != jarak_titik_fokus:
                    # Hitung jarak, tinggi bayangan dan perbesaran bayangan
                    jarak_bayangan = (jarak_benda * jarak_titik_fokus) / (jarak_benda - jarak_titik_fokus)
                    tinggi_bayangan = (-jarak_bayangan / jarak_benda) * tinggi_benda
                    perbesaran = (-jarak_bayangan / jarak_benda)

                    # Tentukan koordinat awal bayangan inti
                    start_bayangan_x1 = (SCREEN_WIDTH // 2) - jarak_bayangan
                    start_bayangan_y1 = SCREEN_HEIGHT // 2

                    # Tentukan koordinat akhir bayangan inti
                    end_bayangan_x1 = start_bayangan_x1
                    end_bayangan_y1 = start_bayangan_y1 - tinggi_bayangan
                    # ======================================================#
                    start_bayangan_x2 = start_bayangan_x1 + (lebar_benda * perbesaran)
                    start_bayangan_y2 = start_bayangan_y1

                    end_bayangan_x2 = start_bayangan_x2
                    end_bayangan_y2 = start_bayangan_y1 - (tinggi_bayangan * 0.615)
                    # ========================================================#
                    start_bayangan_x3 = start_bayangan_x1 - (lebar_benda * perbesaran)
                    start_bayangan_y3 = start_bayangan_y1

                    end_bayangan_x3 = start_bayangan_x3
                    end_bayangan_y3 = start_bayangan_y1 - (tinggi_bayangan * 0.615)
                    # ========================================================#
                    start_bayangan_x4 = end_bayangan_x2
                    start_bayangan_y4 = end_bayangan_y2

                    end_bayangan_x4 = end_bayangan_x2 + (tinggi_bayangan * 0.215)
                    end_bayangan_y4 = end_bayangan_y2
                    # ========================================================#
                    start_bayangan_x5 = end_bayangan_x3
                    start_bayangan_y5 = end_bayangan_y3

                    end_bayangan_x5 = end_bayangan_x3 - (tinggi_bayangan * 0.215)
                    end_bayangan_y5 = end_bayangan_y3
                    # ========================================================#
                    start_bayangan_x6 = end_bayangan_x4
                    start_bayangan_y6 = end_bayangan_y4

                    end_bayangan_x6 = end_bayangan_x1
                    end_bayangan_y6 = end_bayangan_y1
                    # ========================================================#
                    start_bayangan_x7 = end_bayangan_x5
                    start_bayangan_y7 = end_bayangan_y5

                    end_bayangan_x7 = end_bayangan_x1
                    end_bayangan_y7 = end_bayangan_y1

                    # Gambar bayangan menggunakan DDA
                    # draw_line_DDA(screen, GREY, (start_bayangan_x1, start_bayangan_y1), (end_bayangan_x1, end_bayangan_y1))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x2, start_bayangan_y2),
                                  (end_bayangan_x2, end_bayangan_y2))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x3, start_bayangan_y3),
                                  (end_bayangan_x3, end_bayangan_y3))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x4, start_bayangan_y4),
                                  (end_bayangan_x4, end_bayangan_y4))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x5, start_bayangan_y5),
                                  (end_bayangan_x5, end_bayangan_y5))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x6, start_bayangan_y6),
                                  (end_bayangan_x6, end_bayangan_y6))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x7, start_bayangan_y7),
                                  (end_bayangan_x7, end_bayangan_y7))

                    if jarak_benda > 0:

                        if jarak_benda > jarak_titik_fokus:

                            if jarak_benda > jarak_titik_fokus * 2:  # Ruang 3
                                sifat = ("Nyata, Terbalik, Diperkecil")

                            elif jarak_benda == jarak_titik_fokus * 2:  # Di jari-jari kelengkungan
                                sifat = ("Nyata, Terbalik, Sama besar")

                            elif jarak_benda > jarak_titik_fokus:  # Ruang 2
                                sifat = ("Nyata, Terbalik, Diperbesar")

                            # Sinar istimewa pertama
                            # Garis pertama
                            draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                          (start_benda_x1, end_benda_y1), True)
                            # Garis kedua
                            draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                          (start_bayangan_x1, end_bayangan_y1), True)

                            # Sinar istimewa kedua
                            # Garis pertama
                            draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                          (start_bayangan_x1, end_bayangan_y1), True)
                            # Garis kedua
                            draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                          (start_benda_x1, end_benda_y1), True)


                        else:  # Ruang 1
                            sifat = ("Maya, Tegak, Diperbesar")
                            # Sinar istimewa pertama
                            # Garis pertama
                            draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                          (start_benda_x1, end_benda_y1), True)
                            # Garis kedua
                            draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                          (start_bayangan_x1, end_bayangan_y1), True, True)
                            # Garis Ketiga
                            draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                          (titik_fokus_x, titik_fokus_y), True)

                            # Sinar istimewa kedua
                            # Garis pertama
                            draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                          (start_bayangan_x1, end_bayangan_y1), True, True)
                            # Garis kedua
                            draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                          (start_benda_x1, end_benda_y1), True)
                            # Garis Ketiga
                            draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                          (start_bayangan_x1, end_bayangan_y1), True, False, True)

                        draw_text(screen, sifat, BLACK, (
                        start_bayangan_x1, start_bayangan_y1 - (tinggi_bayangan * 1.2)))  # Tampilkan teks sifat bayangan


                    else:  # Cembung
                        sifat = ("Maya, Tegak, Diperkecil")

                        # Sinar istimewa pertama
                        # Garis pertama
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (start_benda_x1, end_benda_y1),True)
                        # Garis kedua
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),(start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis ketiga
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (start_bayangan_x1, end_bayangan_y1), True, False, True)

                        # Sinar istimewa kedua
                        # Garis pertama
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),(start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis kedua
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),(start_benda_x1, end_benda_y1), True)
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),(start_bayangan_x1, end_bayangan_y1), True, False, True)

                        draw_text(screen, sifat, BLACK, (start_bayangan_x1, start_bayangan_y1 - (tinggi_bayangan * 1.2)))  # Tampilkan teks sifat bayangan

                else:
                    # Sinar istimewa pertama
                    # Garis pertama
                    draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (end_benda_x1, end_benda_y1), True)
                    # Garis kedua
                    draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (titik_fokus_x, titik_fokus_y), True)

                    draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (titik_fokus_x, titik_fokus_y),True, True, True)

                    # Sinar istimewa ketiga
                    # Garis pertama
                    draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, start_benda_y1 - (tinggi_benda * 2)), (jari_kelengkungan_x, jari_kelengkungan_y), True)
                    # Garis kedua
                    draw_line_DDA(screen, TURQUOISE, (jari_kelengkungan_x, jari_kelengkungan_y), (start_benda_x1, end_benda_y1), True, True)

            if visible:
                # Gambar persegi panjang berwarna grey
                pygame.draw.rect(screen, GREY, (210, 600, 860, 120))

                # Keterangan slider
                draw_text(screen, "h ->", BLACK, (240, 623.25), size=16)
                draw_text(screen, "d ->", BLACK, (240, 659.5), size=16)
                draw_text(screen, "f ->", BLACK, (240, 695.75), size=16)

                if jarak_benda != 0 and jarak_titik_fokus !=0 and tinggi_benda !=0 and jarak_benda != jarak_titik_fokus:
                    draw_text(screen, f"ho: {round(tinggi_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 623.25), size=16)
                    draw_text(screen, f"hi: {round(tinggi_bayangan, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 623.25), size=16)

                    draw_text(screen, f"do: {round(jarak_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 659.5), size=16)
                    draw_text(screen, f"di: {round(jarak_bayangan, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 659.5), size=16)

                    draw_text(screen, f"f: {round(jarak_titik_fokus, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 695.75), size=16)
                    draw_text(screen, f"M: {round(perbesaran, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 695.75), size=16)

                elif jarak_benda < 0:
                    draw_text(screen, f"ho: {round(tinggi_benda, 1)}    ", BLACK, (SCREEN_WIDTH * 0.69, 623.25), size=16)
                    draw_text(screen, f"hi: {round(tinggi_bayangan, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 623.25), size=16)

                    draw_text(screen, f"do: {round(jarak_benda, 1) * - 1}     ", BLACK, (SCREEN_WIDTH * 0.69, 659.5),
                              size=16)
                    draw_text(screen, f"di: {round(jarak_bayangan, 1) * -1}", BLACK, (SCREEN_WIDTH * 0.775, 659.5), size=16)

                    draw_text(screen, f"f: {round(jarak_titik_fokus, 1) * -1}", BLACK, (SCREEN_WIDTH * 0.69, 695.75),
                              size=16)
                    draw_text(screen, f"M: {round(perbesaran, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 695.75), size=16)

                else:
                    draw_text(screen, f"ho: {round(tinggi_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 623.25), size=16)
                    draw_text(screen, f"hi: ?", BLACK, (SCREEN_WIDTH * 0.775, 623.25), size=16)

                    draw_text(screen, f"do: {round(jarak_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 659.5), size=16)
                    draw_text(screen, f"di: ?", BLACK, (SCREEN_WIDTH * 0.775, 659.5), size=16)

                    draw_text(screen, f"f: {round(jarak_titik_fokus, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 695.75), size=16)
                    draw_text(screen, f"M: ?", BLACK, (SCREEN_WIDTH * 0.775, 695.75), size=16)
                    draw_text(screen, "Tidak ada bayangan", BLACK, (tulisan_x, tulisan_y))  # Tampilkan teks sifat bayangan

        elif pilihan == 2:
            # Bersihkan layar
            screen.fill(WHITE)

            # Gambar grid
            draw_grid_DDA(screen, GREY, SCREEN_WIDTH, SCREEN_HEIGHT,60)  # Ubah nilai 60 sesuai dengan ukuran sel yang Anda inginkan

            # Gambar sumbu utama (x)
            draw_line_DDA(screen, BLACK, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2))

            # Gamabr sumbu y
            draw_line_DDA(screen, BLACK, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT))

            draw_arc(screen, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), math.radians(90), math.radians(90), jarak_titik_fokus, lebar = 1)

            # Tentukan koordinat titik fokus (f1)
            titik_fokus_x1 = (SCREEN_WIDTH // 2) - jarak_titik_fokus
            titik_fokus_y1 = SCREEN_HEIGHT // 2

            # Tentukan koordinat titik fokus (f2)
            titik_fokus_x2 = (SCREEN_WIDTH // 2) - jarak_titik_fokus2
            titik_fokus_y2 = SCREEN_HEIGHT // 2

            # Gambar penanda titik fokus (f1)
            pygame.draw.circle(screen, YELLOW, (titik_fokus_x1, titik_fokus_y1), 5.5)
            # Gambar penanda titik fokus (f2)
            pygame.draw.circle(screen, YELLOW, (titik_fokus_x2, titik_fokus_y2), 5.5)

            # Tentukan koordinat jari-jari kelengkungan (R1)
            jari_kelengkungan_x1 = (SCREEN_WIDTH // 2) - (2 * jarak_titik_fokus)
            jari_kelengkungan_y1 = SCREEN_HEIGHT // 2

            # Tentukan koordinat jari-jari kelengkungan (R1)
            jari_kelengkungan_x2 = (SCREEN_WIDTH // 2) - (2 * jarak_titik_fokus2)
            jari_kelengkungan_y2 = SCREEN_HEIGHT // 2

            # Gambar penanda jari-jari kelengkungan (R1)
            pygame.draw.circle(screen, BLUE, (jari_kelengkungan_x1, jari_kelengkungan_y1), 5.5)

            # Gambar penanda jari-jari kelengkungan (R2)
            pygame.draw.circle(screen, BLUE, (jari_kelengkungan_x2, jari_kelengkungan_y2), 5.5)

            # Tentukan koordinat awal benda
            start_benda_x1 = (SCREEN_WIDTH // 2) - jarak_benda
            start_benda_y1 = SCREEN_HEIGHT // 2

            # Tentukan koordinat akhir benda
            end_benda_x1 = start_benda_x1
            end_benda_y1 = start_benda_y1 - tinggi_benda
            # ================================================#
            start_benda_x2 = start_benda_x1 - lebar_benda
            start_benda_y2 = start_benda_y1

            end_benda_x2 = start_benda_x2
            end_benda_y2 = start_benda_y1 - (tinggi_benda * 0.615)

            # ================================================#
            start_benda_x3 = start_benda_x1 + lebar_benda
            start_benda_y3 = start_benda_y1

            end_benda_x3 = start_benda_x3
            end_benda_y3 = start_benda_y1 - (tinggi_benda * 0.615)
            # ================================================#
            start_benda_x4 = end_benda_x2
            start_benda_y4 = end_benda_y2

            end_benda_x4 = end_benda_x2 - (tinggi_benda * 0.215)
            end_benda_y4 = end_benda_y2
            # ================================================#
            start_benda_x5 = end_benda_x3
            start_benda_y5 = end_benda_y3

            end_benda_x5 = end_benda_x3 + (tinggi_benda * 0.215)
            end_benda_y5 = end_benda_y3
            # ================================================#
            start_benda_x6 = end_benda_x4
            start_benda_y6 = end_benda_y4

            end_benda_x6 = end_benda_x1
            end_benda_y6 = end_benda_y1
            # ================================================#
            start_benda_x7 = end_benda_x5
            start_benda_y7 = end_benda_y5

            end_benda_x7 = end_benda_x1
            end_benda_y7 = end_benda_y1

            # Tentukan koordinat tulisan
            tulisan_x = SCREEN_WIDTH * 0.75
            tulisan_y = SCREEN_HEIGHT * 0.75

            if jarak_benda != 0 and tinggi_benda != 0 and jarak_titik_fokus != 0:
                # Gambar benda menggunakan DDA
                # draw_line_DDA(screen, BLACK, (start_benda_x1, start_benda_y1), (end_benda_x1, end_benda_y1))
                draw_line_DDA(screen, BLACK, (start_benda_x2, start_benda_y2), (end_benda_x2, end_benda_y2))
                draw_line_DDA(screen, BLACK, (start_benda_x3, start_benda_y3), (end_benda_x3, end_benda_y3))
                draw_line_DDA(screen, BLACK, (start_benda_x4, start_benda_y4), (end_benda_x4, end_benda_y4))
                draw_line_DDA(screen, BLACK, (start_benda_x5, start_benda_y5), (end_benda_x5, end_benda_y5))
                draw_line_DDA(screen, BLACK, (start_benda_x6, start_benda_y6), (end_benda_x6, end_benda_y6))
                draw_line_DDA(screen, BLACK, (start_benda_x7, start_benda_y7), (end_benda_x7, end_benda_y7))
                draw_text(screen, "Objek", BLACK, (end_benda_x1, start_benda_y1 - (tinggi_benda * 1.2)))

                # Pemeriksaan jarak benda dan jarak titik fokus
                if jarak_benda != jarak_titik_fokus:
                    # Hitung jarak dan tinggi bayangan
                    jarak_bayangan = (jarak_benda * jarak_titik_fokus) / (jarak_benda - jarak_titik_fokus)
                    tinggi_bayangan = (-jarak_bayangan / jarak_benda) * tinggi_benda
                    perbesaran = (-jarak_bayangan / jarak_benda)

                    # Tentukan koordinat awal bayangan
                    start_bayangan_x1 = (SCREEN_WIDTH // 2) + jarak_bayangan
                    start_bayangan_y1 = SCREEN_HEIGHT // 2

                    # Tentukan koordinat akhir bayangan
                    end_bayangan_x1 = start_bayangan_x1
                    end_bayangan_y1 = start_bayangan_y1 - tinggi_bayangan
                    # ======================================================#
                    start_bayangan_x2 = start_bayangan_x1 + (lebar_benda * perbesaran)
                    start_bayangan_y2 = start_bayangan_y1

                    end_bayangan_x2 = start_bayangan_x2
                    end_bayangan_y2 = start_bayangan_y1 - (tinggi_bayangan * 0.615)
                    # ========================================================#
                    start_bayangan_x3 = start_bayangan_x1 - (lebar_benda * perbesaran)
                    start_bayangan_y3 = start_bayangan_y1

                    end_bayangan_x3 = start_bayangan_x3
                    end_bayangan_y3 = start_bayangan_y1 - (tinggi_bayangan * 0.615)
                    # ========================================================#
                    start_bayangan_x4 = end_bayangan_x2
                    start_bayangan_y4 = end_bayangan_y2

                    end_bayangan_x4 = end_bayangan_x2 + (tinggi_bayangan * 0.215)
                    end_bayangan_y4 = end_bayangan_y2
                    # ========================================================#
                    start_bayangan_x5 = end_bayangan_x3
                    start_bayangan_y5 = end_bayangan_y3

                    end_bayangan_x5 = end_bayangan_x3 - (tinggi_bayangan * 0.215)
                    end_bayangan_y5 = end_bayangan_y3
                    # ========================================================#
                    start_bayangan_x6 = end_bayangan_x4
                    start_bayangan_y6 = end_bayangan_y4

                    end_bayangan_x6 = end_bayangan_x1
                    end_bayangan_y6 = end_bayangan_y1
                    # ========================================================#
                    start_bayangan_x7 = end_bayangan_x5
                    start_bayangan_y7 = end_bayangan_y5

                    end_bayangan_x7 = end_bayangan_x1
                    end_bayangan_y7 = end_bayangan_y1

                    # Gambar bayangan menggunakan DDA
                    # draw_line_DDA(screen, GREY, (start_bayangan_x1, start_bayangan_y1), (end_bayangan_x1, end_bayangan_y1))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x2, start_bayangan_y2),
                                  (end_bayangan_x2, end_bayangan_y2))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x3, start_bayangan_y3),
                                  (end_bayangan_x3, end_bayangan_y3))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x4, start_bayangan_y4),
                                  (end_bayangan_x4, end_bayangan_y4))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x5, start_bayangan_y5),
                                  (end_bayangan_x5, end_bayangan_y5))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x6, start_bayangan_y6),
                                  (end_bayangan_x6, end_bayangan_y6))
                    draw_line_DDA(screen, DARK_GREY, (start_bayangan_x7, start_bayangan_y7),
                                  (end_bayangan_x7, end_bayangan_y7))

                    if jarak_benda > jarak_titik_fokus:

                        if jarak_benda > jarak_titik_fokus * 2:  # Ruang 3
                            sifat = "Nyata, Terbalik, Diperkecil"

                        elif jarak_benda == jarak_titik_fokus * 2:  # Di jari-jari kelengkungan
                            sifat = "Nyata, Terbalik, Sama besar"

                        elif jarak_benda > jarak_titik_fokus:  # Ruang 2
                            sifat = "Nyata, Terbalik, Diperbesar"

                        # Sinar istimewa pertama
                        # Garis pertama
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_benda_x1, end_benda_y1), True)
                        # Garis kedua
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True)
                        #
                        # Sinar istimewa kedua
                        # Garis pertama
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True)
                        # Garis kedua
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_benda_x1, end_benda_y1), True)

                        # Sinar istimewa ketiga
                        # Garis pertama
                        draw_line_DDA(screen, PURPLE, (start_benda_x1, end_benda_y1),
                                      (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), True)
                        # Garis kedua
                        draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      (start_benda_x1, end_benda_y1), True)

                    elif jarak_benda < 0:  # Belakang
                        sifat = "Nyata, Tegak, Diperkecil"
                        # Sinar istimewa pertama
                        # Garis pertama
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_benda_x1, end_benda_y1), True)
                        # Garis kedua
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis ketiga
                        # draw_sinar_DDA(screen, ZAITUN, (SCREEN_WIDTH // 2, end_benda_y1), (start_bayangan_x1, end_bayangan_y1),False, True)
                        # Sinar istimewa kedua
                        # Garis pertama
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis kedua
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_benda_x1, end_benda_y1), True)
                        # Garis ketiga
                        # draw_sinar_DDA(screen, DEEP_PURPLE, (SCREEN_WIDTH // 2, end_bayangan_y1),(start_benda_x1, end_benda_y1), True, False, True)

                        # Garis pertama
                        draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      (start_benda_x1, end_benda_y1), True, True)
                        # Garis kedua
                        draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      (start_benda_x1, end_benda_y1), True, False, True)

                    elif jarak_benda < jarak_titik_fokus:  # Ruang 1
                        sifat = "Maya, Tegak, Diperbesar"
                        # Sinar istimewa pertama
                        # Garis pertama
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_benda_x1, end_benda_y1), True)
                        # Garis kedua
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis ketiga
                        draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, False, True)
                        # Sinar istimewa kedua
                        # Garis pertama
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, True)
                        # Garis kedua
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_benda_x1, end_benda_y1), True)
                        # Garis ketiga
                        draw_line_DDA(screen, TURQUOISE, (SCREEN_WIDTH // 2, end_bayangan_y1),
                                      (start_bayangan_x1, end_bayangan_y1), True, False, True)

                        # Garis pertama
                        draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      (start_benda_x1, end_benda_y1), True, True)
                        # Garis kedua
                        draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      (start_benda_x1, end_benda_y1), True, False, True)

                    draw_text(screen, sifat, BLACK,
                              (start_bayangan_x1, start_bayangan_y1 - (tinggi_bayangan * 1.2)))  # Tampilkan teks sifat bayangan

                else:
                    # Sinar istimewa pertama
                    # Garis pertama
                    draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (start_benda_x1, end_benda_y1),
                                  True)
                    # Garis kedua
                    draw_line_DDA(screen, MAGENTA, (SCREEN_WIDTH // 2, end_benda_y1), (titik_fokus_x2, titik_fokus_y2),
                                  True)

                    # Sinar istimewa ketiga
                    # Garis pertama
                    draw_line_DDA(screen, PURPLE, (start_benda_x1, end_benda_y1),
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), True)
                    # Garis kedua
                    draw_line_DDA(screen, PURPLE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                  (start_benda_x1, end_benda_y1), True)

            if visible:

                # Gambar persegi panjang berwarna grey
                pygame.draw.rect(screen, GREY, (210, 600, 860, 120))

                # Keterangan slider
                draw_text(screen, "h ->", BLACK, (240, 623.25), size=16)

                draw_text(screen, "d ->", BLACK, (240, 659.5), size=16)

                draw_text(screen, "f ->", BLACK, (240, 695.75), size=16)

                if jarak_benda != 0 and jarak_titik_fokus !=0 and tinggi_benda !=0 and jarak_benda != jarak_titik_fokus:

                    draw_text(screen, f"ho: {round(tinggi_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 623.25), size=16)

                    draw_text(screen, f"hi: {round(tinggi_bayangan, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 623.25), size=16)

                    draw_text(screen, f"do: {round(jarak_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 659.5), size=16)

                    draw_text(screen, f"di: {round(jarak_bayangan, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 659.5), size=16)

                    draw_text(screen, f"f: {round(jarak_titik_fokus, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 695.75), size=16)

                    draw_text(screen, f"M: {round(perbesaran, 1)}", BLACK, (SCREEN_WIDTH * 0.775, 695.75), size=16)

                else:

                    draw_text(screen, f"ho: {round(tinggi_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 623.25), size=16)

                    draw_text(screen, f"hi: ?", BLACK, (SCREEN_WIDTH * 0.775, 623.25), size=16)

                    draw_text(screen, f"do: {round(jarak_benda, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 659.5), size=16)

                    draw_text(screen, f"di: ?", BLACK, (SCREEN_WIDTH * 0.775, 659.5), size=16)

                    draw_text(screen, f"f: {round(jarak_titik_fokus, 1)}", BLACK, (SCREEN_WIDTH * 0.69, 695.75), size=16)

                    draw_text(screen, f"M: ?", BLACK, (SCREEN_WIDTH * 0.775, 695.75), size=16)

                    draw_text(screen, "Tidak ada bayangan", BLACK, (tulisan_x, tulisan_y))

        # Tampilkan slider dan elemen UI lainnya
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)

        # Tampilkan perubahan layar
        pygame.display.flip()

main_menu()