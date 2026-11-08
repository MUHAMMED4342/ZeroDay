ZERO DAY
An audio hacking game for blind and low-vision players

WHAT IS IT

Zero Day is a game you play with sound and text. You work through computer networks, one server at a time, to reach a target file. Most missions put you on the right side: a security tester hired by a hospital, an incident responder helping a company that was attacked, a rescue team looking for lost hikers. Every action you take leaves a trace. If your trace reaches 100 percent, the mission fails.

You do not need to see the screen. Sounds come from your left and right ear, so please use headphones.


WHAT YOU NEED

- Windows 10 or 11
- Headphones (stereo)
- Nothing else. The game is a folder called ZeroDay. Keep everything in it together. There is no installer.


STARTING THE GAME

1. Put the whole ZeroDay folder in a place you can write to, for example inside Documents. Do not put it in Program Files.
2. Open the folder and double-click ZeroDay.exe.
3. The first start can take a few seconds.
4. The cursor starts in the command box. Type help and press Enter.

If Windows shows a blue "Windows protected your PC" window, choose More info, then Run anyway. Some antivirus programs also warn about new, unsigned programs. The game does not need internet access and does not send any data anywhere.


THE WINDOW

The window has three tabs.

Terminal (Ctrl+1)   The game text and the command box.
Notes (Ctrl+2)      A text box for your own notes. It saves by itself.
History (Ctrl+3)    Every message from every game you have played, with a search box.

Ctrl+L        Go back to the command box.
Ctrl+M        Open the mission editor.
Ctrl+T        Open the translation editor.
Ctrl+Q        Quit.

If you use a screen reader, the game text is also sent to it as it appears. You can always read the Terminal tab line by line as well.

Your notes and history are saved in the folder .zeroday inside your user folder (for example C:\Users\YourName\.zeroday). They are kept between games.


HOW TO PLAY

A normal game goes like this:

1. Type scan. You hear a ping for each server you can see, and the game lists them.
2. Type connect and the server name, for example: connect gate.net
3. Type ports. The game lists the services on the server, with version and year.
4. Old software has security holes. Pick the oldest service and type exploit and its port number.
5. If the server needs more, use crack or tune (see Locks below).
6. When the game says the server is yours, type ls to see its files and read to read them. Files often contain hints.
7. New servers appear as you take over others. The mission text tells you which server holds the target.
8. Download the target file with get and its name. That ends the mission with a win.

Commands do not need exact capital letters. You can type the first letters of a file or server name, for example connect gate or read notes.


COMMANDS

help                 Show the command list.
scan                 List the servers you know about. Each one pings from a different place from left to right.
connect <name>       Connect to a server you have found.
disconnect           Leave the current server.
ports                List the services on the connected server.
exploit <port>       Attack a service on that port.
crack                Open a tone lock.
tune                 Open a frequency lock.
ls                   List files (only on servers you own).
read <file>          Read a file.
get <file>           Download a file. The target file ends the mission. Some other files are worth credits.
wipe                 Delete your tracks on this server. Lowers trace. Works once per server.
status               Show your trace, your credits and where you are connected.
shop                 Show the black market.
buy <item>           Buy an item with credits.
inv                  Show what you own.
use <item>           Use an item.
voice on / off       Use a text-to-speech voice. Leave it off if you use a screen reader, or you will hear everything twice.
vol 0-10             Set the game volume.
quit                 Close the game.


LOCKS

Every server has one to three locks. Which locks a server has is part of the game, so read the files for hints.

Exploit    Attack an old service with the exploit command. Attacking a service that is up to date fails and raises your trace a lot.
Tune       A frequency lock. Press A or D to move a dial. A ping tells you which side the signal is on: a ping in your left ear means move left, in your right ear means move right. The pitch gets higher as you get closer. You have 14 tries.
Crack      A tone lock. The game plays a row of tones from 1 (lowest, left ear) to 4 (highest, right ear). Repeat the same row with the keys 1 to 4. Press R to hear it again, which costs a little trace.

A server becomes yours only after all of its locks are open, and the game tells you with a message and a rising sound. If you do not hear that message, the server still has another lock. A server can also be a trap, so read the files before you attack.


TRACE

Your trace is the slow ticking sound. The faster it ticks, the higher your trace is. The game warns you at 50, 75 and 90 percent. At 100 percent the mission fails.

Most actions add some trace. Wrong attacks and mistakes add more. You can lower it with wipe, with the Ghost Protocol item, and by luck.

Random events can happen while you play, for example an administrator logging in. Some raise your trace and some help you.


DOWNLOADING AND THE FIREWALL

A download takes about ten seconds. While it runs, a warning sound can come from one ear. Press A if it is in your left ear, or D if it is in your right ear. If you are too slow or press the wrong key, your trace goes up. Left and right arrow keys also work.


THE EQUIPMENT SHOP

You earn credits by taking over servers, by selling files and by luck. Spend them with shop and buy.

