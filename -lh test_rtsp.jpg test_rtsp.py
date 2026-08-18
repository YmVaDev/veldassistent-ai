[1mdiff --git a/cameras/static_camera.py b/cameras/static_camera.py[m
[1mindex a1f38b9..d54aad9 100644[m
[1m--- a/cameras/static_camera.py[m
[1m+++ b/cameras/static_camera.py[m
[36m@@ -1,9 +1,11 @@[m
 [m
[31m-import cv2[m
[32m+[m[32mimport subprocess[m
 import time[m
 from pathlib import Path[m
[32m+[m
 from logger import logger[m
 [m
[32m+[m
 class StaticCamera:[m
 [m
     def __init__([m
[36m@@ -24,7 +26,6 @@[m [mclass StaticCamera:[m
         )[m
 [m
         self.running = False[m
[31m-        self.capture = None[m
 [m
     def start(self, callback):[m
 [m
[36m@@ -36,82 +37,85 @@[m [mclass StaticCamera:[m
 [m
         while self.running:[m
 [m
[32m+[m[32m            frame_path = None[m
[32m+[m
             try:[m
 [m
[31m-                self.capture = cv2.VideoCapture([m
[31m-                    self.url,[m
[31m-                    cv2.CAP_FFMPEG,[m
[31m-                    [[m
[31m-                        cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,[m
[31m-                        cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000,[m
[31m-                    ][m
[32m+[m[32m                timestamp = int([m
[32m+[m[32m                    time.time() * 1000[m
                 )[m
 [m
[31m-                if not self.capture.isOpened():[m
[31m-[m
[31m-                    logger.error([m
[31m-                        "Could not open camera stream"[m
[31m-                    )[m
[31m-[m
[31m-                    self.capture.release()[m
[31m-                    self.capture = None[m
[32m+[m[32m                frame_path = ([m
[32m+[m[32m                    self.output_dir[m
[32m+[m[32m                    / f"static_{timestamp}.jpg"[m
[32m+[m[32m                )[m
 [m
[31m-                    continue[m
[32m+[m[32m                command = [[m
[32m+[m[32m                    "ffmpeg",[m
[32m+[m[32m                    "-rtsp_transport",[m
[32m+[m[32m                    "tcp",[m
[32m+[m[32m                    "-i",[m
[32m+[m[32m                    self.url,[m
[32m+[m[32m                    "-frames:v",[m
[32m+[m[32m                    "1",[m
[32m+[m[32m                    "-q:v",[m
[32m+[m[32m                    "2",[m
[32m+[m[32m                    "-y",[m
[32m+[m[32m                    str(frame_path),[m
[32m+[m[32m                ][m
 [m
                 logger.info([m
[31m-                    "Static camera connected"[m
[32m+[m[32m                    "Capturing static camera frame with FFmpeg"[m
                 )[m
 [m
[31m-                while self.running:[m
[31m-[m
[31m-                    success, frame = ([m
[31m-                        self.capture.read()[m
[31m-                    )[m
[32m+[m[32m                result = subprocess.run([m
[32m+[m[32m                    command,[m
[32m+[m[32m                    stdout=subprocess.DEVNULL,[m
[32m+[m[32m                    stderr=subprocess.PIPE,[m
[32m+[m[32m                    text=True,[m
[32m+[m[32m                    timeout=20,[m
[32m+[m[32m                )[m
 [m
[31m-                    if not success:[m
[32m+[m[32m                if result.returncode != 0:[m
 [m
[31m-                        logger.warning([m
[31m-                            "Failed to read camera frame"[m
[31m-                        )[m
[32m+[m[32m                    logger.error([m
[32m+[m[32m                        "FFmpeg failed to capture camera frame: "[m
[32m+[m[32m                        f"{result.stderr[-1000:]}"[m
[32m+[m[32m                    )[m
 [m
[31m-                        break[m
[32m+[m[32m                    if frame_path.exists():[m
[32m+[m[32m                        frame_path.unlink()[m
 [m
[31m-                    timestamp = int([m
[31m-                        time.time() * 1000[m
[31m-                    )[m
[32m+[m[32m                    time.sleep(5)[m
[32m+[m[32m                    continue[m
 [m
[31m-                    frame_path = ([m
[31m-                        self.output_dir[m
[31m-                        / f"static_{timestamp}.jpg"[m
[31m-                    )[m
[32m+[m[32m                if not frame_path.exists():[m
 [m
[31m-                    saved = cv2.imwrite([m
[31m-                        str(frame_path),[m
[31m-                        frame[m
[32m+[m[32m                    logger.error([m
[32m+[m[32m                        "FFmpeg completed but no frame was created"[m
                     )[m
 [m
[31m-                    if not saved:[m
[32m+[m[32m                    time.sleep(5)[m
[32m+[m[32m                    continue[m
 [m
[31m-                        logger.error([m
[31m-                            f"Could not save frame: "[m
[31m-                            f"{frame_path}"[m
[31m-                        )[m
[32m+[m[32m                logger.info([m
[32m+[m[32m                    f"Static camera frame captured: "[m
[32m+[m[32m                    f"{frame_path}"[m
[32m+[m[32m                )[m
 [m
[31m-                        continue[m
[32m+[m[32m                callback([m
[32m+[m[32m                    str(frame_path),[m
[32m+[m[32m                    self.camera_key[m
[32m+[m[32m                )[m
 [m
[31m-                    logger.info([m
[31m-                        f"Static camera frame captured: "[m
[31m-                        f"{frame_path}"[m
[31m-                    )[m
[32m+[m[32m            except subprocess.TimeoutExpired:[m
 [m
[31m-                    callback([m
[31m-                        str(frame_path),[m
[31m-                        self.camera_key[m
[31m-                    )[m
[32m+[m[32m                logger.warning([m
[32m+[m[32m                    "FFmpeg camera capture timed out"[m
[32m+[m[32m                )[m
 [m
[31m-                    time.sleep([m
[31m-                        self.interval[m
[31m-                    )[m
[32m+[m[32m                if frame_path and frame_path.exists():[m
[32m+[m[32m                    frame_path.unlink()[m
 [m
             except Exception:[m
 [m
[36m@@ -119,20 +123,14 @@[m [mclass StaticCamera:[m
                     "Static camera error"[m
                 )[m
 [m
[31m-            finally:[m
[31m-[m
[31m-                if self.capture:[m
[31m-[m
[31m-                    self.capture.release()[m
[31m-                    self.capture = None[m
[32m+[m[32m                if frame_path and frame_path.exists():[m
[32m+[m[32m                    frame_path.unlink()[m
 [m
[31m-                if self.running:[m
[31m-[m
[31m-                    logger.info([m
[31m-                        "Reconnecting to static camera..."[m
[31m-                    )[m
[32m+[m[32m            if self.running:[m
 [m
[31m-                    time.sleep(5)[m
[32m+[m[32m                time.sleep([m
[32m+[m[32m                    self.interval[m
[32m+[m[32m                )[m
 [m
     def stop(self):[m
 [m
[36m@@ -142,8 +140,3 @@[m [mclass StaticCamera:[m
 [m
         self.running = False[m
 [m
[31m-        if self.capture:[m
[31m-[m
[31m-            self.capture.release()[m
[31m-            self.capture = None[m
[31m-[m
