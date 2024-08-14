import os
from pathlib import Path
import re
import logging
from urllib.parse import urljoin
import requests
if __name__ == "__main__":
    from UrlClass import Url
else:
    from PageLoader.UrlClass import Url
from bs4 import BeautifulSoup
from url_normalize import url_normalize

logger = logging.getLogger(__name__)


def url_to_name(url):
    parse_url = Url(url)
    parse_hostname = "-".join(parse_url.get_hostname().split("."))
    parse_path = "-".join(re.split("/|_", parse_url.get_path()))
    result = f"{parse_hostname}{parse_path}"
    logger.debug(f"\nurl={url}\nurl_to_name={result}")

    return result


def parse_content_link(path_to_html_file, url, tags: list, only_local_content=True):
    if Path(path_to_html_file).exists():
        with open(path_to_html_file, "r", encoding="utf-8") as html_file:
            soup = BeautifulSoup(html_file, "html.parser")
    else:
        logger.warning(f"File {path_to_html_file} does not exists")
        raise FileNotFoundError("File does not exists")
    attrs_tag = {"img": "src", "link": "href", "script": "src"}
    # Создает список со всеми ссылками на изображения
    # И изменяет ссылки в html файлы на локальные пути до изображений
    dir_name = f"{url_to_name(url)}_files"
    url_hostname = Url(url).get_hostname()
    content_links_list = []
    logger.debug(f"\ndir_name={dir_name}\nurl_hostname={url_hostname}")

    for tag in soup(tags):
        # Определяем из какого атрибута брать ссылку
        tag_attr = attrs_tag[f"{tag.name}"]
        if not tag.has_attr(tag_attr):
            logger.debug(f"tag {tag.name} don't have attribute {tag_attr}")
            continue
        content_link = url_normalize(tag[tag_attr])
        local_link = content_link[0] == "/" and content_link[:2] != "//"
        identical_hostname = Url(content_link).get_hostname() == url_hostname
        logger.debug(f"\ncontent_link={content_link}\nlocal_link is {local_link}\n\
                      identical_hostname is {identical_hostname}")
        # Формирование и изменение на локальную ссылку
        if local_link or identical_hostname:
            content_link = urljoin(f"https://{url_hostname}", content_link)
            tag[tag_attr] = f"{dir_name}/{url_to_name(content_link)}"
            content_links_list.append(content_link)
            logger.debug(f"new local link: {tag[tag_attr]}")
            logger.debug(f"content_link={content_link}")
        elif (not only_local_content) and content_link[:4] == "http":
            tag[tag_attr] = f"{dir_name}/{url_to_name(content_link)}"
            content_links_list.append(content_link)
            logger.debug(f"new local link: {tag[tag_attr]}")
            logger.debug(f"content_link={content_link}")
        else:
            logger.debug(f"{content_link} doesn't fit")

    with open(path_to_html_file, "w", encoding="utf-8") as file:
        file.write(str(soup))
    logger.debug(f"content_links_list = \n{content_links_list}")
    return content_links_list


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
    except Exception:
        logger.warning("Connection fail")
        return None
    if req.ok:
        # Считываем текст HTML-документа
        src = req.text
        name_file = url_to_name(url)
        file_path = os.path.normpath(os.path.join(path_to_file, f"{name_file}.html"))
        # Записываем в файл в указанной директории
        try:
            logger.debug(f"write html file: {file_path}")
            with open(file_path, "w", encoding="utf-8") as myfile:
                myfile.write(src)
        except FileNotFoundError:
            return None
        return file_path
    else:
        logger.warning("Connection fail")
        return None


def download_content(path_to_dir, url, client=requests):
    content_name = url_to_name(url)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    # Определение расширение файла
    content_path = Url(url).get_path()
    content_extension = os.path.splitext(content_path)[1]
    logger.debug(f"content_extension={content_extension}")
    if content_extension == ".html" or content_extension == "":
        return download(path_to_file=path_to_dir, url=url)
    try:
        request = client.get(url, headers=headers)
        if request.ok:
            path_content = f"{path_to_dir}/{content_name}"
            with open(path_content, "wb") as file:
                file.write(request.content)
            logger.debug(f"The content has been downloaded successfully. The path to it:\n{path_content}")
            return path_content
        else:
            logger.warn(f"Couldn't connect to the url\nurl={url}")
            return None
    except requests.RequestException:
        logger.warn(f"The url content could not be downloaded\nurl={url}")
        return None


def make_dir_with_files(path_to_dir, url, only_local_content=True):
    name_dir = url_to_name(url) + "_files"
    dir_path = f"{path_to_dir}/{name_dir}"
    logger.info(f"create directory for assets: {dir_path}")
    os.mkdir(dir_path)

    html_file_path = f"{path_to_dir}/{url_to_name(url)}.html"
    tags = ["img", "link", "script"]
    logger.debug(f"html_file_path={html_file_path}")

    content_links = parse_content_link(html_file_path, url, tags=tags,
                                       only_local_content=only_local_content)

    undownloaded_content = []
    for content_link in content_links:
        result = download_content(dir_path, content_link)
        if result is None:
            undownloaded_content.append(content_link)
    # Если есть не скаченные ресурсы, сообщаем об этом
    if len(undownloaded_content):
        logger.info(f"The download assets was successful, but some resources could not be downloaded:\n{undownloaded_content}")
    else:
        logger.info("The download assets was successful")


def full_download(url, path, only_local_content=True):
    logger.info(f"requested url:{url}")
    logger.info(f"output path: {path}")
    path_html_page = download(url=url, path_to_file=path)
    logger.info(f"write html file: {path_html_page}")
    make_dir_with_files(url=url, path_to_dir=path,
                        only_local_content=only_local_content)
    logger.info("The download was successful")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s:%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)
    path = r"C:\Users\Admin\Desktop"
    url = "https://ru.hexlet.io/courses/cli-basics"
    tags = ["img", "link", "script"]
    # download_content(path_to_dir=path, url=url)
    download(path_to_file=path, url=url)
    make_dir_with_files(path_to_dir=path, url=url, only_local_content=False)
