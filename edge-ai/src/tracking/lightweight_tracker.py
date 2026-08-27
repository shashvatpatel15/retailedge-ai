"""
Lightweight Multi-Object Person Tracker for Raspberry Pi / Edge Devices.
Uses pure Python and NumPy for high-speed IoU + Centroid association without PyTorch/Torch overhead.
"""

from typing import List, Dict, Tuple, Any
import numpy as np


def calculate_iou(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes: (x1, y1, x2, y2).
    """
    x1_max = max(box1[0], box2[0])
    y1_max = max(box1[1], box2[1])
    x2_min = min(box1[2], box2[2])
    y2_min = min(box1[3], box2[3])

    intersection_w = max(0, x2_min - x1_max)
    intersection_h = max(0, y2_min - y1_max)
    intersection_area = intersection_w * intersection_h

    area1 = max(0, box1[2] - box1[0]) * max(0, box1[3] - box1[1])
    area2 = max(0, box2[2] - box2[0]) * max(0, box2[3] - box2[1])
    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0

    return float(intersection_area / union_area)


class Track:
    """
    State of an individual tracked person.
    """

    def __init__(self, track_id: int, bbox: Tuple[int, int, int, int], confidence: float):
        self.track_id = track_id
        self.bbox = bbox
        self.confidence = confidence
        self.hits = 1
        self.age = 1
        self.time_since_update = 0

        # Calculate foot coordinate (bottom center)
        self.foot = self._compute_foot(bbox)

    @staticmethod
    def _compute_foot(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        x1, y1, x2, y2 = bbox
        return (int((x1 + x2) // 2), int(y2))

    def update(self, bbox: Tuple[int, int, int, int], confidence: float):
        self.bbox = bbox
        self.confidence = confidence
        self.hits += 1
        self.time_since_update = 0
        self.foot = self._compute_foot(bbox)

    def mark_missed(self):
        self.age += 1
        self.time_since_update += 1


class LightweightTracker:
    """
    Lightweight, resource-efficient person tracker.
    Ideal for Raspberry Pi 3 B+ and edge systems where PyTorch/ByteTrack are too heavy.
    """

    def __init__(
        self,
        max_age: int = 15,
        min_hits: int = 1,
        iou_threshold: float = 0.25,
        max_centroid_distance: float = 120.0
    ):
        """
        :param max_age: Maximum frames to retain a track without new detections.
        :param min_hits: Minimum detection matches before a track is considered active.
        :param iou_threshold: Minimum IoU overlap to associate a detection with a track.
        :param max_centroid_distance: Fallback Euclidean pixel distance for centroid matching.
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.max_centroid_distance = max_centroid_distance

        self.tracks: List[Track] = []
        self._next_id: int = 1

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update tracker with detections from current frame.

        :param detections: List of dicts, each with keys 'bbox' (x1, y1, x2, y2),
                           'foot' (foot_x, foot_y), 'confidence' (float).
        :return: List of active person tracks in format:
                 [{"track_id": int, "bbox": (x1,y1,x2,y2), "foot": (fx, fy), "confidence": float}, ...]
        """
        if not self.tracks:
            # First frame or all tracks expired: create new tracks for all detections
            for det in detections:
                new_track = Track(
                    track_id=self._next_id,
                    bbox=det["bbox"],
                    confidence=det.get("confidence", 1.0)
                )
                self._next_id += 1
                self.tracks.append(new_track)

            return [
                {
                    "track_id": t.track_id,
                    "bbox": t.bbox,
                    "foot": t.foot,
                    "confidence": t.confidence
                }
                for t in self.tracks
                if t.hits >= self.min_hits
            ]

        # Match existing tracks with current detections
        matched_tracks = set()
        matched_dets = set()

        if detections:
            # 1. IoU Association
            cost_matrix = []
            for track in self.tracks:
                row = []
                for det in detections:
                    iou = calculate_iou(track.bbox, det["bbox"])
                    row.append(iou)
                cost_matrix.append(row)

            # Greedy matching for max IoU
            cost_matrix = np.array(cost_matrix) if cost_matrix else np.empty((0, 0))

            if cost_matrix.size > 0:
                # Find best pairs
                while True:
                    max_val = np.max(cost_matrix)
                    if max_val < self.iou_threshold:
                        break
                    tr_idx, det_idx = np.unravel_index(np.argmax(cost_matrix), cost_matrix.shape)
                    matched_tracks.add(tr_idx)
                    matched_dets.add(det_idx)

                    # Update track
                    self.tracks[tr_idx].update(
                        detections[det_idx]["bbox"],
                        detections[det_idx].get("confidence", 1.0)
                    )

                    # Mark row and column as used
                    cost_matrix[tr_idx, :] = -1.0
                    cost_matrix[:, det_idx] = -1.0

            # 2. Centroid Distance Fallback for remaining unmatched detections
            for tr_idx, track in enumerate(self.tracks):
                if tr_idx in matched_tracks:
                    continue

                best_det_idx = None
                best_dist = float("inf")

                for det_idx, det in enumerate(detections):
                    if det_idx in matched_dets:
                        continue

                    det_foot = det.get("foot") or Track._compute_foot(det["bbox"])
                    dist = np.hypot(track.foot[0] - det_foot[0], track.foot[1] - det_foot[1])

                    if dist < self.max_centroid_distance and dist < best_dist:
                        best_dist = dist
                        best_det_idx = det_idx

                if best_det_idx is not None:
                    matched_tracks.add(tr_idx)
                    matched_dets.add(best_det_idx)
                    self.tracks[tr_idx].update(
                        detections[best_det_idx]["bbox"],
                        detections[best_det_idx].get("confidence", 1.0)
                    )

            # 3. Create new tracks for unmatched detections
            for det_idx, det in enumerate(detections):
                if det_idx not in matched_dets:
                    new_track = Track(
                        track_id=self._next_id,
                        bbox=det["bbox"],
                        confidence=det.get("confidence", 1.0)
                    )
                    self._next_id += 1
                    self.tracks.append(new_track)

        # 4. Mark unmatched tracks as missed
        for tr_idx, track in enumerate(self.tracks):
            if tr_idx not in matched_tracks and (len(detections) == 0 or tr_idx < len(self.tracks)):
                if tr_idx not in matched_tracks:
                    track.mark_missed()

        # 5. Remove expired tracks
        self.tracks = [
            t for t in self.tracks
            if t.time_since_update <= self.max_age
        ]

        # 6. Format active tracks
        active_results = []
        for t in self.tracks:
            if t.hits >= self.min_hits and t.time_since_update == 0:
                active_results.append({
                    "track_id": t.track_id,
                    "bbox": t.bbox,
                    "foot": t.foot,
                    "confidence": t.confidence
                })

        return active_results
