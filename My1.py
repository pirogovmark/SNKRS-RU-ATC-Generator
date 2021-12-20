import telebot
import urllib.request
from telebot import types
from datetime import datetime
from time import sleep



def ATC(link):
    if link[0] != 'h':
        link = 'https://' + link

    # Getting SKU and ProductID
    webUrl = urllib.request.urlopen(link)
    data = str(webUrl.read())

    numb = data.find('productId') + 20
    id = ''
    while data[numb] != '"':
        id += data[numb]
        numb += 1

    numb = data.find('styleColor') + 21
    sku = ''
    while data[numb] != '"':
        sku += data[numb]
        numb += 1

    # Getting Size, Stock and Example URL
    url_stock = "https://api.nike.com/deliver/available_gtins/v2/?filter=styleColor(" + sku + ")&filter=merchGroup(XP)"
    url_size = "https://api.nike.com/merch/skus/v2/?filter=productId%28" + id + "%29&filter=country%28RU%29"
    xmpl = link + "?productId=" + id + "&size="

    # Getting Gtin and Stock Info
    webStock = urllib.request.urlopen(url_stock)
    stock = str(webStock.read())
    stock2 = stock

    # Gtin
    gtin_all = []
    gtin_ind = stock.find('gtin')

    while gtin_ind != -1:
        gtin_info = ''
        gtin_ind += 7
        while stock[gtin_ind] != '"':
            gtin_info += stock[gtin_ind]
            gtin_ind += 1

        gtin_all.append(gtin_info)

        stock = stock[gtin_ind + 15::]
        gtin_ind = stock.find('gtin')

        # Stock
    stock_all = []
    stock_ind = stock2.find('level')

    while stock_ind != -1:
        stock_info = ''
        stock_ind += 8
        while stock2[stock_ind] != '"':
            stock_info += stock2[stock_ind]
            stock_ind += 1

        stock_all.append(stock_info)

        stock2 = stock2[stock_ind + 10::]
        stock_ind = stock2.find('level')

    # Getting Size Info with Gtin
    webSize = urllib.request.urlopen(url_size)
    size = str(webSize.read())
    size2 = size

    # Gtin
    gtin_all_2 = []
    gtin_ind = size.find('gtin')

    while gtin_ind != -1:
        gt = ''
        gtin_ind += 9
        while size[gtin_ind] != '"':
            gt += size[gtin_ind]
            gtin_ind += 1

        gtin_all_2.append(gt)

        size = size[gtin_ind + 20::]
        gtin_ind = size.find('gtin')

        # Size
    size_all = []
    size_ind = size2.find('nikeSize')

    while size_ind != -1:
        sz = ''
        size_ind += 13
        while size2[size_ind] != '"':
            sz += size2[size_ind]
            size_ind += 1

        size_all.append(sz)

        size2 = size2[size_ind + 13::]
        size_ind = size2.find('nikeSize')

    # File Writing
    ATK = open('ATK.txt', 'w')
    Link = ''

    for i in range(len(gtin_all_2)):
        size_out = str(size_all[i]) + ' US'
        link = xmpl + str(size_all[i])
        stock_out = stock_all[gtin_all.index(gtin_all_2[i])]
        out = size_out + '\n' + link + '\n' + stock_out + '\n' + '\n'
        Link += out

    return Link


def date(link):
    if link[0] != 'h':
        link = 'https://' + link
    webUrl = urllib.request.urlopen(link)
    data = str(webUrl.read())
    k = data.find("available-date-component")
    if k == -1:
        return "Ex"
    return data[k + 91:k + 91 + 5] + data[k + 91 + 15:k + 91 + 20]


def if_expired(link):
    drop_date_and_time = date(link)
    if drop_date_and_time == "Ex":
        return False

    drop_month = int(drop_date_and_time[:2])
    drop_number = int(drop_date_and_time[3:5])
    drop_hour = int(drop_date_and_time[5:7]) + 2

    today_month = int(datetime.today().strftime('%m'))
    today_number = int(datetime.today().strftime('%d'))
    now = datetime.now()
    current_hour = int(now.strftime("%H"))

    print(drop_month, drop_number, drop_hour)
    print(today_month, today_number, current_hour)
    if (drop_month == today_month):
        if (drop_number == today_number):
            return (current_hour < drop_hour)
        elif (drop_number > today_number):
            return True
        else:
            return False
    elif (drop_month > today_month):
        return True
    else:
        return False






bot = telebot.TeleBot("1635619338:AAGcfKRIueu-vKi3ROCa8J4PaXtrY5CbM9w")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me link from SNKRS")

@bot.message_handler(func=lambda message: True)
def give_atc(message):
    if message.text.find('www.nike.com/ru/launch/t/') != -1:
        # Saving link from user
        Link = open('Link.txt', 'w')
        Link.write(message.text)
        Link.close()


        if (if_expired(message.text)):
            bot.send_message(message.from_user.id, ATC(message.text))

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item_1 = types.KeyboardButton("Yes")
            item_2 = types.KeyboardButton("No")
            markup.add(item_1, item_2)

            bot.send_message(message.from_user.id, 'Do you want to be reminded 15 minutes before the drop?', reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, 'Expired date of this release')

    elif message.text == "Yes" or message.text == "No":
        if message.text == "Yes":
            Link = open('Link.txt', 'r')
            drop_date_and_time = date(Link.readline())
            Link.close()
            drop_date = drop_date_and_time[:5]
            drop_time = drop_date_and_time[5:]
            today = datetime.today().strftime('%m/%d')
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            bot.send_message(message.from_user.id, 'You will get notification 15 minutes before the drop')

            while (current_time != (str(int(drop_time[:2]) + 2) + ':45') or today != drop_date):
                sleep(60)
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                today = datetime.today().strftime('%m/%d')
            bot.send_message(message.from_user.id, 'Be ready for the drop. Good luck)')

    else:
        bot.send_message(message.from_user.id, 'Wrong link. Try again with another link')


bot.polling()
