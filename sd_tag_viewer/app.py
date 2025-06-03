from flask import Flask, render_template_string, send_from_directory
import os
import urllib.parse

app = Flask(__name__)
IMAGE_ROOT = "./images"
MAX_THUMBNAILS = 3

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Noobai Viewer</title>
  <style>
    body { font-family: sans-serif; }
    .block { margin-bottom: 30px; }
    .title { font-size: 1.5em; margin: 10px 0; cursor: pointer; }
    .gallery { display: flex; flex-wrap: wrap; gap: 10px; }
    .item { width: 200px; cursor: pointer; }
    img { width: 100%; border-radius: 12px; }
    .hidden { display: none; }
  </style>
</head>
<body>
<h1>Noobai タグ別ビューア</h1>
{% for folder, images in folders.items() %}
  <div class="block">
    <div class="title" onclick="toggleGallery('{{ folder }}')">📁 {{ folder }}（クリックで展開）</div>
    <div class="gallery" id="thumb-{{ folder }}">
      {% for img in images[:3] %}
        <div class="item" onclick="copyPrompt(`{{ img.prompt }}`)">
          <img src="/images/{{ folder }}/{{ img.filename }}" alt="">
          <p>{{ img.name }}</p>
        </div>
      {% endfor %}
    </div>
    <div class="gallery hidden" id="full-{{ folder }}">
      {% for img in images[3:] %}
        <div class="item" onclick="copyPrompt(`{{ img.prompt }}`)">
          <img src="/images/{{ folder }}/{{ img.filename }}" alt="">
          <p>{{ img.name }}</p>
        </div>
      {% endfor %}
    </div>
  </div>
{% endfor %}
<script>
function copyPrompt(prompt) {
  navigator.clipboard.writeText(prompt).then(() => alert("コピー完了: " + prompt));
}
function toggleGallery(folder) {
  const thumb = document.getElementById("thumb-" + folder);
  const full = document.getElementById("full-" + folder);
  if (full.classList.contains("hidden")) {
    full.classList.remove("hidden");
    thumb.style.display = "none";
  } else {
    full.classList.add("hidden");
    thumb.style.display = "flex";
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    folders = {}
    for subfolder in sorted(os.listdir(IMAGE_ROOT)):
        folder_path = os.path.join(IMAGE_ROOT, subfolder)
        if not os.path.isdir(folder_path):
            continue

        # テンプレート読み込み or 自動作成
        tag_file_path = os.path.join(folder_path, "_tag.txt")
        template_str = None
        if os.path.exists(tag_file_path):
            with open(tag_file_path, encoding="utf-8") as f:
                template_str = f.read().strip()

        images = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                name = os.path.splitext(filename)[0]
                safe_name = urllib.parse.unquote(name)
                if template_str and "????" in template_str:
                    prompt = template_str.replace("????", safe_name)
                else:
                    prompt = safe_name  # fallback
                images.append({
                    "filename": filename,
                    "name": safe_name,
                    "prompt": prompt
                })

        if images:
            folders[subfolder] = images
    return render_template_string(TEMPLATE, folders=folders)

@app.route("/images/<path:filename>")
def image(filename):
    return send_from_directory(IMAGE_ROOT, filename)

if __name__ == "__main__":
    app.run(port=5001)
