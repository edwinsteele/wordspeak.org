.. title: Developing on an iPad
.. slug: developing-on-an-ipad
.. date: 2014/10/05 12:55:47
.. tags: Technical, UNIX, iPad
.. link:
.. description:

# Surely I won't need my laptop
I pack lightly when I travel so I left my laptop at home when we did a recent overseas trip to visit family. I didn't anticipate writing any code or doing anything technical on holidays because I was tired from work, so leaving my laptop at home seemed like a good choice. And then I relaxed, and found a bit of mental energy and I wanted to do exactly what I'd expected not to do. So there I was with my iPad and Bluetooth keyboard, eager to do something technical and figuring that I'd be interesting to have a go with what's at hand.

# And then I attempt a significant upgrade using the iPad
I decided to try a significant upgrade of [Nikola](http://getnikola.org), which I use to publish this site. I'd fallen behind several versions, and there were a number of non-trivial breaking changes that I'd need to work through. Most of this task was unix command-line, text-file editing, a bit of python, reviewing web pages and reading doco. I'd have normally done it offline on my Macbook, but my tools in this case were:

* A 3rd gen iPad.
* A Logitech ultra-thin keyboard cover
* Prompt by Panic (a terminal emulator with ssh)
* A browser (or two)
* my EC2 instance running CentOS 6
* vi for editing

# It's quite effective, once you get used to it

Here's what I found:

* The Logitech keyboard lacks an ESC key, and in its place has the home button. As vi makes extensive use of the ESC key and I have many years of muscle memory with it at the top left of the keyboard, I found myself being kicked out of Prompt with great regularity. Fortunately Prompt allows me to create a ESC soft key, and I've positioned it just above the physical home key on the keyboard, which has helped considerably.
* Prompt doesn't seem to have a copy-and-paste function which is very frustrating. I really hope Prompt2 has it. I tried to setup iSSH but couldn't get access to my private SSH key so I found myself using `:r!grep -A search_term filename` in vi to selectively suck in contents of files to my editor session
* I miss being able to view two apps side-by-side, but a half-swipe in the app switcher is a pretty good workaround. The high-res retina display really shines in this use-case...
* but the app switcher is slow on my iPad 3 (it seemed to slow down on the iOS 6-7 upgrade, I think)
* Having my dotfiles accessible on github made it quite easy to recreate the important bits of my editing environment on the EC2 instance.
* tmux rocks, it allows me to do split screen editing and allows trivial session restoration, which is important because...
* Prompt looses connectivity to the server after a couple of minutes in the background, but setting the initial session command in Prompt to: `tmux attach || tmux`, along with the ssh agent makes restoring my current state a 5 second process.
* I miss being able to "print" PDFs of some pages, which is helpful for capturing receipts. There's no obvious solution but needing to live without something helps question its value, and I'm now less attached to capturing receipts in this manner.

# And I'd do it again
I was surprised how effectively I was able to work. The experience would be better with a terminal client that supported copy-and-paste, a client that maintained connectivity for longer and a keyboard that had a physical ESC key but otherwise it was quite acceptable. It's not my work platform of choice, but if I didn't expect to do a significant amount of work, and had a stable network connection, I'd do it again.
