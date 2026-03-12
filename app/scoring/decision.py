def recommended_action_for_decision(decision: str | None) -> str:
    if decision == "REJECT":
        return "IGNORE_TOKEN"
    if decision == "CAUTION":
        return "MONITOR_WAIT"
    if decision == "WATCH":
        return "ADD_TO_WATCHLIST"
    if decision == "ALERT":
        return "SEND_ALERT"
    return "INSUFFICIENT_DATA"
