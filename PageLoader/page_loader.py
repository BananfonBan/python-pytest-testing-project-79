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


def parse_content_link(path_to_html_file, url, tags: list, only_local_content=True):
    with open(path_to_html_file, "r", encoding="utf-8") as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    attrs_tag = {"img": "src", "link": "href", "script": "src"}
    # Создает список со всеми ссылками на изображения
    # И изменяет ссылки в html файлы на локальные пути до изображений
    dir_name = f"{url_to_name(url)}_files"
    url_hostname = Url(url).get_hostname()
    content_link_list = []

    for tag in soup(tags):
        # Определяем из какого атрибута брать ссылку
        tag_attr = attrs_tag[f"{tag.name}"]
        if not tag.has_attr(tag_attr):
            continue
        content_link = url_normalize(tag[tag_attr])
        local_link = content_link[0] == "/" and content_link[:2] != "//"
        identical_hostname = Url(content_link).get_hostname() == url_hostname
        # Формирование и изменение на локальную ссылку
        if local_link or identical_hostname:
            content_link = urljoin(f"https://{url_hostname}", content_link)
            tag[tag_attr] = f"{dir_name}/{url_to_name(content_link)}"
            content_link_list.append(content_link)
        elif (not only_local_content) and content_link[:4] == "http":
            img_name = url_to_name(content_link)
            tag[tag_attr] = f"{dir_name}/{img_name}"
            content_link_list.append(content_link)

    with open(path_to_html_file, "w", encoding="utf-8") as file:
        file.write(str(soup))
    return content_link_list


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
    try:
        req = client.get(url=url, headers=headers)
    except requests.exceptions.ConnectionError as e:
        print(e, "Connection fail")
        return None
    if req.ok:
        # Считываем текст HTML-документа
        src = req.text
        name_file = url_to_name(url)
        file_path = os.path.normpath(os.path.join(path_to_file, f"{name_file}.html"))
        # Записываем в файл в указанной директории
        try:
            with open(file_path, "w", encoding="utf-8") as myfile:
                myfile.write(src)
        except FileNotFoundError:
            return None
        return file_path
    else:
        return None


def download_content(path_to_dir, url, client=requests):
    content_name = url_to_name(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    # Определение расширение файла
    content_path = Url(url).get_path()
    content_extension = os.path.splitext(content_path)[1]
    correct_extensions = [".png", ".jpg", ".JPG", ".gif",
                          ".js", ".css", ".json", ".svg", ".ico"]
    if content_extension not in correct_extensions:
        return download(path_to_file=path_to_dir, url=url)
    try:
        request = client.get(url, headers=headers)
        if request.ok:
            path_img = f"{path_to_dir}/{content_name}"
            with open(path_img, "wb") as file:
                file.write(request.content)
            return path_img
    except requests.RequestException:
        pass


def make_dir_with_files(path_to_dir, url, only_local_content=True):
    name_dir = url_to_name(url) + "_files"
    dir_path = f"{path_to_dir}/{name_dir}"
    os.mkdir(dir_path)

    html_file_path = f"{path_to_dir}/{url_to_name(url)}.html"
    tags = ["img", "link", "script"]

    content_links = parse_content_link(html_file_path, url, tags=tags,
                                       only_local_content=only_local_content)

    for img_link in content_links:
        download_content(dir_path, img_link)


# if __name__ == "__main__":
    # path = r"C:\Users\Admin\Desktop"
    # url = ""
    # tags = ["img", "link", "script"]
    # download_content(path_to_dir=path, url=url)
    # download(path_to_file=path, url=url)
    # make_dir_with_files(path_to_dir=path, url=url, only_local_content=False)
