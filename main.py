import os, sys, subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QListWidget, QPushButton, QFileDialog, \
    QListWidgetItem, QAbstractItemView, QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtGui import QPixmap

#audio sync
import numpy as np
import scipy.signal as signal
import soundfile as sf

class ImageQuestionDialog(QDialog):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Verification")

        image_file = "frame.jpg"

        # ffmpeg -ss00:00:05 - i input.mp4 - frames: v 1 frame.jpg
        command = [
            "ffmpeg", "-y",  # -y overwrites the output file if it exists
            "-noautorotate",
            "-ss", "00:00:05",  # capture 5 seconds in
            "-i", video_path,  # Input video first
            "-frames:v", "1",  # Stream copy (no re-encoding)
            image_file
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Successfully created: {image_file}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")

        # 1. Create a layout for the popup
        layout = QVBoxLayout(self)

        # 2. Add the Image via QLabel
        self.image_label = QLabel(self)
        pixmap = QPixmap(image_file)

        # Optional: Scale the image to fit nicely if it's too large
        scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # 3. Add the question label
        self.question_label = QLabel("Is this image inverted?", self)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.question_label)

        # 4. Add standard Yes/No buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No,
            self
        )
        self.button_box.accepted.connect(self.accept)  # Maps Yes to accept
        self.button_box.rejected.connect(self.reject)  # Maps No to reject
        layout.addWidget(self.button_box)

        # 3. Clean up the temporary text file
        if os.path.exists(image_file):
            os.remove(image_file)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        self.vid1_ListWgt = QListWidget()
        vid1_GetBtn = QPushButton("Get Vid 1 files")
        self.vid2_ListWgt = QListWidget()
        vid2_GetBtn = QPushButton("Get Vid 2 files")
        self.vid3_ListWgt = QListWidget()
        vid3_GetBtn = QPushButton("Get Vid 3 files")
        self.vid4_ListWgt = QListWidget()
        vid4_GetBtn = QPushButton("Get Vid 4 files")

        # 2. Enabling drag-and-drop internal reordering
        self.vid1_ListWgt.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.vid2_ListWgt.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.vid3_ListWgt.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.vid4_ListWgt.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)


        combineVidsBtn = QPushButton("Combine Vids")
        layout = QGridLayout()

        vid1_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(1, self.vid1_ListWgt))
        vid2_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(2, self.vid2_ListWgt))
        vid3_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(3, self.vid3_ListWgt))
        vid4_GetBtn.pressed.connect(lambda: self.get_vid_files_dialog(4, self.vid4_ListWgt))

        combineVidsBtn.pressed.connect(self.combine_vids)

        layout.addWidget(self.vid1_ListWgt, 0, 0)
        layout.addWidget(self.vid2_ListWgt, 0, 1)
        layout.addWidget(vid1_GetBtn, 1, 0)
        layout.addWidget(vid2_GetBtn, 1, 1)
        layout.addWidget(self.vid3_ListWgt, 2, 0)
        layout.addWidget(self.vid4_ListWgt, 2, 1)
        layout.addWidget(vid3_GetBtn, 3, 0)
        layout.addWidget(vid4_GetBtn, 3, 1)
        layout.addWidget(combineVidsBtn, 4, 0, 1, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_vid_files_dialog(self, ref, list_widget):

        #test if previous list_widget has files
        if ref > 1:
            if self.vid1_ListWgt.count() == 0:
                print("fill list 1 first")
                return
        if ref > 2:
            if self.vid2_ListWgt.count() == 0:
                print("fill list 2 before 3")
                return
        if ref > 3:
            if self.vid3_ListWgt.count() == 0:
                print("fill list 3 before 4")
                return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "video (*.mp4 *.mov);;Python Files (*.py)"
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
        #define concated video names
        vid_concated_list = ["vid1Concat.mp4", "vid2Concat.mp4", "vid3Concat.mp4", "vid4Concat.mp4"]
        vidInverted= [0, 0, 0, 0]
        self.vidPresent = [False, False, False, False]  # this defines which videos are present for future use

        if self.vid1_ListWgt.count() > 0:
            self.vidPresent[0] = True
            item = self.vid1_ListWgt.item(0)
            vid_path = item.data(Qt.ItemDataRole.UserRole)
            popup = ImageQuestionDialog(vid_path, self)
            vidInverted[0] = popup.exec()
        if self.vid2_ListWgt.count() > 0:
            self.vidPresent[1] = True
            item = self.vid2_ListWgt.item(0)
            vid_path = item.data(Qt.ItemDataRole.UserRole)
            popup = ImageQuestionDialog(vid_path, self)
            vidInverted[1] = popup.exec()
        if self.vid3_ListWgt.count() > 0:
            self.vidPresent[2] = True
            item = self.vid3_ListWgt.item(0)
            vid_path = item.data(Qt.ItemDataRole.UserRole)
            popup = ImageQuestionDialog(vid_path, self)
            vidInverted[2] = popup.exec()
        if self.vid4_ListWgt.count() > 0:
            self.vidPresent[3] = True
            item = self.vid4_ListWgt.item(0)
            vid_path = item.data(Qt.ItemDataRole.UserRole)
            popup = ImageQuestionDialog(vid_path, self)
            vidInverted[4] = popup.exec()

        print(f"inv {vidInverted}")

        vid_list = []
        if self.vid1_ListWgt.count() > 0: #todo maybe just rename in case just on file?
            for i in range(self.vid1_ListWgt.count()):
                item = self.vid1_ListWgt.item(i)
                # Extract the custom data
                hidden_data = item.data(Qt.ItemDataRole.UserRole)
                vid_list.append(hidden_data)
            self.concat_vids(vid_list, output_filename=vid_concated_list[0])

        vid_list = []
        if self.vid2_ListWgt.count() > 0:
            for i in range(self.vid2_ListWgt.count()):
                item = self.vid2_ListWgt.item(i)
                # Extract the custom data
                hidden_data = item.data(Qt.ItemDataRole.UserRole)
                vid_list.append(hidden_data)
            self.concat_vids(vid_list, output_filename=vid_concated_list[1])

        vid_list = []
        if self.vid3_ListWgt.count() > 0:
            for i in range(self.vid3_ListWgt.count()):
                item = self.vid3_ListWgt.item(i)
                # Extract the custom data
                hidden_data = item.data(Qt.ItemDataRole.UserRole)
                vid_list.append(hidden_data)
            self.concat_vids(vid_list, output_filename=vid_concated_list[2])

        vid_list = []
        if self.vid4_ListWgt.count() > 0:
            for i in range(self.vid4_ListWgt.count()):
                item = self.vid4_ListWgt.item(i)
                # Extract the custom data
                hidden_data = item.data(Qt.ItemDataRole.UserRole)
                vid_list.append(hidden_data)
            self.concat_vids(vid_list, output_filename=vid_concated_list[3])

        #todo use self.vidPresent to determine output =of MPV
        self.mvp_SBSvid_run(vid_concated_list, vFlip=vidInverted)

    def mvp_SBSvid_run(self, video_list, vFlip=[0,0,0,0]):
        print("mvp_SBSvid_run")
        # orientation 1 - 2
        print(video_list)
        #find offset
        offset_sec = self.vid_offset(video_list)
        print(f"offset mvp:{offset_sec}")

        #Construct command to compile video
        commandS = "mpv "
        commandS += f"{video_list[0]} "
        commandS += f"--external-file={video_list[1]} "

        commandS += f"--lavfi-complex="
        commandS += f"[vid1]{self.lavfi_filt(offset_sec[0], vFlip[0])}[vid1a];" #apply null filter to keep naming convention the same
        commandS += f"[vid2]{self.lavfi_filt(offset_sec[1], vFlip[1])}[vid2a];"
        commandS += "[vid1a][vid2a]hstack[vo]"

        print(commandS)

        try:
            subprocess.run(commandS, check=True)
            print(f"Successfully ran")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        finally:
            # 3. Clean up the temporary vid files
            pass

    def lavfi_filt(self, timeOffset, rot180):
        print("lavfi_filt")
        filtStr = "null,"
        if timeOffset != 0:
            filtStr = f"setpts=PTS+{timeOffset}/TB,"
        if rot180:
            filtStr = "hflip,vflip,"
        return filtStr[:-1] #remove the last comma

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
        print(command)

        try:
            subprocess.run(command, check=True)
            print(f"Successfully created: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        finally:
            # 3. Clean up the temporary text file
            if os.path.exists(temp_txt_file):
                os.remove(temp_txt_file)

    def vid_offset(self, video_list):
        print("vid_offset")
        offset_sec = [0.0, 0.0, 0.0, 0.0]
        print(self.vidPresent)
        #create an audio file for sync for each video in list
        for index, vidPresent in enumerate(self.vidPresent):
            print(f"vid present: {index}")
            if vidPresent:
                print(f"time sync {video_list[index]}")
                abs_path = os.path.abspath(video_list[index])
                # 2. Build and run the FFmpeg command
                command = [
                    "ffmpeg", "-y",  # -y overwrites the output file if it exists
                    "-i", f"{abs_path}",  # Use the concat demuxer
                    "-safe", "0",  # Allows absolute file paths
                    "-vn",
                    "-t", "60",  # only the first 60 seconds of the file for time sync
                    f"{video_list[index]}.wav"
                ]
                try:
                    subprocess.run(command, check=True)
                    print(f"Successfully created: {video_list[index]}.wav")
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred: {e}")
                print(f"index: {index}")
                if index > 0:
                    Lag_samples, offset_secOne = self.find_audio_offset(f"{video_list[0]}.wav", f"{video_list[index]}.wav")
                    print("test2")
                    offset_sec[index] = float(offset_secOne)
                    print("test3")
        print('end of video offset')
        print(offset_sec)

        #remove wave files used for offset check
        for video in video_list:
            if os.path.exists(f"{video}.wav"):
                os.remove(f"{video}.wav")

        return offset_sec

    def find_audio_offset(self, file1_path, file2_path):
        """
        Finds the time offset of file2 relative to file1.
        A positive offset means file2 starts LATER than file1.
        A negative offset means file2 starts EARLIER than file1.
        """
        print("audio offset1")
        # Load audio files
        data1, sr1 = sf.read(file1_path)
        data2, sr2 = sf.read(file2_path)

        print("audio offset2")
        # 1. Verification: Sample rates must match
        if sr1 != sr2:
            raise ValueError(f"Sample rates do not match! File 1: {sr1}Hz, File 2: {sr2}Hz. Resample them first.")

        # 2. Convert to Mono if stereo (average the channels)
        if len(data1.shape) > 1: data1 = np.mean(data1, axis=1)
        if len(data2.shape) > 1: data2 = np.mean(data2, axis=1)

        # 3. Compute cross-correlation using fast FFT convolution
        # Flipping data2 effectively turns convolution into cross-correlation
        correlation = signal.fftconvolve(data1, data2[::-1], mode='full')
        lags = signal.correlation_lags(len(data1), len(data2), mode='full')

        # 4. Find the peak of correlation
        best_lag_idx = np.argmax(np.abs(correlation))
        sample_lag = lags[best_lag_idx]

        # 5. Convert sample lag to seconds
        offset_seconds = sample_lag / sr1

        print(f"--- Alignment Results ---")
        print(f"Sample Lag: {sample_lag:+} samples")
        print(f"Time Offset: {offset_seconds:+.4f} seconds")

        return sample_lag, offset_seconds


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
