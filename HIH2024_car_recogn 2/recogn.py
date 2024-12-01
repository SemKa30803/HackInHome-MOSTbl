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


# Функция рисования полос
def draw_stripes_no_shapely(polygon_points, stripe_width):
    # Определяем границы полигона
    x_min, x_max = min(p[0] for p in polygon_points), max(p[0] for p in polygon_points)
    y_min, y_max = min(p[1] for p in polygon_points), max(p[1] for p in polygon_points)

    # Создаем график
    fig, ax = plt.subplots()
    ax.plot(*zip(*polygon_points), color='black')  # Обводим границу многоугольника

    # Генерируем полосы
    y = y_min
    while y < y_max:
        segments = []
        x = x_min
        inside = False
        segment_start = None

        # Двигаемся вдоль горизонтальной полосы, проверяя точки внутри многоугольника
        while x < x_max:
            if is_inside_polygon((x, y), polygon_points):
                if not inside:
                    segment_start = x
                    inside = True
            else:
                if inside:
                    segments.append((segment_start, x))
                    inside = False
            x += 1  # Шаг проверки по x

        if inside:  # Если полоса закончилась внутри многоугольника
            segments.append((segment_start, x))

        # Рисуем найденные сегменты полосы
        for start, end in segments:
            ax.fill_betweenx([y, y + stripe_width], start, end, color='lightblue', edgecolor='blue', alpha=0.5)

        y += stripe_width

    # Настройка графика
    ax.set_xlim(x_min - 1, x_max + 1)
    ax.set_ylim(y_min - 1, y_max + 1)
    ax.set_aspect('equal', adjustable='datalim')
    plt.show()



def car_recogn ():
    # Вызов функции

    # Load a model
    model = YOLO("best.pt")  # pretrained YOLO11n model

    # Run batched inference on a list of images
    result = model('test.png')  # return a list of Results
    # Process results list
    door_area = 1
    front_left_door, front_right_door, front_bumper,door = 0,0,0,0
    #print(model.names)
    #print(result[0].boxes.cls[0].item()==7)
    result[0].save(filename="result.jpg")  # save to disk
    for i,mask in enumerate(result[0].masks):
        coords = np.vstack([mask.xy[0],mask.xy[0][0]])

        # Считаем площадь по формуле шнурка
        x, y = coords[:, 0], coords[:, 1]
        area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        if result[0].boxes.cls[i].item() == 8:
            front_left_door = area
        if result[0].boxes.cls[i].item() == 10:
            front_right_door = area
        if result[0].boxes.cls[i].item() == 6:
            front_bumper = area

    if front_left_door != 0 and front_right_door!=0:
        door = (front_left_door + front_right_door)/2
    elif front_left_door != 0:
        door = front_left_door
    elif front_right_door!=0:
        door = front_right_door
    #print(door,front_bumper)
    area = door_area/door*front_bumper


    coords = np.vstack([result[0].masks[1].xy[0],result[0].masks[1].xy[0][0]])
    #print(result[0].boxes.cls)
    draw_stripes_no_shapely(coords, stripe_width=50)
    return area
