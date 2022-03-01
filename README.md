# WeWard-Miner
With **WeWard-Miner** you can easily farm accounts or points. The project is based on the "WeWard" class, which contains all the main methods for the most common functions such as:
- Create account
- Sponsor account
- Validate steps
- Watch ads video

### Usage 
Install all the requirements from requirements.txt files and then create your script or use one of my POC.

#### Create account

You can create a new account with:
```sh
python farm_accounts.py <email> <password>
```

- The email password is required so we can use IMAP for reading emails and validate your account.
- Remember to change the host, based on your email service. [#L153](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#L153)
- If you want a different lang or country than **IT** change the lines [#L33-L34](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#L33-L34)  
- If you use the script `farm_accounts.py`, the new account will be automatically referred by my user code. Remember to change this code if you want to referral with your [#L216](https://github.com/Tkd-Alex/WeWard-Miner/blob/main/WeWard.py#L216)
- At the end, the script will generate a session `.json` file

#### Farm points
Basically you need just to load the class with the `.json` session file, submit the steps, validate the steps and jobs It's done. 
```python
from WeWard import WeWard
weward = WeWard("session.json")
weward.push_step_record(25000)
weward.valid_step()
```

The method `push_and_validate_step`, used also in the script `farm_points.py`, automatically pushes the steps and then performs validate operations. I've created this method because I want to solve the challenge and submit the steps periodically during the day. So, the method takes at first argument an integer **job_number**, that corresponds to the times the method was called in a single day. 

### Disclaimer
This project comes with no guarantee or warranty. You are responsible for whatever happens from using this project. It is possible to get soft or hard banned by using this project if you are not careful. This is a personal project and is in no way affiliated with WeWard.
