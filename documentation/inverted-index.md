# Inverted Index

`ts_type_filter` uses a simple inverted index, written in Python.
It includes a demo based on [154 Shakespeare sonnets](https://en.wikipedia.org/wiki/Shakespeare%27s_sonnets) obtained from [Project Gutenberg](https://www.gutenberg.org/ebooks/1041).

## Building

1. Verify you have python version >=3.12. Note that 3.13 may not be supported yet.
1. `pip install poetry` outside of any virtual environment.
2. `git clone https://github.com/MikeHopcroft/ts_type_filter.git`
3. `cd ts_type_filter`
4. `python -m venv .venv`
5. `.venv\Scripts\activate`
6. `poetry install --no-root`

## Running the Query Sample

The `query` sample demonstrates building an index of the 154 sonnets
and running a disjunctive query against the index. Here's an example of
a query for the word `"same"` that matches Sonnets **V**, **L**, and **LXIX**.

~~~
% query same
Search results for 'same':
Found 3 results:

Sonnet V

Those hours, that with gentle work did frame
The lovely gaze where every eye doth dwell,
Will play the tyrants to the very **same**
And that unfair which fairly doth excel;
For never-resting time leads summer on
To hideous winter, and confounds him there;
Sap checked with frost, and lusty leaves quite gone,
Beauty o’er-snowed and bareness every where:
Then were not summer’s distillation left,
A liquid prisoner pent in walls of glass,
Beauty’s effect with beauty were bereft,
Nor it, nor no remembrance what it was:
    But flowers distill’d, though they with winter meet,
    Leese but their show; their substance still lives sweet.

Sonnet L

How heavy do I journey on the way,
When what I seek, my weary travel’s end,
Doth teach that ease and that repose to say,
‘Thus far the miles are measured from thy friend!’
The beast that bears me, tired with my woe,
Plods dully on, to bear that weight in me,
As if by some instinct the wretch did know
His rider lov’d not speed, being made from thee:
The bloody spur cannot provoke him on,
That sometimes anger thrusts into his hide,
Which heavily he answers with a groan,
More sharp to me than spurring to his side;
    For that **same** groan doth put this in my mind,
    My grief lies onward, and my joy behind.

Sonnet LXIX

Those parts of thee that the world’s eye doth view
Want nothing that the thought of hearts can mend;
All tongues, the voice of souls, give thee that due,
Uttering bare truth, even so as foes commend.
Thy outward thus with outward praise is crown’d;
But those **same** tongues, that give thee so thine own,
In other accents do this praise confound
By seeing farther than the eye hath shown.
They look into the beauty of thy mind,
And that in guess they measure by thy deeds;
Then churls their thoughts, although their eyes were kind,
To thy fair flower add the rank smell of weeds:
    But why thy odour matcheth not thy show,
    The soil is this, that thou dost common grow.

Total of 3 results found.
~~~

Here's a query that matches documents with `"thrall"` or `"quench"`. Note that you must wrap the query in quotes so that the shell puts all of the words into the first command-line parameter.

~~~
% query "thrall quench"
Search results for 'thrall quench':
Found 2 results:

Sonnet CXXIV

If my dear love were but the child of state,
It might for Fortune’s bastard be unfather’d,
As subject to Time’s love or to Time’s hate,
Weeds among weeds, or flowers with flowers gather’d.
No, it was builded far from accident;
It suffers not in smiling pomp, nor falls
Under the blow of **thralled** discontent,
Whereto th’ inviting time our fashion calls:
It fears not policy, that heretic,
Which works on leases of short-number’d hours,
But all alone stands hugely politic,
That it nor grows with heat, nor drowns with showers.
    To this I witness call the fools of time,
    Which die for goodness, who have lived for crime.

Sonnet CLIV

The little Love-god lying once asleep,
Laid by his side his heart-inflaming brand,
Whilst many nymphs that vow’d chaste life to keep
Came tripping by; but in her maiden hand
The fairest votary took up that fire
Which many legions of true hearts had warm’d;
And so the general of hot desire
Was, sleeping, by a virgin hand disarm’d.
This brand she **quenched** in a cool well by,
Which from Love’s fire took heat perpetual,
Growing a bath and healthful remedy,
For men diseased; but I, my mistress’ thrall,
    Came there for cure and this by that I prove,
    Love’s fire heats water, water cools not love.

Total of 2 results found.
~~~

## Running the Stats Sample

This sample prints out statistics about the index, including a term frequency table.

Note that at the tail end of the table, that some of the rarest terms contain punctuation. This is a result of the naive
whitespace word breaker.

~~~
% stats | more
Number of documents: 154
Number of unique words: 4034
Number of postings: 13044

Word Frequency Table:
sonnet: 154
and: 148
to: 146
in: 139
the: 135
of: 134
that: 130
my: 117
i: 110
but: 108
with: 98

... many more lines ...

cool: 1
chast: 1
cliv: 1
nymph: 1
by;: 1
perpetual,: 1
warm'd;: 1
heart-inflam: 1
quench: 1
disarm'd.: 1
diseased;: 1
vow'd: 1
love-god: 1
thrall,: 1
votari: 1
sleeping,: 1
by,: 1
virgin: 1
legion: 1
trip: 1
asleep,: 1
~~~
