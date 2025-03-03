import sys
import pygame
import requests

from io import BytesIO

server_address = 'https://static-maps.yandex.ru/v1?'
API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'


def render_search(screen, first=False):
    font = pygame.font.Font(None, 30)
    text = font.render("Адрес:", True, (30, 30, 30))
    screen.blit(text, (10, 25))
    if first:
        pygame.draw.rect(screen, (255, 255, 255), (90, 15, 500, 35), 0)
    pygame.draw.rect(screen, (50, 50, 50), (90, 15, 500, 35), 2)


def map_resp(long, leng, spn="0.05", pt=None):
    params = {"ll": f"{long},{leng}",
              "spn": f"{spn},{spn}",
              "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"}

    if pt:
        params["pt"] = f"{pt},pm2rdm"

    try:
        response = requests.get(server_address, params=params)
        if response:
            im = BytesIO(response.content)
            return im

    except Exception:
        print("Ошибка выполнения запроса")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return None


def geocode(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}" \
                       f"&geocode={address}&format=json"

    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


def input_address(screen, address):
    global long, leng, point
    if event.key == pygame.K_RETURN:
        long, leng = get_coordinates(address)
        address = ""
        try:
            point = f"{long},{leng}"
            mapa = map_resp(long, leng, pt=point)
            if mapa:
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(mapa), (0, 0))
                render_search(screen, first=True)
            else:
                print("Некорректный адрес")

        except Exception:
            print("Ошибка выполнения запроса")

    elif event.key == pygame.K_BACKSPACE:
        address = address[:-1]

    else:
        alpha = event.unicode
        if alpha not in "!@#$%^&*()+=-?:%;№`~{}[]<>":
            address += alpha

    pygame.draw.rect(screen, (255, 255, 255), (90, 15, 500, 35), 0)
    pygame.draw.rect(screen, (200, 200, 200), (90, 15, 500, 35), 2)

    font = pygame.font.Font(None, 40)
    text = font.render(address, True, (80, 80, 80))
    screen.blit(text, (95, 20))
    return address


pygame.init()
screen = pygame.display.set_mode((600, 450))
point = None
long = "37.530887"
leng = "55.703118"
spn = "0.05"
screen.blit(pygame.image.load(map_resp(long, leng, spn)), (0, 0))
render_search(screen, first=True)
pygame.display.flip()
address = ""
inputting = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN and not inputting:
            if event.key == pygame.K_PAGEUP or event.key == pygame.K_w:
                spn = str(round(float(spn) - 0.005, 3))
                if float(spn) <= 0.005:
                    spn = "0.001"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            if event.key == pygame.K_PAGEDOWN or event.key == pygame.K_s:
                spn = str(round(float(spn) + 0.005, 3))
                if float(spn) >= 0.95:
                    spn = "0.95"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            if event.key == pygame.K_UP:
                leng = str(round(float(leng) + 0.01, 3))
                if float(leng) >= 77:
                    leng = "77.000"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            if event.key == pygame.K_DOWN:
                leng = str(round(float(leng) - 0.01, 3))
                if float(leng) <= 35:
                    leng = "35.000"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            if event.key == pygame.K_LEFT:
                long = str(round(float(long) - 0.01, 3))
                if float(long) <= 23:
                    long = "23.000"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            if event.key == pygame.K_RIGHT:
                long = str(round(float(long) + 0.01, 3))
                if float(long) >= 180:
                    long = "180.000"
                screen.fill((0, 0, 0))
                screen.blit(pygame.image.load(map_resp(long, leng, spn, pt=point)), (0, 0))

            render_search(screen, first=True)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0], event.pos[1]
            if x < 590 and x > 90 and y < 50 and y > 15:
                pygame.draw.rect(screen, (200, 200, 200), (90, 15, 500, 35), 2)
                inputting = True
            else:
                render_search(screen)
                inputting = False

        elif inputting and event.type == pygame.KEYDOWN:
             address = input_address(screen, address)

    pygame.display.flip()