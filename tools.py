from strands import tool
import boto3
import json

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")

# 参照ドキュメント
REFERENCE_DOCUMENTS = [
    "LINE Developer CommunityはLINE APIに関連する最新情報や開発Tipsを共有するコミュニティ",
    "LINE Developer Communityは有志メンバーを中心に運営されています。",
    "LINE Developer Community食事のみを目的とした参加を禁止事項としています。",
]

@tool
def grounded_answer(question: str) -> str:
    """
    Bedrock + Contextual Grounding Check
    ブロック時は安全なメッセージを返す
    """
    # 1. モデル応答を生成
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    }
    try:
        model_response = bedrock_runtime.invoke_model(
            modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
            body=json.dumps(request_body)
        )

        response_body = json.loads(model_response["body"].read())
        answer_text = response_body["content"][0]["text"]

        # 2. ApplyGuardrail APIを使用してContextual Grounding Checkを実行
        # 参照ドキュメントを結合
        grounding_source = " ".join(REFERENCE_DOCUMENTS)

        guardrail_response = bedrock_runtime.apply_guardrail(
            guardrailIdentifier="GUARDRAIL_ID", # コンテキストグラウンディングチェック用に作成したガードレールIDを指定
            guardrailVersion="1", # 必要に応じてバージョンを指定
            source="OUTPUT",
            content=[
                {
                    "text": {
                        "text": grounding_source,
                        "qualifiers": ["grounding_source"]
                    }
                },
                {
                    "text": {
                        "text": question,
                        "qualifiers": ["query"]
                    }
                },
                {
                    "text": {
                        "text": answer_text
                    }
                }
            ]
        )

        # 3. アクション結果を確認
        action = guardrail_response.get("action", "NONE")

        if action == "NONE":
            # ブロックされなかった場合
            # さらに詳細にスコアをチェック(オプション)
            assessments = guardrail_response.get("assessments", [])
            if assessments:
                contextual_grounding = assessments[0].get("contextualGroundingPolicy", {})
                filters = contextual_grounding.get("filters", [])

                # いずれかのフィルターでBLOCKアクションがあるかチェック
                blocked = any(f.get("action") == "BLOCK" for f in filters)

                if blocked:
                    # 詳細情報を取得
                    grounding_filter = next((f for f in filters if f.get("type") == "GROUNDING"), None)
                    relevance_filter = next((f for f in filters if f.get("type") == "RELEVANCE"), None)

                    grounding_score = grounding_filter.get("score", 0) if grounding_filter else 1
                    relevance_score = relevance_filter.get("score", 0) if relevance_filter else 1

                    return f"[BLOCKED] この回答は参照情報に基づいていない、または質問と関連性が低いため提供できません。(Grounding: {grounding_score:.2f}, Relevance: {relevance_score:.2f})"

            return f"[FACTUAL] {answer_text}"

        elif action == "GUARDRAIL_INTERVENED":
            # ガードレールが介入した場合
            action_reason = guardrail_response.get("actionReason", "不明な理由")
            return f"[BLOCKED] この質問には安全な回答を提供できません。理由: {action_reason}"

        return f"[SAFE] {answer_text}"

    except Exception as e:
        return f"[ERROR] エラーが発生しました: {str(e)}"


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