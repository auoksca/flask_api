import os
import extract_msg
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'flask_app', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/extract-msg', methods=['POST'])
def extract_msg_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(temp_path)

    try:
        # ✅ Use extract_msg correctly (releases file after use)
        msg = extract_msg.Message(temp_path)
        msg_subject = msg.subject or ''
        msg_sender = msg.sender or ''
        msg_to = msg.to or ''
        msg_cc = msg.cc or ''
        msg_date = msg.date or ''
        msg_body = msg.body or ''
        msg.close()  # 🔐 Important: releases file lock

        # Optional: write to a text file (for PHP)
        output_path = os.path.join(os.getcwd(), 'message.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {msg_subject}\n")
            f.write(f"From: {msg_sender}\n")
            f.write(f"To: {msg_to}\n")
            f.write(f"Cc: {msg_cc}\n")
            f.write(f"Bcc: (none)\n")  # extract_msg doesn’t provide Bcc
            f.write(f"Date: {msg_date}\n")
            f.write("Body\n")
            f.write(msg_body)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # ✅ Try removing the file after ensuring it's not locked
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ Could not delete file: {e}")

    return jsonify({
        'subject': msg_subject,
        'from': msg_sender,
        'to': msg_to,
        'cc': msg_cc,
        'date': msg_date,
        'body': msg_body
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
