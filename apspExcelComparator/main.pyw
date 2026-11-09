import os
import pathlib

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW

_PATH = pathlib.Path(__file__).parent
_LAST_PATH_FILE = "last_path.txt"

_CHECKED = QtC.Qt.Checked
_UNCHECKED = QtC.Qt.Unchecked

class MainWindow(QtW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("apspExcelComparator")

        self.directory_path: str = ""
        self.files_checked_dict: dict[str, bool] = {}

        main_layout = QtW.QHBoxLayout()

        side_container = QtW.QWidget()
        side_layout = QtW.QVBoxLayout()
        side_layout.setContentsMargins(0, 0, 0, 0)

        button_change_dir = QtW.QPushButton("Change directory...")
        button_change_dir.setIcon(self.style().standardIcon(QtW.QStyle.SP_DirLinkIcon))
        button_change_dir.clicked.connect(self.button_change_dir_clicked)
        side_layout.addWidget(button_change_dir)

        self.file_list = QtW.QListWidget()
        #self.file_list.itemClicked.connect(self.file_clicked)
        self.file_list.itemDoubleClicked.connect(self.file_clicked)
        side_layout.addWidget(self.file_list)

        side_container.setLayout(side_layout)
        side_container.setFixedWidth(256)
        main_layout.addWidget(side_container)

        self.memo = QtW.QTextEdit()
        self.memo.setReadOnly(True)
        main_layout.addWidget(self.memo)

        main_container = QtW.QWidget()
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)
        self.setMinimumSize(640, 480)

        # Load directory from previous session, if any
        last_path_path = _PATH / _LAST_PATH_FILE
        if last_path_path.exists():
            with open(last_path_path, "r", encoding="utf-8") as f_in:
                possible_path = pathlib.Path(f_in.read())
                if possible_path.exists():
                    self.directory_path = str(possible_path)
                    self.file_list_refresh()

    def refresh_memo(self):
        self.memo.setText(str(self.files_checked_dict))

    def file_clicked(self, item: QtW.QListWidgetItem):
        was_checked = item.checkState() == _CHECKED
        item.setCheckState(_UNCHECKED if was_checked else _CHECKED)
        self.files_checked_dict[item.text()] = not was_checked
        self.refresh_memo()

    def file_list_refresh(self):
        file_names = [f for f in os.listdir(self.directory_path) if f.endswith(".xlsx")]
        self.file_list.clear()
        self.files_checked_dict.clear()
        for file_name in file_names:
            item = QtW.QListWidgetItem(file_name)
            item.setFlags(QtC.Qt.ItemIsEnabled)
            item.setCheckState(_UNCHECKED)
            self.file_list.addItem(item)
            self.files_checked_dict[file_name] = False

    def button_change_dir_clicked(self):
        dialog = QtW.QFileDialog(self)
        possible_directory_path = dialog.getExistingDirectory(dir=self.directory_path)
        if not os.path.exists(possible_directory_path):
            return
        self.directory_path = possible_directory_path
        self.file_list_refresh()
        with open(_PATH / _LAST_PATH_FILE, "w", encoding="utf-8") as f_out:
            f_out.write(self.directory_path)

    def button_reveal_dir_clicked(self):
        QtG.QDesktopServices.openUrl(QtC.QUrl.fromLocalFile(self.directory_path))

if __name__ == "__main__":
    app = QtW.QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
