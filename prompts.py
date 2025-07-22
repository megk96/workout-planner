# prompts.py

def workout_email_prompt(workout):
    return f"""
Write a lighthearted, funny, and motivational email to my friend Salad (he/him), who is rebuilding his fitness routine with daily 30-minute YouTube workouts. The tone should feel like a chaotic, loving gym buddy who also sends memes and root-for-you energy. It should balance humor, kindness, and consistency reinforcement.

Input Data:

Workout Title: {workout['title']}

Workout Type: {workout['type']}

Duration: {workout['duration']} minutes

YouTube Link: {workout['youtube_url']}

The email should include:
1. Quirky Opener (1–2 lines)
Set the vibe. Use irreverent humor, affectionate nicknames, or internet-coded affirmations.
Examples:
“Goooo SALAD 🥗 May you be as lean as your namesake and just as loved by influencer cali girls.”
“Good morning to everyone except boys who skip leg day. But not you. Never you. Couldn't be”
“Thanks for doing me a solid and beta testing this revolutionary new bicep-builder today.”

2. Workout Summary (2–3 lines)
Describe the workout in an exaggerated or silly way, while still making it clear what it’s about.
Examples:
“Today’s workout: {workout['title']} — a {workout['type']} session that’ll leave you 14% stronger, 60% hotter, and 100% in love with your own calves.”
“This one hits chest, back, and that mysterious muscle called ‘deltoids.’ No equipment. Just vibes.”
“Warning: may induce accidental swagger.”

3. Playful Closer (1–2 lines)
Reinforce the habit with humor and gentle hype.
Examples:
“You won’t regret this. You’ll only be late to work by 54 minutes — 30 for the workout, 24 to admire your pump.”
“10/10 people survived this workout. The other 90 were mysteriously not found.”
“Keep going. You’re not just building muscle, you’re building lore. You're not just reading a ChatGPT prompt, you're reading your destiny.”
Optional: Add memespeak, gym gremlin energy, or light absurdism to keep it unexpected and fun.
"""
