from ultralytics import YOLO
import numpy as np
import matplotlib.pyplot as plt


# Функция проверки, находится ли точка внутри многоугольника (алгоритм лучевого теста)
def is_inside_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def find_max_chord(points):
    max_distance = 0
    max_pair = (None, None)
    num_points = len(points)

    for i in range(num_points):
        for j in range(i + 1, num_points):
            dist = np.linalg.norm(points[i] - points[j])
            if dist > max_distance:
                max_distance = dist
                max_pair = (points[i], points[j])

    return max_pair, max_distance


# Функция получения полос
def get_stripes(polygon_points, stripe_width, offset):
    x_min, x_max = min(p[0] for p in polygon_points) - offset, max(p[0] for p in polygon_points) + offset
    y_min, y_max = min(p[1] for p in polygon_points) - stripe_width, max(p[1] for p in polygon_points) + stripe_width

    stripes = []
    y = y_min
    while y < y_max:
        segments = []
        x = x_min
        inside = False
        segment_start = None

        while x < x_max:
            if not ((not is_inside_polygon((x, y), polygon_points)) and (
            not is_inside_polygon((x, y + stripe_width), polygon_points))) or \
                    (is_inside_polygon((x + offset, y), polygon_points) and is_inside_polygon(
                        (x + offset, y + stripe_width), polygon_points)):
                if not inside:
                    segment_start = x - offset
                    inside = True
            else:
                if inside:
                    segments.append((segment_start, x + offset))
                    inside = False
            x += 1  # Шаг по x

        if inside:
            segments.append((segment_start, x))

        stripes.append((y, segments))
        y += stripe_width

    return stripes


# Функция рисования полос
def draw_stripes_1(polygon_points, stripes, stripe_width):
    """Рисует полосы на основе данных о полосах."""
    fig, ax = plt.subplots()
    ax.plot(*zip(*polygon_points), color='black')  # Обводим границу многоугольника

    for y, segments in stripes:
        for start, end in segments:
            ax.fill_betweenx([y, y + stripe_width], start, end, color='lightblue', edgecolor='blue', alpha=0.5)

    ax.set_aspect('equal', adjustable='datalim')
    plt.savefig('fig1.png')

def draw_stripes_2(polygon_points, stripes, stripe_width):
    """Рисует полосы на основе данных о полосах."""
    fig, ax = plt.subplots()
    ax.plot(*zip(*polygon_points), color='black')  # Обводим границу многоугольника

    for y, segments in stripes:
        for start, end in segments:
            ax.fill_betweenx([y, y + stripe_width], start, end, color='lightblue', edgecolor='blue', alpha=0.5)

    ax.set_aspect('equal', adjustable='datalim')
    plt.savefig('fig2.png')

def rotate_polygon(polygon_points, alpha):
    """Поворачивает точки многоугольника на угол alpha."""
    rotation_matrix = np.array([
        [np.cos(alpha), -np.sin(alpha)],
        [np.sin(alpha), np.cos(alpha)]
    ])
    #print(rotation_matrix)
    rotated_points = np.dot(polygon_points, rotation_matrix.T)
    return rotated_points


# Функция для подсчета площади всех полос
def calculate_total_area(stripes, stripe_width):
    total_area = 0
    for y, segments in stripes:
        for start, end in segments:
            total_area += (end - start) * stripe_width
    return total_area


# Функция для нахождения минимальной площади при варьировании угла поворота
def find_min_area(polygon_points, stripe_width, offset, step=0.1):
    """Находит минимальную площадь покрытия полосами, варьируя угол поворота."""
    min_area = float('inf')
    best_angle = 0

    # Поворот на угол от 0 до 2*pi с шагом
    for angle in np.arange(0, np.pi, step):
        print(angle)
        rotated_polygon = rotate_polygon(polygon_points, angle)

        # Получаем полосы для покрытия
        stripes = get_stripes(rotated_polygon, stripe_width, offset)

        # Вычисляем площадь
        area = calculate_total_area(stripes, stripe_width)

        if area < min_area:
            min_area = area
            best_angle = angle

    return min_area, best_angle


