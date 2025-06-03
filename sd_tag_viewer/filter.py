from flask import Flask, render_template_string, send_from_directory, request, jsonify
import os
import urllib.parse

app = Flask(__name__)
IMAGE_ROOT = "./images"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"UTF-8\">
  <title>Noobai タグフィルタ</title>
  <style>
    body { font-family: sans-serif; }
    input { margin: 20px; padding: 8px; width: 300px; font-size: 1em; }
    .gallery { display: flex; flex-wrap: wrap; gap: 10px; }
    .item { width: 200px; cursor: pointer; }
    img { width: 100%; border-radius: 12px; }
    p { font-size: 0.9em; word-break: break-all; }
  </style>
</head>
<body>
<h1>Noobai タグ比較ビューア</h1>
<input type=\"text\" id=\"filterInput\" placeholder=\"タグ検索（スペース区切り, 2文字以上）\">
<div class=\"gallery\" id=\"gallery\"></div>

<script>
function copyPrompt(prompt) {
  navigator.clipboard.writeText(prompt).then(() => alert("コピー完了: " + prompt));
}

document.getElementById("filterInput").addEventListener("input", function () {
  const query = this.value.trim();
  if (query.length < 2) {
    document.getElementById("gallery").innerHTML = "";
    return;
  }

  fetch(`/search?query=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      const gallery = document.getElementById("gallery");
      gallery.innerHTML = "";
      data.forEach(img => {
        const div = document.createElement("div");
        div.className = "item";
        div.onclick = () => copyPrompt(img.prompt);
        div.innerHTML = `
          <img src="/images/${img.folder}/${img.filename}" alt="">
          <p class="prompt-text">${img.prompt}</p>
        `;
        gallery.appendChild(div);
      });
    });
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE)

@app.route("/search")
def search():
    query = request.args.get("query", "").lower().split()
    results = []

    for folder in sorted(os.listdir(IMAGE_ROOT)):
        folder_path = os.path.join(IMAGE_ROOT, folder)
        if not os.path.isdir(folder_path):
            continue

        tag_file_path = os.path.join(folder_path, "_tag.txt")
        template_str = None
        if os.path.exists(tag_file_path):
            with open(tag_file_path, encoding="utf-8") as f:
                template_str = f.read().strip()

        for filename in sorted(os.listdir(folder_path)):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                name = os.path.splitext(filename)[0]
                safe_name = urllib.parse.unquote(name)
                if template_str and "????" in template_str:
                    prompt = template_str.replace("????", safe_name)
                else:
                    prompt = safe_name

                prompt_lc = prompt.lower()
                if all(q in prompt_lc for q in query):
                    results.append({
                        "folder": folder,
                        "filename": filename,
                        "prompt": prompt
                    })

    return jsonify(results)

@app.route("/images/<path:filename>")
def image(filename):
    return send_from_directory(IMAGE_ROOT, filename)

if __name__ == "__main__":
    app.run(port=5002)
