import os
import pathlib

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtWidgets as QtW
import openpyxl

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
        # self.file_list.itemClicked.connect(self.file_clicked)
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
        files_to_compare = [k for k, v in self.files_checked_dict.items() if v]

        if len(files_to_compare) < 2:
            self.memo.setText("Select at least 2 files to compare")
            return

        path = pathlib.Path(self.directory_path)
        sheets = [openpyxl.load_workbook(path / x).active for x in files_to_compare]
        sheets = [x for x in sheets if x is not None]

        max_row = max([x.max_row for x in sheets])
        max_col = max([x.max_column for x in sheets])

        result_text = ""

        for row_n in range(1, max_row - 1):
            sheet_rows = []
            for sheet in sheets:
                sheet_row = []
                for col_n in range(1, max_col - 1):
                    sheet_row.append(sheet.cell(row=row_n, column=col_n).value)
                sheet_rows.append(sheet_row)

            all_same = True
            for col_idx in range(max_col):
                col_set = set()
                for sheet_row in sheet_rows:
                    if col_idx < len(sheet_row):
                        col_set.add(sheet_row[col_idx])
                if len(col_set) > 1:
                    all_same = False
                    break

            if not all_same:
                result_text += f"\n\nRow {row_n}:"
                for sheet_row in sheet_rows:
                    result_text += f"\n{sheet_row}"

        self.memo.setText(result_text)

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
