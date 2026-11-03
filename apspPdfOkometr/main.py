import os
import pathlib

import PySide6.QtCore as QtC
import PySide6.QtGui as QtG
import PySide6.QtPdf as QtP
import PySide6.QtPdfWidgets as QtPW
import PySide6.QtWidgets as QtW

_PATH = pathlib.Path(__file__).parent
_LAST_PATH_FILE = "last_path.txt"


class MainWindow(QtW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("apspPdfOkometr")

        self.directory_path: str = ""
        self.file_name = ""

        main_layout = QtW.QHBoxLayout()

        # Side container for the 'open directory' button and the file table
        side_container = QtW.QWidget()  # Side layout must be wrapped in a widget to add it to the main layout
        side_layout = QtW.QVBoxLayout()
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_container.setLayout(side_layout)
        side_container.setFixedWidth(256)

        button_change_dir = QtW.QPushButton("Open directory...")
        button_change_dir.clicked.connect(self.button_change_dir_clicked)
        side_layout.addWidget(button_change_dir)

        self.table_files = QtW.QTableWidget()
        self.table_files.setEditTriggers(QtW.QAbstractItemView.EditTrigger.NoEditTriggers)  # Read-only cells
        self.table_files.cellClicked.connect(self.table_files_cell_clicked)  # Click to show said file
        self.table_files.setFocusPolicy(QtC.Qt.FocusPolicy.NoFocus)  # No tab/arrow keys to change the selection
        side_layout.addWidget(self.table_files)

        main_layout.addWidget(side_container)

        # Main star of the show: Pdf viewer
        self.pdf_document = QtP.QPdfDocument()
        pdf_view = QtPW.QPdfView(self)
        pdf_view.setDocument(self.pdf_document)

        main_layout.addWidget(pdf_view)

        # Main layout must be wrapped in a widget to "assign" it to a window
        main_container = QtW.QWidget()
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        # Keyboard shortcuts
        # - Enter to switch between 'A' and 'B' documents
        file_switch_shortcut = QtG.QShortcut(self)
        file_switch_shortcut.setKeys([
            QtG.QKeySequence(QtC.Qt.Key.Key_Return),
            QtG.QKeySequence(QtC.Qt.Key.Key_Enter),
        ])
        file_switch_shortcut.activated.connect(self.file_switch)

        self.showMaximized()

        # Load directory from previous session, if any
        last_path_path = _PATH / _LAST_PATH_FILE
        if last_path_path.exists():
            with open(last_path_path, "r", encoding="utf-8") as f_in:
                possible_path = pathlib.Path(f_in.read())
                if possible_path.exists():
                    self.directory_path = str(possible_path)
                    self.table_refresh()

    def file_switch(self):
        if self.file_name[0] == "A":
            self.file_name = "B" + self.file_name[1:]
        elif self.file_name[0] == "B":
            self.file_name = "A" + self.file_name[1:]
        self.file_show()

    def file_show(self):
        """Show PDF file in the viewer according to `self.directory_path` and `self.file_name`."""
        file_path = os.path.join(self.directory_path, self.file_name)
        self.pdf_document.load(file_path)

    def button_change_dir_clicked(self):
        """Show dialog for user to choose a folder, refresh table
        with files from chosen folder, save path for next session."""
        dialog = QtW.QFileDialog(self)
        possible_directory_path = dialog.getExistingDirectory()

        if not os.path.exists(possible_directory_path):
            return

        self.directory_path = possible_directory_path
        self.table_refresh()
        with open(_PATH / _LAST_PATH_FILE, "w", encoding="utf-8") as f_out:
            f_out.write(self.directory_path)

    def table_files_cell_clicked(self, row, column):
        """User clicks on a file in the table, show it in the PDF viewer."""
        item = self.table_files.item(row, column)
        if item is not None:
            item_text = item.text()
            letter = "A" if column == 0 else "B"
            self.file_name = letter + item_text
            self.file_show()

    def table_refresh(self):
        """Refresh table with the files from `self.directory_path`."""
        file_names = [f for f in os.listdir(self.directory_path) if f.endswith(".pdf")]

        file_names_a = set()
        file_names_b = set()
        for file_name in file_names:
            if file_name[0] == "A":
                file_names_a.add(file_name[1:])
            elif file_name[0] == "B":
                file_names_b.add(file_name[1:])

        file_names_both = file_names_a.intersection(file_names_b)
        file_names_only_a = file_names_a.difference(file_names_both)
        file_names_only_b = file_names_b.difference(file_names_both)
        n_rows = len(file_names_both) + len(file_names_only_a) + len(file_names_only_b)

        self.table_files.reset()
        horizontal_header_labels = ["A", "B"]
        self.table_files.setColumnCount(len(horizontal_header_labels))
        self.table_files.setHorizontalHeaderLabels(horizontal_header_labels)
        self.table_files.setRowCount(n_rows)

        row_n = 0
        for file_name in file_names_both:
            self.table_files.setItem(row_n, 0, QtW.QTableWidgetItem(str(file_name)))
            self.table_files.setItem(row_n, 1, QtW.QTableWidgetItem(str(file_name)))
            row_n += 1

        for file_name in file_names_only_a:
            self.table_files.setItem(row_n, 0, QtW.QTableWidgetItem(str(file_name)))
            row_n += 1

        for file_name in file_names_only_b:
            self.table_files.setItem(row_n, 1, QtW.QTableWidgetItem(str(file_name)))
            row_n += 1


if __name__ == "__main__":
    app = QtW.QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
