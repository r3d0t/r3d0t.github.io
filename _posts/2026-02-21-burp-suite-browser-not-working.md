---
title: Burp Suite browser not working (Fix)
description: >-
 Fixing an issue with the browser within Burp Suite on Linux
author: r3d0t
date: 2026-02-21 16:03:00 -0500
categories: [Application Security, Burp Suite, Browser Issue]
tags: [burp suite, chromium, linux]
pin: true
media_subpath: ''
comments: true
image: /Burp_Suite/burp_suite_icon.png
---

I ran into an issue where Burp Suite’s embedded Chromium browser wouldn’t launch on Linux. 

These are the steps that fixed it.

> This is a quick, common fix that adds a new setuid root binary to your system, which has security implications. It's good to be aware of that.
{: .prompt-warning}

## The less Secure & Common Fix

### 1. Find the `chrome-sandbox` binary

I used the installer.sh to install burp suite, so my path was something like this
```bash
~/BurpSuiteCommunity/burpbrowser/*/chrome-sandbox
```

If you’re not sure where it is, you can locate it with find:
```bash
find ~ -type f -name "chrome-sandbox"
```


You’ll likely see multiple versions. For example:

![listing_versions](/Burp_Suite/listing_versions.png)

In my case, the latest version was 

```bash
/home/kali/.BurpSuite/burpbrowser/142.0.7444.175/chrome-sandbox
```


```bash
cd /home/kali/.BurpSuite/burpbrowser && ls
```
![checking_versions](/Burp_Suite/checking_versions.png)

Then remove the ones you don’t want:

```bash
rm -rf 126.0.6478.126 137.0.7151.68 141.0.7390.65 142.0.7444.134
```
> Adjust to match the versions you actually have

### 2. Fix owner and permissions

```bash
# Replace the /path/to/chrome-sandbox with the actual path
sudo chown root:root /path/to/chrome-sandbox
sudo chmod 4755 /path/to/chrome-sandbox
```

This sets `chrome-sandbox` as setuid root, which Chromium’s sandbox requires on some Linux setups. Only do this if you are comfortable adding another setuid binary to your system.

You can verify it worked with
```bash
ls -l /path/to/chrome-sandbox
```


### 3. Launch the Burp browser

Close Burp Suite completely and reopen it, then try launching the embedde browser again.

In my case, it worked immediately without restarting Burp.
If it doesn’t for you, try fully closing Burp Suite and open it again before retrying.


## The less common & Secure Fix

If you’d prefer a more security-conscious approach, Anthony Hanel wrote [a great post](https://anthonyhanel.me/posts/Fixing-Burp-Suite's-Default-Browser-Ubuntu-24.04/) on confinement instead of adding another setuid binary. 

I have not personally used it to fix the issue I had, but, it's worth a read. 

His method doesn't rely on setting up a new setuid chrome-sandbox binary, which is a better long-term option if you care about security.