import requests
import json
import os
import logging
class EFile:
    """Object to handle downloading, loading, and reading cached etagged file"""
    def __init__(
        self,
        url:str,
        filename:str,
        folder:str="downloads/downloads"
    ):
        self.url = url
        self.folder = os.path.abspath(folder)
        self.path = os.path.join(self.folder, filename)
        self.etag_path = self.path + ".etag"

    @property
    def exists(self) -> bool:
        print(self.path)
        return os.path.exists(self.path)
    
    @property
    def etag(self) -> str | None:
        if not os.path.exists(self.etag_path):
            return None
        if not os.path.exists(self.path):
            os.remove(self.etag_path)
            return None
        with open(self.etag_path, 'r', encoding='utf-8') as etag_file:
            return etag_file.read().strip()
            
    def download(self) -> str:
        """Checks if a new version of a file is available or returns old"""
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        if os.path.exists(self.path) and os.path.exists(self.etag_path):
            with open(self.etag_path, 'r', encoding='utf-8') as etag_file:
                last_etag = etag_file.read().strip()
        else:
            last_etag = None
        try:
            response = requests.head(self.url)
            if any(i in response.headers for i in ("etag", 'ETag', 'ETAG')):
                for i in ("etag", "ETag", "ETAG"):
                    if (server_etag := response.headers.get(i)):
                        break             
                server_etag = server_etag.strip('\"')
                if server_etag == last_etag:
                    logging.info("File is up-to-date. No need to download.")
                    # Read content from the local file
                    with open(self.path, 'r', encoding='utf-8') as file:
                        content = file.read()
                else:
                    logging.info("File has been updated. Downloading new version...")
                    content = self._download_and_save(server_etag)
            else:
                logging.info("Server does not support ETags. Downloading the file.")
                content = self._download_and_save(None)
        except requests.RequestException as e:
            logging.info(f"Unable to check for updates: {e}")
            logging.info("Downloading the file.")
            content = self._download_and_save(None)
        return content

    def _download_and_save(self, new_etag:str) -> str:
        """Downloads file and returns file contents"""
        response = requests.get(self.url)
        with open(self.path, 'w+', encoding='utf-8') as file:
            file.write(response.text)
        if new_etag is not None:
            with open(self.etag_path, 'w') as etag_file:
                etag_file.write(new_etag)
        logging.info(f"File downloaded and saved to {self.path} with ETag {new_etag}")
        return response.text
    
    def read(self) -> str:
        """Reads file contents"""
        if not self.exists: self.download()
        with open(self.path, encoding='utf-8') as f:
            return f.read()
        
    def read_json(self) -> str:
        """Loads json content"""
        if not self.exists: self.download()
        with open(self.path, encoding='utf-8') as f:
            return json.load(f)

    def remove(self) -> bool:
        """Removes file and etag file"""
        if os.path.exists(self.etag_path):
            os.remove(self.etag_path)
        if not os.path.exists(self.path):
            logging.info(f"File {self.path} already deleted")
            return False
        os.remove(self.path)
        logging.info(f"Deleted {self.path}")
        return True

# def test() -> None:
#     """
#     Clears cache from previous tests
#     Downloads file
#     Gets cached file    
#     """
#     test_url = "https://api.github.com/repos/microsoft/vscode/releases"
#     f = etagged_file(test_url, "vscode.json")
#     f.remove()
#     input("Press Enter to continue")
#     # First access is slow
#     f = etagged_file(test_url, "vscode.json")
#     data = json.loads(f.download())
#     input("Press Enter to continue")
#     print(json.dumps(data, indent=4))
#     input("Press Enter to continue")
#     # Second access should be faster
#     f = etagged_file(test_url, "vscode.json")
#     data = json.loads(f.download())
#     input("Press Enter to continue")
#     print(json.dumps(data, indent=4))

# if __name__ == "__main__":
#     test()