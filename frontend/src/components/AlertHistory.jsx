function AlertHistory({
    metrics
}) {

    const alerts = metrics
        .filter(
            (item) =>
                item.alert === true
        )
        .slice(
            0,
            10
        );


    return (
        <div className="history-card">

            <div className="section-heading">

                <div>

                    <p className="section-label">
                        CLOUD HISTORY
                    </p>

                    <h2>
                        Recent Queue Alerts
                    </h2>

                </div>

            </div>


            {alerts.length === 0 ? (

                <div className="empty-state">

                    No congestion alerts
                    recorded yet.

                </div>

            ) : (

                <div className="alert-history-list">

                    {alerts.map(
                        (item) => {

                            const date =
                                new Date(
                                    item.recorded_at
                                );

                            return (

                                <div
                                    className="alert-history-item"
                                    key={
                                        item.event_id
                                    }
                                >

                                    <div>

                                        <strong>
                                            Queue Congestion
                                        </strong>

                                        <p>
                                            {
                                                date
                                                    .toLocaleString()
                                            }
                                        </p>

                                    </div>


                                    <div className="alert-history-metrics">

                                        <span>
                                            Queue{" "}
                                            <strong>
                                                {
                                                    item
                                                        .queue_length
                                                }
                                            </strong>
                                        </span>

                                        <span>
                                            Longest{" "}
                                            <strong>
                                                {
                                                    Number(
                                                        item
                                                            .longest_wait
                                                    )
                                                        .toFixed(
                                                            1
                                                        )
                                                }
                                                s
                                            </strong>
                                        </span>

                                    </div>

                                </div>

                            );
                        }
                    )}

                </div>

            )}

        </div>
    );
}


export default AlertHistory;