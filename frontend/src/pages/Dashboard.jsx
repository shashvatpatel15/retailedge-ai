import {
    useEffect,
    useState
} from "react";

import MetricCard
    from "../components/MetricCard";

import QueueAlert
    from "../components/QueueAlert";

import StatusBadge
    from "../components/StatusBadge";

import QueueHistoryChart
    from "../components/QueueHistoryChart";

import AlertHistory
    from "../components/AlertHistory";

import {
    getQueueData,
    getHealth,
    getQueueHistory
} from "../services/queueApi";


function Dashboard() {

    const [queueData, setQueueData] =
        useState({
            tracked_people: 0,
            queue_length: 0,
            average_wait: 0,
            longest_wait: 0,
            alert: false
        });


    const [connected, setConnected] =
        useState(false);


    const [history, setHistory] =
        useState([]);


    const [lastUpdated, setLastUpdated] =
        useState(null);


    const [historyError, setHistoryError] =
        useState(null);


    // ============================================
    // LIVE DATA
    // ============================================

    async function loadQueueData() {

        try {

            const data =
                await getQueueData();


            setQueueData(data);

            setConnected(true);

            setLastUpdated(
                new Date()
            );

        } catch (error) {

            console.error(
                error
            );

            setConnected(false);
        }
    }


    // ============================================
    // HEALTH
    // ============================================

    async function checkHealth() {
        try {
            const data = await getHealth();
            setConnected(Boolean(data.edge_engine_running || data.status === "ok"));
        } catch {
            setConnected(false);
        }
    }



    // ============================================
    // HISTORY
    // ============================================

    async function loadHistory() {

        try {

            const data =
                await getQueueHistory();


            setHistory(
                data.metrics || []
            );


            setHistoryError(null);

        } catch (error) {

            console.error(
                error
            );

            setHistoryError(
                "Cloud analytics unavailable"
            );
        }
    }


    // ============================================
    // POLLING
    // ============================================

    useEffect(() => {

        loadQueueData();
        checkHealth();
        loadHistory();


        const queueInterval =
            setInterval(
                loadQueueData,
                1000
            );


        const healthInterval =
            setInterval(
                checkHealth,
                5000
            );


        const historyInterval =
            setInterval(
                loadHistory,
                20000
            );


        return () => {

            clearInterval(
                queueInterval
            );

            clearInterval(
                healthInterval
            );

            clearInterval(
                historyInterval
            );
        };

    }, []);


    return (

        <div className="app-shell">

            {/* ================================= */}
            {/* TOP NAV */}
            {/* ================================= */}

            <nav className="top-nav">

                <div className="brand">

                    <div className="brand-logo">
                        R
                    </div>

                    <div>

                        <h2>
                            RetailEdge
                        </h2>

                        <span>
                            AI Intelligence
                        </span>

                    </div>

                </div>


                <div className="nav-right">

                    <div className="live-pill">

                        <span className="live-dot" />

                        LIVE

                    </div>


                    <StatusBadge
                        connected={
                            connected
                        }
                    />

                </div>

            </nav>


            {/* ================================= */}
            {/* DASHBOARD */}
            {/* ================================= */}

            <main className="dashboard">

                {/* HERO */}

                <section className="hero-section">

                    <div>

                        <p className="eyebrow">
                            SMART RETAIL OPERATIONS
                        </p>

                        <h1>
                            Queue Intelligence
                            <span>
                                {" "}in real time.
                            </span>
                        </h1>

                        <p className="hero-description">

                            Privacy-first queue analytics
                            powered by on-device AI with
                            cloud-backed operational
                            intelligence.

                        </p>

                    </div>


                    <div className="hero-meta">

                        <div>

                            <span>
                                DEVICE
                            </span>

                            <strong>
                                edge-01
                            </strong>

                        </div>


                        <div>

                            <span>
                                MODE
                            </span>

                            <strong>
                                Edge + Cloud
                            </strong>

                        </div>

                    </div>

                </section>


                {/* ================================= */}
                {/* LIVE METRICS */}
                {/* ================================= */}

                <section className="metrics-grid">

                    <MetricCard
                        title="Tracked People"
                        value={
                            String(
                                queueData
                                    .tracked_people
                            ).padStart(
                                2,
                                "0"
                            )
                        }
                        subtitle="Visible people"
                    />


                    <MetricCard
                        title="Queue Length"
                        value={
                            String(
                                queueData
                                    .queue_length
                            ).padStart(
                                2,
                                "0"
                            )
                        }
                        subtitle="Confirmed customers"
                    />


                    <MetricCard
                        title="Average Wait"
                        value={
                            `${Number(
                                queueData
                                    .average_wait
                            ).toFixed(1)}s`
                        }
                        subtitle="Current queue"
                    />


                    <MetricCard
                        title="Longest Wait"
                        value={
                            `${Number(
                                queueData
                                    .longest_wait
                            ).toFixed(1)}s`
                        }
                        subtitle="Longest active wait"
                    />

                </section>


                {/* ================================= */}
                {/* MAIN ANALYTICS */}
                {/* ================================= */}

                <section className="analytics-grid">

                    <QueueHistoryChart
                        metrics={
                            history
                        }
                    />


                    <AlertHistory
                        metrics={
                            history
                        }
                    />

                </section>


                {/* ================================= */}
                {/* ALERT */}
                {/* ================================= */}

                <section className="queue-status-section">

                    <QueueAlert

                        alert={
                            queueData.alert
                        }

                        queueLength={
                            queueData
                                .queue_length
                        }

                        longestWait={
                            Number(
                                queueData
                                    .longest_wait
                            )
                        }

                    />

                </section>


                {/* ================================= */}
                {/* ARCHITECTURE */}
                {/* ================================= */}

                <section className="architecture-card">

                    <div className="architecture-header">

                        <div>

                            <p className="section-label">
                                SYSTEM ARCHITECTURE
                            </p>

                            <h3>
                                Privacy-first Edge Processing
                            </h3>

                        </div>


                        <span className="privacy-tag">
                            RAW VIDEO STAYS LOCAL
                        </span>

                    </div>


                    <div className="architecture-flow">

                        <div className="architecture-node">

                            <span>
                                01
                            </span>

                            <strong>
                                Camera
                            </strong>

                            <small>
                                IP Stream
                            </small>

                        </div>


                        <div className="flow-line">
                            →
                        </div>


                        <div className="architecture-node">

                            <span>
                                02
                            </span>

                            <strong>
                                YOLO11n
                            </strong>

                            <small>
                                Detection
                            </small>

                        </div>


                        <div className="flow-line">
                            →
                        </div>


                        <div className="architecture-node">

                            <span>
                                03
                            </span>

                            <strong>
                                ByteTrack
                            </strong>

                            <small>
                                Tracking
                            </small>

                        </div>


                        <div className="flow-line">
                            →
                        </div>


                        <div className="architecture-node">

                            <span>
                                04
                            </span>

                            <strong>
                                SQLite
                            </strong>

                            <small>
                                Offline buffer
                            </small>

                        </div>


                        <div className="flow-line">
                            →
                        </div>


                        <div className="architecture-node">

                            <span>
                                05
                            </span>

                            <strong>
                                Supabase
                            </strong>

                            <small>
                                Analytics
                            </small>

                        </div>

                    </div>

                </section>


                {/* ================================= */}
                {/* CLOUD ERROR */}
                {/* ================================= */}

                {historyError && (

                    <div className="cloud-warning">

                        <span>
                            !
                        </span>

                        {historyError}

                    </div>

                )}


                {/* ================================= */}
                {/* FOOTER */}
                {/* ================================= */}

                <footer className="dashboard-footer">

                    <div>

                        RetailEdge AI
                        <span>
                            /
                        </span>
                        Queue Intelligence
                    </div>


                    <div>

                        {
                            lastUpdated
                                ? `Updated ${
                                    lastUpdated
                                        .toLocaleTimeString()
                                }`
                                : "Waiting for edge data"
                        }

                    </div>

                </footer>

            </main>

        </div>
    );
}


export default Dashboard;