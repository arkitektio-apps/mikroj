import PyInstaller.__main__
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os
import shutil


def download_and_unzip(url, extract_to=".", label=""):
    if not os.path.exists(os.path.join(extract_to, label)):
        http_response = urlopen(url)
        print(f"Downloading {url}")
        zipfile = ZipFile(BytesIO(http_response.read()))
        print(f"Extracting {zipfile.filelist[0].filename}")
        zipfile.extractall(path=extract_to)
        os.rename(
            os.path.join(extract_to, zipfile.filelist[0].filename),
            os.path.join(extract_to, label),
        )


print("Copying shares")

JDK_LINK = "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.16.1%2B1/OpenJDK11U-jdk_x64_windows_hotspot_11.0.16.1_1.zip"
MAVEN_LINK = (
    "https://dlcdn.apache.org/maven/maven-3/3.9.4/binaries/apache-maven-3.9.4-bin.zip"
)

download_and_unzip(MAVEN_LINK, "share", "mvn")
download_and_unzip(JDK_LINK, "share", "jdk")


APP_NAME = "MikroJ"

PyInstaller.__main__.run(
    [
        "entrypoint.py",
        "--clean",
        "--windowed",
        "--onedir",
        f"--name={APP_NAME}",
        "--noconfirm",
        "--hiddenimport=scyjava",
        "--copy-metadata=scyjava",
        "--copy-metadata=imglyb",
        "--copy-metadata=pyimagej",
        "--hiddenimport=imglyb",
        "--hiddenimport=imagej",
        "--hiddenimport=pyimagej",
        "--add-data=share;share",
        "--additional-hooks-dir=hooks",
        "--icon=mikroj-logo.ico",
    ]
)


shutil.make_archive("./dist/MikroJApp", "zip", "./dist/MikroJ")
print("Made archive")
