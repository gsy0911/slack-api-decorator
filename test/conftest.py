import os
import sys

# テスト対象のファイルへのパスを通している
# pytestの設定
PARENT_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
SOURCE_PATH = PARENT_PATH.rsplit('/', 1)[0]

sys.path.append(f"{SOURCE_PATH}")
