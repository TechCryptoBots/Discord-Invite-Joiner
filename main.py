from argparse import ArgumentError
from loaders.account_loader import Account, AccountLoader
from loguru import logger
from tqdm import tqdm
from time import sleep
from sys import stderr
import json
import yaml
import requests
import random


def create_discord_session(account: Account):
    session = requests.Session()
    session.headers['authorization'] = account.auth_token
    session.headers.update(
        {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"})

    if account.use_proxy:
        session.proxies.update({'http': account.proxy, 'https': account.proxy})

    return session


def enter_server(invite_code, account=None, session=None):
    if not session:
        if account:
            session = create_discord_session(account)
        else:
            raise ArgumentError("No account/session provided")

    invite_link = f"https://discord.com/api/v9/invites/{invite_code}"
    r = session.post(invite_link)


def react_to_message(message_url, account=None, session=None):
    if not session:
        if account:
            session = create_discord_session(account)
        else:
            raise ArgumentError("No account/session provided")

    r = session.put(message_url)
    return r.status_code == 200 or r.status_code == 204


def accept_rules(server_id, account=None, session=None):
    if not session:
        if account:
            session = create_discord_session(account)
        else:
            raise ArgumentError("No account/session provided")

    rules_url = f"https://discord.com/api/v9/guilds/{server_id}/member-verification?with_guild=false"
    rules_response = session.get(rules_url)
    rules_response_json = json.loads(rules_response.text)
    rules = rules_response_json["form_fields"]
    for rule in rules:
        rule["response"] = True

    accept_url = f"https://discord.com/api/v9/guilds/{server_id}/requests/@me"
    data = {"form_fields": rules, "version": rules_response_json["version"]}
    r = session.put(url=accept_url, data=json.dumps(data),
                    headers={"Content-Type": "application/json"})


def start(config):

   
    invite_code = config["invite_code"]
    verification_reaction_url = config["verification_reaction"]
    giveaway_reaction_url = config["giveaway_reaction"]
    server_id = config["server_id"]
    accept_server_rules = config["accept_server_rules"]

    loaded_accounts = AccountLoader("accounts.txt").load_accounts()

    logger.info("Включаем бота...")
    successful_verification = 0
    successful_giveaway = 0
    for account in tqdm(loaded_accounts):
        session = create_discord_session(account)

        # Enter server
        enter_server(invite_code=invite_code, session=session)

        # If a server has rules, accept them
        if accept_server_rules:
            accept_rules(server_id=server_id, session=session)

        # Verify account on server
        verification_success = react_to_message(
            verification_reaction_url, session=session)
        if verification_success:
            successful_verification += 1

        sleep(1)

        # Enter giveaway
        raffle_success = react_to_message(
            giveaway_reaction_url, session=session)
        if raffle_success:
            successful_giveaway += 1

    if successful_giveaway == len(loaded_accounts):
        logger.success("Все аккаунты успешно нажали на реакцию для гива")
    else:
        logger.warning(
            f"Зашел в гив с {successful_giveaway}/{len(loaded_accounts)} аккаунтов")

    


if __name__ == "__main__":
    logger.remove()
    logger.add(
        stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>")

    random_number = random.randint(0, 19)
    if random_number == 5:
        logger.warning("Bot created by @tech_crypt0 (если вы купили этого бота или получили его в приватке, админ вас обманывает, бот бесплатный в нашем канале)")


    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Успешно прочитал конфиг")

    start(config)
    
    if random_number == 5:
        logger.warning("Bot created by @tech_crypt0 (если вы купили этого бота или получили его в приватке, админ вас обманывает, бот бесплатный в нашем канале)")


    print("Нажмите ENTER чтобы выйти")
    input()
