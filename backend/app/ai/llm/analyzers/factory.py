class AnalyzerFactory:

    @staticmethod
    def get_analyzer(
        *,
        log_type: str,
        llm_service,
    ):

        log_type = (
            log_type or ""
        ).strip().lower()

        # ---------------------------------------------------------
        # Existing Web/Laravel mapping
        # ---------------------------------------------------------

        if log_type == "laravel":

            return WebLogAnalyzer(
                llm_service
            )

        # ---------------------------------------------------------
        # Existing Apache mapping
        # ---------------------------------------------------------

        if log_type.startswith(
            "apache"
        ):

            return WebLogAnalyzer(
                llm_service
            )

        # ---------------------------------------------------------
        # NEW - Telephony
        # ---------------------------------------------------------

        if log_type.startswith(
            "asterisk"
        ):

            return TelephonyLogAnalyzer(
                llm_service
            )

        if log_type.startswith(
            "vicidial"
        ):

            return TelephonyLogAnalyzer(
                llm_service
            )

        raise ValueError(
            f"No analyzer configured "
            f"for log type '{log_type}'"
        )