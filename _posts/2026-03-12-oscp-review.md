---
title: OSCP Exam Review 
description: >-
 Reviewing the OSCP Exam
author: r3d0t
date: 2026-03-12 10:41:00 -0500
categories: [Blog, OSCP]
tags: [oscp, ethical hacking, certificates, penetration testing, pentesting, penetration tester, oscp review, exam ]
pin: false
media_subpath: ''
comments: true
image: /post_images/Offsec.jpg
---

I passed the OffSec Certified Professional (OSCP) in March 2026, on my second attempt. My first attempt was in December 2025.

## Why the OSCP?

Why not?

The OSCP is still one of the names that instantly gets recognized in the security space. It won’t make you the best hacker, and it doesn’t replace real world experience. But if you get the opportunity, especially if you’re not paying for it out of your own pocket, it’s hard to argue against taking it.

## The OSCP Exam – Round 1

I won’t pretend I walked into my first attempt overflowing with confidence. I was nervous, yet excited at the same time. There’s a specific kind of thrill that comes from knowing you’re about to test yourself against something difficult.


My game plan going in the exam was simple: have my notes ready, have a few trusted references open (HackTricks, HackViser, etc.), and let Google fill in the gaps when needed.

I was pretty new to the whole proctoring experience, so that made me anxious. Having someone on the other side of the screen that you can't see, but they can see you isn't fun at all. I also had a preview of my webcam feed so I could see myself, making sure I wasn't doing anything strange that could violate offsec policy. That was not the best idea since it made me stress even more.

The pre-exam checks went smoothly overall, except: the proctor noticed TeamViewer installed on my computer. It wasn’t running, but that didn’t matter, I had to uninstall it before I could start the exam. So, I did.

Once I finally got into the exam, things settled. I worked through the machines, starting with the Active Directory Set. At some point, I had 50 points with several hours left on the clock. I only needed 20 more points to pass the exam.

I could go after the Domain Controller’s (DC) flag for 20 points, or I could try to squeeze 2 × 10 points out of the standalone machines by getting the missing flags there.

At that point, I had one standalone fully compromised (user and root), user on another, and I was close to getting the DC flag. I had the DC credentials; I just needed to decrypt them. In my head, the DC felt like the cleaner, easier play. I was already halfway in. It looked like the easiest path to my 20 points.

So, I focused on getting the DC flag. I tried every technique I could recall. I went back to my notes, back to Google, back to every mental drawer where I store “things that might help decrypt this kind of credential.”

Nothing worked. When the clock finally ran out, I was still stuck. No DC flag. No extra standalone flags. Just a flat 50 points.

Fail. 

## After Failing the First Attempt (The Redemption Arc)

After the exam ended, I decided to wrap up my report just so I could have it for review.

Since I’d been documenting everything during the exam, most of the heavy lifting was already done. I had the report template formatted and open before the exam even started. Screenshots were in place. The exploit I’d modified, a C exploit I had to tweak to fit my needs, was already explained, line by line, with what I changed and why. For the flags I had failed to obtain, I wrote out the approaches I had tried and the ideas I’d test if I ever saw those machines again.

Emotionally, I was locked onto one thing: those damn credentials I couldn’t decrypt.

At first, I wasn’t even sad about failing. I was curious. I wanted to understand what I’d missed. I went down a rabbit hole of documentation, blog posts, forum threads, anything that mentioned that type of credential. I kept digging until, eventually, I found a guide that laid out exactly how to decrypt them.

Seeing the solution laid out hurt in a very specific way. I felt that if I had known this one extra piece during the exam or if I had just a few more hours, I probably would have passed.

That’s when the emotions caught up. The disappointment and the frutration.

I was disappointed, but I also knew this: If I took the exam again, I had a very real shot at passing.

## The OSCP Exam – Round 2 (Rematch)

For my second attempt, I was a bit more relaxed. The fear of the unknown was gone. I knew what the proctoring felt like, how quickly time moved, and where I tend to get anxious.

What I didn’t fully have back yet was my belief in myself.

When the day came for the exam, I had everything ready. My Kali VM was already running. Obsidian was open with my notes and templates. I even had my report from the first attempt available, in case I ran into the same machines again, which I was hoping to.

The pre-exam steps with the proctor went smoothly again, but this time I changed one small detail: I turned off the webcam preview. I didn’t want to see my own face. I didn’t want to monitor every twitch and eye movement. That single change lowered my anxiety more than I expected. I could forget about the camera and just work.

Then, I started enumerating some of the machines and eventually I realized that none of the machines from my first exam were there.

The machines I’d hoped to “redeem,” the ones I wanted a rematch with, didn’t show up. Brand new targets. It felt like a new exam.

