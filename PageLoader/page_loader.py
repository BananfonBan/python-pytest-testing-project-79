import os
from pathlib import Path
import requests
from PageLoader.UrlClass import Url
from bs4 import BeautifulSoup


def parsing_url_to_name(url):
    parse_url = Url(url)
    parse_hostname = "-".join(parse_url.get_hostname().split("."))
    parse_path = "-".join(parse_url.get_path().split("/"))

    return f"{parse_hostname}{parse_path}"


def parse_img_link(path_to_html_file, url_hostname):
    with open(path_to_html_file,) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    # Создает список со всеми ссылками на изображения
    # И изменяет ссылки в html файлы на локальные пути до изображений
    img_list = []
    for img in soup.find_all("img"):
        img_list.append(img["src"])
        if img["src"][0] == "/":
            img["src"] = parsing_url_to_name(f"{url_hostname}{img['src']}")
        else:
            img["src"] = parsing_url_to_name(img['src'])

    return img_list


def download(url, path_to_file=Path.cwd(), client=requests):
    """Creates a file with the html code of the specified url
    in the specified directory
    """
    # Если директории не существует, вызывается ошибка
    if not Path(path_to_file).exists():
        raise FileNotFoundError("The directory does not exist")

    name_file = parsing_url_to_name(url)
    # Говорим веб-серверу, что хотим получить html
    st_accept = "text/html"

    # Формируем хеш заголовков
    headers = {"Accept": st_accept}

    # Отправляем запрос с заголовками по нужному адресу
    req = client.get(url=url, headers=headers)

    # Считываем текст HTML-документа
    src = req.text

    # Записываем в файл в указанной директории
    with open(f"{path_to_file}/{name_file}.html", "w", encoding="utf-8") as myfile:
        myfile.write(src)

    return os.path.normpath(os.path.join(path_to_file, f"{name_file}.html",))


def download_img(path_to_dir, url, client=requests):
    img_name = parsing_url_to_name(url)
    request = client.get(url)
    correct_extension = ["png", "jpg", "gif"]
    if request.ok:
        if img_name[-3:] in correct_extension:
            path_img = f"{path_to_dir}/{img_name}"
        else:
            path_img = f"{path_to_dir}/{img_name}.jpg"
        with open(path_img, "wb") as file:
            file.write(request.content)
        return path_img
    else:
        return None


def make_dir_with_files(path_to_dir, url):
    name_dir = parsing_url_to_name(url) + "_files"
    dir_path = f"{path_to_dir}/{name_dir}"
    os.mkdir(dir_path)

    url_netlock = Url(url).get_hostname()
    html_file_path = f"{path_to_dir}/{parsing_url_to_name(url)}.html"
    img_link_list = parse_img_link(html_file_path, url)

    for img_link in img_link_list:
        # Если файл находиться по тому же адресу, что и страница
        if img_link[0] == "/":
            download_img(dir_path, f"{url_netlock}{img_link}")
        else:
            download_img(dir_path, url=img_link)
