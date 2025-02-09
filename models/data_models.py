import pickle
import hashlib
import bisect
import os
import json
from filelock import FileLock


class PickleShardManager:
    def __init__(self, num_shards=3, folder="data_shards"):
        self.num_shards = num_shards
        self.folder = folder
        self.metadata_file = f"{folder}/metadata.json"
        self.shard_keys = []
        self.shards = {}
        self.metadata = {}

        os.makedirs(folder, exist_ok=True)
        for i in range(num_shards):
            shard_key = self._hash(f"shard-{i}")
            self.shard_keys.append(shard_key)
            self.shards[shard_key] = f"{folder}/shard_{i}.pkl"

        self.shard_keys.sort()
        self._load_metadata()

    def _hash(self, key):
        """Generate hash integer from key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _get_shard_file(self, key):
        """Choose file pickle"""
        key_hash = self._hash(key)
        idx = bisect.bisect(self.shard_keys, key_hash) % self.num_shards
        return self.shards[self.shard_keys[idx]]

    def _save_metadata(self):
        """Save metadata"""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def _load_metadata(self):
        """Load metadata if exists"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)

    def exists(self, key):
        """Check if key exists"""
        key = str(key)
        return key in self.metadata

    def find_by_key(self, key):
        """Find data of a key"""
        key = str(key)
        if not self.exists(key):
            return None

        file_path = self.metadata[key]
        data = self.load_shard(file_path)
        return data.get(key, None)

    def insert(self, key, data):
        """Insert new record to file pickle"""
        key = str(key)
        if self.exists(key):
            return "Key already exists"

        file_path = self._get_shard_file(key)
        self.metadata[key] = file_path
        self._save_metadata()

        # Append an object safely
        with FileLock(file_path + ".lock"):
            with open(file_path, "ab") as f:
                pickle.Pickler(f).dump({key: data})

        return "Inserted"

    def update(self, key, new_data):
        """Update data of a key"""
        key = str(key)
        if not self.exists(key):
            return "Key does not exist"

        file_path = self.metadata[key]
        temp_data = self.load_shard(file_path)
        temp_data[key] = temp_data.get(key, "") + new_data

        with FileLock(file_path + ".lock"):
            with open(file_path, "wb") as f:
                pickle.dump(temp_data, f)

        return "Updated"

    def load_shard(self, file_path):
        """Read data of a shard"""
        if not os.path.exists(file_path):
            return {}

        data = {}
        with open(file_path, "rb") as f:
            while True:
                try:
                    record = pickle.load(f)
                    data.update(record)
                except EOFError:
                    break
        return data

    def load_all(self):
        """Read data of all shards"""
        all_data = {}
        for file_path in self.shards.values():
            all_data.update(self.load_shard(file_path))
        return all_data
