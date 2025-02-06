import pyperclip
from PIL import ImageGrab, ImageChops
import pytesseract
from PIL.Image import Resampling
from thefuzz import fuzz

from dotenv import load_dotenv
import os
import re
import keyboard

from arrow_detector import convert_pil_to_ocv, get_arrow_direction
from hints import DofusDB
from rows_detector import get_rows

load_dotenv()
TOKEN = os.getenv("RCAPTCHA")
dofus_db = DofusDB(TOKEN)

start_pos_crop_rect = (82, 377, 250, 400)
current_pos_crop_rect = (0, 62, 70, 82)
step_crop_rect = (68, 350, 90, 365)
hint_start_crop_rect = (0, 422,1, 600)

def get_start_pos():
    start_pos_image = ImageChops.invert(ImageGrab.grab(start_pos_crop_rect))
    start_values = pytesseract.image_to_string(start_pos_image, lang='fra', config='--psm 7')

    values = re.findall('-?\d+', start_values)

    if len(values) != 2:
        print("ERROR: Fenêtre de chasse au trésor mal positionnée")
        print("       " + start_values + " trouvées")
        print("       Les valeurs de position devrait être affichées")
        start_pos_image.show()
        exit(1)

    return values

def get_current_pos():
    current_pos_image = ImageChops.invert(ImageGrab.grab(current_pos_crop_rect))
    current_values = pytesseract.image_to_string(current_pos_image, lang='fra', config='--psm 7')

    values = re.findall('-?\d+', current_values)

    return values

def get_step():
    step_image = ImageChops.invert(ImageGrab.grab(step_crop_rect))
    step_values = pytesseract.image_to_string(step_image, lang='fra', config='--psm 7').replace('\n', '')
    return step_values.split('/')

def double_image_size(image):
    return image.resize((image.width * 2, image.height * 2), Resampling.BICUBIC)

def find_poi(hint_list, search):
    if fuzz.ratio(search, 'Phorreur') > 50:
        return {'x': 0, 'y': 0}, 'Phorreur'

    for hint_elt in reversed(hint_list):
        for poi_elt in hint_elt['pois']:
            if fuzz.ratio(poi_elt, search) > 80:
                return hint_elt, poi_elt

    return {'x': 0, 'y': 0}, 'Inconnu'

while True:
    steps = get_step()
    current_step = steps[0]
    max_step = steps[1]

    start_pos = get_start_pos()
    pos_values = start_pos
    for i in range(int(current_step), int(max_step)):
        rows = get_rows(hint_start_crop_rect)
        counter = 0
        phorreur = False
        while counter < len(rows):
            row = rows[counter]

            hints_crop_rect = (30, row['start_y'], 170, row['end_y'])
            hints_image = ImageChops.invert(ImageGrab.grab(hints_crop_rect))
            hints_value = pytesseract.image_to_string(hints_image, lang='fra', config='--psm 6')

            arrows_crop_rect = (10,row['start_y'],30,row['end_y'])
            arrows_pos_image = double_image_size(ImageChops.invert(ImageGrab.grab(arrows_crop_rect)))
            ocv_arrows = convert_pil_to_ocv(arrows_pos_image)
            arrow = get_arrow_direction(ocv_arrows)

            hints = dofus_db.get_hints(pos_values[0], pos_values[1], arrow)

            hints_value = hints_value.replace('\n', ' ')
            hint, poi = find_poi(hints, hints_value)

            if poi == 'Phorreur':
                print('Indice: Phorreur, chercher le et appuyer sur la touche "<"')
                phorreur = True
            elif poi == 'Inconnu':
                print('Erreur lors de la reconnaissance de l\'indice, chasse potentiellement mauvaise')
                print('Réinitialisation de la chasse au trésor')
                counter = 0
                break
            else:
                pyperclip.copy('/travel ' + str(hint['x']) + ',' + str(hint['y']))
                print('Indice: ' + poi + ' à la position x=' + str(hint['x']) + ', y=' + str(hint['y']))

            done = False
            while not done:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == '²':
                        done = True
                    elif event.name == '<':
                        if phorreur:
                            pos_values = get_current_pos()
                            phorreur = False
                        else:
                            pos_values = [hint['x'], hint['y']]

                        counter += 1
                        done = True
                    elif event.name == '>':
                        if counter > 0:
                            counter -= 1
                            temp_row = rows[counter - 1]
                            pos_values = [temp_row['x'], temp_row['y']]
                        else :
                            pos_values = start_pos

                        done = True

    print('Chasse au trésor terminée')
    print('Appuyez sur la touche "!" pour recommencer une chasse au trésor')
    event = keyboard.read_event()
    if event.event_type == keyboard.KEY_DOWN:
        if event.name != '!':
            break