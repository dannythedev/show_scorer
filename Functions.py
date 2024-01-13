import json
import os
import re

EXPORT_FILE = 'data.json'


def wrap_text(text, limit):
    words = text.split()
    if not words:
        return ""

    wrapped_text = words[0]
    current_length = len(words[0])

    for word in words[1:]:
        if current_length + len(word) + 1 <= limit:
            wrapped_text += ' ' + word
            current_length += len(word) + 1
        else:
            wrapped_text += '\n' + word
            current_length = len(word)

    return wrapped_text

def regexify(regex, data):
    """Extracts regex string from data string."""
    try:
        return re.findall(regex, str(data))[0]
    except:
        return

def truncate_string(s):
    lim = 34
    return s if len(s.split('\n')[1]) <= lim else next((s[:lim+i] + "..." for i, c in enumerate(s) if not c.isalnum() and not c.isspace()), s)

def read_json():
    if not os.path.exists(EXPORT_FILE):
        with open(EXPORT_FILE, 'w') as f:
            f.write('[]')
    f = open(EXPORT_FILE, 'r')
    try:
        json_data = json.loads(f.read())
        if not json_data:
            return {}
    except:
        json_data = {}

    f.close()
    return json_data


def write_json(dumps):
    f = open(EXPORT_FILE, 'w')
    f.write(json.dumps(dumps))
    f.close()

def scale_image_url(original_url, scale):
    # Regex to find the relevant part of the URL
    pattern = r'(UY\d+)_CR(\d+),(\d+),(\d+),(\d+)'
    match = re.search(pattern, original_url)
    if not match:
        return "Invalid URL format"

    # Extracting the current dimensions
    uy, cr1, current_width, cr3, current_height = match.groups()

    # Calculating new dimensions
    new_height = int(current_height) * scale
    new_width = int(current_width) * scale

    # Replacing with new dimensions
    new_url = re.sub(pattern, f'UY{new_height}_CR{cr1},{cr3},{new_width},{new_height}', original_url)
    return new_url