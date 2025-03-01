import circuitbreaker


class ResettableCircuitBreaker(circuitbreaker.CircuitBreaker):
    def reset(self) -> None:
        self._last_failure = None
        self._failure_count = 0
        self._state = circuitbreaker.STATE_CLOSED