This set of machines felt tougher. Not impossibly hard, but less straight forward. I followed the same methodology: enumerate, document, pivot, reassess.

By sometime between 10 and 11 PM, I had 60 points. It was deja vu with 10 more points left.

I was working on a standalone box that looked promising. I had some credentials that should have worked but didn’t.

At that point, I started thinking about sleep.

Part of me wanted to shut everything down, go to bed, and try a different machine in the morning with a fresh mind. I even set an alarm for 11:55 PM as a hard cutoff. Once that alarm went off, I would stop.

But between setting the alarm and the time it actually rang, I kept trying to understand the machine. I tried a few more small variations, different combinations, slight changes. 

And then, suddenly, it worked.

The credentials went through. I got in. I set up a reverse shell, pulled the user flag, took the screenshot, and did the math lol. I had the 70 points required to pass the exam.

Once again, my habit of writing the report in parallel paid off. Most of the content was already there. All I needed to do was stitch it together, add a few words between the screenshots and commands, and make sure everything met OffSec’s requirements. I finished and submitted my report around 2 AM in the morning (Sunday), thanked the proctor, turned off my computer, and went to bed.

I checked Offsec Dashboard later around 10pm, and I saw that I had passed the exam. The official email came around 2 AM on Monday.


## My thoughts

Looking back, I don’t think the OSCP is a super advanced or difficult exam. Technically, it’s challenging but not absurd. You don’t need to pull off some crazy exploits or techniques to pass. You might run into a harder than average machine or two, but nothing advance.

The real difficulty is in the range of possible techniques you can use and the discipline it takes to not get lost in that space. It’s the ability to recognize when you’re stuck in a rabbit hole, chasing a dead end because you’re emotionally invested in “making it work.”

Credentials, in particular, messed with my head. A password is just a password, but the username that goes with it can change everything. The same password might be valid for multiple accounts, each with different privilege levels. You can spend an absurd amount of time trying to force your way in as the wrong user while the right one is a few rows down in a file you thought you’d already carefully read.

Another lesson was that the answer isn’t always “run another exploit” or “launch another enumeration script.” Sometimes the thing you need is right there in a config file, a scheduled task, a weird permission, or a piece of console history. 

Also sometimes the thing that’s “broken” isn’t the target, but your own tool, misconfigured or missing a dependency.

That’s why methodology matters so much. Without a clear process, it’s easy to mistake motion for progress. For me, having a mental checklist when I landed on a new machine kept me grounded: check the running services, understand who’s logged in, enumerate users, know the version of the OS and environment, look for stored credentials, inspect history files, and so on. Then move to the next layer. And the next. One step at a time.

PEN_200 helped give names and structure to techniques, but it didn’t, and I don't think it supposed to give me an answer key to the exam. I believe the OSCP is designed to push you into situations where you don’t have step by step instructions. It’s less about, “Do you know this exact command?” and more about, “Can you figure it out and adapt?”

In the end, that’s what I took away from the whole experience.

## My tips and advice

[Hacktricks](https://hacktricks.wiki/en/index.html), [Hackviser](https://hackviser.com/tactics/pentesting) & [HackingArticles](https://www.hackingarticles.in/) were my go to resources. I found myself on those websites quite a lot during the exam while I was googling things. They are extremely valuable resources.

The [Hacker Blueprint's](https://www.youtube.com/watch?v=ey_GeabfQpg&list=PLM1644RoigJvm0L7RcK-64aVTp1vZkDv5) videos are probably some of the best videos I have seen when it comes to Active Directory. He has a very good methodology, I highly recommend watching his videos and his channel in general.

Breaks are important. I took a lot more breaks during my second attempt compared to my first attempt. I used this [online clock](https://vclock.com/) to set an alarm reminding (forcing) myself to take breaks.

When pivoting with chisel and proxychains, always check your tunnel when a command suddenly stops working. Sometimes the tunnel just dies. People recommending ligolo-ng are right. What I like to do is keep multiple terminal windows open (I had around eight), with two dedicated to the chisel client and server so I can see instantly when the tunnel breaks. You could also try [zellij](https://zellij.dev) which a friend recommended recently.

As you work on the machines, take screenshots and save them in obsidian. I had 2 screens I was working on, my Kali VM on one, and my notes, obsidian, and everything else on the other screen. That helped.

Message the proctor whenever you need to do something, but you don't have to wait for them to respond. Also, if you are not sure of something ask for clarification before you do it.

Building your methodology is way more important than building your notes. There are thousands of public notes you can borrow any time. Your methodology is unique to you. Figure out what works, what feels natural, what actually clicks in your head.


That’s all I can think of for now. I’m probably forgetting a few things, but I’m always happy to answer questions. If you’re taking or planning to take the OSCP, remember: pass or fail, you’re still learning. 



