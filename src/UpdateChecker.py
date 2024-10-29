import requests


class UpdateChecker:
    def __init__(self, repo, current_version):
        """
        Initialize the UpdateChecker with the repository and current version.

        :param repo: str, GitHub repository in the format 'owner/repo'
        :param current_version: str, current version of the software
        """
        self.repo = repo
        self.current_version = current_version
        self.latest_release = None

    def get_latest_release(self):
        """
        Get the latest release from the GitHub repository.

        :return: dict, latest release information
        """
        url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()

    def check_for_update(self):
        """
        Check if there is a new release available.

        :return: bool, True if an update is available, False otherwise
        """
        latest_release = self.get_latest_release()
        self.latest_release = latest_release['tag_name']
        print(f"Latest release: {self.latest_release}")
        return self.latest_release != self.current_version
    
    def download_update(self, path):
        """
        Download the latest release from the GitHub repository.

        :return: bytes, content of the latest release
        """
        if self.latest_release is None:
            self.check_for_update()
        url = f'https://github.com/{self.repo}/releases/download/{self.latest_release}/eyeball_project.exe'
        response = requests.get(url, stream=True)
        response.raise_for_status()
        if response.status_code == 200:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        else:
            raise Exception(f"Failed to download the latest release: {response.status_code}")