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
    water_pdf = None
    do_enc = False
    user_password = ''
    owner_password = ''
    info = {}
    reader = None

    def __init__(self, reader, dst):
        super().__init__()
        self.reader = reader
        self.dst = dst

    def _add_bookmark(self, writer, bookmarks, parent=None):
        last = None
        for book in bookmarks:
            if isinstance(book, list):
                self._add_bookmark(writer, book, last)
            else:
                last = writer.addBookmarkDict(book, parent)

    def run(self):
        try:
            self.add_watermark_to_pdf()
        except Exception as err:
            self.progress_failed.emit(str(err))

    def add_watermark_to_pdf(self):
        water_reader = PdfFileReader(self.water_pdf)
        water_page = water_reader.getPage(0)

        dest_write = PdfFileWriter()
        for pageNum in range(0, self.reader.numPages):
            self.progress_changed.emit(pageNum + 1, self.reader.numPages)
            pdf_page = self.reader.getPage(pageNum)
            pdf_page.mergePage(water_page)
            dest_write.addPage(pdf_page)

        org_info = self.reader.getDocumentInfo()
        infos = {}
        for k in org_info:
            infos[k] = org_info[k]
            print(k, org_info[k])

        for k in self.info:
            if isinstance(self.info[k], str):
                infos[k] = self.info[k]
        infos['/Creator'] = 'https://github.com/xxNull-lsk/pdf_plus'

        dest_write.addMetadata(infos)
        outlines = self.reader.getOutlines()
        self._add_bookmark(dest_write, outlines)
        with open(self.dst, 'wb') as f:
            dest_write.write(f)

        self.progress_changed.emit(self.reader.numPages + 1, self.reader.numPages)


