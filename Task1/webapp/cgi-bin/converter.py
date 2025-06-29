#!/usr/bin/env python3

import cgi
import os
from datetime import datetime
import subprocess

# Константы
HTML_DIR = "/var/www/webapp/html"
ORIGINAL_DIR = "/var/www/webapp/original"
CONVERTED_DIR = "/var/www/webapp/converted"
RESULT_PAGE = os.path.join(HTML_DIR, "result.html")
ERROR_PAGE = os.path.join(HTML_DIR, "error.html")

def save_upload(form):
    if 'image' not in form:
        return None, None, "No file uploaded"

    file_item = form['image']
    if not file_item.filename:
        return None, None, "No filename provided"

    content_type = file_item.type
    if content_type not in ['image/jpeg', 'image/png']:
        return None, None, "Invalid file type"

    # Формируем уникальное имя
    unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.getpid()}"
    ext = ".jpg" if content_type == 'image/jpeg' else ".png"
    unique_name += ext

    # Сохраняем оригинал
    original_path = os.path.join(ORIGINAL_DIR, unique_name)
    with open(original_path, 'wb') as f:
        f.write(file_item.file.read())

    return original_path, unique_name, None


def convert_image(input_path, output_path):
    try:
        subprocess.run(['convert', input_path, '-colorspace', 'Gray', output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"<!-- Conversion error: {e} -->")
        return False


def render_template(template_path, filename=None):
    with open(template_path, 'r') as f:
        content = f.read()
    if filename:
        content = content.replace("{{filename}}", filename)
    return content


def main():
    print("Content-Type: text/html\n")

    try:
        form = cgi.FieldStorage()
        original_path, unique_name, error = save_upload(form)

        if error:
            with open(ERROR_PAGE) as f:
                print(f.read())
            return

        converted_path = os.path.join(CONVERTED_DIR, unique_name)

        if not convert_image(original_path, converted_path):
            with open(ERROR_PAGE) as f:
                print(f.read())
            return

        result_html = render_template(RESULT_PAGE, unique_name)
        print(result_html)

    except Exception as e:
        # Любая неожиданная ошибка → показываем error.html
        print("Content-Type: text/html\n")
        try:
            with open(ERROR_PAGE) as f:
                print(f.read())
        except Exception:
            print("<h1>Internal Server Error</h1>")
            print("<p>Could not load error page.</p>")


if __name__ == '__main__':
    main()