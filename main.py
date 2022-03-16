import discord
import json
import gspread
import random
from datetime import datetime
from datetime import timedelta
from oauth2client.service_account import ServiceAccountCredentials

client = discord.Client()

with open('names.json', encoding="utf8")as namesFile:
    names = json.load(namesFile)

days_EN = ("Monday", "Tuesday", "Thursday", "Wednesday", "Friday")
days_PL = ("PONIEDZIAŁEK", "WTOREK", "ŚROD", "CZWARTEK", "PIĄTEK")

awaits = ["Już patrzę :blush:",
          "Sekundka :face_with_monocle:",
          "Momencik :relaxed:",
          "Zaraz poszukam :studia:"
          ]

def rowToHour(row):
    hour = 8
    min = 0
    for i in range(1, row):
        min+=15
        if(min >= 60):
            min = 0
            hour+=1
    if(min == 0):
        return str("{}.00".format(hour))
    else:
        return str("{}.{}".format(hour, min))
def getData(requestedDay, who):
    global embedMessage

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    gclient = gspread.authorize(creds)
    sheet = gclient.open("[3EiT/3E/3E&T] Podział grup").sheet1
    vals = sheet.get_all_values()
    colStart = 0
    countFLag = 0
    colEnd = 0

    wyklady = []
    przedmioty = []
    for i in range(0,len(vals[0])):
        if (countFLag == 1 and vals[0][i] != ''):
            colEnd = i
            countFLag = 0
        if(requestedDay in vals[0][i]):
            colStart = i
            countFLag = 1

    for rows in range(0, len(vals)):
        for cols in range(colStart, colEnd):
            if("[W]" in vals[rows][cols]):
                wyklady.append(str("**"+vals[rows][cols] + "** __" + rowToHour(rows)+"__\n"))
            if(who in vals[rows][cols]):
                przedmioty.append(str("**"+vals[rows][cols][0:vals[rows][cols].find(']')+1] + "** __" + rowToHour(rows)+"__\n"))

    if(requestedDay.lower() == "środ"):
        requestedDay = "środę"
    embedMessage = discord.Embed(title="{}! Twój plan na {}:".format(who,requestedDay.lower()), colour=discord.Colour.from_rgb(234, 46, 255))
    embedMessage.add_field(name="Wykłady", value=str(wyklady)[1:len(str(wyklady))-1].replace('\'', '').replace(',','').replace("\\n", "\n"), inline=True)
    embedMessage.add_field(name="Przdmioty", value=str(przedmioty)[1:len(str(przedmioty))-1].replace('\'', '').replace(',','').replace("\\n", "\n"), inline=True)
    return embedMessage

@client.event
async def on_ready():
    print(f'{client.user} has connected')

@client.event
async def on_message(message):
    global askedDay, askedName, flag
    if message.author == client.user:
        if(flag==1):
            await message.edit(content="", embed=getData(askedDay, askedName))
        flag = 0
        return
    elif message.content.lower().startswith("co w") and message.content.endswith("?"):
        for i in range(len(days_PL)):
            if str(days_PL[i]).lower() in message.content.lower():
                askedName = names[str(message.author.id)]
                askedDay = days_PL[i]
                flag = 1
                await message.channel.send(awaits[random.randint(0,len(awaits)-1)])
    elif "co jutro" in message.content.lower() and message.content.lower().endswith('?'):
        try:
            tommorow = datetime.today() + timedelta(days=1)
            askedName = names[str(message.author.id)]
            askedDay = days_PL[tommorow.timetuple()[6]]
            flag = 1
            print(len(awaits))
            await message.channel.send(awaits[random.randint(0,len(awaits)-1)])
        except:
            await message.channel.send("Coś poszło nie tak :sweat_smile:\nCzy napewno jutro jest szkółka?")
    elif message.content.lower().startswith("co dzi") and message.content.lower().endswith("?"):
        try:
            askedName = names[str(message.author.id)]
            askedDay = days_PL[datetime.today().timetuple()[6]]
            flag = 1
            await message.channel.send(awaits[random.randint(0,len(awaits)-1)])
        except:
            await message.channel.send("Coś poszło nie tak :sweat_smile:\nCzy napewno dzisiaj jest szkółka?")

client.run("TOKEN :)")