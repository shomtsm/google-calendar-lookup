#!/usr/bin/env python3
"""
Google Calendar イベント情報取得スクリプト
特定のイベントの作成日時、更新日時、作成者などの情報を取得します。
"""

import os
import sys
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 必要なスコープ（読み取り専用）
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# 認証情報ファイルのパス
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def authenticate():
    """Google Calendar APIの認証を行う"""
    creds = None

    # 保存済みトークンがあれば読み込む
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 有効な認証情報がない場合は再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"エラー: {CREDENTIALS_FILE} が見つかりません。")
                print("Google Cloud Consoleからダウンロードしてください。")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # トークンを保存
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_calendar_service():
    """Calendar APIサービスを取得"""
    creds = authenticate()
    return build('calendar', 'v3', credentials=creds)


def list_calendars(service):
    """利用可能なカレンダー一覧を表示"""
    print("\n=== カレンダー一覧 ===")
    calendars = service.calendarList().list().execute()

    for i, calendar in enumerate(calendars.get('items', []), 1):
        print(f"{i}. {calendar['summary']} (ID: {calendar['id']})")

    return calendars.get('items', [])


def search_events(service, calendar_id='primary', query=None, max_results=10, days_back=30, days_forward=90):
    """
    イベントを検索

    Args:
        service: Calendar APIサービス
        calendar_id: カレンダーID
        query: 検索キーワード
        max_results: 最大取得件数
        days_back: 何日前からのイベントを取得するか
        days_forward: 何日先までのイベントを取得するか
    """
    time_min = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'
    time_max = (datetime.utcnow() + timedelta(days=days_forward)).isoformat() + 'Z'

    print(f"\n=== イベント検索結果 ===")
    print(f"検索範囲: 過去{days_back}日 〜 未来{days_forward}日")
    if query:
        print(f"検索キーワード: {query}")

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q=query
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print("該当するイベントが見つかりませんでした。")
            return []

        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{i}. {event['summary']} ({start})")

        return events

    except HttpError as error:
        print(f"エラーが発生しました: {error}")
        return []


def get_event_details(service, calendar_id, event_id):
    """
    イベントの詳細情報を取得

    Args:
        service: Calendar APIサービス
        calendar_id: カレンダーID
        event_id: イベントID
    """
    try:
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        return event

    except HttpError as error:
        print(f"エラーが発生しました: {error}")
        return None


def format_datetime(dt_string):
    """ISO形式の日時を読みやすい形式に変換"""
    if not dt_string:
        return "不明"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y年%m月%d日 %H:%M:%S')
    except:
        return dt_string


def display_event_info(event):
    """イベント情報を整形して表示"""
    print("\n" + "=" * 60)
    print("イベント詳細情報")
    print("=" * 60)

    # 基本情報
    print(f"\n【タイトル】")
    print(f"  {event.get('summary', '(タイトルなし)')}")

    print(f"\n【説明】")
    print(f"  {event.get('description', '(説明なし)')}")

    # 日時情報
    start = event.get('start', {})
    end = event.get('end', {})
    start_time = start.get('dateTime', start.get('date'))
    end_time = end.get('dateTime', end.get('date'))

    print(f"\n【開始日時】")
    print(f"  {format_datetime(start_time)}")

    print(f"\n【終了日時】")
    print(f"  {format_datetime(end_time)}")

    # 作成・更新情報
    print(f"\n【作成日時】")
    print(f"  {format_datetime(event.get('created'))}")

    print(f"\n【最終更新日時】")
    print(f"  {format_datetime(event.get('updated'))}")

    # 作成者・主催者
    creator = event.get('creator', {})
    organizer = event.get('organizer', {})

    print(f"\n【作成者】")
    creator_info = creator.get('displayName', creator.get('email', '不明'))
    print(f"  {creator_info}")
    if creator.get('email') and creator.get('displayName'):
        print(f"  Email: {creator.get('email')}")

    print(f"\n【主催者】")
    organizer_info = organizer.get('displayName', organizer.get('email', '不明'))
    print(f"  {organizer_info}")
    if organizer.get('email') and organizer.get('displayName'):
        print(f"  Email: {organizer.get('email')}")

    # 参加者
    attendees = event.get('attendees', [])
    if attendees:
        print(f"\n【参加者】({len(attendees)}名)")
        for attendee in attendees:
            name = attendee.get('displayName', attendee.get('email'))
            status = attendee.get('responseStatus', '未回答')
            status_ja = {
                'accepted': '参加',
                'declined': '不参加',
                'tentative': '未定',
                'needsAction': '未回答'
            }.get(status, status)
            print(f"  - {name} ({status_ja})")

    # その他の情報
    print(f"\n【ステータス】")
    status = event.get('status', '不明')
    status_ja = {
        'confirmed': '確定',
        'tentative': '仮',
        'cancelled': 'キャンセル'
    }.get(status, status)
    print(f"  {status_ja}")

    print(f"\n【イベントID】")
    print(f"  {event.get('id')}")

    print(f"\n【リンク】")
    print(f"  {event.get('htmlLink', 'なし')}")

    # 繰り返し設定
    if event.get('recurrence'):
        print(f"\n【繰り返し設定】")
        for rule in event.get('recurrence', []):
            print(f"  {rule}")

    print("\n" + "=" * 60)


def interactive_mode(service):
    """対話モードでイベント情報を取得"""
    # カレンダー選択
    calendars = list_calendars(service)

    if not calendars:
        print("利用可能なカレンダーがありません。")
        return

    print("\nカレンダー番号を選択してください (デフォルト: 1): ", end="")
    try:
        choice = input().strip()
        cal_index = int(choice) - 1 if choice else 0
        if cal_index < 0 or cal_index >= len(calendars):
            cal_index = 0
    except ValueError:
        cal_index = 0

    calendar_id = calendars[cal_index]['id']
    print(f"選択されたカレンダー: {calendars[cal_index]['summary']}")

    # 検索キーワード
    print("\n検索キーワードを入力 (空欄で全件表示): ", end="")
    query = input().strip() or None

    # 検索期間
    print("過去何日間を検索？ (デフォルト: 30): ", end="")
    try:
        days_back = int(input().strip() or "30")
    except ValueError:
        days_back = 30

    print("未来何日間を検索？ (デフォルト: 90): ", end="")
    try:
        days_forward = int(input().strip() or "90")
    except ValueError:
        days_forward = 90

    # イベント検索
    events = search_events(service, calendar_id, query, max_results=500, days_back=days_back, days_forward=days_forward)

    if not events:
        return

    # イベント選択
    print("\n詳細を表示するイベント番号を選択 (0で終了): ", end="")
    try:
        event_choice = int(input().strip())
        if event_choice == 0:
            return
        if event_choice < 1 or event_choice > len(events):
            print("無効な選択です。")
            return
    except ValueError:
        print("無効な入力です。")
        return

    # イベント詳細取得・表示
    selected_event = events[event_choice - 1]
    event_details = get_event_details(service, calendar_id, selected_event['id'])

    if event_details:
        display_event_info(event_details)


def main():
    """メイン関数"""
    print("Google Calendar イベント情報取得ツール")
    print("-" * 40)

    try:
        service = get_calendar_service()
        interactive_mode(service)

    except KeyboardInterrupt:
        print("\n終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
