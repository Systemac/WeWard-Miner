# WeWard-Miner
With **WeWard-Miner** you can easily farm accounts or points. The project is based on the "WeWard" class, which contains all the main methods for the most common functions such as:
- Create account
- Sponsor account
- Validate steps
- Watch ads video

### Usage
Install all the requirements from requirements.txt files and then create your script or use one of my POC.

#### Recover account

You can retieve an account with:
```sh
python request_account.py <email>
```
- You will need to access your mailbox and copy the link on the Weward login button to enter it when the script tells you to.
- At the end, the script will generate a session `.json` file.

#### Create account

You can create a new account with:
```sh
python farm_accounts.py <email> <password>
```

- The email password is required so we can use IMAP for reading emails and validate your account.
- Remember to change the host, based on your email service. [#148](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#148)
- If you want a different lang or country than **IT** change the lines [#L34-L35](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#L34-L35) or use `change_country` method.
- If you use the script `farm_accounts.py`, the new account will be automatically referred by my user code. Remember to change this code if you want to referral with your [#L232](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#L232)
- At the end, the script will generate a session `.json` file

#### Farm points
Basically you need just to load the class with the `.json` session file, submit the steps, validate the steps and jobs It's done.
```python
from WeWard import WeWard
weward = WeWard()
weward.load_session("session.json")
weward.push_step_record(25000)
weward.valid_step()
```

The method `push_and_validate_step`, used also in the script `farm_points.py`, automatically pushes the steps and then performs validate operations. I've created this method because I want to solve the challenge and submit the steps periodically during the day. So, the method takes at first argument an integer **job_number**, that corresponds to the times the method was called in a single day.

____

If you like my work and you want to support me, you can offer me a coffee, I would be grateful ❤️

<a href="https://www.buymeacoffee.com/tkdalex" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/lato-yellow.png" alt="Buy Me A Coffee" height="41" width="174"></a>

|                                                                                                                                                                                                                                                                                                           |                                               |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| <img src="https://dynamic-assets.coinbase.com/e785e0181f1a23a30d9476038d9be91e9f6c63959b538eabbc51a1abc8898940383291eede695c3b8dfaa1829a9b57f5a2d0a16b0523580346c6b8fab67af14b/asset_icons/b57ac673f06a4b0338a596817eb0a50ce16e2059f327dc117744449a47915cb2.png" alt="Donate BTC" height="16" width="16"> | `36GSMYngiiXYqBMnNwYwZc8n6s67LGn4V5`          |
| <img src="https://dynamic-assets.coinbase.com/dbb4b4983bde81309ddab83eb598358eb44375b930b94687ebe38bc22e52c3b2125258ffb8477a5ef22e33d6bd72e32a506c391caa13af64c00e46613c3e5806/asset_icons/4113b082d21cc5fab17fc8f2d19fb996165bcce635e6900f7fc2d57c4ef33ae9.png" alt="Donate ETH" height="16" width="16"> | `0x3cc331b8AB0634CCcfa3bd57E0C625F7E886cAfa`  |
| <img src="https://dynamic-assets.coinbase.com/d2ba1ad058b9b0eb4de5f0ccbf0e4aecb8d73d3a183dbaeabbec2b6fd77b0a636598e08467a05da7e69f39c65693f627edf7414145ee6c61e01efc831652ca0f/asset_icons/8733712db93f857c04b7c58fb35eafb3be360a183966a1e57a6e22ee5f78c96d.png" alt="Donate SOL" height="16" width="16"> | `pg8Z2VqMVskSEA77g5QqppaQjehGGCWJfVPw9n91AX1` |

### Disclaimer
This project comes with no guarantee or warranty. You are responsible for whatever happens from using this project. It is possible to get soft or hard banned by using this project if you are not careful. This is a personal project and is in no way affiliated with WeWard.
