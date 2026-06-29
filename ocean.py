# adapted from the-sea.js by plaao (me)

# The ocean is stored as a list of strings which is combined into one string when rendered.
# It is rendered internally in 40x8 resolution.
import math
import random

ocean_time = random.randrange(2000)
alphabet = "abcdefghijklmnopqrstuvwxyz"
OCEAN_SPACE = "\u00a0"

def get_wave_y(xr):
    x = xr / 5
    c = math.cos(0.2 * x) + math.sin(0.3 * x) * math.sin(0.23 * x)
    return -math.floor(2 * c * math.sin(x)) + 3


def get_random_letter():
    return random.choice(alphabet)


def init_populate_ocean():
    global ocean_time

    # Create 12 lists of 80 chars each and get an ocean slice for every ocean time value needed.
    ocean_base = get_ocean_slices(ocean_time, ocean_time + 80)

    ocean_time += 80
    return ocean_base


def get_ocean_slice(xr, glitch):
    y = get_wave_y(xr)
    cont_list = []

    for i in range(10):
        if random.random() <= 0.002 * glitch:
            cont_list.append(get_random_letter())
        elif i == y:
            cont_list.append("#")
        elif i > y:
            cont_list.append(".")
        else:
            cont_list.append(OCEAN_SPACE)

    return cont_list


def mutate_text(txt, glitch):
    chars = list(txt)

    mutation_chance = (
        0.0002 + (ocean_time % 1200) / 1_200_000
    ) * glitch

    for i, ch in enumerate(chars):
        if ch in "#." + OCEAN_SPACE and random.random() <= mutation_chance:
            chars[i] = get_random_letter()

    return "".join(chars)


def get_ocean_slices(x1, x2):
    cont_list = ["" for _ in range(10)]

    for xr in range(x1, x2):
        ocean_slice = get_ocean_slice(xr, 1)

        for i, char in enumerate(ocean_slice):
            cont_list[i] += char

    return cont_list


def update_ocean_slices(ocean_content, ocean_glitch):
    global ocean_time
    
    # edits in place
    # get the new slice
    ocean_slice = get_ocean_slice(ocean_time, ocean_glitch)
    ocean_time += 1
    
    # for every line in content, remove the first char and add the slice char
    for i in range(10):
        ocean_content[i] = ocean_content[i][1:] + ocean_slice[i]

    raw_txt = unpack_content_to_text(ocean_content)
    
    return mutate_text(raw_txt, ocean_glitch)


def unpack_content_to_text(content):
    # Join every line with \n
    return "".join(line for line in content)


def begin_ocean():
    return init_populate_ocean()
