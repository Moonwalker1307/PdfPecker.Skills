"""Zips each skill folder for upload to Claude.ai (Settings, Capabilities, Skills) or the Skills API.

    python3 tools/package.py [out_dir]     -> dist/<skill>.zip, one folder with SKILL.md at its root
"""
import os
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist")
os.makedirs(out_dir, exist_ok=True)
plugins = os.path.join(ROOT, "plugins")
for plugin in sorted(os.listdir(plugins)):
    skills = os.path.join(plugins, plugin, "skills")
    for name in sorted(os.listdir(skills)):
        folder = os.path.join(skills, name)
        target = os.path.join(out_dir, f"{name}.zip")
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            for base, dirs, files in os.walk(folder):
                dirs[:] = sorted(d for d in dirs if d != "__pycache__")
                for file in sorted(files):
                    path = os.path.join(base, file)
                    z.write(path, os.path.join(name, os.path.relpath(path, folder)))
        print(target)
