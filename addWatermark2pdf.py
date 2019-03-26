# -*- coding: utf-8 -*-
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QWorkThread(QThread):
    progress_changed = pyqtSignal(int, int)
    progress_failed = pyqtSignal(str)

    def __init__(self, src, dst, water):
        super().__init__()
        self.src = src
        self.dst = dst
        self.water = water

    def _add_bookmark(self, writer, bookmarks, parent=None):
        last = None
        for book in bookmarks:
            if isinstance(book, list):
                self._add_bookmark(writer, book, last)
            else:
                last = writer.addBookmarkDict(book, parent)

    def run(self):
        try:
            self.add_watermark_to_pdf(self.src, self.dst, self.water)
        except Exception as err:
            self.progress_failed.emit(str(err))

    def add_watermark_to_pdf(self, src, dst, water):
        file_src = open(water, 'rb')
        water_reader = PdfFileReader(file_src)
        water_page = water_reader.getPage(0)

        source_reader = PdfFileReader(open(src, 'rb'))
        dest_write = PdfFileWriter()
        for pageNum in range(0, source_reader.numPages):
            self.progress_changed.emit(pageNum + 1, source_reader.numPages)
            pdf_page = source_reader.getPage(pageNum)
            pdf_page.mergePage(water_page)
            dest_write.addPage(pdf_page)

        org_info = water_reader.getDocumentInfo()
        infos = {}
        for k in org_info:
            infos[k] = org_info[k]
            print(k, org_info[k])

        infos['/Producer'] = 'LiuShengKun'
        infos['/Title'] = os.path.basename(src)
        dest_write.addMetadata(infos)
        outlines = source_reader.getOutlines()
        self._add_bookmark(dest_write, outlines)
        with open(dst, 'wb') as f:
            dest_write.write(f)

        file_src.close()
        self.progress_changed.emit(source_reader.numPages + 1, source_reader.numPages)


class MainWin(QWidget):
    thread = None

    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)

        pm = QPixmap('./res/app.png')
        ico = QIcon(pm)
        self.setWindowIcon(ico)

        self.edit_src = QLineEdit()
        self.edit_src.setFixedWidth(240)
        self.edit_src.setPlaceholderText('源文件')
        layout.addWidget(self.edit_src, 0, 0, 1, 2)
        self.button_src = QPushButton("选择源")
        self.button_src.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_src, 0, 2)

        self.edit_water = QLineEdit()
        self.edit_water.setPlaceholderText('水印文件')
        layout.addWidget(self.edit_water, 1, 0, 1, 2)
        self.button_water = QPushButton("选择水印")
        self.button_water.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_water, 1, 2)

        self.edit_dst = QLineEdit()
        self.edit_dst.setPlaceholderText('目标文件')
        layout.addWidget(self.edit_dst, 2, 0, 1, 2)
        self.button_dst = QPushButton("选择目标")
        self.button_dst.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_dst, 2, 2)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        layout.addWidget(self.progress, 3, 0, 1, 3)

        self.button_add = QPushButton("添加")
        self.button_add.clicked.connect(self.on_add)
        layout.addWidget(self.button_add, 4, 1)

    def on_select_file(self):
        if self.sender() == self.button_dst:
            f = QFileDialog.getSaveFileName(self)
        else:
            f = QFileDialog.getOpenFileNames(self)
        if f is None or len(f) == 0:
            return
        if self.sender() == self.button_src:
            self.edit_src.setText(f[0][0])
        elif self.sender() == self.button_dst:
            self.edit_dst.setText(f[0])
        elif self.sender() == self.button_water:
            self.edit_water.setText(f[0][0])

    def on_progress_changed(self, curr, total):
        if curr > total:
            self.button_add.setEnabled(True)
            self.edit_dst.setEnabled(True)
            self.edit_src.setEnabled(True)
            self.edit_water.setEnabled(True)
            self.button_dst.setEnabled(True)
            self.button_water.setEnabled(True)
            self.button_src.setEnabled(True)
            QMessageBox.information(self, "Information", "成功添加水印")
        else:
            self.progress.setValue(curr * 1000 / total)

    def on_progress_failed(self, err):
        self.button_add.setEnabled(True)
        self.edit_dst.setEnabled(True)
        self.edit_src.setEnabled(True)
        self.edit_water.setEnabled(True)
        self.button_dst.setEnabled(True)
        self.button_water.setEnabled(True)
        self.button_src.setEnabled(True)
        QMessageBox.critical(self, "Error", "添加失败，原因：\n{}".format(err))

    def on_add(self):
        self.thread = QWorkThread(self.edit_src.text(), self.edit_dst.text(), self.edit_water.text())
        self.thread.progress_changed.connect(self.on_progress_changed)
        self.thread.progress_failed.connect(self.on_progress_failed)
        self.thread.start()
        self.button_add.setEnabled(False)
        self.edit_dst.setEnabled(False)
        self.edit_src.setEnabled(False)
        self.edit_water.setEnabled(False)
        self.button_dst.setEnabled(False)
        self.button_water.setEnabled(False)
        self.button_src.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    wnd = MainWin()

    wnd.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
