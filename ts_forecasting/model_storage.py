import os

from pathlib import Path
from joblib import dump


class Storage:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)

    def save(self, model_obj, model_path: str, user_id: str = None, private: bool = False):
        if user_id is None and private:
            raise ValueError('Private saving need user_id')

        model_path = Path(model_path)
        model_name = model_path.name
        path_in_storage = str(model_path.parent)
        if path_in_storage[0] == os.sep:
            path_in_storage = path_in_storage[1:]

        if private:
            model_storage_dir = self.storage_dir / 'private' / user_id / path_in_storage
        else:
            model_storage_dir = self.storage_dir / 'public' / path_in_storage

        if not model_storage_dir.exists():
            model_storage_dir.mkdir(parents=True, exist_ok=True)

        full_model_path = model_storage_dir / model_name

        dump(model_obj, full_model_path)




