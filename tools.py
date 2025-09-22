from strands import tool


@tool
def get_staff_schedule(date: str, staff_name: str = None) -> dict:
    """Get staff schedule and availability for Hair Salon MIKA.

    Args:
        date: The date to check schedule (YYYY-MM-DD format)
        staff_name: Optional specific staff name to check
    """
    try:
        # Sample schedule data for Hair Salon MIKA
        schedule_data = {
            "2025-09-24": {
                "田中美香": {
                    "10:00-12:00": {"status": "予約済", "service": "カット+カラー"},
                    "13:00-14:00": {"status": "予約済", "service": "カット"},
                    "15:00-17:00": {"status": "空き"},
                    "17:00-19:00": {"status": "予約済", "service": "パーマ"},
                },
                "佐藤裕子": {
                    "10:00-11:00": {"status": "予約済", "service": "カット"},
                    "12:00-13:30": {"status": "予約済", "service": "カラー"},
                    "14:00-15:00": {"status": "空き"},
                    "15:30-16:15": {"status": "予約済", "service": "トリートメント"},
                },
            },
            "2025-09-25": {
                "田中美香": {
                    "10:00-11:00": {"status": "空き"},
                    "11:30-13:30": {"status": "予約済", "service": "カット+カラー"},
                    "14:30-15:30": {"status": "空き"},
                    "16:00-17:00": {"status": "予約済", "service": "カット"},
                },
                "佐藤裕子": {
                    "10:00-12:00": {"status": "予約済", "service": "パーマ"},
                    "13:00-14:00": {"status": "空き"},
                    "14:30-16:00": {"status": "予約済", "service": "カラー"},
                    "16:30-18:00": {"status": "空き"},
                },
            },
        }

        # Get schedule for the specified date
        date_schedule = schedule_data.get(date, {})

        if not date_schedule:
            return {
                "status": "error",
                "content": [
                    {"text": f"スケジュールデータが見つかりません: {date}"}
                ]
            }

        # Return specific staff schedule if requested
        if staff_name:
            staff_schedule = date_schedule.get(staff_name, {})
            if not staff_schedule:
                return {
                    "status": "error",
                    "content": [
                        {"text": f"スタッフ「{staff_name}」のスケジュールが見つかりません: {date}"}
                    ]
                }

            result_data = {
                "date": date,
                "staff": staff_name,
                "schedule": staff_schedule
            }
        else:
            # Return all staff schedules
            result_data = {
                "date": date,
                "allStaff": date_schedule
            }

        return {
            "status": "success",
            "content": [
                {"json": result_data}
            ]
        }

    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"Error: {e}"}
            ]
        }