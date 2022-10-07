from flask import Flask, render_template, request, redirect

from main import start_render_excel
import os

app = Flask(__name__)


def make_tree():
    path = os.getcwd()
    files_list = []
    for x in os.listdir():
        if x.endswith(".xlsx"):
            # Prints only text file present in My Folder
            files_list.append(x)
    print(files_list)
    return files_list


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city_name = request.form.get("city_name")
        start_render_excel(city_name)
        return redirect("downloads")
    return render_template('index.html')


@app.route('/downloads')
def list_downloads():
    dloads_dir = os.getcwd()
    files_list = []
    for x in os.listdir():
        if x.endswith(".xlsx"):
            files_list.append(x)
    dloads_src = ['/downloads/{}'.format(i) for i in files_list]
    return render_template('download.html', dloads=files_list, dloads_src=dloads_src)


if __name__ == '__main__':
    app.run("localhost",5001)
