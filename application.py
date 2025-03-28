from flask import Flask, render_template
import os
import re

app = Flask(__name__)

def parse_image_name(filename):
    pattern = r"PA_Mouse(\d+)_(left|right)_lung_(pre|2hpi|4hpi|6hpi)_p_2_(\d+).*"
    match = re.match(pattern, filename)
    if match:
        return {
            'mn': match.group(1),
            'side': match.group(2),
            'time': match.group(3),
            'wavelength': match.group(4),
            'extension': os.path.splitext(filename)[1]
        }
    return None


def organize_images(images):
    organized = {}
    for img in images:
        info = parse_image_name(img)
        if info:
            mn = info['mn']
            if mn not in organized:
                organized[mn] = {
                    'left': {'pre': {}, '2hpi': {}, '4hpi': {}, '6hpi': {}},
                    'right': {'pre': {}, '2hpi': {}, '4hpi': {}, '6hpi': {}}
                }
            organized[mn][info['side']][info['time']][info['extension']] = img

    # Sort the organized dictionary by mouse number (mn)
    sorted_organized = dict(sorted(organized.items(), key=lambda x: int(x[0])))
    return sorted_organized

def get_wavelength_images(wavelength):
    image_dir = os.path.join(app.static_folder, 'imgs')
    images = [img for img in os.listdir(image_dir) if wavelength in img and (img.endswith('.gif') or img.endswith('.png'))]
    return organize_images(images)

@app.route('/')
@app.route('/750nm')
def nm750():
    organized_images = get_wavelength_images('750')
    return render_template('index.html', content='750nm Information', organized_images=organized_images)

@app.route('/806nm')
def nm806():
    organized_images = get_wavelength_images('806')
    return render_template('index.html', content='806nm Information', organized_images=organized_images)

@app.route('/850nm')
def nm850():
    organized_images = get_wavelength_images('850')
    return render_template('index.html', content='850nm Information', organized_images=organized_images)

if __name__ == '__main__':
    app.run(debug=True)