VPN Tunnel        Permanently lowers the trace you gain by 30 percent.
Tone Decoder      The next tone lock opens by itself.
Signal Jammer     The next download has no firewall alerts.
Ghost Protocol    Lowers your trace by 30 right away.


WHEN THE GAME ENDS

If you win, the game shows a rank (Ghost, Operator or Script Kiddie) based on how low your trace was. If the mission fails, you can start again. Press Enter when the game asks.


MISSIONS

A mission is a set of servers to break into, with its own story. At the start of every game the game lists the missions and asks you to type the number of one. Seven come with the game. If you are new, start with Training Lab: it teaches every lock step by step. The others are Open Doors (a hospital security test), Ransom Clock (helping a company that was hit by ransomware), Lost Signal (a search for lost hikers), Clean Water (protecting a water plant), The Missing Ledger (a court-ordered audit) and Zero Day.

You can write your own missions, so you do not have to break into the same company every time. Open the mission editor from the Tools menu (Ctrl+M).

1. Choose the language you write in, then give the mission a name and a short story.
2. Choose Add server. For each server give a name, an IP address and its services (port, name, version and year). Old versions look weak and new ones look safe, which is how players decide what to attack.
3. Choose the locks: a weak port to exploit, a frequency lock, a tone lock, or any mix. Choose how many credits the server pays.
4. Choose which servers must be taken over before this one appears. The start server needs none.
5. Write the files of the server, one per line, as: file name | text. Add a third part with a number to let players sell the file for credits, or the word target for the file that wins the game.
6. Choose the start server, then Save mission. The editor checks that the mission can be won and tells you what is missing.

TRANSLATING A MISSION
Open the mission, choose the language you want to translate into in the field "Language you are writing in", then choose Translate this mission. The editor reads you one text at a time: where it is used, the original text, and an empty box for your translation. Type it, then press Alt+N for the next one (Alt+P goes back). Leave a box empty to keep the original. Choose Done and save at the end. You never have to look inside the files.

Missions are saved in a folder named missions next to ZeroDay.exe. To share one, send the .json file. The other person puts it in the same folder.


TRANSLATION EDITOR

The translation editor (Tools menu, Ctrl+T) translates the whole game in one place, without opening any file: the game texts, and the texts of every mission.

1. Type the language code, for example tr, de or fr, and choose Start. If you translated before, your earlier work is loaded.
2. The editor reads you one text at a time: where it is used, the original text, and an empty box for your translation. It starts at the first text you have not translated yet. Mission texts start with the mission name, for example Open Doors: Story, paragraph 1.
3. Type the translation and press Alt+N for the next one (Alt+P goes back). Leave a box empty to keep the original text.
4. Keep any word in curly braces, such as {name}, exactly as it is. The game fills those words in while it runs. The editor warns you if you add one that the original does not have.
5. Players type the English commands (scan, connect, ports and so on) in every language. The box for command words is optional: fill it only if you want extra words in your language to work as well. The English commands always keep working.
6. Choose Done and save. The game texts are saved as lang\xx.json, and every mission that got a translation is saved in the folder missions next to ZeroDay.exe. Restart the game to use the new language.

Language codes: two letters such as fr, pt or de are best. The game reads your Windows language and looks for a file with that code. A regional code such as pt-br also works: a Windows set to Brazilian Portuguese uses pt-br.json first and then pt.json, and a Windows set to Portuguese in Portugal uses pt.json. If there is no file for the Windows language, the game stays in English.

You can stop at any time and come back later. Texts you skipped simply stay in English. When you add a new mission later, open the editor again and it will take you straight to the new texts.

Not translated on purpose: server names, IP addresses, port and service names, and file names.

If your Windows language is not the one you translated, create a text file named language.txt next to ZeroDay.exe with the language code on one line, for example: tr


LANGUAGES AND SOUNDS

The game uses your Windows language when a translation for it exists. English and Turkish are included. You can add more languages with the translation editor.

You can change things without any other tools. These folders are in the game folder, next to ZeroDay.exe:

lang      Put a translation file here, for example tr.json. The game picks it up on the next start if your Windows language matches.
sounds    Put sound files here to replace the built-in sounds. Files must be named like the original sound, for example click.ogg, click.mp3 or click.wav.
missions  Your own missions. The mission editor saves here.


PROBLEMS

Something went wrong and a window shows an error
The same text is saved in the file error.log inside the .zeroday folder of your user folder. Please send that file to the person who gave you the game.

No sound
Check that your headphones are the default Windows playback device, then restart the game. The game needs a stereo output.

I hear everything twice
You have the voice turned on and also use a screen reader. Type voice off.

The game says it does not know a command
Type help to see the exact words. Check for typing mistakes.

An editor cannot save
The game folder is probably protected. Move the ZeroDay folder into Documents.

The program does not start
Try running it again after moving it to Documents. If your antivirus removed it, add an exception for ZeroDay.exe.


LICENSE

This game is free and in the public domain (Unlicense). You can use it, change it, share it and sell it. Sound files that you add keep their own licenses.
