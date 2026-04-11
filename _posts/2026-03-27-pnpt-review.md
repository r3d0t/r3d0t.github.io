---
title: PNPT Exam Review 
description: >-
 Reviewing the PNPT Exam
author: r3d0t
date: 2026-03-27 18:15:00 -0500
categories: [Blog, PNPT]
tags: [oscp, ethical hacking, certificates, penetration testing, pentesting, penetration tester, pnpt review]
pin: false
media_subpath: ''
comments: true
image: /post_images/PNPT.png
---

I took and passed the Practical Network Penetration Tester (PNPT) exam in May 2025 on my first attempt.

## Why Go for the PNPT?

The PNPT is one of the most enjoyable and practical pentesting certifications out there, and compared to others in the field, it's affordable. It's also beginner friendly, making it a great choice for anyone curious about whether penetration testing is something they'd actually enjoy doing.

For me, the PNPT wasn't about chasing a credential. It was about testing myself, applying what I'd been learning casually, and seeing what a real penetration test feels like from start to finish.

## Before the PNPT (The Prelude)

Before starting the PNPT, I had already spent some time solving Hack The Box (HTB) machines. But back then, I didn't really have a solid process. My approach was basically to poke around, Google everything, and learn as I went.

I would often spend days, sometimes even weeks, on a single "easy" box. But honestly, I enjoyed that. There was no pressure. Every failed attempt just meant more late night reading, more small discoveries about services, ports, IPs, and subnets. Gradually, I started to see how all these pieces fit together and formed a system's attack surface. So while I wasn't completely new to pentesting, I knew I needed structure before tackling something like the PNPT.

That's what drew me to the Practical Ethical Hacking (PEH) course.

## How It Started: My Preparation Journey

I bought the PNPT voucher during the Black Friday 2024 sale and started the PEH course in January 2025. The course is taught by Heath Adams (aka The Cyber Mentor), who explains technical topics in a clear and practical way. His teaching style really stood out to me: easy to follow and grounded in real experience.

Even so, I hit a wall early on. After a few videos, I found myself struggling to remember what I'd watched. It took some reflection to realize that I learn best through reading, not watching videos. I can listen to videos just fine, but I retain information much better when I read, take notes, and study written materials.

The early parts of the course included notes and summaries, which helped a lot. But once those stopped appearing, I had to change my learning style. I kept watching the videos, but I also started doing a lot of reading. I went through HackTricks, technical blogs, and many Hack The Box write-ups.

During this time, I focused mostly on Windows and Active Directory (AD) machines. I wrote my own write-ups for each box I solved, compared my approach with others', and learned how different people can approach and think through the same problem. That process helped me build my own methodology.

When I wasn't studying, I often had IppSec videos playing in the background. For two or three months, that was basically the only YouTube channel I watched while relaxing or eating.

> I learn best by reading when I'm exploring something new, but once I understand the topic, I can easily switch to videos. The only thing I actually watch for fun is anime! :)
{: .prompt-info}

By early April 2025, I finally stopped overthinking and decided to take the exam in early May.

## The Exam (The Fight)

The exam lasted seven days: five days for hacking and compromising the Domain Controller (DC) and two days for writing and submitting the report.

Going into it, I was a bit anxious since I wasn't sure what to expect. It was my first time taking an exam like this. I was used to the usual multiple-choice format, but this one already felt different. I was excited and nervous at the same time.

The exam isn't proctored, which took some pressure off. It was just me, my PC, and my room; exactly how I like it.

Once I started, everything went smoothly. I received my VPN credentials and the Rules of Engagement (ROE) via email, which I read very carefully. I probably spent more time than needed going through it, but I wanted to be absolutely sure I didn't miss or do anything out of scope.

After that, I documented the IP addresses and got to work. As always, I began with information gathering, followed by port scanning and service enumeration to identify what I could access.

Everything was going well until I hit my first big roadblock after getting inside the network. Since I'm used to solving HTB machines, I initially defaulted to that mindset. I paused and thought, "Wait a minute, there's no flag here... so what am I chasing?"

In CTFs, your target is always a flag. For a second I completely forgot that in a real penetration test, there are no flags. Every step felt familiar to my CTF habits, but I needed to shift my perspective.

