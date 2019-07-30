<!-- 
.. title: Bible Translation Confidence
.. slug: bible-translation-confidence
.. date: 2018-10-03 11:50:11 UTC+10:00
.. spellcheck_exceptions: Hartley,ConnectBox,repo,Github
.. tags: 
.. stylesheet_urls: /translation-confidence/css/translation-confidence.css,/translation-confidence/css/bigfoot-number.css
.. script_urls: /translation-confidence/js/jquery-2.2.4.min.js,/translation-confidence/js/bigfoot.min.js,/translation-confidence/js/translation-confidence.js
.. link: 
.. description: 
.. type: text
.. template: project.tmpl
-->

# Background

While scholars agree on the translation of most passages in scripture, some chapters and verses are difficult to translate and there are varying levels of consensus on the meaning of the text. While reading _The New International Commentary of the Old Testament - The Book of Job_ by John E. Hartley, I realised that my application of scripture would be helped if I understood the degree of confidence that scholars have in the translation that I'm reading. This is a proof-of-concept of an inline indicator of translation confidence. It shows footnotes from the commentary and the purpose of the footnote, either a clarification with no impact to meaning, some disagreement as to the correctness of the translation or a significant disagreement as to the correctness of the translation.

This proof-of-concept shows part of chapter 30 from the book of Job, with text and notes from _The New International Commentary of the Old Testament - The Book of Job_ by John E. Hartley.

# Components of Confidence

* Text: How agreed the scholars are on what was actually written in the original text. Lack of consensus may be because of a word that seems out of place, or looks like it may have transcription errors based on content.
* Translation: Lack of consensus may be because the word is unfamiliar, uncommon in this context
* Meaning: Often because of problems with translation, but may also happen because of turns of phrase that are unfamiliar or not understood


# Legend
Bundling all the components of confidence gives the following legend:

* <span class="clarification">Consensus, with elaboration in footnotes</span>: There is consensus on the translation and the footnotes provide additional information
* <span class="minor">Some consensus</span>: There is some consensus on the translation and the footnotes explain diverging opinion
* <span class="major">Little/no consensus</span>: There is little consensus on the translation and the footnotes explain diverging opinion

Open the footnote references to show the translation notes.

<div class="passage">
<div class="initial-verse-line"><span class="verse-number">16</span>Now my soul is emptied from me;</div>
<div class="additional-verse-line">days of affliction seize me.</div>
<div class="initial-verse-line"><span class="verse-number">17</span><span class="minor">At night God</span><sup id="fnref:1"><a href="#fn:1" rel="footnote">1</a></sup> painfully pierces my bonds,</div>
<div class="additional-verse-line">and <span class="minor">my veins</span><sup id="fnref:2"><a href="#fn:2">2</a></sup> do not sleep.</div>
<div class="initial-verse-line"><span class="verse-number">18</span> With great force <span class="clarification">he</span><sup id="fnref:3"><a href="#fn:3">3</a></sup> <span class="minor">seizes</span><sup id="fnref:4"><a href="#fn:4">4</a></sup> my clothing</div>
<div class="additional-verse-line">and girds me about <span class="minor">like the collar of</span><sup id="fnref:5"><a href="#fn:5">5</a></sup> my tunic</div>
<div class="initial-verse-line"><span class="verse-number">19</span><span class="clarification">He</span><sup id="fnref:6"><a href="#fn:6">6</a></sup> <span class="minor">has cast me</span><sup id="fnref:7"><a href="#fn:7">7</a></sup> into the mire;</div>
<div class="additional-verse-line">I have become as dust and ashes.</div>
<div class="initial-verse-line"><span class="verse-number">20</span>I cry to you, but you do not answer me;</div>
<div class="additional-verse-line">I stand, but you do <span class="clarification">not</span><sup id="fnref:8"><a href="#fn:8">8</a></sup> heed me.</div>
<div class="initial-verse-line"><span class="verse-number">21</span>You have grown cruel toward me;</div>
<div class="additional-verse-line">with your strong hand you act hatefully against me.</div>
<div class="initial-verse-line"><span class="verse-number">22</span>You lift me up and mount me on the wind;</div>
<div class="additional-verse-line">you toss me about <span class="minor">with a tempest</span>.<sup id="fnref:10"><a href="#fn:10">10</a></sup></div>
<div class="initial-verse-line"><span class="verse-number">23</span>I know that you will bring me to death,</div>
<div class="additional-verse-line">to the meeting house for all the living.”</div>
<div class="initial-verse-line"><span class="verse-number">24</span>“<span class="major">Yet God does not stretch out his hand in destruction,</span></div>
<div class="additional-verse-line"><span class="major">if one cries to him for help in his disaster</span>.<sup id="fnref:11"><a href="#fn:11">11</a></sup></div>
<div class="initial-verse-line"><span class="verse-number">25</span>Did I not weep for him whose day was hard?</div>
<div class="additional-verse-line">Was not my soul <span class="clarification">grieved</span><sup id="fnref:12"><a href="#fn:12">12</a></sup> for the poor?</div>
<div class="initial-verse-line"><span class="verse-number">26</span><span class="clarification">But</span><sup id="fnref:13"><a href="#fn:13">13</a></sup> when I looked for good, evil came;</div>
<div class="additional-verse-line">when I hoped for light, darkness came.</div>
<div class="initial-verse-line"><span class="verse-number">27</span>My bowels boil unceasingly;</div>
<div class="additional-verse-line">days of affliction meet me.</div>
<div class="initial-verse-line"><span class="verse-number">28</span>I go about blackened, but <span class="minor">not by the sun</span>;<sup id="fnref:14"><a href="#fn:14">14</a></sup></div>
<div class="additional-verse-line">I stand in the assembly and <span class="clarification">cry for help</span>.<sup id="fnref:15"><a href="#fn:15">15</a></sup></div>
<div class="initial-verse-line"><span class="verse-number">29</span>I am a brother of jackals</div>
<div class="additional-verse-line">and a companion of ostriches.</div>
<div class="initial-verse-line"><span class="verse-number">30</span>My skin blackens and peels;</div>
<div class="additional-verse-line"><span class="clarification">my body</span><sup id="fnref:16"><a href="#fn:16">16</a></sup> burns with fever.</div>
<div class="initial-verse-line"><span class="verse-number">31</span>My lyre is tuned to wailing,</div>
<div class="additional-verse-line">and my flute to <span class="minor">the voice of mourners</span>.”<sup id="fnref:17"><a href="#fn:17">17</a></sup></div>
</div>

