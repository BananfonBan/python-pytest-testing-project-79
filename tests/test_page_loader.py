import os
from pathlib import Path
import pytest
from bs4 import BeautifulSoup
import pook
from PageLoader.page_loader import download, download_img, parse_img_link


class fake_request:
    def __init__(self, data):
        self.text = data
        self.content = data
        self.ok = True

    def get(self, url="url", headers="headers"):
        return self


@pytest.fixture
def fixture_html_1():
    path_dir = Path.cwd()
    with open(f"{path_dir}/tests/Fixture_for_test_1.html", 'r', encoding="utf-8") as f:
        data = f.read()
        return data


@pytest.fixture
def fixture_html_2():
    path_dir = Path.cwd()
    with open(f"{path_dir}/tests/Fixture_for_test_2.html", 'r', encoding="utf-8") as f:
        data = f.read()
        return data


@pytest.fixture
def fixture_img_1():
    path_dir = Path.cwd()
    with open(f"{path_dir}/tests/Justcat.jpg", 'rb') as f:
        data = f.read()
        return data


@pytest.fixture
def fixture_img_2():
    path_dir = Path.cwd()
    with open(f"{path_dir}/tests/Avagadro.png", 'rb') as f:
        data = f.read()
        return data


@pook.on
def test_download_push_request(tmp_path):
    mock_1 = pook.get('http://test.com')
    assert mock_1.calls == 0

    download(url="http://test.com", path_to_file=tmp_path)
    assert mock_1.calls == 1

    mock_2 = pook.get("http://test_2.io/download/push")
    download(url="http://test_2.io/download/push", path_to_file=tmp_path)
    assert mock_2.calls == 1

    mock_3 = pook.get("http://test.com/push/test")
    download(url="http://test.com/push/test", path_to_file=tmp_path)
    assert mock_3.calls == 1


def test_download_create_correct_file(tmp_path, fixture_html_1):
    name_file = download("https://test.io/1", tmp_path, client=fake_request(fixture_html_1))

    with open(f"{tmp_path}/test-io-1.html", "r") as result_file:
        file_data = result_file.read()

    path_file = Path(os.path.join(Path(tmp_path), "test-io-1.html"))
    assert path_file.exists()
    assert os.path.normpath(name_file) == os.path.normpath(path_file)
    assert file_data == fixture_html_1


def test_download_img(tmp_path, fixture_img_1, fixture_img_2):
    client_1 = fake_request(fixture_img_1)
    client_2 = fake_request(fixture_img_2)

    url_1 = "https://justcat.cute/black/cat.jpg"
    path_img_1 = download_img(tmp_path, url_1, client=client_1)
    path_file = Path(path_img_1)
    with open(path_img_1, "rb") as img_file:
        file_data = img_file.read()

    assert path_file.exists()
    assert file_data == fixture_img_1

    url_2 = "https://sciense.co/chemists/avagadro.png"
    path_img_2 = download_img(tmp_path, url_2, client=client_2)
    path_file = Path(path_img_2)
    with open(path_img_2, "rb") as img_file:
        file_data = img_file.read()

    assert path_file.exists()
    assert file_data == fixture_img_2


@pook.on
def test_download_img_requests(tmp_path, fixture_img_1):
    mock_1 = pook.get('http://test.jpg')
    assert mock_1.calls == 0

    download_img(url="http://test.jpg", path_to_dir=tmp_path)
    assert mock_1.calls == 1

    mock_2 = pook.get("http://test_2/something.png", reply=404)
    result = download_img(url="http://test_2/something.png", path_to_dir=tmp_path)
    assert mock_2.calls == 1
    assert result is None


def test_parse_img_link(tmp_path, fixture_html_2):
    path_file = f"{tmp_path}/file.html"
    with open(path_file, "w", encoding="utf-8") as file:
        file.write(fixture_html_2)
    result_list = parse_img_link(path_file, url="https://test.net")

    assert result_list == ["/assets/professions/python.png",
                           "https://i.ytimg.com/vi/mpvdTb2J9dg/hqdefault.jpg"]

    with open(path_file, "r", encoding="utf-8") as correct_file:
        soup = BeautifulSoup(correct_file, "html.parser")
    new_img_list = []
    for img in soup.find_all("img"):
        new_img_list.append(img["src"])

    assert new_img_list == ["test-net_files/test-net-assets-professions-python.png",
                            "test-net_files/i-ytimg-com-vi-mpvdTb2J9dg-hqdefault.jpg"]
