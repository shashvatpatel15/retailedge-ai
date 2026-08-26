import {
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from "recharts";


function QueueHistoryChart({
    metrics
}) {

    const chartData = [...metrics]
        .reverse()
        .map((item) => {

            const date =
                new Date(
                    item.recorded_at
                );

            return {
                time:
                    date.toLocaleTimeString(
                        [],
                        {
                            hour: "2-digit",
                            minute: "2-digit"
                        }
                    ),

                queue_length:
                    item.queue_length,

                average_wait:
                    Number(
                        item.average_wait
                    ),

                longest_wait:
                    Number(
                        item.longest_wait
                    )
            };
        });


    return (
        <div className="history-card">

            <div className="section-heading">

                <div>

                    <p className="section-label">
                        CLOUD ANALYTICS
                    </p>

                    <h2>
                        Queue Length Trend
                    </h2>

                </div>

                <span className="history-count">
                    {metrics.length} records
                </span>

            </div>


            {chartData.length === 0 ? (

                <div className="empty-state">
                    No cloud history available yet.
                </div>

            ) : (

                <div className="chart-container">

                    <ResponsiveContainer
                        width="100%"
                        height="100%"
                    >

                        <LineChart
                            data={chartData}
                        >

                            <CartesianGrid
                                strokeDasharray="3 3"
                                opacity={0.15}
                            />

                            <XAxis
                                dataKey="time"
                            />

                            <YAxis
                                allowDecimals={false}
                            />

                            <Tooltip />

                            <Line
                                type="monotone"
                                dataKey="queue_length"
                                name="Queue Length"
                                stroke="currentColor"
                                strokeWidth={3}
                                dot={false}
                            />

                        </LineChart>

                    </ResponsiveContainer>

                </div>

            )}

        </div>
    );
}


export default QueueHistoryChart;