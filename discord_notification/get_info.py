import os
from WeWard2 import WeWard
from lib_discord import set_base_embed, create_field_by_account, create_field_total

def get_profile_data() -> list:
    path = os.path.join(os.getcwd(), "../sessions")
    sessions_files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".json")
    ]
    sessions = []
    for fname in sessions_files:
        try:
            s = WeWard()
            s.load_session_no_print(os.path.join(path, fname))
            profile_data = s.get_profile_no_print()
            sessions.append(profile_data)
        except Exception:
            pass
    return (sessions)

async def send_daily_notification(client, channel_id:int) -> None:
    sessions = get_profile_data()
    today_total:list = [0.0, 0.0]
    account_total:list = [0.0, 0.0]
    embed = set_base_embed("WeWard | Actual balance", "", 0x17D0A6)
    for i in range(len(sessions)):
        account_name:str = (str)(sessions[i]['username'])
        kward_to_eur:float = (float)(sessions[i]['kward_to_eur'])

        today_balance_W:float = (float)(sessions[i]['today_balance'])
        today_balance_E:float = today_balance_W * kward_to_eur
        today_total[0] += today_balance_W
        today_total[1] += today_balance_E

        total_balance_W:float = (float)(sessions[i]['balance'])
        total_balance_E:float = total_balance_W * kward_to_eur
        account_total[0] += total_balance_W
        account_total[1] += total_balance_E
        embed = create_field_by_account(embed, account_name, today_balance_W, today_balance_E, total_balance_W, total_balance_E)
    embed = create_field_total(embed, "/!\ Total", today_total, account_total)
    channel = client.get_channel(channel_id)
    await channel.send(embed = embed)
