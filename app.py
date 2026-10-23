from flask import Flask, render_template_string, request, jsonify
import pyotp
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2FA 动态验证码生成器</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #fff; width: 100%; max-width: 440px; padding: 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); text-align: center; }
        h2 { margin-bottom: 20px; color: #1a1a1a; font-size: 20px; }
        input[type="text"] { width: 100%; padding: 12px 15px; font-size: 16px; border: 2px solid #e1e8ed; border-radius: 8px; outline: none; text-align: center; letter-spacing: 1px; margin-bottom: 20px; }
        input[type="text"]:focus { border-color: #0066ff; }
        .code-box { background: #f0f4f8; border-radius: 8px; padding: 20px; cursor: pointer; }
        .code-display { font-size: 38px; font-weight: bold; font-family: monospace; letter-spacing: 6px; color: #0066ff; }
        .timer { font-size: 13px; color: #666; margin-top: 10px; }
        .copy-hint { font-size: 12px; color: #888; margin-top: 5px; }
        .toast { font-size: 14px; color: #4caf50; height: 20px; opacity: 0; transition: opacity 0.3s; margin-top: 10px; }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>

<div class="card">
    <h2>2FA 在线生成器</h2>
    <input type="text" id="secretInput" placeholder="请输入 2FA 密钥 (Secret Key)" autocomplete="off">

    <div class="code-box" onclick="copyCode()">
        <div class="code-display" id="codeDisplay">------</div>
        <div class="timer" id="timerDisplay">剩余时间: -- 秒</div>
        <div class="copy-hint">点击此处复制验证码</div>
    </div>
    <div class="toast" id="toast">已成功复制到剪贴板！</div>
</div>

<script>
    const secretInput = document.getElementById('secretInput');
    const codeDisplay = document.getElementById('codeDisplay');
    const timerDisplay = document.getElementById('timerDisplay');
    const toast = document.getElementById('toast');

    async function fetchCode() {
        const secret = secretInput.value.trim();
        if (!secret) {
            codeDisplay.innerText = "------";
            timerDisplay.innerText = "剩余时间: -- 秒";
            return;
        }

        try {
            const response = await fetch('/api/get-code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ secret: secret })
            });
            const data = await response.json();
            
            if (response.ok) {
                codeDisplay.innerText = data.code;
                timerDisplay.innerText = `剩余时间: ${data.remaining} 秒`;
            } else {
                codeDisplay.innerText = "密钥错误";
                timerDisplay.innerText = "请检查 Secret 是否正确";
            }
        } catch (e) {
            console.error(e);
        }
    }

    function copyCode() {
        const code = codeDisplay.innerText;
        if (code && code !== "------" && code !== "密钥错误") {
            navigator.clipboard.writeText(code).then(() => {
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
            });
        }
    }

    secretInput.addEventListener('input', fetchCode);
    setInterval(fetchCode, 1000);
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get-code', methods=['POST'])
def get_code():
    data = request.get_json()
    secret = data.get('secret', '').replace(" ", "")
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        remaining = 30 - (int(time.time()) % 30)
        return jsonify({'code': code, 'remaining': remaining})
    except Exception:
        return jsonify({'error': 'Invalid secret key'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)