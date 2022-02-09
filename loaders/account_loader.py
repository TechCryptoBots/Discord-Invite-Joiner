from typing import List


class Account:

    def __init__(self, account_id, auth_token, proxy='') -> None:
        self.auth_token = auth_token
        self.use_proxy = False
        self.account_id = account_id
        self.proxy = proxy


class AccountLoader:

    def __init__(self, accounts_file, proxy_file=None) -> None:
        self.accounts_file = accounts_file
        self.proxy_file = proxy_file

    def load_accounts(self) -> List[Account]:
        accounts_set = open(self.accounts_file, 'r',
                           encoding='utf-8').read().splitlines()
        account_list = []        
        
        for i, token in zip(range(1, len(accounts_set)+1), accounts_set):
            account_list.append(Account(i, token))
            
        if self.proxy_file:
            proxies = open(self.proxy_file, 'r',
                           encoding='utf-8').read().splitlines()
            
            for i in range(len(proxies)):
                account_list[i].proxy = proxies[i]
            
        

        return account_list
