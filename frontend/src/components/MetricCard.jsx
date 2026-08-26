function MetricCard({
    title,
    value,
    subtitle
}) {

    return (

        <div className="metric-card">

            <div className="metric-top">

                <p>
                    {title}
                </p>

                <span className="metric-dot" />

            </div>


            <div className="metric-value">

                {value}

            </div>


            <div className="metric-footer">

                {subtitle}

            </div>

        </div>
    );
}


export default MetricCard;