I decided to take a break and play one of my favorite games, Apollo Justice: Ace Attorney. During the second case, something in the storyline reminded me of what I needed to do, to look at the problem differently, or as Phoenix would say, "turn the case upside down."

That moment clicked for me. My real goal was to compromise the DC. Everything in between was just part of figuring out how to get there. There were no points for flags. I either owned the DC or I didn't.

After that, I began thinking like a real attacker, for real this time. I started mapping out the network, identifying IPs and hosts, and connecting pieces together. I had a blank sheet of paper (no lines. I can't think on lined paper!) and drew a small network map, labeling each host based on the information I found.

As I progressed, I refined that drawing until I no longer needed it. I had a mental map of the entire network and the systems I was interacting with.

Whenever a command didn't work, I asked ChatGPT to break it down for me line by line and explain what it did. Even when I already had an idea, I liked seeing how the explanation would sometimes reveal deeper insights or new ways to tweak the syntax for my situation. That approach helped me better understand some of the tools and scripts I'd picked up from blogs or write-ups.

It took me about four days to compromise the DC. To be honest, I spent a lot of that time playing Apollo Justice, taking naps, cleaning, and watching anime between attempts. For me, the exam felt like another game I needed to beat within five days. I already had a second attempt at no extra cost if I failed, so I stayed relaxed.

Once I finally compromised the DC, I couldn't resist doing something a little funny. Let's call it "Red Team flair." I left a small creative mark to prove I had control of the network, took a screenshot, and added it to my report.

After submitting, I let the timer run out in case I remembered something I'd missed and needed another screenshot. Then I left it running in the background and went back to my game.

### The Presentation

A few days later, I received an email confirming that my report had been accepted and that I could schedule my presentation. I was excited to walk through everything I'd done.

The presentation went smoothly. I explained how I approached the engagement, the vulnerabilities I found, and how I exploited them. I also highlighted what the "security team" did well, what could be improved, and gave specific recommendations on how to address the identified issues.

Of course, I shared the funny little thing I did at the end too.

The interviewer seemed genuinely pleased with my report and presentation. After I finished, he smiled, congratulated me, and told me that I'd passed the exam. I was stunned. I expected to wait a while for the results, so hearing it right then was a pleasant surprise, shocking and a huge relief.

And just like that, I had officially passed the PNPT on my very first attempt.

After the presentation, I finally had a moment to breathe and reflect on the whole experience; what went well, what surprised me, and what the PNPT really taught me.

## After the Exam: My Thoughts

The PNPT was a great experience and easily one of the most practical and realistic exams I've taken. It forces you to think like an attacker rather than just running commands. You can't simply copy commands from memory and expect results. You have to understand what each command does and why it works in that specific context.

The main goal is simple: compromise the Domain Controller (DC). But getting there feels like doing a real engagement. It's not a CTF. There are no flags. You have to move through the network, find entry points, pivot between systems, and validate every piece of access you get.

The process starts with OSINT (Open Source Intelligence). You gather information on the target, such as employee names, domains, and possible passwords, and use that as the foundation for attacks. The OSINT portion of the exam was fairly light, but it showed me how much more there is to learn in that area. Deep OSINT is its own skill set, and I'd like to explore it further.

After OSINT, the next stage is external enumeration. Tools like nmap help you discover the company's external IPs, open ports, and exposed services. Those are your possible footholds.

Once you're inside, the real work starts. You enumerate internal hosts, identify vulnerabilities, and pivot through the network toward the domain controller. Every set of credentials you find needs to be tested and validated. If you only have one piece of the puzzle, like a username or password, you can use password spraying to find the other.

It's a methodical process that requires patience and logic. It's less about chasing flags and more about thinking strategically, adapting, and connecting the dots in a live network.

One of the biggest takeaways from my PNPT journey wasn't just technical, it was learning how I learn. I realized I'm at my best when I can slow down, read, take notes, and connect ideas at my own pace. That process helps me understand why something works instead of just memorizing commands. Once the concept clicks, I can move on to videos or visual learning without struggling. Understanding that changed how I approach learning in general.











