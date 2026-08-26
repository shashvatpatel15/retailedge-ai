function QueueAlert({
    alert,
    queueLength,
    longestWait
}) {

    if (alert) {

        return (

            <div className="queue-alert danger">

                <div className="queue-alert-content">

                    <div className="alert-symbol">
                        !
                    </div>


                    <div>

                        <p className="alert-label">
                            ACTION REQUIRED
                        </p>

                        <h2>
                            Open Another Billing Counter
                        </h2>

                        <p>

                            Queue length is{" "}
                            <strong>
                                {queueLength}
                            </strong>

                            {" "}with a longest
                            wait of{" "}

                            <strong>
                                {
                                    longestWait
                                        .toFixed(1)
                                }s
                            </strong>.

                        </p>

                    </div>

                </div>


                <div className="alert-action">

                    CONGESTION

                </div>

            </div>
        );
    }


    return (

        <div className="queue-alert normal">

            <div className="queue-alert-content">

                <div className="alert-symbol">
                    ✓
                </div>


                <div>

                    <p className="alert-label">
                        LIVE QUEUE STATUS
                    </p>

                    <h2>
                        Queue Operating Normally
                    </h2>

                    <p>
                        No additional billing
                        counter is currently required.
                    </p>

                </div>

            </div>


            <div className="alert-action">

                NORMAL

            </div>

        </div>
    );
}


export default QueueAlert;