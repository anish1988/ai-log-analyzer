"""
Step 3.10 API test.
"""

import asyncio
import json

import httpx


async def main():

    print("=" * 100)
    print("STEP 3.10 - END TO END AI TEST")
    print("=" * 100)

    payload = {

        "tier": "web",

        "errors": [

            {

                "error_id": "TEST-WEB-001",

                "tier": "web",

                "log_type": "laravel",

                "server": "test-server",

                "file_name": "laravel.log",

                "file_path": (
                    "/var/log/laravel/laravel.log"
                ),

                "title": (
                    "[2019-02-04 11:42:00] "
                    "local.ERROR: "
                    "Route [dashboard.analytical] "
                    "not defined."
                ),

                "severity": "ERROR",

                "timestamp": (
                    "2019-02-04 11:42:00"
                ),

                "start_line": 100,

                "end_line": 108,

                "total_lines": 9,

                "error_content": (
                    "Route [dashboard.analytical] "
                    "not defined."
                ),

                "lines": [

                    {
                        "line_number": 100,

                        "raw": (
                            "[2019-02-04 11:42:00] "
                            "local.ERROR: "
                            "Route [dashboard.analytical] "
                            "not defined."
                        ),
                    },

                    {
                        "line_number": 101,

                        "raw": (
                            "Stack trace example"
                        ),
                    },

                    {
                        "line_number": 102,

                        "raw": (
                            "resources/views/layout/"
                            "navbar.blade.php"
                        ),
                    },

                ],
            }
        ],
    }

    async with httpx.AsyncClient(
        base_url="http://localhost:8000",
        timeout=180.0,
    ) as client:

        response = await client.post(

            "/api/ai/analyze",

            json=payload,
        )

    print()
    print("=" * 100)
    print("HTTP STATUS")
    print("=" * 100)

    print(
        response.status_code
    )

    print()
    print("=" * 100)
    print("BACKEND RESPONSE")
    print("=" * 100)

    try:

        print(
            json.dumps(
                response.json(),
                indent=2,
            )
        )

    except Exception:

        print(
            response.text
        )


if __name__ == "__main__":

    asyncio.run(main())