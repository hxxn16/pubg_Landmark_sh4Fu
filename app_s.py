from flask import Flask, render_template, request, redirect, url_for, send_file
import cv2
from datetime import datetime
from coordinates import coordinates
from teams_s import teams
from color import color_dict
import os
import zipfile

app = Flask(__name__)

image_paths = {
    'Erangel': './static/images/Erangel.JPG',
    'Miramar': './static/images/Miramar.JPG',
    'Sanhok': './static/images/Sanhok.JPG',
}

@app.route('/')
def index():
    leagues = list(teams.keys())
    return render_template('index.html', leagues=leagues)

@app.route('/select_teams', methods=['POST'])
def select_teams():
    selected_league = request.form.get('league')
    if selected_league not in teams:
        return redirect(url_for('index'))
    league_teams = teams[selected_league]
    return render_template('select_teams.html', league=selected_league, teams=league_teams)

@app.route('/generate', methods=['POST'])
def generate():
    selected_teams = request.form.getlist('teams')
    selected_league = request.form.get('league')
    if selected_league not in teams:
        return redirect(url_for('index'))

    radius = 40
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.0
    thickness = 2
    used_coords = {}
    offset = 40

    output_image_paths = []

    for map_name, image_path in image_paths.items():
        image = cv2.imread(image_path)

        for team_name in selected_teams:
            if team_name in teams[selected_league]:
                team_data = teams[selected_league][team_name]
                team_color = team_data['color']
                team_maps = team_data['maps']

                if map_name in team_maps:
                    location_names = team_maps[map_name]
                    for location_name in location_names:
                        if location_name and location_name in coordinates[map_name]:
                            coord = list(coordinates[map_name][location_name])
                            if tuple(coord) in used_coords:
                                shift_x, shift_y = used_coords[tuple(coord)]
                                coord[0] += shift_x * offset
                                coord[1] += shift_y * offset
                                used_coords[tuple(coordinates[map_name][location_name])][0] += 1
                            else:
                                used_coords[tuple(coord)] = [1, 0]

                            cv2.circle(image, tuple(coord), radius, color_dict[team_color], thickness=-1)
                            text = team_name
                            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
                            text_x = coord[0] - text_size[0] // 2
                            text_y = coord[1] + text_size[1] // 2

                            cv2.putText(image, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness + 2)
                            cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness)

        now = datetime.now()
        date_str = now.strftime("%Y%m%d_%H%M%S")
        output_image_path = f'./static/output_images/output_image_{map_name}_{date_str}.jpg'
        cv2.imwrite(output_image_path, image)
        output_image_paths.append(output_image_path)

    return render_template('result.html', image_paths=output_image_paths)

@app.route('/download_zip')
def download_zip():
    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    zip_filename = f'output_images_{date_str}.zip'

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in os.listdir('./static/output_images'):
            if file_path.endswith('.jpg'):
                zipf.write(os.path.join('./static/output_images', file_path), file_path)

    return send_file(zip_filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('./static/output_images'):
        os.makedirs('./static/output_images')
    app.run(debug=True, port=5004)