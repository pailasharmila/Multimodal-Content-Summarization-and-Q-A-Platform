# preprocessor.py
import re

def preprocess_transcript(raw_text: str) -> str:
    """
    Cleans a raw transcript text by removing timestamps,
    bracketed artifacts, and de-duplicating lines.
    
    This will clean text from both YouTube captions (Sample 1)
    and raw ASR (Sample 2).
    """
    
    # 1. Remove all timestamps and VTT-style tags (e.g., <00:00:00.000> or <c>)
    text = re.sub(r"<.*?>", "", raw_text)
    
    # 2. Remove all bracketed artifacts (e.g., [Music] or [Laughter])
    text = re.sub(r"\[.*?\]", "", text)
    
    # 3. Handle duplicate lines from caption formats and empty lines
    cleaned_lines = []
    seen = set()
    
    for line in text.splitlines():
        # Get rid of leading/trailing whitespace
        cleaned_line = line.strip()
        
        # If the line has content and we haven't seen it before, add it.
        # This handles both empty lines and the duplicate lines
        # found in your first sample.
        if cleaned_line and cleaned_line not in seen:
            cleaned_lines.append(cleaned_line)
            seen.add(cleaned_line)
    
    # 4. Join back into a single block of text
    print("--- Preprocessing Complete ---")
    ans= "\n".join(cleaned_lines)
    return ans

