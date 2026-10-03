import os, sys, subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QListWidget, QPushButton, QFileDialog, \
    QListWidgetItem, QAbstractItemView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        self.vid1_ListWgt = QListWidget()
        vid1_GetBtn = QPushButton("Get Vid 1 files")
        self.vid2_ListWgt = QListWidget()
        vid2_GetBtn = QPushButton("Get Vid 2 files")
        self.vid3_ListWgt = QListWidget()
        self.vid4_ListWgt = QListWidget()

        # 2. Enabling drag-and-drop internal reordering
        self.vid1_ListWgt.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        combineVidsBtn = QPushButton("Combine Vids")
        layout = QGridLayout()

        vid1_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(self.vid1_ListWgt))
        vid2_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(self.vid2_ListWgt))
        combineVidsBtn.pressed.connect(self.combine_vids)

        layout.addWidget(self.vid1_ListWgt, 0, 0)
        layout.addWidget(vid1_GetBtn, 1, 0)
        layout.addWidget(self.vid2_ListWgt, 0, 1)
        layout.addWidget(vid2_GetBtn, 1, 1)
        layout.addWidget(self.vid3_ListWgt, 2, 0)
        layout.addWidget(self.vid4_ListWgt, 2, 1)
        layout.addWidget(combineVidsBtn, 3, 0)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def get_vid_files_dialog(self, list_widget):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if files:
            list_widget.clear()
            for file_path in files:
                file_name = os.path.basename(file_path)
                item = QListWidgetItem(file_name)
                item.setData(Qt.ItemDataRole.UserRole, file_path) #set the full path
                list_widget.addItem(item)


    def combine_vids(self):
        #get list of vids to concat from list 1
        print("Combine Vids")
        vid_list = []
        for i in range(self.vid1_ListWgt.count()):
            item = self.vid1_ListWgt.item(i)
            # Extract the custom data
            hidden_data = item.data(Qt.ItemDataRole.UserRole)
            vid_list.append(hidden_data)

        print(vid_list)
        self.concat_vids(vid_list)


    def concat_vids(self, video_list, output_filename="output.mp4"):
        print("Concatenating Vids")
        temp_txt_file = "temp_vid_list.txt"

        # 1. Create the text file that FFmpeg needs
        with open(temp_txt_file, "w", encoding="utf-8") as f:
            for video in video_list:
                # Get the absolute path and escape single quotes if necessary
                abs_path = os.path.abspath(video)
                f.write(f"file '{abs_path}'\n")
                print(f"{abs_path}")

        # 2. Build and run the FFmpeg command
        command = [
            "ffmpeg", "-y",  # -y overwrites the output file if it exists
            "-f", "concat",  # Use the concat demuxer
            "-safe", "0",  # Allows absolute file paths
            "-i", temp_txt_file,  # Input text file
            "-c", "copy",  # Stream copy (no re-encoding)
            output_filename
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Successfully created: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        finally:
            # 3. Clean up the temporary text file
            if os.path.exists(temp_txt_file):
                os.remove(temp_txt_file)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

'''
import sys
from PyQt6.QtWidgets import QApplication, QListWidget, QAbstractItemView

app = QApplication(sys.argv)

list_widget = QListWidget()

# 1. Populating the listbox
list_widget.addItems(["Item A", "Item B", "Item C", "Item D"])

# 2. Enabling drag-and-drop internal reordering
list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

# 3. Optional visual cues
list_widget.setDropIndicatorShown(True)  # Shows a line where the item will be dropped
list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

# 4. Optional: Detecting when the order changes
# Connecting a function to the rowsMoved signal of the underlying model
list_widget.model().rowsMoved.connect(lambda: print("List has been reordered!"))

list_widget.show()
sys.exit(app.exec())
'''