def app_path():
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWin(QWidget):
    thread = None
    reader = None

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        pm = QPixmap(resource_path('res/app.png'))
        ico = QIcon(pm)
        self.setWindowIcon(ico)

        layout = QGridLayout()
        self.edit_src = QLineEdit()
        self.edit_src.setFixedWidth(240)
        self.edit_src.setPlaceholderText('源文件')
        layout.addWidget(self.edit_src, 0, 0, 1, 2)
        self.button_src = QPushButton("选择源")
        self.button_src.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_src, 0, 2)
        self.edit_src.textChanged.connect(self.on_src_file_changed)

        self.edit_dst = QLineEdit()
        self.edit_dst.setPlaceholderText('目标文件')
        layout.addWidget(self.edit_dst, 1, 0, 1, 2)
        self.button_dst = QPushButton("选择目标")
        self.button_dst.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_dst, 1, 2)

        main_layout.addLayout(layout)

        self.tab = QTabWidget()
        main_layout.addWidget(self.tab)

        self.tab.addTab(self._tab_property(), '基本属性')
        self.tab.addTab(self._tab_water(), '添加水印')
        self.tab.addTab(self._tab_safe(), '安全')

        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.button_add = QPushButton("修改")
        self.button_add.setFixedWidth(120)
        self.button_add.clicked.connect(self.on_add)
        layout.addWidget(self.button_add)
        main_layout.addLayout(layout)

    def on_check_encrypt(self, checked):
        self.edit_user_pwd.setEnabled(self.check_encrypt.isChecked())
        self.edit_user_pwd2.setEnabled(self.check_encrypt.isChecked())
        self.edit_owner_pwd.setEnabled(self.check_encrypt.isChecked())
        self.edit_owner_pwd2.setEnabled(self.check_encrypt.isChecked())
        self.check_128bit.setEnabled(self.check_encrypt.isChecked())

    def _tab_safe(self):
        tab_safe = QWidget()
        layout = QVBoxLayout(tab_safe)
        self.check_encrypt = QCheckBox('加密')
        self.check_encrypt.clicked.connect(self.on_check_encrypt)
        layout.addWidget(self.check_encrypt)

        sub_layout = QVBoxLayout()
        layout.addLayout(sub_layout)
        sub_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        sub_layout.setContentsMargins(24, 0, 0, 0)

        self.edit_user_pwd = QLineEdit()
        self.edit_user_pwd.setEchoMode(QLineEdit.Password)
        self.edit_user_pwd.setPlaceholderText("用户密码")
        sub_layout.addWidget(self.edit_user_pwd)

        self.edit_user_pwd2 = QLineEdit()
        self.edit_user_pwd2.setEchoMode(QLineEdit.Password)
        self.edit_user_pwd2.setPlaceholderText("用户密码(确认)")
        sub_layout.addWidget(self.edit_user_pwd2)

        self.edit_owner_pwd = QLineEdit()
        self.edit_owner_pwd.setEchoMode(QLineEdit.Password)
        self.edit_owner_pwd.setPlaceholderText("所有者密码")
        sub_layout.addWidget(self.edit_owner_pwd)

        self.edit_owner_pwd2 = QLineEdit()
        self.edit_owner_pwd2.setEchoMode(QLineEdit.Password)
        self.edit_owner_pwd2.setPlaceholderText("所有者密码(确认)")
        sub_layout.addWidget(self.edit_owner_pwd2)

        self.check_128bit = QCheckBox('128位加密')
        self.check_128bit.setChecked(True)
        sub_layout.addWidget(self.check_128bit)

        self.on_check_encrypt(True)

        return tab_safe

    def _tab_water(self):
        tab_water = QWidget()
        layout = QHBoxLayout(tab_water)
        self.edit_water = QLineEdit()
        self.edit_water.setPlaceholderText('水印文件')
        layout.addWidget(self.edit_water)
        self.button_water = QPushButton("选择水印")
        self.button_water.clicked.connect(self.on_select_file)
        layout.addWidget(self.button_water)
        return tab_water

    def _tab_property(self):
        tab_property = QWidget()
        layout = QVBoxLayout(tab_property)
        self.edit_producer = QLineEdit("PDF_Forge")
        self.edit_producer.setPlaceholderText("制作工具")
        layout.addWidget(self.edit_producer)

        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("标题")
        self.edit_title.setToolTip("标题")
        layout.addWidget(self.edit_title)

        self.edit_author = QLineEdit()
        self.edit_author.setPlaceholderText("作者")
        self.edit_author.setToolTip("作者")
        layout.addWidget(self.edit_author)

        self.edit_subject = QLineEdit()
        self.edit_subject.setPlaceholderText("主题")
        self.edit_subject.setToolTip("主题")
        layout.addWidget(self.edit_subject)
        return tab_property

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
            self.tab.setEnabled(True)
            QMessageBox.information(self, "Information", "处理完成")
            cmd = 'explorer /e,/select,{}'.format(os.path.abspath(self.edit_dst.text()))
            os.system(cmd)
        else:
            self.progress.setValue(curr * 1000 / total)

    def on_progress_failed(self, err):
        self.button_add.setEnabled(True)
        self.edit_dst.setEnabled(True)
        self.edit_src.setEnabled(True)
        self.button_dst.setEnabled(True)
        self.button_src.setEnabled(True)
        self.tab.setEnabled(True)
        QMessageBox.critical(self, "Error", "添加失败，原因：\n{}".format(err))

    def on_add(self):
        if self.edit_user_pwd.text() != self.edit_user_pwd2.text():
            QMessageBox.critical(self, "错误", '用户密码不一致！')
            return
        if self.edit_owner_pwd.text() != self.edit_owner_pwd2.text():
            QMessageBox.critical(self, "错误", '所有者密码不一致！')
            return
        if self.edit_src.text() == '' or self.reader is None:
            QMessageBox.critical(self, "错误", '源文件打开失败！')
            return
        if self.edit_dst.text() == '':
            QMessageBox.critical(self, "错误", '请设置输出文件！')
            self.edit_dst.setFocus()
            return
        self.thread = QWorkThread(self.reader, self.edit_dst.text())
        self.thread.water_pdf = self.edit_water.text()

        self.thread.info['/Title'] = self.edit_title
        self.thread.info['/Author'] = self.edit_author
        self.thread.info['/Subject'] = self.edit_subject
        self.thread.info['/Producer'] = self.edit_producer

        self.thread.do_enc = self.check_encrypt.isChecked()
        self.thread.user_password = self.edit_user_pwd.text()
        self.thread.owner_password = self.edit_owner_pwd.text()

        self.thread.progress_changed.connect(self.on_progress_changed)
        self.thread.progress_failed.connect(self.on_progress_failed)
        self.thread.start()
        self.tab.setEnabled(False)
        self.button_add.setEnabled(False)
        self.edit_dst.setEnabled(False)
        self.edit_src.setEnabled(False)
        self.button_dst.setEnabled(False)
        self.button_src.setEnabled(False)

    def on_src_file_changed(self, txt):
        if not os.path.exists(txt):
            return
        self.reader = PdfFileReader(txt)
        if self.reader.isEncrypted:
            password, ok = QInputDialog.getText(self, "警告", '该文件已经加密', QLineEdit.Password)
            if not ok:
                self.edit_src = ''
                return
            if self.reader.decrypt(password) == 0:
                QMessageBox.critical(self, "错误", '密码错误！')
                self.edit_src = ''
                return
        doc = self.reader.getDocumentInfo()
        self.edit_producer.setText(doc.producer)
        self.edit_author.setText(doc.author)
        self.edit_title.setText(doc.title)
        self.edit_subject.setText(doc.subject)


def main():
    app = QApplication(sys.argv)
    wnd = MainWin()

    wnd.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
