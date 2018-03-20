from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import FTPClient_
import os
from MainWindow import Ui_MainWindow

PASSWORD_MODE = 2
NORMAL_MODE = 0

POSSIBLE_CLIENT_OPERATIONS = ['', 'List', 'Upload', 'Download', 'Move', 'Delete']
POSSIBLE_OPERATIONS_ACTION = {'': 0, 'List': 1, 'Upload': 2, 'Download': 3, 'Move': 4, 'Delete': 5}


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.show()
        self._server_message = ''
        self._ftp_client = FTPClient_.FTPclient()
        self._userAction = ''
        self._download_path = ''
        self._uploadFile = ''
        self._loggedIn = False
        # Setting up check list
        self.cb_show_password.setChecked(False)
        self.pb_upload.setValue(0)
        self.pb_download.setValue(0)

        # Setting Up the labels
        f = self.lb_ftp_server_address.font()
        f.setPointSize(8)
        self.lb_password.setFont(f)
        self.lb_username.setFont(f)
        self.lb_ftp_server_address.setFont(f)
        self.lb_server_response.setFont(f)
        self.lb_action.setFont(f)
        self.lb_movepath.setFont(f)
        self.lb_upload_path.setFont(f)
        self.lb_filename.setFont(f)
        self.lb_create_file.setFont(f)
        self.lb_delete_directory.setFont(f)

        # Setting up line edits (User Input textbox)
        self.le_ftp_server_address.setPlaceholderText('i.e ftp.mirror.ac.za')
        self.le_username.setPlaceholderText('hint: Your account username')
        self.le_password.setPlaceholderText('hint: Your account password')
        self.le_move.setPlaceholderText('hint: /home/documents')
        self.le_password.setEchoMode(PASSWORD_MODE)  # Hides the text

        # Setting up Combo Box
        self.comboBox_userAction.addItems(POSSIBLE_CLIENT_OPERATIONS)

        # Handling events
        self.btn_connect.pressed.connect(self.btn_connect_handler)
        self.btn_disconnect.pressed.connect(self.btn_disconnect_handler)
        self.cb_show_password.stateChanged.connect(self.cb_show_password_handler)
        self.comboBox_userAction.currentIndexChanged[str].connect(self.comboBox_userAction_handler)
        self.btn_proceed.pressed.connect(self.btn_proceed_handler)
        self.btn_loadfile.pressed.connect(self.btn_loadfile_handler)
        self.btn_upload.pressed.connect(self.btn_upload_handler)
        self.btn_move.pressed.connect(self.btn_move_handler)
        # self.btn_upload.clicked.connect(self.uploadProgress)
        self.btn_download.pressed.connect(self.btn_download_handler)
        self.btn_saveto.pressed.connect(self.btn_saveto_handler)
        self.btn_create.pressed.connect(self.btn_create_handler)
        self.btn_delete.pressed.connect(self.btn_delete_handler)

    # LOADING TO SERVER HANDLER
    def btn_loadfile_handler(self):
        self._uploadFile, _ = QFileDialog.getOpenFileName(self, 'Open File', '', '', 'All files(*.*)')
        print(self._uploadFile)
        # if filename:
        #     with open(filename, 'rb') as f:
        #         file = f.read()
        #         self._uploadedFile = file
        #         # self.td_server_response.setText(self._uploadedFile)
        # else:
        #     print("No filename")

    def btn_upload_handler(self):
        path = self.le_upload_path.text()
        print(path)

        if self._loggedIn and self._userAction == 'Upload':
            self._ftp_client.stor(str(path), self._uploadFile)
        else:
            print("Cannot Upload")
        self._server_message += self._ftp_client.getServerMessage()
        # self.td_server_response.setText(self._server_message)

    # DOWNLOAD BUTTON HANDLER
    def btn_download_handler(self):
        file_to_download = self.le_download_path.text()

        if self._loggedIn and self._userAction == 'Download':
            self._ftp_client.retr(file_to_download, self._download_path)
        else:
            print('Not logged in')
        self._server_message += self._ftp_client.getServerMessage()

    def btn_saveto_handler(self):
        self._download_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', '', 'All files(*.*)')

    # CONNECTION BUTTONS HANDLERS
    def btn_connect_handler(self):
        ftp_server_address = self.le_ftp_server_address.text()
        username = self.le_username.text()
        password = self.le_password.text()
        if len(ftp_server_address) > 3:
            self._loggedIn = self._ftp_client.login(ftp_server_address, username, password)
            self._server_message = self._ftp_client.getServerMessage()
            self.td_server_response.setText(self._server_message)
            # print(self._server_message)
        else:
            pass

        if self._loggedIn:
            # lock all the inputs for user name and servers.
            self.le_username.setReadOnly(True)
            self.le_password.setReadOnly(True)
            self.le_ftp_server_address.setReadOnly(True)
        else:
            # Handled a failed scenario
            pass

    def btn_disconnect_handler(self):
        if self._loggedIn:
            self._loggedIn = False
            self._ftp_client.quit()
            self._server_message += self._ftp_client.getServerMessage()
            self.td_server_response.setText(self._server_message)
            self.le_username.setReadOnly(False)
            self.le_password.setReadOnly(False)
            self.le_ftp_server_address.setReadOnly(False)
        else:
            pass # Not logged in message

    # RADIO BUTTON HANDLERS
    def cb_show_password_handler(self, s):
        if s == Qt.Checked:
            self.le_password.setEchoMode(NORMAL_MODE)
        else:
            self.le_password.setEchoMode(PASSWORD_MODE)

    # COMBOBOX HANDLER ['':0, 'List':1, 'Upload':2, 'Download':3, 'Move':4, 'Delete':5]
    def comboBox_userAction_handler(self, choice):
        self._userAction = choice

    # PROCEED BUTTON HANDLER
    def btn_proceed_handler(self):
        if self._loggedIn:
            if self._userAction == 'List':
                self._ftp_client.list()
                self._server_message += self._ftp_client.getServerMessage()
                self.td_server_response.setText(self._server_message)
            else:
                print(self._userAction)
        else:
            print("You are not logged in")

    # MOVE BUTTON HANDLER
    def btn_move_handler(self):
        path = self.le_move.text()
        if path == '':
            self._ftp_client.cdup()
        elif self._loggedIn and self._userAction == 'Move':
            self._ftp_client.cwd(path)
        else:
            print("Did not change directories")
        self._server_message += self._ftp_client.getServerMessage()
        self.td_server_response.setText(self._server_message)

    # PROGRESS BAR UPLOAD
    def uploadProgress(self):
        completed = 0
        while completed < 100:
            self.completed += 0.0001
            self.progressBar.setValue(completed)

    # CREATE A FILE
    def btn_create_handler(self):
        filename = self.le_create_file.text()
        self._ftp_client.mkd(filename)

    def btn_delete_handler(self):
        filename = self.le_delete_file.text()
        print(filename)
        self._ftp_client.dele(str(filename))


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    app.exec_()