<div class="footnotes"><ol>
    <li class="footnote" id="fn:1">
        <p>In this verse God, the cause of all Job's afflication, is assumed to be the undefined subject of “pierce” <i>(niqqar)</i>. Two other possibilities of treating MT <i>niqqar</i> are to take <i>laylâ</I>, “night”, as its subject or to revocalize it as Pual, <i>nuqqar</i>, with <i>‘ªṣāmay</i>, “my bones,” as its subject: “At night my bones are pierced with pains.”<a href="#fnref:1" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:2">
        <p>Of the many suggestions for MT <i>‘ōrᵉqay</i>, two are more likely. One is “my veins,” gained from the Arab. <i>ᵉirq</i>, “veins and sinews” (Tur-Sinai, Gordis). This view has the advantage of having a part of the body parallel to “bones.” The other is “my gnawing pains.” based on a gonate root in Syriac and Arabic. A major problem with this position is that since the Syriac version translates the word here “my body,” the Syriac translators did not equate <i>‘ōrᵉqay</i> with the same root in their language.<a href="#fnref:2" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:3">
        <p>The subject of the very <i>yiṯḥappēś</i>, “he seizes,” is either indefinite, alluding to the disease, or God (Pope, NIV). Either way God is the final cause and thus is accepted as the subject.<a href="#fnref:3" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:4">
        <p>For MT <i>yiṯḥappēś</i>, “disguise oneself,” Dhorme, Fohrer, and Pope read <i>yiṯpōś</i>, “he seizes,” based on LXX. But Gordis thinks that Heb. <i>ḥāpaś</i> may be a phonetic variant of <i>ḥāḇaš</i>, “bind up.” He argues that the Hithpael arose as a conflation of second and third person forms by reason of the shift from third person (vv. 17, 19) to second person (vv. 20-23).<a href="#fnref:4" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:5">
        <p>Some (e.g., Pope and Gordis) think that for <i>kᵉpî</i>, “like the collar of,” it is better to read <i>bᵉpî</i>, “by the collar of.” Since it is possible to make sense out of MT, it is better not to emend the text.<a href="#fnref:5" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:6">
        <p>Since the first line is unusually short, Pope may be correct in supplying “God” as the subject.<a href="#fnref:6" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:7">
        <p>Many (e.g. Duhm, Hölscher, Fohrer) believe the verb <i>hōrānî</i>, “throw me,” often use of shooting arrows, is an error of haplography for <i>hōriḏanî</i>, “he has sent me down.” This view is possible, but not compelling.<a href="#fnref:7" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:8">
        <p>It seems best to read <i>lō’</i>, “not,” or <i>wᵉlō’</i>, “and not.” before <i>tiṯbōnen</i>, with Vulg. (so Dhorme, Rowley)<a href="#fnref:8" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:10">
        <p>The Qere <i>tušîyâ</i>, “success,” is less preferable than the Ketib <i>tᵉšuwwâ</i> as a variant spelling of <i>tᵉšu’â</i>, “noise, roar” (of a storm) (cf. 36:29, 39:7). Dhorme takes it as subject, but it is possible to interpret it as the accusative of place (Gordis).<a href="#fnref:10" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:11">
         <p>Verse 24 is very difficult and has received numerous reconstructions. For MT <i>‛î</i>, “heap,” Pope and Dhorme read <i>‛ānî</i>, “needy, afflicted”: “One does not turn his hand against the needy, when in distress he cries fo help.” Hakam takes <i>bᵉ‛î</i> as equivalent to a common Aramaic word for “prayer, request” (cf. Dan. 6:8, 14 [Eng. 7, 13]), with the preposition <i>bᵉ</i> omitted for assonance. This word parallels <i>šûaᵉ</i> in the second line, which is elliptical for <i>ᵉāraḵ šûaᵉ</i>, “cry for help.” As for the antecedent of <i>lāhen</i>, “to them,” Hakam identifies them as “death” and Sheol (“meeting house”) in v. 23 and “hand” in v. 24a, and he reasons that <i>lāhen</i> is a feminine plural, for <i>šᵉ’ôl</i> and <i>yāḏ</i> are feminine: “Surely God does not bring death by petitiion, If in his distress one cries for them (i.e., death, its instrument and its abode).” Although this interpretation is somewhat strained, it has the advantage of reading the existing text.</p>
        <p>Gaining a clue from T.B. <i>Aboda Zara</i> 4a, Grabbe (<i>Comparative Philology</i>, pp. 101-103), believes that <i>‛î</i> could mean “destruction”: “Indeed let him not send (his) hand with (complete) destruction/ruin if in his calamity there is accordingly a cry (for help).” This suggestion, too, has the advantage of no textual change plus some rabbinic support. This view of <i>‛î</i> is accepted tentatively, but it seems best to find <i>lōh yᵉšawwēaᵉ</i>, “one cries to him,” in <i>lāhen šûaᵉ</i> (see BHS). Such a view takes the <i>n</i> as a scribal error rising from the coalescing of an <i>h</i> and a <i>y</i>.<a href="#fnref:11" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:12">
         <p>The meaning of <i>ᵉāgam</i>, “be grieved,” is clear from its use in Mishnaic Hebrew. Perhaps this word occurs in the Ugraritic text Krt 26-27: <i>yᵉrb bḥdrh ybky bṯn []gmm wydmᵉ</i>, “He entered his chamber to weep; while repeating his grief, he shed tears” (cf. A. Ceresko, <i>Job 29-31</i>, pp. 91-92).<a href="#fnref:12" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:13">
         <p>Gordis suggests that the <i>kî</i> gives reason for v. 27.<a href="#fnref:13" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:14">
         <p>The expresssion <i>bᵉlō’ ḥammâ</i>, “without the sun,” may be elliptical for “without the light of the sun” (Delitzsch), or it may mean that one’s face is covered so that he does not see the sun (Hakam). Duhm, Budde, and Fohrer read <i>bᵉlō’ neḥāmâ</i>, “where there was no comfort.” Although this change makes excellent sense, both LXX (despite its own textual problem) and Syr. read the same consonants as MT, which is thus retained.<a href="#fnref:14" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:15">
        <p>The use of the imperfect <i>’ªšawwēaᵉ</i>, “I cry for help,” after the perfect <i>qamtî</i>, “I stand,” comes close to having the sense of a final clause (Driver-Gray; GKC, § 120c; Driver, <i>Hebrew Tenses</i>, § 163).<a href="#fnref:15" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:16">
        <p>Dhorme shows that <i>‛aṣmî</i> (lit. “my bone[s]”) in the singular denotes one’s frame; cf. Ps 102:6 (Eng. 5): “My frame <i>[‛aṣmî]</i> cleaves to my flesh.”<a href="#fnref:16" title="return to article"> ↩</a></p>
    </li>
    <li class="footnote" id="fn:17">
        <p>Gordis suggests that <i>bōḵîm</i>, “those who weep,” may be an abstract noun, “weeping,” parallel to <i>’ēḇel</i>, “mourning.”<a href="#fnref:17" title="return to article"> ↩</a></p>
    </li>
</ol></div>


Source code is available in my [Github repo](https://github.com/edwinsteele/translation-confidence).

Please let me know if you are aware of any translations with any sort of confidence indicator.
