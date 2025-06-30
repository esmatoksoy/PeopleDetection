import cv2
import time
from datetime import datetime
from collections import OrderedDict
import csv
from ultralytics import YOLO

class VisitLogger:
    def __init__(self, csv_path="visits_today.csv"):
        self.active = OrderedDict()  # id → entry_time (datetime)
        self.records = []  # (id, entry_time, exit_time)
        self.csv_path = csv_path

    def person_entered(self, pid):
        self.active[pid] = datetime.now()

    def person_exited(self, pid):
        entry = self.active.pop(pid, None)
        if entry:
            exit_time = datetime.now()
            self.records.append((pid, entry, exit_time))

    def finalize_open_visits(self):
        for pid in list(self.active):
            self.person_exited(pid)

    def flush_to_csv(self):
        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "entry_time", "exit_time", "duration_seconds"])
            for pid, start, end in self.records:
                duration = (end - start).total_seconds()
                writer.writerow([pid, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S"), f"{duration:.2f}"])

    def print_report(self):
        if not self.records:
            print("\n[REPORT] No visitors recorded.")
            return
        print("\n[REPORT] Visit durations:")
        for pid, start, end in self.records:
            dur = (end - start).total_seconds()
            print(f"  ID {pid:<3}  {start.strftime('%H:%M:%S')}  ➜  {end.strftime('%H:%M:%S')}   stayed {dur:.1f} s")
        avg = sum((end - start).total_seconds() for _, start, end in self.records) / len(self.records)
        print(f"\nAverage stay: {avg:.1f} s over {len(self.records)} visitor(s)")

class PeopleTimer:
    def __init__(self, cam=0, width=480, detect_interval=0.2, max_lost=8):
        self.cap = cv2.VideoCapture(cam)
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")
        
        self.scale_w = width
        self.model = YOLO("yolov8n.pt")  # Load YOLOv8
        self.detect_interval = detect_interval
        self.max_lost = max_lost
        self.trackers = OrderedDict()  # id → {bbox, lost_frames}
        self.next_id = 0
        self.logger = VisitLogger()
        self.last_detect_time = time.time()
        self.t0, self.fcnt, self.fps = time.time(), 0, 0.0

    def _draw_fps(self, frame):
        """Draw FPS counter on frame"""
        self.fcnt += 1
        if self.fcnt >= 15:
            now = time.time()
            self.fps = self.fcnt / (now - self.t0)
            self.t0, self.fcnt = now, 0
        cv2.putText(frame, f"{self.fps:.1f} FPS", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def _detect_people(self, frame):
        """Detects humans using YOLOv8 tracking"""
        results = self.model.track(
            frame, 
            persist=True, 
            tracker="bytetrack.yaml",  # Built-in tracker
            conf=0.5,  # Min confidence
            classes=[0]  # Only 'person' class
        )
        
        boxes = []
        if results[0].boxes.id is not None:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((box.id.item(), (x1, y1, x2 - x1, y2 - y1)))
        return boxes

    def run(self):
        print("[INFO] Running… Press Q to quit.")
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            
            scale = self.scale_w / frame.shape[1]
            small = cv2.resize(frame, None, fx=scale, fy=scale)

            # Detect and track people
            tracked_boxes = []
            current_time = time.time()
            if current_time - self.last_detect_time >= self.detect_interval:
                tracked_boxes = self._detect_people(small)
                self.last_detect_time = current_time
                for pid, box in tracked_boxes:
                    if pid not in self.trackers:
                        self.trackers[pid] = {"bbox": box, "lost": 0}
                        self.logger.person_entered(pid)

            # Update existing trackers
            current_pids = [p[0] for p in tracked_boxes]
            for pid in list(self.trackers.keys()):
                if pid in current_pids:
                    self.trackers[pid]["lost"] = 0  # Reset lost counter
                    # Update bbox position
                    idx = current_pids.index(pid)
                    self.trackers[pid]["bbox"] = tracked_boxes[idx][1]
                else:
                    self.trackers[pid]["lost"] += 1
                    if self.trackers[pid]["lost"] > self.max_lost:
                        self.logger.person_exited(pid)
                        del self.trackers[pid]

            # Draw bounding boxes
            for pid, data in self.trackers.items():
                x, y, w, h = data["bbox"]
                x, y, w, h = int(x/scale), int(y/scale), int(w/scale), int(h/scale)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, f"ID {pid}", (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            self._draw_fps(frame)
            cv2.imshow("People Timer", frame)
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.logger.finalize_open_visits()
        self.logger.print_report()
        self.logger.flush_to_csv()

if __name__ == "__main__":
    PeopleTimer(cam=0, width=480, detect_interval=0.2).run()