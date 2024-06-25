import os
import sys
import shutil
import zipfile


def copy_files(src: str, dst: str, replace: bool = False):
	"""Copy files from a directory to another.
	Args:
		src (str): The source directory
		dst (str): The destination directory
		replace (bool, optional): Replace existing files. Defaults to False.
	"""
	if not os.path.exists(src):
		raise FileNotFoundError(f"Source directory '{src}' not found")
	if os.path.exists(dst):
		if replace:
			if os.path.isdir(dst):
				shutil.rmtree(dst)
			else:
				os.remove(dst)
		else:
			raise FileExistsError(f"Destination directory '{dst}' already exists")
	if os.path.isfile(src):
		shutil.copy2(src, dst)
	else:
		shutil.copytree(src, dst)


def move_files(src: str, dst: str, replace: bool = False):
	"""Move files from a directory to another.
	Args:
		src (str): The source directory
		dst (str): The destination directory
		replace (bool, optional): Replace existing files. Defaults to False.
	"""
	if not os.path.exists(src):
		raise FileNotFoundError(f"Source directory '{src}' not found")
	if os.path.exists(dst):
		if replace:
			if os.path.isdir(dst):
				shutil.rmtree(dst)
			else:
				os.remove(dst)
		else:
			raise FileExistsError(f"Destination directory '{dst}' already exists")
	shutil.move(src, dst)


def remove_files(paths: list):
	"""Remove files or directories.
	Args:
		paths (list): The paths to remove
	"""
	for path in paths:
		if os.path.exists(path):
			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)


def remove_all(filenames: list, path: str):
	"""Remove all files recursively in a directory.
	Args:
		filenames (list): The files to remove
		path (str): The directory path
	"""
	files = os.listdir(path)
	for file in files:
		full_path = os.path.join(path, file)
		if file in filenames:
			if os.path.isdir(full_path):
				shutil.rmtree(full_path)
			else:
				os.remove(full_path)
		else:
			if os.path.isdir(full_path):
				remove_all(filenames, full_path)


def zip_files(src: str, dst: str, include_dir: bool = False, replace: bool = False):
	"""Zip files in a directory.
	Args:
		src (str): The source directory
		dst (str): The destination zip file
		include_dir (bool, optional): Include the directory in the zip file. Defaults to True.
		replace (bool, optional): Replace existing zip file. Defaults to False.
	"""
	if not os.path.exists(src):
		raise FileNotFoundError(f"Source directory '{src}' not found")
	if os.path.exists(dst):
		if replace:
			os.remove(dst)
		else:
			raise FileExistsError(f"Destination zip file '{dst}' already exists")
	with zipfile.ZipFile(dst, 'w') as zipf:
		for root, _, files in os.walk(src):
			for file in files:
				zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), src))
		if include_dir:
			zipf.write(src, os.path.basename(src))


if __name__ == "__main__":
	replace = True
	if "--no-replace" in sys.argv:
		replace = False
		sys.argv.remove("--no-replace")

	include_dir = False
	if "--zip-dir" in sys.argv:
		include_dir = True
		sys.argv.remove("--zip-dir")

	if not os.path.exists("temp"):
		os.makedirs("temp")

	copy_files("eymo.sh", "temp/eymo.sh", replace)
	copy_files("src/rpi", "temp/app", replace)
	copy_files("requirements.txt", "temp/app/requirements.txt", replace)
	if not os.path.exists("temp/app/arduino"):
		os.makedirs("temp/app/arduino")
	copy_files("src/arduino/arduino.ino", "temp/app/arduino/arduino.ino", replace)
	remove_files(["temp/app/logs"])
	remove_all(["__pycache__", ".DS_Store"], "temp")

	zip_files("temp/app", "temp/eymo_app.zip", False, replace)
	remove_files(["temp/app"])
	zip_files("temp", "eymo.zip", include_dir, replace)
	remove_files(["temp"])

	print("EYMO package created successfully.")
