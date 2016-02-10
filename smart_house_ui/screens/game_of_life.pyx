# -*- coding: utf-8 -*-

def compute_next_step(width, height, cells):
    to_update = {}

    for x in range(width):
        for y in range(height):
            x_l = x - 1 if x > 0 else width - 1
            x_g = x + 1 if x < width - 1 else 0
            y_l = y - 1 if y > 0 else height - 1
            y_g = y + 1 if y < height - 1 else 0

            neighbours_total_life = 0
            for xi in [x_l, x, x_g]:
                for yi in [y_l, y, y_g]:
                    if xi == x and yi == y:
                        continue

                    neighbours_total_life += cells[(xi, yi)].a

            if cells[(x, y)].a:
                if neighbours_total_life < 2 or neighbours_total_life > 3:
                    to_update[(x, y)] = 0
            else:
                if neighbours_total_life == 3:
                    to_update[(x, y)] = 1

    for key, value in to_update.iteritems():
        cells[key].a = value
