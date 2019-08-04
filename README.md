# exmetacrawler
My MESSY and BUGGY crawler for ExHentai metadata. Can generate A SINGLE json file like (at least looks like) Sachia Lanlus's [gdata](https://mega.nz/#F!oh1U0SIA!WBUcf3PaOvrfIF238fnbTg), 
and functionally worked with Tlaster's [Ehdb](https://github.com/Tlaster/ehdb).
No, it's not originally for this. It's originally a part of my updater for my local exhentai metadatabase (in SQLite).

#Usage:
`exmetacrawler.py [-t <OldestTimestamp to Search>] [-o <outputfile>] [-m <ipb_member_id>] [-p <ipb_pass_hash>]`
 
##Arguments:
* -t <timestamp>: Oldest timestamp to search. Default: input from file 'latestPosted'
* -o <filename>: Output file name. Default: gdata.json
* -m <ipb_member_id>: Set 'ipb_member_id' of cookie manually. Default:9999999 (Unusable)
* -p <ipb_pass_hash>: Set 'ipb_pass_hash' of cookie manually. Default:ffffffffffffffff (Unusable)

Run it with command line, set your cookie, then wait, and u will get (at least I got) a .json file.

---
Maintaince? Maybe no, cuz my goal has been achieved. :)
