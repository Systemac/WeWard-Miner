import discord
from datetime import datetime

from matplotlib.colors import hex2color

def get_localtime():
    current_time = datetime.now()
    return (current_time)

def set_base_embed(title:str, description:str, color:hex2color):
    embed = discord.Embed(
        title = title,
        color = color,
        description = description
    )
    embed.set_footer(text = "WeWard |", icon_url = "https://play-lh.googleusercontent.com/XmY7-isLvKgo2Ggvp2b34GBjC6hbyIJKRJIGp0y6r-r5a1FNfQTEcKgSUVXyxsB7XQ")
    embed.timestamp = get_localtime()
    return (embed)

def float_to_str(value_f:float, around:int) -> str:
    value_str:str = (str)(round(value_f, around))
    return (value_str)

def create_field_by_account(embed, account_name:str, today_balance_W:float, today_balance_E:float, total_balance_W:float, total_balance_E:float):
    message = "balance daily: " + float_to_str(today_balance_W, 2) + "W - " + float_to_str(today_balance_E, 2) + "€\n"
    message += "balance total: " + float_to_str(total_balance_W, 2) + "W - " + float_to_str(total_balance_E, 2) + "€"
    embed.add_field(name = account_name, value = message, inline = False)
    return (embed)

def create_field_total(embed, account_name:str, today_total:list, account_total:list):
    message = "reward daily: " + float_to_str(today_total[0], 2) + "W - " + float_to_str(today_total[1], 2) + "€\n"
    message += "reward total: " + float_to_str(account_total[0], 2) + "W - " + float_to_str(account_total[1], 2) + "€"
    embed.add_field(name = account_name, value = message, inline = False)
    return (embed)
