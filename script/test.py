import os
import random
import glob
import shutil
import string
from typing import Any


def main():
    phase = "test"
    folder_path = '/Users/hienhuynhdang/Movies/dataset'
    destination_folder = "/Users/hienhuynhdang/Movies/dataset_sub"
    num = 20

    for i in range(num):
        os.makedirs(f"{destination_folder}/dataset{i+1}", exist_ok=True)
        os.makedirs(f"{destination_folder}/dataset{i+1}/{phase}", exist_ok=True)
        for alphabet in string.ascii_lowercase:
            os.makedirs(f"{destination_folder}/dataset{i+1}/{phase}/{alphabet}", exist_ok=True)

    for alphabet in string.ascii_lowercase:
        input_path = f"{folder_path}/{phase}/{alphabet}"
        jpg_files = list(glob.glob(os.path.join(input_path, '*.jpg')))
        random.shuffle(jpg_files)
        size_ = len(jpg_files) // num
        for i in range(num):
            print(i)
            output_path = f"{destination_folder}/dataset{i+1}/{phase}/{alphabet}"
            sub_folder_content = jpg_files[i:i + size_]
            for path_ in sub_folder_content:
                shutil.copy(path_, output_path)


def main1():
    a = "/Users/hienhuynhdang/Movies/dataset/data.yaml"
    destination_folder = "/Users/hienhuynhdang/Movies/dataset_sub"
    num = 20
    for i in range(num):
        des = f"{destination_folder}/dataset{i+1}"
        shutil.copy(a, des)


class MyClass:
    def __getattr__(self, *args: Any, **kwargs: Any):
        print(f"Fallback function called for attribute: ")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        print("haha")


if __name__ == '__main__':
    # main()
    # main1()
    # Create an instance of the class
    obj = MyClass()

    # Access an attribute that is not defined in the class
    obj.undefined_attribute
