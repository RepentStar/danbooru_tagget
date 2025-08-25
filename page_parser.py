import requests
import lxml.etree
import re


class PageParser:
    def __init__(self, url, filter_tags_list=[], need_filter=True):
        try:
            self.page = requests.get(url).text
        except Exception:
            raise Exception
        self.need_filter = need_filter
        self.filter_tags_list = (
            [
                "original",
                "commentary",
                "non-web source",
                ".*request$",
                "highres",
                "absurdres",
                "^bad",
                "lowres",
            ]
            if not filter_tags_list
            else filter_tags_list
        )

        self.tree = lxml.etree.HTML(self.page)
        self.sequence = [
            "artist-tag-list",
            "copyright-tag-list",
            "character-tag-list",
            "general-tag-list",
            "meta-tag-list",
        ]
        self.tag_dict = dict()

    def _path_is_exists(self, path):
        return len(self.tree.xpath(path)) > 0

    def _check_tag_type(self, tag_name):
        return True if tag_name in self.sequence else False

    def _get_tag_list(self):
        for i in range(1, 6):
            path = f"//*[@id='tag-list']/div/ul[{i}]"
            if not self._path_is_exists(path=path):
                continue
            class_attr = self.tree.xpath(f"{path}/@class")
            tag_list_name = class_attr[0] if class_attr else "None"
            if not self._check_tag_type(tag_list_name):
                continue
            self.tag_dict[tag_list_name] = [
                tag.replace("_", " ").replace("(", "\(").replace(")", "\)")  # type: ignore
                for tag in self.tree.xpath(f"{path}/li/@data-tag-name")
            ]

    def _format_tags(self):
        self._get_tag_list()
        if self.need_filter:
            self._filter_tags()
        result = []
        for tag_name in self.sequence:
            tag_list = self.tag_dict.get(tag_name, False)
            if not tag_list:
                continue
            result.append(
                ", ".join(tag_list),
            )
            result.append(",")
            result.append("\n")
        return "".join(result)

    def _filter_tags(self):
        compiled_patterns = [re.compile(pattern) for pattern in self.filter_tags_list]

        for tag_name in self.tag_dict:
            self.tag_dict[tag_name] = [
                tag
                for tag in self.tag_dict[tag_name]
                if not any(pattern.search(tag) for pattern in compiled_patterns)
            ]

    def get_tags(self):
        return self._format_tags()


if __name__ == "__main__":
    url = r"https://danbooru.donmai.us/posts/9850932"
    parser = PageParser(url)
    print(parser.get_tags())
