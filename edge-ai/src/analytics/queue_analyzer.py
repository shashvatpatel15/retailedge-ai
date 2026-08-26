from core.config import (
    QUEUE_ZONE,
    QUEUE_LENGTH_THRESHOLD,
    WAIT_TIME_THRESHOLD,
    QUEUE_CONFIRM_TIME,
    QUEUE_EXIT_GRACE,
    TRACK_TIMEOUT
)


class QueueAnalyzer:

    def __init__(self):

        # ============================================
        # QUEUE CANDIDATES
        #
        # Person entered ROI but has not yet
        # stayed long enough to be considered
        # an actual queue customer.
        #
        # track_id -> first entered time
        # ============================================

        self.queue_candidates = {}


        # ============================================
        # CONFIRMED QUEUE MEMBERS
        #
        # track_id -> confirmed queue entry time
        # ============================================

        self.queue_entry_times = {}


        # ============================================
        # LAST TIME PERSON WAS INSIDE QUEUE ROI
        # ============================================

        self.last_inside_time = {}


        # ============================================
        # LAST TIME TRACK WAS SEEN
        # ============================================

        self.last_seen = {}


    # ================================================
    # CHECK ROI
    # ================================================

    def inside_queue(
        self,
        x,
        y
    ):

        x1, y1, x2, y2 = (
            QUEUE_ZONE
        )


        return (
            x1 <= x <= x2
            and
            y1 <= y <= y2
        )


    # ================================================
    # MAIN UPDATE
    # ================================================

    def update(
        self,
        people,
        now
    ):

        wait_by_track = {}

        confirmed_queue_ids = []


        # ============================================
        # PROCESS CURRENT TRACKS
        # ============================================

        for person in people:

            track_id = person[
                "track_id"
            ]


            foot_x, foot_y = (
                person[
                    "foot"
                ]
            )


            # Track is visible

            self.last_seen[
                track_id
            ] = now


            in_queue = self.inside_queue(
                foot_x,
                foot_y
            )


            # ========================================
            # PERSON INSIDE QUEUE ROI
            # ========================================

            if in_queue:

                self.last_inside_time[
                    track_id
                ] = now


                # ------------------------------------
                # ALREADY CONFIRMED
                # ------------------------------------

                if (
                    track_id
                    in
                    self.queue_entry_times
                ):

                    wait_time = (

                        now
                        -
                        self.queue_entry_times[
                            track_id
                        ]
                    )


                    wait_by_track[
                        track_id
                    ] = wait_time


                    confirmed_queue_ids.append(
                        track_id
                    )


                # ------------------------------------
                # NOT CONFIRMED YET
                # ------------------------------------

                else:

                    # First frame inside queue ROI

                    if (
                        track_id
                        not in
                        self.queue_candidates
                    ):

                        self.queue_candidates[
                            track_id
                        ] = now


                    candidate_duration = (

                        now
                        -
                        self.queue_candidates[
                            track_id
                        ]
                    )


                    # --------------------------------
                    # CONFIRM AS QUEUE CUSTOMER
                    # --------------------------------

                    if (
                        candidate_duration
                        >=
                        QUEUE_CONFIRM_TIME
                    ):

                        # We use candidate start time
                        # so waiting time includes the
                        # confirmation period.

                        self.queue_entry_times[
                            track_id
                        ] = (
                            self.queue_candidates[
                                track_id
                            ]
                        )


                        self.queue_candidates.pop(
                            track_id,
                            None
                        )


                        wait_time = (

                            now
                            -
                            self.queue_entry_times[
                                track_id
                            ]
                        )


                        wait_by_track[
                            track_id
                        ] = wait_time


                        confirmed_queue_ids.append(
                            track_id
                        )


                        print(
                            f"ID {track_id} "
                            f"confirmed in queue"
                        )


            # ========================================
            # PERSON CURRENTLY OUTSIDE ROI
            # ========================================

            else:

                # ------------------------------------
                # QUEUE CANDIDATE LEFT TOO EARLY
                # ------------------------------------

                if (
                    track_id
                    in
                    self.queue_candidates
                ):

                    self.queue_candidates.pop(
                        track_id,
                        None
                    )


                # ------------------------------------
                # CONFIRMED PERSON
                # ------------------------------------

                if (
                    track_id
                    in
                    self.queue_entry_times
                ):

                    last_inside = (
                        self.last_inside_time.get(
                            track_id,
                            now
                        )
                    )


                    time_outside = (
                        now - last_inside
                    )


                    # Still inside grace period

                    if (
                        time_outside
                        <=
                        QUEUE_EXIT_GRACE
                    ):

                        wait_time = (

                            now
                            -
                            self.queue_entry_times[
                                track_id
                            ]
                        )


                        wait_by_track[
                            track_id
                        ] = wait_time


                        confirmed_queue_ids.append(
                            track_id
                        )


                    # Person has actually left queue

                    else:

                        total_wait = (

                            last_inside
                            -
                            self.queue_entry_times[
                                track_id
                            ]
                        )


                        print(
                            f"ID {track_id} "
                            f"left queue after "
                            f"{total_wait:.1f}s"
                        )


                        self.queue_entry_times.pop(
                            track_id,
                            None
                        )


                        self.last_inside_time.pop(
                            track_id,
                            None
                        )


        # ============================================
        # CLEAN UP LOST TRACKS
        # ============================================

        stale_tracks = []


        for (
            track_id,
            seen_time
        ) in list(
            self.last_seen.items()
        ):

            if (
                now - seen_time
                >
                TRACK_TIMEOUT
            ):

                stale_tracks.append(
                    track_id
                )


        for track_id in stale_tracks:

            self.queue_candidates.pop(
                track_id,
                None
            )


            self.queue_entry_times.pop(
                track_id,
                None
            )


            self.last_inside_time.pop(
                track_id,
                None
            )


            self.last_seen.pop(
                track_id,
                None
            )


        # ============================================
        # QUEUE STATISTICS
        # ============================================

        wait_times = list(
            wait_by_track.values()
        )


        queue_length = len(
            confirmed_queue_ids
        )


        if wait_times:

            average_wait = (

                sum(wait_times)
                /
                len(wait_times)
            )


            longest_wait = max(
                wait_times
            )


        else:

            average_wait = 0.0

            longest_wait = 0.0


        # ============================================
        # ALERT
        # ============================================

        alert = (

            queue_length
            >=
            QUEUE_LENGTH_THRESHOLD

            and

            longest_wait
            >=
            WAIT_TIME_THRESHOLD
        )


        # ============================================
        # RETURN LIVE ANALYTICS
        # ============================================

        return {

            "queue_length":
                queue_length,

            "average_wait":
                average_wait,

            "longest_wait":
                longest_wait,

            "alert":
                alert,

            "wait_by_track":
                wait_by_track,

            "queue_ids":
                confirmed_queue_ids
        }