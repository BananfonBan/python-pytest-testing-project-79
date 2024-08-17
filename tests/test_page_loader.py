import os
from pathlib import Path
import logging
import pytest
from bs4 import BeautifulSoup
import pook
from PageLoader.page_loader import download, parse_content_link
from PageLoader.page_loader import url_to_name, make_dir_with_content

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s:%(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)


class fake_request:
    def __init__(self, data):
        self.text = data
        self.content = data
        self.ok = True

    def get(self, url="url", headers="headers"):
        return self


@pytest.fixture
def fixture_url():
    urls = ["https://tests.net.co/path/to/page",
            "http://tests.co/path_to_page,",
            "http://a.tests-test.io/page#part",
            "https://b.test-t.io/page?part=1",
            "http://b.test-t.io/page?part=1&p=2",]

    correct_name = ["tests-net-co-path-to-page",
                    "tests-co-path-to-page,",
                    "a-tests-test-io-page",
                    "b-test-t-io-page",
                    "b-test-t-io-page",]

    data = {"url": urls, "name": correct_name}
    return data


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


def test_url_to_name(fixture_url):
    name_url = []
    for url in fixture_url["url"]:
        name_url.append(url_to_name(url))
    assert name_url == fixture_url["name"]


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

    with open(f"{tmp_path}/test-io-1.html", "r", encoding="utf-8") as result_file:
        file_data = result_file.read()

    path_file = Path(os.path.join(Path(tmp_path), "test-io-1.html"))
    assert path_file.exists()
    assert os.path.normpath(name_file) == os.path.normpath(path_file)
    assert file_data == fixture_html_1


def test_parse_local_content_link(tmp_path, fixture_html_2):
    path_file = f"{tmp_path}/file.html"
    with open(path_file, "w", encoding="utf-8") as file:
        file.write(fixture_html_2)
    local_link = set(parse_content_link(path_file, "https://test.net"))

    assert local_link == {
        "https://test.net/assets/professions/python.png",
        "https://test.net/page/path/part",
        "https://test.net/page/tests",
        "https://test.net/scripts/java/script-42",
        }

    with open(path_file, "r", encoding="utf-8") as correct_file:
        soup = BeautifulSoup(correct_file, "html.parser")

    all_tags = set()
    for img in soup.find_all("img"):
        all_tags.add(img["src"])
    for script in soup.find_all("script"):
        if script.has_attr("src"):
            all_tags.add(script["src"])
    for link in soup.find_all("link"):
        all_tags.add(link["href"])

    chanched_tags = {
        "test-net_files/test-net-assets-professions-python.png",
        "test-net_files/test-net-scripts-java-script-42",
        "test-net_files/test-net-page-path-part",
        "test-net_files/test-net-page-tests",
    }
    assert chanched_tags.issubset(all_tags)


def test_parse_img_link(tmp_path, fixture_html_2):
    path_file = f"{tmp_path}/file.html"
    with open(path_file, "w", encoding="utf-8") as file:
        file.write(fixture_html_2)
    all_link = set(parse_content_link(path_file, "https://test.net",
                                      only_local_content=False))

    assert all_link == {
        "https://test.net/assets/professions/python.png",
        "https://i.ytimg.com/vi/mpvdTb2J9dg/hqdefault.jpg",
        "https://yan.de.re/tests/path",
        "https://test.net/scripts/java/script-42",
        "https://java.org/script/85",
        "https://java.org/script/99",
        "https://tests.org/page/path",
        "https://test.net/page/path/part",
        "https://yan.de.re/tests/path",
        "https://test.net/page/tests",
    }

    with open(path_file, "r", encoding="utf-8") as correct_file:
        soup = BeautifulSoup(correct_file, "html.parser")

    all_tags = set()
    for img in soup.find_all("img"):
        all_tags.add(img["src"])
    for script in soup.find_all("script"):
        if script.has_attr("src"):
            all_tags.add(script["src"])
    for link in soup.find_all("link"):
        all_tags.add(link["href"])
    all_tags_file = {
        "test-net_files/test-net-assets-professions-python.png",
        "test-net_files/i-ytimg-com-vi-mpvdTb2J9dg-hqdefault.jpg",
        "test-net_files/yan-de-re-tests-path",
        "test-net_files/test-net-scripts-java-script-42",
        "test-net_files/java-org-script-85",
        "test-net_files/java-org-script-99",
        "test-net_files/tests-org-page-path",
        "test-net_files/test-net-page-path-part",
        "test-net_files/yan-de-re-tests-path",
        "test-net_files/test-net-page-tests",
    }
    assert all_tags == all_tags_file


def test_except_parse_content_link(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_content_link(f"{tmp_path}/tests/fixture.html", "https://www.tests.com")


def test_except_dowload(tmp_path, fixture_html_1):
    with pytest.raises(FileNotFoundError):
        download("test.com/example", f"{tmp_path}/notfound",
                 client=fake_request(fixture_html_1))


def test_except_make_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        make_dir_with_content(f"{tmp_path}/notexist",
                              "http://tests.co/page1")
