# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import zipfile
from datetime import datetime
import cv2  # Assuming OpenCV is used
from coordinates import coordinates
from teams import teams
from color import color_dict

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Define image paths
image_paths = {
    'Erangel': './static/images/Erangel.JPG',
    'Miramar': './static/images/Miramar.JPG',
    'Sanhok': './static/images/Sanhok.JPG',
}

# Route for the home page
@app.route('/')
def index():
    leagues = list(teams.keys())  # Get list of leagues
    return render_template('index.html', leagues=leagues)

# Route for selecting teams from a league
@app.route('/select_teams', methods=['POST'])
def select_teams():
    selected_league = request.form.get('league')  # Get selected league from form
    if selected_league not in teams:
        return redirect(url_for('index'))  # Redirect to home page if league not found

    league_teams = teams[selected_league]  # Get teams for the selected league
    return render_template('select_teams.html', league=selected_league, teams=league_teams)

# Route for generating images based on selected teams and maps
@app.route('/generate', methods=['POST'])
def generate():
    selected_teams = request.form.getlist('teams')  # Get selected teams from form
    selected_league = request.form.get('league')  # Get selected league from form
    if selected_league not in teams:
        return redirect(url_for('index'))  # Redirect to home page if league not found

    radius = 40
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.0
    thickness = 2
    used_coords = {}
    offset = 40

    output_image_paths = []

    # Loop through each map and generate images
    for map_name, image_path in image_paths.items():
        image = cv2.imread(image_path)

        for team_name in selected_teams:
            if team_name in teams[selected_league]:
                team_data = teams[selected_league][team_name]
                team_color = team_data['color']
                team_maps = team_data['maps']

                if map_name in team_maps:
                    location_name = team_maps[map_name]
                    if location_name in coordinates[map_name]:
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
        cv2.imwrite(output_image_path, image)
        output_image_paths.append(output_image_path)

    session['output_image_paths'] = output_image_paths  # Store output image paths in session
    return render_template('result.html', image_paths=output_image_paths)

# Route for downloading generated images as a ZIP file
@app.route('/download_zip')
def download_zip():
    output_image_paths = session.get('output_image_paths', [])
    if not output_image_paths:
        return redirect(url_for('index'))  # Redirect to home if no images found in session

    now = datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    zip_filename = f'output_images_{date_str}.zip'

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file_path in output_image_paths:
            zipf.write(file_path, os.path.basename(file_path))

    return send_file(zip_filename, as_attachment=True)

# Route for listing teams and their maps
@app.route('/list_teams')
def list_teams():
    leagues = teams  # Get all leagues and teams
    return render_template('list_teams.html', teams=leagues)

if __name__ == '__main__':
    if not os.path.exists('./static/output_images'):
        os.makedirs('./static/output_images')  # Create directory for output images if it doesn't exist
    app.run(debug=True, port=5005)  # Run the Flask application