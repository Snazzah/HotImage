import os
import random
import sys
import logging
import json

from collections import namedtuple
from flask import Flask, jsonify, send_from_directory, abort, redirect, render_template
from pathtools.patterns import match_any_paths
from .watcher import observe_images, observe_config

__version__ = '1.0.0'

class HotImage:
    def __init__(self, config=None):
        self.app = Flask('hotimage', template_folder='../templates')
        self.config = config if config else self._load_config()
        self.images = {}

        self.app.route('/')(self._index)
        self.app.route('/docs')(self._docs)
        self.app.route('/assets/<path:filename>')(self._assets)
        self.app.route('/favicon.ico')(self._favicon)
        self.app.route('/<path:category>/<filename>')(self._get_image)

        self.app.route('/api/v1/random')(self._random_image)
        self.app.route('/api/v1/random.json')(self._random_image_json)
        self.app.route('/api/v1/<path:category>/random')(self._random_image_from_cat)
        self.app.route('/api/v1/<path:category>/random.json')(self._random_image_from_cat_json)
        self.app.route('/api/v1/list')(self._list)
        self.app.route('/api/v1/<path:category>/list')(self._list_cat)

        self._load_images()
        if self.config.watcher:
            self._image_observer = observe_images(self.config.images_path, self)
            self._config_observer = observe_config(self)
        logging.basicConfig(level = 'DEBUG' if self.config.debug else 'INFO')

    def _load_images(self):
        self.images = {}
        for root, dirs, files in os.walk(self.config.images_path):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.isfile(filepath):
                    relpath = os.path.relpath(filepath, self.config.images_path)
                    if match_any_paths([relpath], excluded_patterns=self.config.ignore_patterns):
                        category, filename = os.path.split(relpath)
                        if self.images.get(category):
                            if not filename in self.images[category]:
                                self.images[category].append(filename)
                        else:
                            self.images[category] = [filename]
    
    def _load_config(self):
        try:
            with open("config.json", encoding='utf-8') as data:
                config = json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        except FileNotFoundError:
            print("Could not find config.json!")
            sys.exit()
        return config

    def image_count(self):
        count = 0
        for files in self.images.values():
            count += len(files)
        return count
    
    def domain(self):
        domain = self.config.domain
        if self.config.localhost:
            domain = f"http://localhost:{self.config.port}/"
        return domain
    
    def get_random_image(self, category=None, use_json=False):
        if not category:
            category = random.choice(list(self.images.keys()))
        elif not self.images.get(category):
            return abort(404)
        image = random.choice(self.images[category])

        if use_json:
            return jsonify({
                "category": category,
                "filename": image,
                "url": f"{self.domain()}{category}/{image}"
            })
        else:
            return redirect(f"/{category}/{image}")

    def start(self):
        self.app.run(port=self.config.port, debug=self.config.debug)

    # routes

    def _index(self):
        def get_cat_color(category):
            if (hasattr(self.config, 'metadata')
            and hasattr(self.config.metadata, 'category_info')
            and hasattr(self.config.metadata.category_info, category)
            and hasattr(getattr(self.config.metadata.category_info, category), 'color')):
                return getattr(getattr(self.config.metadata.category_info, category), 'color')
            return "alizarin"
        
        metadata = self.config.metadata if hasattr(self.config, 'metadata') else {}

        return render_template(
            'index.html', metadata=metadata, domain=self.domain(),
            cat_count=len(self.images), image_count=self.image_count(), categories=self.images,
            random=random.choice, cat_color=get_cat_color, version=__version__
        )

    def _docs(self):
        metadata = self.config.metadata if hasattr(self.config, 'metadata') else {}

        return render_template(
            'docs.html', metadata=metadata, domain=self.domain(),
            categories=self.images, random=random.choice, version=__version__
        )

    def _assets(self, filename):
        return send_from_directory("../templates/assets", filename)

    def _favicon(self):
        return send_from_directory("../templates/assets/images", "icon.png")

    def _get_image(self, category, filename):
        if self.images.get(category) and filename in self.images[category]:
            return send_from_directory(os.path.join("../images", category), filename)
        else:
            return abort(404)

    def _random_image(self):
        return self.get_random_image()

    def _random_image_json(self):
        return self.get_random_image(use_json=True)

    def _random_image_from_cat(self, category):
        return self.get_random_image(category=category)

    def _random_image_from_cat_json(self, category):
        return self.get_random_image(category=category, use_json=True)

    def _list(self):
        category_data = {}
        for key in self.images:
            files = self.images[key]
            category_data[key] = {
                "count": len(files),
                "files": files
            }

        return jsonify({
                "categories": category_data,
                "category_keys": list(self.images),
                "count": len(self.images),
                "image_count": self.image_count()
            })

    def _list_cat(self, category):
        files = self.images.get(category)
        if not files:
            return abort(404)

        return jsonify({
                "files": files,
                "count": len(files)
            })
