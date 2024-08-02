from pathlib import Path
import requests
from PageLoader.UrlCLass import Url


def parsing_url_to_name(url):
    parse_url = Url(url)
    parse_hostname = "-".join(parse_url.get_hostname().split("."))
    parse_path = "-".join(parse_url.get_path().split("/"))

    return parse_hostname + parse_path


def download(url: str, path_to_file=Path.cwd(), client=requests):
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
    with open(f"{path_to_file}/{name_file}.html", "w") as myfile:
        myfile.write(src)
