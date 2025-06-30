import cv2
import time
from datetime import datetime
from collections import OrderedDict
import csv


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
    def __init__(self, cam=0, width=480, detect_interval=30, iou_thresh=0.2, max_lost=8):
        self.cap = cv2.VideoCapture(cam)
        if not self.cap.isOpened():
            raise IOError("Cannot open camera")
        self.scale_w = width
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.detect_interval = detect_interval
        self.iou_thresh = iou_thresh
        self.max_lost = max_lost
        self.trackers = OrderedDict()  # id → dict(tracker,obj_bbox,lost_frames)
        self.next_id = 0
        self.logger = VisitLogger()
        self.frame_idx = 0
        self.t0, self.fcnt, self.fps = time.time(), 0, 0.0

    @staticmethod
    def iou(boxA, boxB):
        xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
        xB, yB = min(boxA[0] + boxA[2], boxB[0] + boxB[2]), min(boxA[1] + boxA[3], boxB[1] + boxB[3])
        inter = max(0, xB - xA) * max(0, yB - yA)
        union = boxA[2] * boxA[3] + boxB[2] * boxB[3] - inter
        return inter / union if union else 0

    def _draw_fps(self, frame):
        self.fcnt += 1
        if self.fcnt >= 15:
            now = time.time()
            self.fps = self.fcnt / (now - self.t0)
            self.t0, self.fcnt = now, 0
        cv2.putText(frame, f"{self.fps:.1f} FPS", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def run(self):
        print("[INFO] Running…  Press Q to quit.")
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            scale = self.scale_w / frame.shape[1]
            small = cv2.resize(frame, None, fx=scale, fy=scale)

            # Track existing objects
            gone = []
            for pid, data in list(self.trackers.items()):
                ok, box = data['tracker'].update(small)
                if ok:
                    data['bbox'] = box
                    data['lost'] = 0
                    x, y, w, h = [int(v / scale) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, f"ID {pid}", (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                else:
                    data['lost'] += 1
                    if data['lost'] > self.max_lost:
                        gone.append(pid)

            # Remove lost trackers & log exit times
            for pid in gone:
                self.logger.person_exited(pid)
                del self.trackers[pid]

            # Detect new people every detect_interval frames
            if self.frame_idx % self.detect_interval == 0:
                boxes, _ = self.hog.detectMultiScale(small, winStride=(4, 4), padding=(8, 8), scale=1.05)
                for box in boxes:
                    # Skip if overlaps with existing tracker
                    if any(self.iou(box, d['bbox']) > self.iou_thresh for d in self.trackers.values()):
                        continue
                    
                    trk = cv2.legacy.TrackerCSRT_create()
                   
                    trk.init(small, tuple(box))
                    pid = self.next_id
                    self.trackers[pid] = dict(tracker=trk, bbox=box, lost=0)
                    self.logger.person_entered(pid)
                    self.next_id += 1

            self._draw_fps(frame)
            cv2.imshow("People Timer", frame)
            self.frame_idx += 1
            if cv2.waitKey(1) & 0xFF in (ord('q'), ord('Q')):
                break

        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.logger.finalize_open_visits()
        self.logger.print_report()
        self.logger.flush_to_csv()

if __name__ == "__main__":
    PeopleTimer(cam=0, width=480, detect_interval=10).run()


