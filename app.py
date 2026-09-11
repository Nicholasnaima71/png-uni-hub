from flask import Flask, request, jsonify, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.', static_url_path='')

# ============================================
# CONFIGURATION
# ============================================
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'webm', 'ogg', 'avi', 'mov', 'mkv'},
    'logo': {'png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'gallery': {'png', 'jpg', 'jpeg', 'webp', 'gif'}
}

# Ensure upload directories exist
for folder in ['videos', 'logos', 'audio', 'gallery']:
    os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)

def allowed_file(filename, file_type):
    """Check if file extension is allowed for a given file type"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

# ============================================
# SERVE STATIC FILES
# ============================================
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve files from the uploads folder"""
    return send_from_directory('uploads', filename)

# ============================================
# UPLOAD ROUTES
# ============================================
@app.route('/upload/<file_type>', methods=['POST'])
def upload_file(file_type):
    """Upload video, logo, or audio files"""
    if file_type not in ['video', 'logo', 'audio']:
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    uni_id = request.form.get('uni_id')
    
    if not uni_id:
        return jsonify({'success': False, 'message': 'University ID missing'}), 400
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename, file_type):
        return jsonify({'success': False, 'message': f'File type not allowed for {file_type}'}), 400
    
    # Determine folder and filename
    folder_map = {
        'video': 'videos',
        'logo': 'logos',
        'audio': 'audio'
    }
    
    # For audio, use a fixed name
    if file_type == 'audio':
        filename = 'background_music.mp3'
    else:
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'mp4'
        # For logo, use .png extension if it's an image
        if file_type == 'logo' and ext in ['jpg', 'jpeg', 'webp']:
            ext = 'png'  # Convert to PNG for consistency
        filename = f"{uni_id}.{ext}"
    
    folder = folder_map.get(file_type, file_type)
    save_path = os.path.join(UPLOAD_FOLDER, folder, filename)
    
    # Save the file
    file.save(save_path)
    
    return jsonify({
        'success': True, 
        'message': 'Upload successful', 
        'filename': filename,
        'filepath': f'uploads/{folder}/{filename}'
    })

@app.route('/upload/gallery', methods=['POST'])
def upload_gallery():
    """Upload multiple gallery images"""
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No files uploaded'}), 400
    
    uni_id = request.form.get('uni_id')
    if not uni_id:
        return jsonify({'success': False, 'message': 'University ID missing'}), 400
    
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'success': False, 'message': 'No files selected'}), 400
    
    gallery_folder = os.path.join(UPLOAD_FOLDER, 'gallery', uni_id)
    os.makedirs(gallery_folder, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        if allowed_file(file.filename, 'gallery'):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid duplicate filenames
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            import time
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.{ext}"
            save_path = os.path.join(gallery_folder, filename)
            file.save(save_path)
            saved_files.append(filename)
    
    if saved_files:
        return jsonify({
            'success': True, 
            'message': f'{len(saved_files)} images uploaded',
            'files': saved_files
        })
    else:
        return jsonify({'success': False, 'message': 'No valid images uploaded'}), 400

# ============================================
# DELETE ROUTES
# ============================================
@app.route('/delete/<uni_id>/<file_type>', methods=['DELETE'])
def delete_file(uni_id, file_type):
    """Delete video, logo, or audio files"""
    if file_type not in ['video', 'logo', 'audio']:
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    
    folder_map = {
        'video': 'videos',
        'logo': 'logos',
        'audio': 'audio'
    }
    
    folder = folder_map.get(file_type, file_type)
    
    if file_type == 'audio':
        filename = 'background_music.mp3'
    else:
        ext = 'mp4' if file_type == 'video' else 'png'
        filename = f"{uni_id}.{ext}"
    
    file_path = os.path.join(UPLOAD_FOLDER, folder, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True, 'message': 'File deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'File not found'}), 404

@app.route('/delete/gallery/<uni_id>/<filename>', methods=['DELETE'])
def delete_gallery_file(uni_id, filename):
    """Delete a specific gallery image"""
    file_path = os.path.join(UPLOAD_FOLDER, 'gallery', uni_id, secure_filename(filename))
    
    if os.path.exists(file_path):
        os.remove(file_path)
        # Check if folder is empty and remove it if it is
        folder_path = os.path.join(UPLOAD_FOLDER, 'gallery', uni_id)
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Image not found'}), 404

@app.route('/delete/gallery/<uni_id>', methods=['DELETE'])
def delete_all_gallery(uni_id):
    """Delete all gallery images for a university"""
    folder_path = os.path.join(UPLOAD_FOLDER, 'gallery', uni_id)
    if os.path.exists(folder_path):
        # Remove all files in the folder
        for filename in os.listdir(folder_path):
            os.remove(os.path.join(folder_path, filename))
        os.rmdir(folder_path)
        return jsonify({'success': True, 'message': 'All gallery images deleted'})
    else:
        return jsonify({'success': False, 'message': 'Gallery folder not found'}), 404

# ============================================
# HELPER ROUTES - LIST FILES
# ============================================
@app.route('/list/videos/<uni_id>')
def list_videos(uni_id):
    """List all videos for a university"""
    folder_path = os.path.join(UPLOAD_FOLDER, 'videos')
    if not os.path.exists(folder_path):
        return jsonify({'files': []})
    
    files = []
    for filename in os.listdir(folder_path):
        if filename.startswith(uni_id):
            files.append({
                'name': filename,
                'path': f'uploads/videos/{filename}'
            })
    return jsonify({'files': files})

@app.route('/list/logos/<uni_id>')
def list_logos(uni_id):
    """List all logos for a university"""
    folder_path = os.path.join(UPLOAD_FOLDER, 'logos')
    if not os.path.exists(folder_path):
        return jsonify({'files': []})
    
    files = []
    for filename in os.listdir(folder_path):
        if filename.startswith(uni_id):
            files.append({
                'name': filename,
                'path': f'uploads/logos/{filename}'
            })
    return jsonify({'files': files})

@app.route('/list/gallery/<uni_id>')
def list_gallery(uni_id):
    """List all gallery images for a university"""
    folder_path = os.path.join(UPLOAD_FOLDER, 'gallery', uni_id)
    if not os.path.exists(folder_path):
        return jsonify({'files': []})
    
    files = []
    for filename in os.listdir(folder_path):
        files.append({
            'name': filename,
            'path': f'uploads/gallery/{uni_id}/{filename}'
        })
    return jsonify({'files': files})

@app.route('/list/audio')
def list_audio():
    """List audio files"""
    folder_path = os.path.join(UPLOAD_FOLDER, 'audio')
    if not os.path.exists(folder_path):
        return jsonify({'files': []})
    
    files = []
    for filename in os.listdir(folder_path):
        files.append({
            'name': filename,
            'path': f'uploads/audio/{filename}'
        })
    return jsonify({'files': files})

# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')