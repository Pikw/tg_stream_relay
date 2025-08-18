import yaml
from pathlib import Path
from typing import Any

class Localizer:
    def __init__(self, locales_dir: Path, default_lang: str = "en"):
        self.dir = locales_dir
        self.default = default_lang
        self._cache: dict[str, dict[str, Any]] = {}

    def _load(self, lang: str) -> dict[str, Any]:
        if lang not in self._cache:
            f = self.dir / f"{lang}.yml"
            if not f.exists():
                f = self.dir / f"{self.default}.yml"
            self._cache[lang] = yaml.safe_load(f.read_text(encoding="utf-8"))
        return self._cache[lang]

    def t(self, key: str, lang: str | None = None, **kwargs) -> str:
        lang = lang or self.default
        data = self._load(lang)
        parts = key.split(".")
        node: Any = data
        for p in parts:
            node = node.get(p, {})
        if not isinstance(node, str):
            # fallback to default
            data = self._load(self.default)
            node = data
            for p in parts:
                node = node.get(p, {})
            if not isinstance(node, str):
                return key
        return node.format(**kwargs)
