from gtts import gTTS

# Example conversation text
conversation = """
Priya (PM):  
Thanks everyone for joining. The goal today is to finalize the Q1 roadmap. We need clarity on deadlines and ownership for the new analytics dashboard.

Meera (BA):  
From the business side, stakeholders want the dashboard live by the end of March. They emphasized that the KPI tracking module is the highest priority.

Arjun (Tech Lead):  
That’s doable, but we’ll need at least six weeks for backend integration. If we start next week, we can deliver by mid-March, leaving two weeks for QA.

Rahul (QA Lead):  
I’ll need a stable build by March 10th to run regression tests. If development slips, testing will be compressed, which increases risk.

Priya (PM):  
So action items: Arjun’s team starts backend integration on Feb 10th. Rahul prepares the test plan by Feb 20th. Meera, can you draft user stories by next Monday?

Meera (BA):  
Yes, I’ll have them ready by Feb 9th.

Arjun (Tech Lead):  
One blocker: we still don’t have API documentation from the vendor. Without it, integration will stall.

Priya (PM):  
I’ll escalate with procurement today. Let’s set a deadline: vendor must deliver docs by Feb 12th.

Rahul (QA Lead):  
If that slips, we’ll need to adjust timelines. I’ll flag it in the risk register.
Priya (PM):  
Perfect. Let’s summarize:

Backend integration starts Feb 10th (Arjun).

User stories ready by Feb 9th (Meera).

QA test plan by Feb 20th (Rahul).

Vendor API docs by Feb 12th (Priya to follow up).

Anything else before we close?

Meera (BA):  
No, that covers it. Thanks.

Arjun (Tech Lead):  
All good.

Rahul (QA Lead):  
Ready to proceed.
"""

# Convert to speech
tts = gTTS(conversation, lang="en")
tts.save("conversation.mp3")  # creates an audio file