# --- ADDED TEST BLOCK ---
if __name__ == "__main__":
    
    print("--- TESTING SAMPLE 1 (YouTube Captions) ---")
    sample_text_1 = """
    [Music]
H<00:00:08.280><c> so</c><00:00:09.000><c> tight</c><00:00:10.000><c> to</c><00:00:10.280><c> the</c><00:00:10.480><c> RO</c><00:00:10.840><c> that</c><00:00:10.960><c> I'm</c><00:00:11.160><c> H</c>
H so tight to the RO that I'm H
from<00:00:13.960><c> off</c><00:00:14.320><c> this</c><00:00:15.199><c> island</c><00:00:16.199><c> this</c><00:00:16.400><c> was</c><00:00:16.520><c> an</c><00:00:16.760><c> Escape</c>
from off this island this was an Escape
Plan<00:00:18.480><c> Escape</c><00:00:19.480><c> carefully</c><00:00:20.359><c> timed</c><00:00:20.960><c> it</c><00:00:21.279><c> so</c><00:00:21.560><c> let</c><00:00:21.800><c> me</c>
Plan Escape carefully timed it so let me
go<00:00:23.800><c> and</c><00:00:24.039><c> dive</c><00:00:24.279><c> into</c><00:00:24.599><c> the</c><00:00:24.760><c> waves</c>
go and dive into the waves
below<00:00:27.240><c> who</c><00:00:27.519><c> turns</c><00:00:28.119><c> the</c>
below who turns the
who<00:00:30.400><c> fixes</c><00:00:31.119><c> up</c><00:00:31.439><c> the</c><00:00:32.000><c> cables</c><00:00:33.000><c> emotional</c>
who fixes up the cables emotional
torture<00:00:35.719><c> from</c><00:00:35.920><c> the</c><00:00:36.200><c> h</c><00:00:37.079><c> high</c><00:00:37.600><c> table</c><00:00:38.600><c> who</c>
torture from the h high table who
fetches<00:00:39.559><c> the</c>
fetches the
water<00:00:41.399><c> from</c><00:00:41.600><c> the</c><00:00:41.840><c> rocky</c><00:00:42.480><c> mountain</c><00:00:43.399><c> spring</c><00:00:44.399><c> and</c>
water from the rocky mountain spring and
walk<00:00:45.160><c> back</c><00:00:45.440><c> down</c><00:00:45.840><c> again</c><00:00:46.399><c> to</c><00:00:46.600><c> feel</c><00:00:47.120><c> your</c><00:00:47.440><c> words</c>
walk back down again to feel your words
and<00:00:48.320><c> the</c><00:00:48.640><c> Shar</c>
and the Shar
sting<00:00:51.480><c> and</c><00:00:51.600><c> I'm</c><00:00:51.920><c> getting</c><00:00:52.399><c> [&nbsp;__&nbsp;]</c>
sting and I'm getting [&nbsp;__&nbsp;]
tired<00:00:55.760><c> in</c><00:00:55.960><c> my</c><00:00:56.280><c> eyes</c><00:00:56.600><c> are</c><00:00:56.879><c> bursting</c><00:00:57.600><c> if</c><00:00:57.760><c> I</c><00:00:58.120><c> of</c>
tired in my eyes are bursting if I of
would<00:00:59.160><c> that</c><00:00:59.359><c> be</c><00:00:59.519><c> the</c><00:00:59.640><c> worst</c>
would that be the worst
somebody<00:01:01.440><c> I</c><00:01:01.719><c> thought</c><00:01:02.079><c> was</c><00:01:02.399><c> my</c><00:01:02.600><c> sa</c><00:01:03.199><c> sure</c><00:01:03.640><c> make</c>
somebody I thought was my sa sure make
me<00:01:04.040><c> do</c><00:01:04.600><c> a</c><00:01:04.799><c> whole</c><00:01:05.119><c> lot</c><00:01:05.239><c> of</c><00:01:05.519><c> Labor</c><00:01:06.280><c> the</c><00:01:06.479><c> C</c><00:01:07.200><c> on</c><00:01:07.400><c> my</c>
me do a whole lot of Labor the C on my
hands<00:01:08.119><c> is</c><00:01:08.320><c> cracking</c><00:01:09.000><c> if</c><00:01:09.640><c> love</c><00:01:10.000><c> end</c><00:01:10.439><c> would</c><00:01:10.640><c> that</c>
hands is cracking if love end would that
be<00:01:10.960><c> a</c><00:01:11.200><c> b</c><00:01:11.560><c> thing</c><00:01:12.240><c> and</c><00:01:12.400><c> the</c><00:01:12.640><c> silence</c><00:01:13.080><c> h</c><00:01:13.439><c> of</c><00:01:13.720><c> a</c>
be a b thing and the silence h of a
chamber<00:01:14.759><c> you</c><00:01:15.080><c> made</c><00:01:15.240><c> me</c><00:01:15.479><c> do</c><00:01:16.200><c> too</c><00:01:16.600><c> much</c>
chamber you made me do too much
[Music]
labor<00:01:27.600><c> too</c><00:01:28.000><c> much</c><00:01:28.400><c> labor</c>
labor too much labor
apologies<00:01:31.079><c> for</c><00:01:31.320><c> my</c>
apologies for my
tongue
never<00:01:35.720><c> busy</c><00:01:36.079><c> laughing</c><00:01:36.520><c> from</c>
never busy laughing from
flowing<00:01:38.720><c> and</c><00:01:38.920><c> stabbing</c><00:01:39.640><c> with</c>
flowing and stabbing with
your<00:01:41.920><c> I</c><00:01:42.040><c> know</c><00:01:42.200><c> you're</c><00:01:42.399><c> a</c><00:01:42.520><c> smart</c><00:01:43.360><c> I</c><00:01:43.520><c> know</c><00:01:43.720><c> you're</c>
your I know you're a smart I know you're
smart<00:01:45.200><c> and</c>
smart and
weapon<00:01:47.320><c> the</c><00:01:47.520><c> FSE</c><00:01:48.479><c> incompetence</c><00:01:49.479><c> it's</c>
weapon the FSE incompetence it's
dominance<00:01:50.840><c> under</c><00:01:51.439><c> a</c><00:01:51.960><c> guy</c><00:01:52.960><c> if</c><00:01:53.200><c> we</c><00:01:53.520><c> had</c><00:01:53.719><c> a</c>
dominance under a guy if we had a
to<00:01:55.799><c> I'd</c><00:01:56.200><c> watch</c><00:01:56.399><c> and</c><00:01:56.719><c> could</c><00:01:56.920><c> not</c><00:01:57.560><c> sa</c><00:01:58.560><c> the</c>
to I'd watch and could not sa the
emotional<00:01:59.560><c> to</c>
emotional to
from<00:02:01.680><c> the</c><00:02:01.960><c> head</c><00:02:02.200><c> of</c><00:02:02.439><c> your</c><00:02:02.840><c> high</c><00:02:03.280><c> table</c><00:02:04.280><c> she</c><00:02:04.600><c> do</c>
from the head of your high table she do
what<00:02:05.240><c> you</c><00:02:05.439><c> T</c><00:02:06.079><c> her</c><00:02:07.079><c> she</c><00:02:07.320><c> to</c><00:02:07.560><c> meet</c><00:02:07.880><c> the</c><00:02:08.080><c> same</c><00:02:08.440><c> cool</c>
what you T her she to meet the same cool
fade<00:02:10.000><c> so</c><00:02:10.520><c> now</c><00:02:10.879><c> I</c><00:02:11.120><c> got</c><00:02:11.400><c> to</c><00:02:11.720><c> run</c><00:02:12.360><c> so</c><00:02:12.720><c> I</c><00:02:12.879><c> can</c><00:02:13.280><c> undo</c>
fade so now I got to run so I can undo
this
mistake<00:02:17.400><c> at</c><00:02:17.680><c> least</c><00:02:18.239><c> I</c><00:02:18.599><c> got</c><00:02:18.720><c> to</c><00:02:19.440><c> try</c><00:02:20.440><c> look</c><00:02:20.640><c> upes</c>
mistake at least I got to try look upes
in<00:02:21.720><c> my</c><00:02:22.040><c> eyes</c><00:02:22.360><c> are</c><00:02:22.640><c> gting</c><00:02:23.319><c> if</c><00:02:23.519><c> I</c><00:02:23.879><c> love</c><00:02:24.319><c> di</c><00:02:24.760><c> would</c>
in my eyes are gting if I love di would
that<00:02:25.120><c> be</c><00:02:25.280><c> the</c><00:02:25.480><c> worst</c><00:02:25.840><c> thing</c><00:02:26.319><c> for</c><00:02:26.519><c> somebody</c><00:02:27.200><c> I</c>
that be the worst thing for somebody I
thought<00:02:27.840><c> was</c><00:02:28.080><c> my</c><00:02:28.360><c> sa</c><00:02:28.800><c> you</c><00:02:28.920><c> sure</c><00:02:29.360><c> make</c><00:02:29.519><c> it</c><00:02:29.640><c> to</c><00:02:30.280><c> a</c>
thought was my sa you sure make it to a
whole<00:02:30.800><c> lot</c><00:02:30.920><c> of</c><00:02:31.200><c> Labor</c><00:02:32.040><c> the</c><00:02:32.239><c> CIS</c><00:02:32.920><c> on</c><00:02:33.120><c> my</c><00:02:33.360><c> hands</c>
whole lot of Labor the CIS on my hands
is<00:02:34.040><c> cracking</c><00:02:34.760><c> if</c><00:02:34.959><c> I</c><00:02:35.360><c> love</c><00:02:35.720><c> ends</c><00:02:36.200><c> would</c><00:02:36.360><c> that</c><00:02:36.599><c> be</c>
is cracking if I love ends would that be
a<00:02:36.959><c> bad</c><00:02:37.319><c> thing</c><00:02:37.959><c> and</c><00:02:38.160><c> the</c><00:02:38.360><c> silence</c><00:02:38.840><c> on</c><00:02:39.200><c> of</c><00:02:39.480><c> a</c>
a bad thing and the silence on of a
chamber<00:02:40.519><c> you</c><00:02:40.800><c> make</c><00:02:40.959><c> me</c><00:02:41.239><c> do</c><00:02:41.879><c> too</c><00:02:42.280><c> much</c><00:02:42.760><c> labor</c>
chamber you make me do too much labor
day<00:02:44.120><c> everyday</c><00:02:44.800><c> therapist</c><00:02:45.480><c> brother</c><00:02:45.640><c> the</c><00:02:45.879><c> made</c>
day everyday therapist brother the made
Li<00:02:46.560><c> and</c><00:02:46.720><c> a</c><00:02:47.000><c> virgin</c><00:02:47.959><c> than</c><00:02:48.120><c> a</c><00:02:48.400><c> Serv</c><00:02:49.120><c> just</c><00:02:49.400><c> an</c>
Li and a virgin than a Serv just an
appendage<00:02:50.760><c> to</c><00:02:51.040><c> aend</c><00:02:51.560><c> him</c><00:02:51.920><c> so</c><00:02:52.280><c> that</c><00:02:52.400><c> he</c><00:02:52.680><c> never</c>
appendage to aend him so that he never
lifts<00:02:53.800><c> a</c><00:02:54.040><c> finger</c><00:02:55.040><c> 24/7</c><00:02:56.040><c> baby</c><00:02:56.480><c> machine</c><00:02:57.319><c> so</c><00:02:57.560><c> he</c>
lifts a finger 24/7 baby machine so he
can<00:02:57.920><c> live</c><00:02:58.280><c> out</c><00:02:58.800><c> his</c><00:02:58.959><c> picket</c><00:02:59.319><c> fence</c><00:02:59.599><c> dream</c>
can live out his picket fence dream
it's<00:03:00.800><c> not</c><00:03:01.000><c> an</c><00:03:01.280><c> act</c><00:03:01.519><c> of</c><00:03:01.800><c> love</c><00:03:02.120><c> if</c><00:03:02.319><c> you</c><00:03:02.640><c> make</c><00:03:03.000><c> her</c>
it's not an act of love if you make her
you<00:03:03.680><c> make</c><00:03:03.840><c> me</c><00:03:04.720><c> too</c><00:03:05.159><c> much</c><00:03:05.519><c> labor</c><00:03:06.200><c> all</c><00:03:06.640><c> day</c>
you make me too much labor all day
everyday<00:03:07.640><c> therapist</c><00:03:08.319><c> mother</c><00:03:08.680><c> maid</c><00:03:09.400><c> than</c><00:03:09.560><c> a</c>
everyday therapist mother maid than a
virgin<00:03:10.799><c> than</c><00:03:10.959><c> a</c><00:03:11.200><c> servant</c><00:03:12.000><c> just</c><00:03:12.239><c> an</c><00:03:12.519><c> appendage</c>
virgin than a servant just an appendage
live<00:03:13.599><c> to</c><00:03:13.920><c> attend</c><00:03:14.440><c> him</c><00:03:14.760><c> so</c><00:03:15.120><c> that</c><00:03:15.280><c> he</c><00:03:15.560><c> never</c>
live to attend him so that he never
lifts<00:03:16.680><c> a</c><00:03:16.920><c> finger</c><00:03:17.959><c> 247</c><00:03:18.959><c> baby</c><00:03:19.400><c> machine</c><00:03:20.239><c> so</c><00:03:20.440><c> he</c>
lifts a finger 247 baby machine so he
can<00:03:20.879><c> live</c><00:03:21.200><c> out</c><00:03:21.640><c> his</c><00:03:21.840><c> py</c><00:03:22.239><c> fence</c><00:03:22.560><c> dreams</c><00:03:23.400><c> it's</c>
can live out his py fence dreams it's
not<00:03:23.840><c> an</c><00:03:24.120><c> act</c><00:03:24.360><c> of</c><00:03:24.680><c> love</c><00:03:24.959><c> if</c><00:03:25.200><c> you</c><00:03:25.519><c> make</c><00:03:25.840><c> her</c><00:03:26.239><c> you</c>
not an act of love if you make her you
make<00:03:26.680><c> me</c><00:03:26.920><c> do</c><00:03:27.599><c> too</c><00:03:28.000><c> much</c><00:03:28.480><c> labor</c><00:03:29.480><c> thing</c>
[Music]
it's
not<00:03:49.120><c> you</c><00:03:49.360><c> make</c><00:03:49.519><c> me</c><00:03:49.760><c> do</c><00:03:50.439><c> too</c><00:03:50.879><c> much</c><00:03:51.239><c> labor</c>
    """
    cleaned_text_1 = preprocess_transcript(sample_text_1)
    print(cleaned_text_1)

    print("\n" + "="*40 + "\n")

    print("--- TESTING SAMPLE 2 (Raw ASR) ---")
    sample_text_2 = """
     I wanna be a fault container I will never run If you like your coffee, I'll Let me be a coffee, ma'am You call the shots, babe I just wanna be your Secrets I have held in my heart I've had too high than I thought Maybe I just wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be your own Let me be your lucky meter And I'll never run out Let me be the portable heater And charge it cold out I wanna be a setting lotion Won't you hear a deep deflection? At least as deep as the Pacific Ocean I wanna be your Secrets I have held in my heart I've had too high than I thought Maybe I just wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours I wanna be yours Won't be alone Won't be alone When the sun soul will roupa out He tried 13 years of concern You have simple And before You're only one being left to smile with You're only one being left to smile with You're only one being You're only one being left to smile with You're only one being left to smile with
    """
    cleaned_text_2 = preprocess_transcript(sample_text_2)
    print(cleaned_text_2)