def calculate_perimeter_area_with_thickness(polygon_points, thickness):
    """
    Вычисляет площадь, занимаемую периметром многоугольника с заданной толщиной.

    :param polygon_points: Массив точек многоугольника (каждая точка - [x, y])
    :param thickness: Толщина полосы вокруг периметра

    :return: Площадь, занимаемая периметром с толщиной
    """
    n = len(polygon_points)
    total_area = 0

    # Проходим по всем рёбрам многоугольника
    for i in range(n - 1):
        p1 = polygon_points[i]
        p2 = polygon_points[i + 1]

        # Находим вектор рёбер
        edge_vector = p2 - p1
        edge_length = np.linalg.norm(edge_vector)  # Длина рёбра

        # Площадь полосы вокруг рёбра (толщина * длина рёбра)
        total_area += edge_length * thickness

    # Закрываем многоугольник (соединяем последнюю и первую точку)
    p1 = polygon_points[-1]
    p2 = polygon_points[0]
    edge_vector = p2 - p1
    edge_length = np.linalg.norm(edge_vector)  # Длина рёбра
    total_area += edge_length * thickness  # Добавляем последнюю полосу

    return total_area


# Вызов функции

# Load a model
model = YOLO("best (1).pt")  # pretrained YOLO11n model

# Run batched inference on a list of images
result = model('image_2024-12-01_09-46-33.png')  # return a list of Results
# Process results list
door_area = 1
front_left_door, front_right_door, front_car_fender,door = 0,0,0,0
print(model.names)
#print(result[0].boxes.cls[0].item()==7)
result[0].save(filename="result.jpg")  # save to disk
front_car_fender_id = -1
for i,mask in enumerate(result[0].masks):
    coords = np.vstack([mask.xy[0],mask.xy[0][0]])

    # Считаем площадь по формуле шнурка
    x, y = coords[:, 0], coords[:, 1]
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    if result[0].boxes.cls[i].item() == 10:
        front_left_door = area
    if result[0].boxes.cls[i].item() == 12:
        front_right_door = area
    if result[0].boxes.cls[i].item() == 8:
        front_car_fender = area
        front_car_fender_id = i


if front_left_door != 0 and front_right_door!=0:
    door = (front_left_door + front_right_door)/2
elif front_left_door != 0:
    door = front_left_door
elif front_right_door!=0:
    door = front_right_door
#print(door,front_bumper)
area = door_area/door*front_car_fender



print(area)
polygon_points = np.vstack([result[0].masks[front_car_fender_id].xy[0],result[0].masks[front_car_fender_id].xy[0][0]])
print(result[0].boxes.cls)
offset = 4
stripe_width = 10

# Вызов функции для нахождения минимальной площади
min_area, best_angle = find_min_area(polygon_points, stripe_width=stripe_width, offset=offset)
print(f"Минимальная площадь: {min_area}")
print(f"Лучший угол поворота: {best_angle}")

perimeter_area = calculate_perimeter_area_with_thickness(polygon_points, stripe_width)
print(f"Площадь периметра с толщиной {stripe_width}: {perimeter_area}")

rotated_polygon = rotate_polygon(polygon_points, 0)
#print(polygon_points,rotated_polygon)
# Получаем полосы для покрытия многоугольника
stripes = get_stripes(rotated_polygon, stripe_width=stripe_width, offset=offset)

# Рисуем полосы
draw_stripes_1(rotated_polygon, stripes, stripe_width=stripe_width)

# Вычисляем суммарную площадь всех полос
total_area_1 = calculate_total_area(stripes, stripe_width=stripe_width) + perimeter_area
print(f"Суммарная площадь всех полос: {total_area_1}")

rotated_polygon = rotate_polygon(polygon_points, best_angle)
print(polygon_points,rotated_polygon)
# Получаем полосы для покрытия многоугольника
stripes = get_stripes(rotated_polygon, stripe_width=stripe_width, offset=offset)

# Рисуем полосы
draw_stripes_2(rotated_polygon, stripes, stripe_width=stripe_width)

# Вычисляем суммарную площадь всех полос
total_area_2 = calculate_total_area(stripes, stripe_width=stripe_width) + perimeter_area
print(f"Суммарная площадь всех полос: {total_area_2}")
