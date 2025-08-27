import pyperclip
import queue
import threading
import time
from page_parser import PageParser
import re


def main_thread(stop_queue):
    last_url = ""
    while True:
        url = pyperclip.paste()
        pure_path = url[: url.rfind("?")]
        if (
            url.startswith(r"https://danbooru")
            and "posts" in url
            and bool(re.search(r"/posts/\d+$", pure_path))
            and url != last_url
        ):
            try:
                parser = PageParser(url)
                tags = parser.get_tags()
                pyperclip.copy(tags)
                print(time.asctime(), ":")
                print(tags)
                last_url = url
            except Exception as e:
                print(f"Error processing URL: {e}")
        if not stop_queue.empty():
            break
        time.sleep(1)


def main():
    stop_queue = queue.Queue()

    monitor_thread = threading.Thread(target=main_thread, args=(stop_queue,))
    monitor_thread.start()

    input("Press Enter to stop the script...\n")
    stop_queue.put(True)
    monitor_thread.join()


if __name__ == "__main__":
    main()
