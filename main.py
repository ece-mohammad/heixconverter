#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI tool that converts and saves HEIC, HEIF images as png, jpg, jpeg files.
"""

from argparse import ArgumentParser
from concurrent.futures import (
    ThreadPoolExecutor as ExecPool,
    as_completed
)
from pathlib import Path
from random import randint
from time import sleep
from typing import List

from PyQt6.QtCore import (
    pyqtSignal,
    QObject,
    QRunnable,
    QThreadPool,
)
from PyQt6.QtWidgets import (
    QFrame,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QApplication,
    QMessageBox,
    QComboBox,
    QSizePolicy,
    QProgressBar,
)
from tqdm import tqdm

from heixconverter import HEIX


class CLI:
    """
    CLI for HEXIConverter
    """

    def __init__(self):
        self.parser: ArgumentParser = self.make_parser()

    @staticmethod
    def make_parser() -> ArgumentParser:
        """Initialize a new argument parser"""
        parser = ArgumentParser(
            description="Convert and save HEIX (HEIC, HEIF) images as jpeg, jpg or png images"
        )
        parser.add_argument(
            "src",
            help="Path to directory that contains HEIX images to convert",
            type=Path,
            metavar="SOURCE",
        )
        parser.add_argument(
            "format",
            help="format to convert images to, supported formats: jpeg, jpg, png",
            metavar="FORMAT",
        )
        parser.add_argument(
            "-o", "--out",
            help="Path to directory where images will be saved. Default is ./converted_images",
            type=Path,
            default=Path("./converted_images"),
        )
        return parser

    @staticmethod
    def _worker(dst_dir: Path, image_path: Path, fmt: str) -> Path:
        heix_image: HEIX = HEIX(image_path)
        sleep(randint(1, 5) / 10)
        return heix_image.save_as(dst_dir, fmt)

    def run(self):
        """Run CLI """
        args = vars(self.parser.parse_args())
        src_dir: Path = args["src"].absolute()
        dst_dir: Path = args["out"].absolute()
        fmt: str = args["format"]

        if not src_dir.exists():
            raise OSError(f"Source directory {src_dir} doesn't exist")

        if not src_dir.is_dir():
            raise ValueError(f"Source directory path: {src_dir} is a file")

        if not dst_dir.exists():
            dst_dir.mkdir(parents=True)

        heix_images: List[Path] = [i for i in src_dir.glob("*.hei[cf]")]
        num_images: int = len(heix_images)
        print(f"Found {num_images} images.")
        pbar = tqdm(total=num_images, desc="Progress: ", unit="image")
        errors = list()
        with ExecPool() as pool:
            result_to_image = {
                pool.submit(self._worker, dst_dir, img, fmt): img
                for img in heix_images
            }
            for res in as_completed(result_to_image):
                img = result_to_image[res]
                try:
                    res.result()
                except Exception as exc:
                    errors.append(img)
                else:
                    pbar.update(1)


class GUI:
    """
    GUI for HEIXConverter
    """

    class EPushButton(QPushButton):
        """
        Expanding push button
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.setSizePolicy(
                QSizePolicy(
                    QSizePolicy.Policy.MinimumExpanding,
                    QSizePolicy.Policy.MinimumExpanding,
                )
            )

    class WorkerSignals(QObject):
        progress = pyqtSignal(int)
        finished = pyqtSignal()

    class Worker(QRunnable):
        def __init__(self, src_dir: Path, dst_dir: Path, fmt: str):
            super().__init__()
            self.src_dir: Path = src_dir
            self.dst_dir: Path = dst_dir
            self.format: str = fmt
            self.signals = GUI.WorkerSignals()

        def run(self) -> None:
            heix_images = [i for i in self.src_dir.glob("*.hei[c|f]")]
            image_count = len(heix_images)
            for image_index, image_path in enumerate(heix_images):
                try:
                    image = HEIX(image_path)
                except (OSError, ValueError):
                    pass
                else:
                    image.save_as(self.dst_dir, self.format)
                self.signals.progress.emit(
                    int(100 * image_index / image_count)
                )
                sleep(randint(1, 5) / 10)
            self.signals.finished.emit()

    def __init__(self, *args):
        self.app = QApplication(list(args))
        self.main_win = QMainWindow()
        self.main_win.setWindowTitle("HEIX Converter")
        self.main_win.setMinimumSize(320, 320)
        self.frame = QFrame(parent=self.main_win)
        self.layout = QVBoxLayout(self.frame)
        self.status_bar = self.main_win.statusBar()
        self.src_dir: Path | None = None
        self.dst_dir: Path | None = None
        self.thread_pool = QThreadPool()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.src_dir_button = GUI.EPushButton(self.frame)
        self.src_dir_button.setText("Source Directory")
        self.src_dir_label = QLabel(parent=self.frame)
        self.src_selector = QFileDialog(self.frame)

        self.dst_dir_button = GUI.EPushButton(self.frame)
        self.dst_dir_button.setText("Save To")
        self.dst_dir_label = QLabel(parent=self.frame)
        self.dst_selector = QFileDialog(self.frame)

        format_frame = QFrame(self.main_win)
        hlayout = QHBoxLayout(format_frame)
        self.format_label = QLabel(format_frame)
        self.format_label.setText("Select format")
        self.format_cbox = QComboBox(format_frame)
        self.format_cbox.addItems(HEIX.SupportedFormats.keys())
        hlayout.addWidget(self.format_label)
        hlayout.addWidget(self.format_cbox)

        accept_frame = QFrame(self.main_win)
        hlayout = QHBoxLayout(accept_frame)
        self.start_button = QPushButton(accept_frame)
        self.start_button.setText("Start")
        self.clear_button = QPushButton(accept_frame)
        self.clear_button.setText("Clear")
        self.exit_button = QPushButton(accept_frame)
        self.exit_button.setText("Exit")

        hlayout.addWidget(self.start_button)
        hlayout.addWidget(self.clear_button)
        hlayout.addWidget(self.exit_button)

        # add widgets to layout
        self.layout.addWidget(self.src_dir_button)
        self.layout.addWidget(self.src_dir_label)
        self.layout.addWidget(self.dst_dir_button)
        self.layout.addWidget(self.dst_dir_label)
        self.layout.addWidget(format_frame)
        self.layout.addWidget(accept_frame)
        self.layout.setSpacing(10)

        # signals & slots
        self.src_dir_button.clicked.connect(self.on_src_dir_button_clicked)
        self.dst_dir_button.clicked.connect(self.on_dst_dir_button_clicked)
        self.clear_button.clicked.connect(self.on_clear_button_clicked)
        self.exit_button.clicked.connect(self.on_exit_button_clicked)
        self.start_button.clicked.connect(self.on_start_button_clicked)

        # make main frame the central widget of the main window
        self.main_win.setCentralWidget(self.frame)
        self.update_src_dir_label()
        self.update_dst_dir_label()
        self.main_win.show()

    def update_src_dir_label(self):
        visible_chars = int(
            self.src_dir_label.width() / self.src_dir_label.fontMetrics().averageCharWidth()
        )
        if len(str(self.src_dir)) > visible_chars:
            text = self.src_dir.name
        else:
            text = str(self.src_dir)
        self.src_dir_label.setText(
            f"Selected: {text}"
        )

    def update_dst_dir_label(self):
        visible_chars = int(
            self.dst_dir_label.width() / self.dst_dir_label.fontMetrics().averageCharWidth()
        )
        if len(str(self.dst_dir)) > visible_chars:
            text = self.dst_dir.name
        else:
            text = str(self.dst_dir)
        self.dst_dir_label.setText(
            f"Selected: {text}"
        )

    def on_src_dir_button_clicked(self):
        selected_dir = QFileDialog.getExistingDirectory(self.main_win)
        if selected_dir:
            self.src_dir = Path(selected_dir)
            self.update_src_dir_label()

    def on_dst_dir_button_clicked(self):
        selected_dir = QFileDialog.getExistingDirectory(self.main_win)
        if selected_dir:
            self.dst_dir = Path(selected_dir)
            self.update_dst_dir_label()

    def on_clear_button_clicked(self):
        self.update_src_dir_label("")
        self.update_dst_dir_label("")

    def on_exit_button_clicked(self):
        self.app.exit(0)

    def on_start_button_clicked(self):
        if self.src_dir is None:
            return self.show_error(
                "Please, select a source directory that contains images!"
            )

        if self.dst_dir is None:
            return self.show_error(
                "Please, select a directory to save converted images to!"
            )
        self.enable_controls(False)
        worker = GUI.Worker(
            self.src_dir, self.dst_dir, self.format_cbox.currentText()
        )
        worker.signals.progress.connect(self.show_progress)
        worker.signals.finished.connect(self.work_done)
        self.thread_pool.start(worker)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Running...")

    def enable_controls(self, enable: bool = True):
        self.start_button.setEnabled(enable)
        self.clear_button.setEnabled(enable)
        self.src_dir_button.setEnabled(enable)
        self.dst_dir_button.setEnabled(enable)
        self.format_cbox.setEnabled(enable)

    def show_error(self, message: str) -> None:
        error = QMessageBox(parent=self.main_win)
        error.setText(message)
        error.show()

    def show_progress(self, progress: int):
        self.progress_bar.setValue(progress)

    def work_done(self):
        self.enable_controls(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Complete!", 10000)

    def run(self):
        self.app.exec()


def main():
    GUI().run()


if __name__ == "__main__":
    main()
