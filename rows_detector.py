from PIL import ImageGrab

def __is_row_separator(rgb):
    return 80 < rgb[0] < 90 and 80 < rgb[1] < 90 and 80 < rgb[2] < 90

def __is_end_of_rows(rgb):
    return 40 <= rgb[0] < 44 and 40 <= rgb[1] < 44 and 40 <= rgb[2] < 44

def get_rows(crop_rect):
    return __translate_rows_to_crop_rect(__get_rows(crop_rect), crop_rect)

def __get_rows(crop_rect):
    image = ImageGrab.grab(crop_rect)
    rgb_image = image.convert('RGB')

    rows = []
    previous = None
    for i in range(1, crop_rect[3] - crop_rect[1], 1):
        rgb_i = rgb_image.getpixel((0, i))

        if __is_end_of_rows(rgb_i):
            rows.append({'start_y': previous + 1, 'end_y': i})
            break
        elif (not __is_row_separator(rgb_i)
              or not __is_row_separator(rgb_image.getpixel((0, i - 1)))):
            continue


        if not previous is None:
            rows.append({'start_y': previous + 1, 'end_y': i - 1})

        previous = i

    return rows

def __translate_rows_to_crop_rect(rows, crop_rect):
    return [{'start_y': crop_rect[1] + row['start_y'], 'end_y': crop_rect[1] + row['end_y']} for row in rows]