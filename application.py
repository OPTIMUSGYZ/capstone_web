from flask import Flask, render_template
import os
import re

app = Flask(__name__)


def parse_fmode_image_name(filename):
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


def parse_dwt_image_name(filename):
    pattern = r"(US|PA)_Mouse(\d+)_(left|right)_lung_(pre|4hpi|6hpi)_p_2_wav806_haar_(AvgWavelet|AreaUnderCurve|AUC)\.png"
    match = re.match(pattern, filename)
    if match:
        return {
            'mode': match.group(1),
            'mn': match.group(2),
            'side': match.group(3),
            'time': match.group(4),
            'type': match.group(5)
        }
    return None


def organize_fmode_images(images):
    organized = {}
    for img in images:
        info = parse_fmode_image_name(img)
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


def organize_dwt_images(images):
    organized = {}
    for img in images:
        info = parse_dwt_image_name(img)
        if info:
            mn = info['mn']
            if mn not in organized:
                organized[mn] = {
                    'left': {'pre': {}, '4hpi': {}, '6hpi': {}},
                    'right': {'pre': {}, '4hpi': {}, '6hpi': {}}
                }
            organized[mn][info['side']][info['time']][info['type']] = img

    # Sort the organized dictionary by mouse number (mn)
    sorted_organized = dict(sorted(organized.items(), key=lambda x: int(x[0])))
    return sorted_organized


def get_wavelength_images(wavelength):
    image_dir = os.path.join(app.static_folder, 'imgs')
    images = [img for img in os.listdir(image_dir) if wavelength in img and (img.endswith('.gif') or img.endswith('.png'))]
    return organize_fmode_images(images)


def get_dwt_images(mode):
    image_dir = os.path.join(app.static_folder, 'imgs')
    images = [img for img in os.listdir(image_dir) if img.startswith(f'{mode}_Mouse') and img.endswith('.png')]
    return organize_dwt_images(images)


def get_average_plot_images():
    image_dir = os.path.join(app.static_folder, 'imgs')
    pattern = r"PA_Average_ROI_mean_(left|right)_lung_mice_[\d+_]+_(\d+)nm\.png"
    avg_plots = {}

    for img in os.listdir(image_dir):
        match = re.match(pattern, img)
        if match:
            side, wavelength = match.groups()
            if wavelength not in avg_plots:
                avg_plots[wavelength] = {'left': None, 'right': None}
            avg_plots[wavelength][side] = img
    return avg_plots


@app.route('/')
def index():
    return render_template('index.html', content='Welcome')


@app.route('/f-mode/<wavelength>')
def f_mode(wavelength):
    if wavelength in ['750', '806', '850']:
        organized_images = get_wavelength_images(wavelength)
        return render_template('index.html', content=f'{wavelength}nm Information', organized_images=organized_images)
    elif wavelength == 'avg_plots':
        avg_plots = get_average_plot_images()
        return render_template('index.html', content='Average Plots', avg_plots=avg_plots)
    else:
        return "Invalid wavelength", 400


@app.route('/dwt/<mode>')
def dwt(mode):
    if mode in ['US', 'PA']:
        organized_images = get_dwt_images(mode)
        return render_template('index.html', content=f'DWT {mode}', organized_images=organized_images)
    else:
        return "Invalid DWT mode", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3180, debug=False)
