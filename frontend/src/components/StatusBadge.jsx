function StatusBadge({
    connected
}) {
    return (
        <div
            className={
                connected
                    ? "status-badge connected"
                    : "status-badge disconnected"
            }
        >

            <span className="status-dot" />

            {connected
                ? "Edge AI Online"
                : "Edge AI Offline"}

        </div>
    );
}


export default StatusBadge;