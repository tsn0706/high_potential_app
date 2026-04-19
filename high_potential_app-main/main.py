from flask import Flask, render_template, request
from utils.parser import parse_uploaded_file
from utils.candidate_profile import create_candidate_profile
from utils.talent_vector import generate_talent_vector

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            if file.filename == '':
                continue
            try:
                records = parse_uploaded_file(file)
                for row in records:
                    profile = create_candidate_profile(row)
                    vector = generate_talent_vector(profile)
                    results.append(vector)
            except Exception as e:
                print(f"處理檔案 {file.filename} 時出錯: {e}")

    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run(debug=True, port=5000)