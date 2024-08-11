import os
from pathlib import Path
import re
from urllib.parse import urljoin
import requests
if __name__ == "__main__":
    from UrlClass import Url
else:
    from PageLoader.UrlClass import Url
from bs4 import BeautifulSoup
from url_normalize import url_normalize


def url_to_name(url):
    parse_url = Url(url)
    parse_hostname = "-".join(parse_url.get_hostname().split("."))
    parse_path = "-".join(re.split("/|_", parse_url.get_path()))

    return f"{parse_hostname}{parse_path}"


def parse_img_link(path_to_html_file, url, only_local_img=True):
    with open(path_to_html_file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    # Создает список со всеми ссылками на изображения
    # И изменяет ссылки в html файлы на локальные пути до изображений
    dir_name = f"{url_to_name(url)}_files"
    url_hostname = Url(url).get_hostname()
    img_list = []
    for img in soup("img"):
        img_link = url_normalize(img["src"])
        local_link = img_link[0] == "/" and img_link[:2] != "//"
        identical_hostname = Url(img_link).get_hostname() == url_hostname
        # Формирование и изменение на локальную ссылку
        if local_link or identical_hostname:
            img_link = urljoin(f"https://{url_hostname}", img_link)
            img["src"] = f"{dir_name}/{url_to_name(img_link)}"
            img_list.append(img_link)
        elif (not only_local_img) and img_link[:4] == "http":
            img_name = url_to_name(img_link)
            img["src"] = f"{dir_name}/{img_name}"
            img_list.append(img_link)

    with open(path_to_html_file, "w", encoding="utf-8") as file:
        file.write(str(soup))
    return img_list


def download(url, path_to_file=Path.cwd(), client=requests):
    """Creates a file with the html code of the specified url
    in the specified directory
    """
    # Если директории не существует, вызывается ошибка
    if not Path(path_to_file).exists():
        raise FileNotFoundError("The directory does not exist")

    # Говорим веб-серверу, что хотим получить html
    st_accept = "text/html"

    # Формируем хеш заголовков
    headers = {"Accept": st_accept,
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

    # Отправляем запрос с заголовками по нужному адресу
    req = client.get(url=url, headers=headers)

    # Считываем текст HTML-документа
    src = req.text

    name_file = url_to_name(url)
    file_path = os.path.normpath(os.path.join(path_to_file, f"{name_file}.html"))
    # Записываем в файл в указанной директории
    with open(file_path, "w", encoding="utf-8") as myfile:
        myfile.write(src)

    return file_path


def download_img(path_to_dir, url, client=requests):
    img_name = url_to_name(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    try:
        request = client.get(url, headers=headers)
        correct_extension = ["png", "jpg", "gif", "JPG",]
        if request.ok:
            if img_name[-3:] in correct_extension:
                path_img = f"{path_to_dir}/{img_name}"
            else:
                path_img = f"{path_to_dir}/{img_name}.jpg"
            with open(path_img, "wb") as file:
                file.write(request.content)
            return path_img
    except requests.RequestException:
        pass


def make_dir_with_files(path_to_dir, url):
    name_dir = url_to_name(url) + "_files"
    dir_path = f"{path_to_dir}/{name_dir}"
    os.mkdir(dir_path)

    html_file_path = f"{path_to_dir}/{url_to_name(url)}.html"
    img_link_list = parse_img_link(html_file_path, url)

    for img_link in img_link_list:
        download_img(dir_path, img_link)
