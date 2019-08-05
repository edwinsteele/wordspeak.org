<!--
.. title: Exploring Australian indigenous bible translation
.. slug: exploring-australian-indigenous-bible-translation
.. date: 2019-08-05 16:53:00 UTC+10:00
.. tags: 
.. category: 
.. speelcheck_exceptions: Kukatja,SIL's,AIATSIS,AUSTLANG,Tindale's,Jaru
.. link: 
.. description: 
.. type: text
-->

Everyone deserves to have access to the bible in their native language.

Given the large number of Australian indigenous languages, I wanted to see how far data could take me towards answering the question _Which Australian indigenous language group is most in need of bible translation?_

It turns out that data can go a long way. As to the question itself:

Spoiler: It's the [Kukatja](https://language-explorer.wordspeak.org/language/iso/kux.html) people in Western Australia.

I answered this question by writing some software to aggregate data on bible translation efforts, language groups, language relationships, speaker count and locations and English language competency. I used data from the [Joshua Project](https://www.joshuaproject.net), the [World Atlas of Language Structure (WALS)](https://wals.info), the [2011 Australian Census](https://www.abs.gov.au/websitedbs/D3310114.nsf/Home/Census), [SIL's ISO language code mappings](https://iso639-3.sil.org/), [Find A Bible](https://find.bible), [AIATSIS AUSTLANG](https://collection.aiatsis.gov.au/austlang/about) and [Tindale's Catalogue of Australian Aboriginal Tribes](http://archives.samuseum.sa.gov.au/tindaletribes/index.html) and after a bit of recent inspiration and rework I've published the output from the tool. Keep in mind that this was written as a proof-of-concept - the user interface has plenty of rough edges, and the data has only had limited review.

You can see it at [https://language-explorer.wordspeak.org](https://language-explorer.wordspeak.org).

# Why the Kukatja?

Most importantly, they don't have *any* of the bible in their native language. Given the first book of the bible to be translated is usually one of the gospels, a language group with even a single book has access to the key parts of the message of Jesus. Given everyone should have some chance to read about Jesus, it's important to prioritise a giving that first opportunity.
Secondly, while the Kukatja aren't the largest language group without bible access (that would be the [Jaru](https://language-explorer.wordspeak.org/language/iso/ddj.html)) their low (self-assessed) ability in Australia's national language, English, means that they can't use an English-language bible either, so they're quite stuck.

Here's output from the software showing only language groups without a bible (filter by _No Scripture_) and sorted by count of non English language readers.

{{% wordspeak_image cloudinary_id="language-table" title="Language table showing Kukatja as most in need" href="https://language-explorer.wordspeak.org/table.html" %}}

The software also has a map of language groups, with size corresponding to speaker count and colour showing scripture access (red circles are groups without any scripture, yellow circles are groups with only a single book of scripture)

{{% wordspeak_image cloudinary_id="language-map1" title="Filterable language map" href="https://language-explorer.wordspeak.org/map.html" %}}

The data shown in the software is a few years old, so it's quite possible that the Kukatja and the Jaru people have a bible translation underway, but I think there's promise in combining a data-driven approach with God's leading as we work towards giving everyone access to the bible in their native language. If you're interested in current Australian indigenous bible translation efforts, take a look at [Aboriginal Bibles](https://www.aboriginalbibles.org.au).

The source code is available on [Github](https://github.com/edwinsteele/language_explorer)
